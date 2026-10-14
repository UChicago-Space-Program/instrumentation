import os
import urllib.request
import tkinter as tk
from tkinter import filedialog, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# main_gates.py's telemetry loop only writes a packet when tlm_count == 10,
# and tlm_count starts at 0 and is incremented (rather than checked-then-
# incremented) every other pass:
#   if tlm_count == 10: write(); tlm_count = 0
#   else: tlm_count += 1
# so tlm_count runs 0,1,2,...,10 (11 values) between writes -> 11 loop
# iterations per logged TLM row. The logger's Time field never increments,
# so each row instead gets a synthetic timestamp based on its position in
# the stream.
STEP = 11

IGNORED_KEYS = {"ID", "Time", "Checksum", "Terminator"}

# Display names for thermistors, taken from the wiring comments next to each
# Thermistor(adc, ch) line in hasp817/hasp/main_gates.py. Channels with no
# comment there keep their raw ThermN name.
THERM_DISPLAY_NAMES = {
    "Therm4": "Panel South",
    "Therm5": "Panel North",
    "Therm6": "L1 Therm 2",
    "Therm8": "L2 North",
    "Therm9": "Panel Top",
    "Therm10": "Panel East",
    "Therm11": "Panel West",
    "Therm12": "Pump South",
    "Therm13": "L2 South",
    "Therm14": "Pump North",
    "Therm15": "Pump Middle",
    "Therm24": "POPS",
    "Therm25": "L1 Therm 1",
    "Therm26": "24V Regulator",
    "Therm27": "12V Regulator",
    "Therm28": "5V Regulator",
    "Therm29": "6V Regulator",
    "Therm30": "Broken (Therm30)",
    "Therm31": "Broken (Therm31)",
    "Therm32": "Thermocouple",
    "Therm33": "RTD",
}


def display_name(key):
    return THERM_DISPLAY_NAMES.get(key, key)


# main_gates.py stores therm ids 0-31 as round(temp * 10), but the
# thermocouple (id 32) and RTD (id 33) are stored raw, while
# Telem.make_tlm_packet() divides every Therm value by 10 when formatting
# the log line. So Therm32/Therm33 need to be scaled back up by 10 to be
# comparable in degrees to the rest of the thermistors.
SCALE_OVERRIDES = {
    "Therm32": 10,
    "Therm33": 10,
}

DEFAULT_LOG_URL = ""
POLL_INTERVAL_MS = 5000


def fetch_url_lines(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=15) as resp:
        text = resp.read().decode(errors="replace")
    return text.splitlines()


def parse_line(line):
    line = line.strip()
    if not line.startswith("TLM"):
        return None
    row = {}
    for field in line.split(",")[2:]:
        field = field.strip()
        if ":" not in field:
            continue
        key, _, value = field.partition(":")
        key = key.strip()
        if key in IGNORED_KEYS:
            continue
        try:
            row[key] = float(value.strip()) * SCALE_OVERRIDES.get(key, 1)
        except ValueError:
            continue
    return row or None


class PlotWindow:
    def __init__(self, master, app, label):
        self.app = app
        self.label = label

        name = display_name(label)

        self.top = tk.Toplevel(master)
        self.top.title(name)
        self.top.geometry("760x500")
        self.top.protocol("WM_DELETE_WINDOW", self._on_close)

        self.fig = Figure(figsize=(7, 4.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.line, = self.ax.plot([], [], color="C0")
        self.ax.set_xlabel(f"Sample # (synthetic time, step={STEP})")
        self.ax.set_ylabel(name)
        self.ax.set_title(name)
        self.ax.grid(True, alpha=0.3)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.top)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas, self.top)
        toolbar.update()

        self.refresh()

    def refresh(self):
        y = self.app.data.get(self.label, [])
        x = self.app.times[:len(y)]
        self.line.set_data(x, y)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()

    def is_alive(self):
        return bool(self.top.winfo_exists())

    def lift(self):
        self.top.lift()
        self.top.focus_force()

    def _on_close(self):
        self.app.forget_plot(self.label)
        self.top.destroy()

    def close(self):
        self.top.destroy()


class TlmPlotterApp:
    def __init__(self, root):
        self.root = root
        root.title("HASP 817 TLM Plotter")

        self.times = []
        self.data = {}
        self.columns_order = []
        self.loaded_files = []
        self.open_plots = {}
        self.label_buttons = {}
        self.auto_refresh_active = False
        self.auto_refresh_job = None

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_main_close)

    def _on_main_close(self):
        self._stop_auto_refresh()
        self.root.destroy()

    def _build_ui(self):
        top = tk.Frame(self.root, padx=8, pady=8)
        top.pack(fill="x")
        tk.Button(top, text="Load / Refresh Log File", command=self.load_files).pack(side="left", padx=4)

        url_row = tk.Frame(self.root, padx=8)
        url_row.pack(fill="x")
        tk.Label(url_row, text="URL:").pack(side="left")
        self.url_var = tk.StringVar(value=DEFAULT_LOG_URL)
        tk.Entry(url_row, textvariable=self.url_var).pack(side="left", fill="x", expand=True, padx=4)
        tk.Button(url_row, text="Load from URL", command=self.load_from_url).pack(side="left", padx=2)
        self.auto_refresh_btn = tk.Button(url_row, text="Start Auto-Refresh", command=self.toggle_auto_refresh)
        self.auto_refresh_btn.pack(side="left", padx=2)

        self.status_var = tk.StringVar(value="No data loaded.")
        tk.Label(self.root, textvariable=self.status_var, anchor="w", padx=8, justify="left").pack(fill="x")

        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, borderwidth=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.button_frame = tk.Frame(canvas)
        self.button_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.button_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_files(self):
        # Each log file is cumulative (previous contents plus whatever's new),
        # so a (re)load always replaces the dataset rather than appending to it.
        paths = filedialog.askopenfilenames(
            title="Load TLM log file(s)",
            filetypes=[("Log files", "*.log *.txt"), ("All files", "*.*")],
        )
        if not paths:
            return
        self._stop_auto_refresh()
        self._reset()
        self._ingest_files(paths)

    def load_from_url(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Enter a log file URL first.")
            return
        self._fetch_and_store(url)

    def toggle_auto_refresh(self):
        if self.auto_refresh_active:
            self._stop_auto_refresh()
        else:
            self._start_auto_refresh()

    def _start_auto_refresh(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Enter a log file URL first.")
            return
        self.auto_refresh_active = True
        self.auto_refresh_btn.config(text="Stop Auto-Refresh")
        self._poll_url()

    def _stop_auto_refresh(self):
        self.auto_refresh_active = False
        self.auto_refresh_btn.config(text="Start Auto-Refresh")
        if self.auto_refresh_job is not None:
            self.root.after_cancel(self.auto_refresh_job)
            self.auto_refresh_job = None

    def _poll_url(self):
        self._fetch_and_store(self.url_var.get().strip())
        if self.auto_refresh_active:
            self.auto_refresh_job = self.root.after(POLL_INTERVAL_MS, self._poll_url)

    def _fetch_and_store(self, url):
        try:
            lines = fetch_url_lines(url)
        except Exception as e:
            self.status_var.set(f"Fetch failed ({e}). Will retry." if self.auto_refresh_active else f"Fetch failed: {e}")
            return
        self._reset()
        self._parse_and_store(lines)
        self.loaded_files.append(url.rsplit("/", 1)[-1])
        self._finish_ingest()

    def _reset(self):
        # Clears the data buffers so the next _ingest() call rebuilds them from
        # scratch. Open plot windows are left alone and keyed by label, so they
        # just refresh onto the reloaded data instead of closing.
        self.times.clear()
        self.data.clear()
        self.columns_order.clear()
        self.loaded_files.clear()
        for btn in self.label_buttons.values():
            btn.destroy()
        self.label_buttons.clear()

    def _ingest_files(self, paths):
        for path in sorted(paths):
            try:
                with open(path, "r", errors="replace") as f:
                    lines = f.readlines()
            except OSError as e:
                messagebox.showerror("Error reading file", f"{path}\n{e}")
                continue
            self._parse_and_store(lines)
            self.loaded_files.append(os.path.basename(path))
        self._finish_ingest()

    def _parse_and_store(self, lines):
        for line in lines:
            row = parse_line(line)
            if row is None:
                continue
            self.times.append(len(self.times) * STEP)
            for key, value in row.items():
                if key not in self.data:
                    self.data[key] = [float("nan")] * (len(self.times) - 1)
                    self.columns_order.append(key)
                    self._add_label_button(key)
                self.data[key].append(value)
            for key in self.columns_order:
                if len(self.data[key]) < len(self.times):
                    self.data[key].append(float("nan"))

    def _finish_ingest(self):
        recent = ", ".join(self.loaded_files[-3:])
        self.status_var.set(
            f"{len(self.loaded_files)} source(s) loaded, {len(self.times)} samples.\nMost recent: {recent}"
        )
        for win in self.open_plots.values():
            win.refresh()

    def _add_label_button(self, label):
        btn = tk.Button(
            self.button_frame, text=display_name(label), width=16, command=lambda l=label: self.open_plot(l)
        )
        row, col = divmod(len(self.label_buttons), 6)
        btn.grid(row=row, column=col, padx=3, pady=3)
        self.label_buttons[label] = btn

    def open_plot(self, label):
        existing = self.open_plots.get(label)
        if existing is not None and existing.is_alive():
            existing.lift()
            return
        self.open_plots[label] = PlotWindow(self.root, self, label)

    def forget_plot(self, label):
        self.open_plots.pop(label, None)


def main():
    root = tk.Tk()
    root.geometry("560x480")
    TlmPlotterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
