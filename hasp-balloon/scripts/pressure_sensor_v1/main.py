import time
import board
import busio
import digitalio
import adafruit_max31865
import adafruit_bmp3xx
from w1thermsensor import W1ThermSensor

# SPI - PT100 (MAX31865)
spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)
rtd = adafruit_max31865.MAX31865(spi, cs, wires=3, rtd_nominal=100.0, ref_resistor=430.0)

# I2C - BMP388
i2c = busio.I2C(board.SCL, board.SDA)
bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)

# 1-Wire - DS18B20
ds = W1ThermSensor()

print("Reading sensors... (Ctrl+C to stop)\n")

while True:
    print(f"PT100:   {rtd.temperature:7.2f} °C  |  {rtd.resistance:7.2f} Ω")
    print(f"DS18B20: {ds.get_temperature():7.2f} °C")
    print(f"BMP388:  {bmp.temperature:7.2f} °C  |  {bmp.pressure:7.2f} hPa")
    print("-" * 45)
    time.sleep(1)
