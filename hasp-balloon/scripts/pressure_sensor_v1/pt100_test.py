import time
import board
import digitalio
import adafruit_max31865

spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)   # BCM 5 (Pin 29)

rtd = adafruit_max31865.MAX31865(
    spi, cs,
    wires=3,
    rtd_nominal=100.0,
    ref_resistor=430.0
)

while True:
    print(f"T={rtd.temperature:8.2f} C | R={rtd.resistance:8.2f} ohm")
    time.sleep(1)
