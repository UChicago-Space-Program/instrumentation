import time
import busio
import digitalio
import board
"""
addr = 0x23


def config_io(bus_i2c, gpio_bus, pin, input_output): # output is 0, input is 1
    current_state = bytearray(1)
    register = 0x00
    if gpio_bus == 1:
        register = 0x00
    elif gpio_bus == 2:
        register = 0x01
    else:
        print("invalid bus assignment")
        exit(1)

    bus_i2c.writeto_then_readfrom(addr, bytes([register]), current_state)
    text = "".join(f"{b:08b}" for b in current_state)
    text = text[:7 - pin] + str(input_output) + text[7 - pin + 1:]

    write_bits = int(text, 2) 
    bus_i2c.writeto(addr, bytes([register, write_bits]))


def set_gpio(bus_i2c, gpio_bus, pin, low_high):
    current_state = bytearray(1)
    register = 0x12
    if gpio_bus == 1:
        register = 0x12
    elif gpio_bus == 2:
        register = 0x13
    else:
        print("invalid bus assignment")
        exit(1)

    bus_i2c.writeto_then_readfrom(addr, bytes([register]), current_state)
    text = "".join(f"{b:08b}" for b in current_state)
    text = text[:7 - pin] + str(low_high) + text[7 - pin + 1:]

    write_bits = int(text, 2) 
    bus_i2c.writeto(addr, bytes([register, write_bits]))

def get_gpio(bus_i2c, gpio_bus, pin):
    current_state = bytearray(1)
    register = 0x12
    if gpio_bus == 1:
        register = 0x12
    elif gpio_bus == 2:
        register = 0x13
    else:
        print("invalid bus assignment")
        exit(1)

    bus_i2c.writeto_then_readfrom(addr, bytes([register]), current_state)
    text = "".join(f"{b:08b}" for b in current_state)
    return int(text[7-pin])"""

class GpioExpander:
    def __init__(self, i2c_bus, addr):
        self.addr = addr
        self.i2c_bus = i2c_bus
    def config_io(self, gpio_bus, pin, input_output):
        current_state = bytearray(1)
        register = 0x00
        if gpio_bus == 1:
            register = 0x00
        elif gpio_bus == 2:
            register = 0x01
        else:
            print("invalid bus assignment")
            exit(1)
        self.i2c_bus.writeto_then_readfrom(self.addr, bytes([register]), current_state)
        text = "".join(f"{b:08b}" for b in current_state)
        text = text[:7 - pin] + str(input_output) + text[7 - pin + 1:]
        write_bits = int(text, 2)
        self.i2c_bus.writeto(self.addr, bytes([register, write_bits]))
    def set_gpio(self, gpio_bus, pin, low_high):
        current_state = bytearray(1)
        register = 0x12
        if gpio_bus == 1:
            register = 0x12
        elif gpio_bus == 2:
            register = 0x13
        else:
            print("invalid bus assignment")
            exit(1)
        self.i2c_bus.writeto_then_readfrom(self.addr, bytes([register]), current_state)
        text = "".join(f"{b:08b}" for b in current_state)
        text = text[:7 - pin] + str(low_high) + text[7 - pin + 1:]
        write_bits = int(text, 2)
        self.i2c_bus.writeto(self.addr, bytes([register, write_bits]))
    def get_gpio(self, gpio_bus, pin):
        current_state = bytearray(1)
        register = 0x12
        if gpio_bus == 1:
            register = 0x12
        elif gpio_bus == 2:
            register = 0x13
        else:
            print("invalid bus assignment")
            exit(1)
        self.i2c_bus.writeto_then_readfrom(self.addr, bytes([register]), current_state)
        text = "".join(f"{b:08b}" for b in current_state)
        return int(text[7-pin])

if __name__ == "__main__":
    print("testing GPIO expander")

    i2c_bus = busio.I2C(board.SCL, board.SDA)
    """config_io(i2c_bus, 1, 0, 0)
    current = get_gpio(i2c_bus,1,0)
    print(f"PA0 is currently at {current}")
    NOT = 0 if current else 1
    print(f"setting PA0 to {NOT}")
    set_gpio(i2c_bus, 1, 0, NOT)"""
    gpio_ex = GpioExpander(i2c_bus, 0x23)
    gpio_ex.config_io(1, 1, 0)
    current = gpio_ex.get_gpio(1, 1)
    print(f"PA0 is currently at {current}")
    NOT = 0 if current else 1
    print(f"setting PA0 to {NOT}")
    gpio_ex.set_gpio(1, 1, NOT)

