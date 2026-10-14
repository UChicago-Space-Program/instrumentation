"""
Heater/thermistor association test.

For each heater, turns it on, samples all five heater-zone thermistors for a
while, turns it back off, samples again during cooldown, then reports which
thermistor actually responded. If the thermistor that heated up the most
isn't the one main.py assumes is paired with that heater, that's evidence of
a wiring/channel mismatch.

Run on the payload Pi (needs the same I2C/GPIO hardware as main.py).
"""
import argparse
import csv
import time
from datetime import datetime

import board
import busio

from hasp_lib.gpio_expander import GpioExpander
from hasp_lib.sensor import ADC_8Bit, Thermistor
from hasp_lib.heater import Heater

# Same addresses/pins as main.py
GPIO_EX_ADDR = 0x20
ADC_ADDRS = {"adc1": 0x48, "adc2": 0x49, "adc3": 0x4A, "adc4": 0x4B}

# (heater id, name, heater bank, heater pin, adc name, thermistor channel) — mirrors main.py
PAIRINGS = [
    (1, "heater1", 1, 6, "adc1", 0),
    (2, "heater2", 1, 7, "adc1", 2),
    (3, "heater3", 2, 4, "adc1", 4),
    (4, "heater4", 2, 3, "adc1", 6),
    (5, "heater5", 2, 2, "adc3", 4),
]


def build_hardware():
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    gpio_ex = GpioExpander(i2c_bus, GPIO_EX_ADDR)
    adcs = {name: ADC_8Bit(name, i2c_bus, addr) for name, addr in ADC_ADDRS.items()}

    heaters = {}
    thermistors = {}
    for hid, _hname, bank, pin, adc_name, chan in PAIRINGS:
        heaters[hid] = Heater(gpio_ex, bank, pin)
        thermistors[hid] = Thermistor(adcs[adc_name], chan)
    return heaters, thermistors


def read_all(thermistors):
    """Read every heater-zone thermistor; None on a failed read instead of raising."""
    readings = {}
    for hid, therm in thermistors.items():
        try:
            readings[hid] = therm.read()
        except (ValueError, OSError) as e:
            readings[hid] = None
            print(f"  [warn] thermistor {hid} read failed: {e}")
    return readings


def sample_phase(thermistors, duration_s, interval_s, label, log_rows, heater_id):
    """Sample all thermistors every interval_s for duration_s. Returns list of readings dicts."""
    samples = []
    elapsed = 0.0
    while elapsed <= duration_s:
        readings = read_all(thermistors)
        samples.append(readings)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        row = {"timestamp": ts, "phase": label, "heater_under_test": heater_id}
        row.update({f"thm{hid}": readings[hid] for hid in thermistors})
        log_rows.append(row)
        print(f"  [{label}] t={elapsed:5.1f}s " +
              " ".join(f"thm{hid}={v:.2f}C" if v is not None else f"thm{hid}=ERR"
                        for hid, v in readings.items()))
        time.sleep(interval_s)
        elapsed += interval_s
    return samples


def delta(samples):
    """Per-thermistor (last - first) using the first/last non-None reading available."""
    deltas = {}
    for hid in samples[0]:
        first = next((s[hid] for s in samples if s[hid] is not None), None)
        last = next((s[hid] for s in reversed(samples) if s[hid] is not None), None)
        deltas[hid] = None if (first is None or last is None) else last - first
    return deltas


def test_heater(hid, heater, thermistors, on_duration, off_duration, interval, log_rows):
    name = f"Heater {hid}"
    print(f"\n=== Testing {name} (expected pair: Thermistor {hid}) ===")

    try:
        print("Baseline read...")
        baseline = read_all(thermistors)

        print(f"Turning {name} ON for {on_duration}s...")
        heater.turn_on()
        on_samples = sample_phase(thermistors, on_duration, interval, "ON", log_rows, hid)
    finally:
        print(f"Turning {name} OFF.")
        heater.turn_off()

    print(f"Cooling down, sampling for {off_duration}s...")
    off_samples = sample_phase(thermistors, off_duration, interval, "OFF", log_rows, hid)

    on_deltas = delta([baseline] + on_samples)
    off_deltas = delta(off_samples)

    valid_on = {k: v for k, v in on_deltas.items() if v is not None}
    hottest = max(valid_on, key=valid_on.get) if valid_on else None
    hottest_rise = valid_on.get(hottest)

    return {
        "heater_id": hid,
        "expected_thermistor": hid,
        "on_deltas": on_deltas,
        "off_deltas": off_deltas,
        "hottest_thermistor": hottest,
        "hottest_rise": hottest_rise,
    }


def judge(result, rise_threshold):
    hid = result["heater_id"]
    expected_rise = result["on_deltas"].get(hid)

    if expected_rise is None:
        return "INCONCLUSIVE", f"Thermistor {hid} could not be read during the test."
    if result["hottest_thermistor"] is None:
        return "INCONCLUSIVE", "No thermistor produced a valid reading."
    if expected_rise < rise_threshold:
        return ("INCONCLUSIVE",
                f"Thermistor {hid} only rose {expected_rise:.2f}C (< {rise_threshold}C threshold) "
                "- heater may be weak, run longer, or thermistor may be faulty.")
    if result["hottest_thermistor"] != hid:
        return ("FAIL",
                f"Thermistor {result['hottest_thermistor']} rose the most "
                f"({result['hottest_rise']:.2f}C) instead of the expected Thermistor {hid} "
                f"({expected_rise:.2f}C). Possible wiring/channel swap.")
    return "PASS", f"Thermistor {hid} rose {expected_rise:.2f}C and was the largest riser, as expected."


def print_report(results, rise_threshold):
    print("\n" + "=" * 70)
    print("HEATER / THERMISTOR ASSOCIATION REPORT")
    print("=" * 70)
    verdicts = {}
    for r in results:
        verdict, reason = judge(r, rise_threshold)
        verdicts[r["heater_id"]] = verdict
        print(f"\nHeater {r['heater_id']}  ->  expected Thermistor {r['expected_thermistor']}")
        print("  ON-phase deltas (C): " +
              ", ".join(f"thm{k}={v:+.2f}" if v is not None else f"thm{k}=ERR"
                        for k, v in sorted(r["on_deltas"].items())))
        print("  OFF-phase deltas (C): " +
              ", ".join(f"thm{k}={v:+.2f}" if v is not None else f"thm{k}=ERR"
                        for k, v in sorted(r["off_deltas"].items())))
        print(f"  Verdict: {verdict} - {reason}")

    print("\n" + "-" * 70)
    print("SUMMARY")
    for hid, v in sorted(verdicts.items()):
        print(f"  Heater {hid}: {v}")
    print("-" * 70)
    return verdicts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--on-duration", type=float, default=45.0, help="seconds to hold each heater on")
    parser.add_argument("--off-duration", type=float, default=30.0, help="seconds to sample after turning off")
    parser.add_argument("--interval", type=float, default=3.0, help="seconds between samples")
    parser.add_argument("--rise-threshold", type=float, default=2.0, help="min C rise to count as a real response")
    parser.add_argument("--heaters", type=str, default="1,2,3,4,5", help="comma-separated heater ids to test")
    parser.add_argument("--log-csv", type=str, default=None, help="path to write raw time-series samples")
    args = parser.parse_args()

    heater_ids = [int(x) for x in args.heaters.split(",")]

    print("Building hardware interfaces (I2C/GPIO expander/ADCs)...")
    heaters, thermistors = build_hardware()

    log_rows = []
    results = []
    try:
        for hid in heater_ids:
            result = test_heater(
                hid, heaters[hid], thermistors,
                args.on_duration, args.off_duration, args.interval,
                log_rows,
            )
            results.append(result)
    finally:
        print("\nEnsuring all tested heaters are off...")
        for hid in heater_ids:
            heaters[hid].turn_off()

    print_report(results, args.rise_threshold)

    log_path = args.log_csv or f"heater_test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    if log_rows:
        fieldnames = list(log_rows[0].keys())
        with open(log_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(log_rows)
        print(f"\nRaw time-series samples written to {log_path}")


if __name__ == "__main__":
    main()
