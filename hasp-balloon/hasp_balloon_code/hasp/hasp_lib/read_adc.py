import time
import busio
import digitalio
import board
from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15

addr = 0x23

i2c_bus = busio.I2C(board.SCL, board.SDA)

adc = ADS1115(i2c_bus)
#adc.mode = Mode.CONTINUOUS

chan = AnalogIn(adc, ads1x15.Pin.A0)

while True:
    print("current value:", chan.value, chan.voltage)
    time.sleep(0.2)
