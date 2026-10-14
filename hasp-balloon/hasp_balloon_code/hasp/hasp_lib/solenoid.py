import RPi.GPIO as GPIO
import time
class Solenoid:
    def __init__(self, gpio_to_open, gpio_to_close):
        self.gpio_to_open = gpio_to_open
        self.gpio_to_close = gpio_to_close
        self.state = "closed"
    def open_solenoid(self):
        GPIO.output(self.gpio_to_open, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(self.gpio_to_open, GPIO.LOW)
        self.state = "open"
    def close_solenoid(self):
        GPIO.output(self.gpio_to_close, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(self.gpio_to_close, GPIO.LOW)
        self.state = "closed"
    def get_state(self):
        return self.state



if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(24, GPIO.OUT)
    GPIO.output(24, GPIO.HIGH)
    GPIO.setup(19, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)
    GPIO.output(13, GPIO.LOW)
    sol = Solenoid(19, 13)
    sol.open_solenoid()
    print("hi")

   


