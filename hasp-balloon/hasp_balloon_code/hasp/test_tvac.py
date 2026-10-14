from hasp_lib import servo, sensor, gpio_expander
from hasp_lib.gpio_expander import GpioExpander
from hasp_lib.sensor import *
from hasp_lib.servo import ContinuousServo
#from hasp_lib.image import Camera
#from hasp_lib.pops import Pops
#from hasp_lib.hasp_comms import hasp_comms
from hasp_lib.pumps import Pump
import board
import busio
import digitalio
import csv
from datetime import datetime

import select
import sys
filename = "test1.csv"
fieldnames = ["timestamp", "Thermistors", "Thermocouple 1", "Thermocouple 2", "RTD","BMP", "Pump 1", "Pump 2"]
i2c_bus = busio.I2C(board.SCL, board.SDA)
spi_bus = busio.SPI(board.SCLK, board.MOSI, board.MISO)
adc1 = ADC_8Bit("adc 1", i2c_bus, 0x4A)
cs_tmc1 = digitalio.DigitalInOut(board.D5)
cs_tmc2 = digitalio.DigitalInOut(board.D6)
cs_rtd = digitalio.DigitalInOut(board.D13)
#cs_bmp = digitalio.DigitalInOut(board.D19)

therm1 = MAX31855(spi_bus, cs_tmc1)
therm2 = MAX31855(spi_bus, cs_tmc2)

rtd = MAX31865(spi_bus, cs_rtd)

#bmp = BMP388(spi_bus, cs_bmp)

gpio_ex = GpioExpander(i2c_bus, 0x23)

pump1 = Pump(gpio_ex, 1, 1)
pump2 = Pump(gpio_ex, 1, 2)


with open(filename, "w", newline="") as f:
    csv.DictWriter(f, fieldnames=fieldnames).writeheader()

while True:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    thermistor = adc1.read()
    therm1_read = therm1.read()
    therm2_read = therm2.read()

    rtd_read = rtd.read()
    bmp_read = "hi"

    pump1_stat = pump1.get_state()
    pump2_stat = pump2.get_state()

    print("Therm1 read: " + str(therm1_read))
    print("Therm2 read: " + str(therm2_read))
    print("Thermistor read: " + str(thermistor))
    print("RTD read: " + str(rtd_read))
  #  print("BMP: "+ str(bmp_read))

    row = {"timestamp": timestamp, "Thermistors": thermistor, "Thermocouple 1": therm1_read, "Thermocouple 2": therm2_read, "RTD": rtd_read, "BMP": bmp_read, "Pump 1": pump1_stat, "Pump 2": pump2_stat}

    with open(filename, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=fieldnames).writerow(row)
    
    
    ready, _, _ = select.select([sys.stdin], [], [], 2.0)

    if ready:
        line = sys.stdin.readline().strip()

        print(line)
        if line == "1":
            print("pump1 toggled")
            pump1.toggle()
        elif line == "2":
            print("pump2 toggled")
            pump2.toggle()


