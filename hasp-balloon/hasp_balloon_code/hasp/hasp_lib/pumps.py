from .gpio_expander import GpioExpander
import time
import board
import busio
class Pump:
    def __init__(self, gpio_ex, gpio_bus, gpio_pin):
        self.gpio_pin = gpio_pin
        gpio_ex.config_io(gpio_bus, gpio_pin, 0)
        self.state = gpio_ex.get_gpio(gpio_bus, gpio_pin)
        self.gpio_bus = gpio_bus
        self.gpio_ex = gpio_ex


    def turn_on(self):
        self.gpio_ex.set_gpio(self.gpio_bus, self.gpio_pin, 1)
        self.state = 1
    def turn_off(self):
        self.gpio_ex.set_gpio(self.gpio_bus, self.gpio_pin, 0)
        self.state = 0
    def toggle(self):
        new_state = 0 if self.state == 1 else 1 
        self.gpio_ex.set_gpio(self.gpio_bus, self.gpio_pin, new_state)
        self.state = new_state
    def get_state(self):
        return self.state
if __name__ == "__main__":
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    gpio_ex = GpioExpander(i2c_bus, 0x20)
    # A:1 B:2
    # Pins 0-7
    pump1 = Pump(gpio_ex, 1, 0)
    pump2 = Pump(gpio_ex, 1, 1)
    pump3 = Pump(gpio_ex, 1, 2)
    pump4 = Pump(gpio_ex, 1, 3)
    pump5 = Pump(gpio_ex, 1, 4)
    pump6 = Pump(gpio_ex, 1, 5)
    pump7 = Pump(gpio_ex, 2, 5)
    pump8 = Pump(gpio_ex, 2, 6)
    pump9 = Pump(gpio_ex, 2, 7)
    pump1.turn_on()
    pump2.turn_on()
    pump3.turn_on()
    pump4.turn_on()
    pump5.turn_on()
    pump6.turn_on()
    pump7.turn_on()
    pump8.turn_on()
    pump9.turn_on()
    time.sleep(1)
    pump1.turn_off()
    pump2.turn_off()
    pump3.turn_off()
    pump4.turn_off()
    pump5.turn_off()
    pump6.turn_off()
    pump7.turn_off()
    pump8.turn_off()
    pump9.turn_off()
