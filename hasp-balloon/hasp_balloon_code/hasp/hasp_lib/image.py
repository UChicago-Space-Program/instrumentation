from picamera2 import Picamera2
from PIL import Image
import base64
import struct
import io
import time

class Camera:
    def __init__(self, num, header):
        self.header = header
        self.cam = Picamera2(num)
        config = self.cam.create_still_configuration()
        self.cam.configure(config)
        time.sleep(0.2)
        self._pending_image = None
        self._pending_offset = 0

    def start(self):
        self.cam.start()

    def capture(self, path):
        # Start autofocus
        print("hi")
        self.cam.set_controls({"AfMode": 1, "AfTrigger": 0})

        # Wait for AF to settle (poll metadata)
        t0 = time.perf_counter()
        print("hi")
        while True:
            md = self.cam.capture_metadata()
            print("hi2")
            state = md.get("AfState", None)
            print("hi")
            # Common: 2 = focused, 3 = failed (varies by version)
            if state in (2, 3):
                print("hi")
                break
            if time.perf_counter() - t0 > 1.0:
                print("hi")
                break

        self.cam.capture_file(path)
        print("hi")
        print("captured (AfState =", state, ")")


    def prepare_image(self, path="fast.jpg", max_size=(640, 480), quality=50):
        print("got here")
        self.capture(path)
        print("captured")
        img = Image.open(path)
        print("got here")
        img.thumbnail(max_size)
        print("got to thumbnail")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        self._pending_image = buf.getvalue()
        self._pending_offset = 0

    def send_next_chunk(self, hasp_comms_obj, chunk_size=92):
        if self._pending_image is None:
            return False
        total_len = len(self._pending_image)
        this_chunk = self._pending_image[self._pending_offset:self._pending_offset + chunk_size]

        frame = struct.pack(">H", self.header)
        frame += struct.pack(">I", total_len)
        frame += struct.pack(">I", self._pending_offset)
        frame += struct.pack(">H", len(this_chunk))
        frame += this_chunk
        frame += struct.pack(">H", 0x030D)
        hasp_comms_obj.write(frame)

        self._pending_offset += len(this_chunk)
        if self._pending_offset >= total_len:
            self._pending_image = None
            return False
        return True

    def send_all(self, hasp_comms_obj):
        total_len = len(self._pending_image)
        frame = struct.pack(">H", self.header)
        frame += struct.pack(">I", total_len)
        frame += self._pending_image
        frame += struct.pack(">H", 0x030D)
        hasp_comms_obj.write(base64.b64encode(frame) + b"\n")


    def close(self):
        self.cam.stop()
        self.cam.close()

    # Context manager support — even better
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.close()

if __name__ == "__main__":
    with Camera() as cam:
        cam.start()
        cam.capture(".")
