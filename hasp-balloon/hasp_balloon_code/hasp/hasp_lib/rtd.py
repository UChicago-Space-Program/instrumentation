
import time
import busio
import digitalio
import board
import adafruit_max31865

#SPI - PT100
spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)
rtd = adafruit_max31865.MAX31865(spi, cs, wires = 3, rtd_nominal=100.0, ref_resistor=430.0)


while True:  # Simulate for 100 time steps
    pv = rtd.temperature # in real life replace this with sensor data
    print("current temp:", pv)
    time.sleep(0.1)
