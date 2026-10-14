import time
import atexit
from gpiozero import DigitalOutputDevice, OutputDevice

import digitalio
import RPi.GPIO as GPIO
class Plunger:
    def __init__(
        self,
        step_pin,
        dir_pin,
        en_pin=None,
        steps_per_rev=1600,   # 1.8 deg NEMA 17, full step
        pulse_us=5,          # STEP high-time in microseconds
    ):
        self.steps_per_rev = steps_per_rev
        self.pulse_s = pulse_us / 1_000_000.0

        # STEP: plain digital output we pulse manually
        self.step = DigitalOutputDevice(step_pin, initial_value=False)

        # DIR: on() = one direction, off() = the other
        self.dir = OutputDevice(dir_pin, initial_value=False)

        # EN is active LOW. active_high=False means .on() drives the pin LOW.
        # initial_value=False -> starts .off() -> pin HIGH -> motor disabled.
        self.en = en_pin
        if en_pin is not None:
            self.en = OutputDevice(en_pin, active_high=False, initial_value=False)

        
        



    # ---- power ---------------------------------------------------------
    def enable(self):
        if self.en is not None:
            self.en.on()      # drives EN LOW

    def disable(self):
        if self.en is not None:
            self.en.off()     # drives EN HIGH

    # ---- motion --------------------------------------------------------
    def set_direction(self, clockwise=True):
        if clockwise:
            self.dir.on()
        else:
            self.dir.off()

    def move_steps(self, n_steps, clockwise=True, rpm=60):
        """Move n_steps (full steps) at a constant speed."""
        self.set_direction(clockwise)

        steps_per_sec = (rpm / 60.0) * self.steps_per_rev
        period = 1.0 / steps_per_sec
        low_time = max(period - self.pulse_s, 0)
        print("in move steps")

        for x in range(int(n_steps)):
            
            self.step.on()
            time.sleep(self.pulse_s)
            self.step.off()
            time.sleep(low_time)

    def rotate_degrees(self, degrees, clockwise=True, rpm=60):
        print("in rotate degrees")
        n = round(self.steps_per_rev * (degrees / 360.0))
        self.move_steps(n, clockwise=clockwise, rpm=rpm)

    def rotate_revolutions(self, revs, clockwise=True, rpm=60):
        self.move_steps(round(self.steps_per_rev * revs),
                        clockwise=clockwise, rpm=rpm)

    def close(self):
        self.enable()
        for i in range(32):
            self.rotate_degrees(360, clockwise=False, rpm=30)
        self.rotate_degrees(180, clockwise=False, rpm=30)
        self.disable()
        
    def open(self):
        self.enable()
        for i in range(32):
            self.rotate_degrees(360, clockwise=True, rpm=30)
        self.rotate_degrees(180, clockwise=True, rpm=30)
        self.disable()

if __name__ == "__main__":
    plunger1 = Plunger(17, 27, 23)
    
    val = 0
    plunger1.close()

        


