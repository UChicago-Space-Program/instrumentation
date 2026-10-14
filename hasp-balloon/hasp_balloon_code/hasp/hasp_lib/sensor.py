import time
import board
import math
import busio
import digitalio
import adafruit_bmp3xx
import adafruit_max31855
from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15
from digitalio import DigitalInOut, Direction
import adafruit_max31865
import adafruit_ads7830.ads7830
from adafruit_ads7830.analog_in import AnalogIn as AnalogIn30

class Sensor:
    def __init__(self, name):
        self.name = name
    def read(self):
        raise NotImplementedError
    def __enter__(self):
        return self
class SPI_Sensor(Sensor):
    def __init__(self, name, spi,cs):
        super().__init__(name)
        self.spi = spi
        self.cs = cs
class I2C_Sensor(Sensor):
    def __init__(self, name, i2c_bus, address):
        super().__init__(name)
        self.i2c_bus = i2c_bus
        self.address = address
class MAX31855(SPI_Sensor):
    def __init__(self, spi, cs):
        super().__init__("max31855", spi, cs)
        self.device = adafruit_max31855.MAX31855(spi, cs)
        print(cs)
    def read(self):
        return self.temperature()
    def temperature(self):
        return self.device.temperature

class BMP388(I2C_Sensor):
    def __init__(self, i2c_bus, addr):
        super().__init__("bmp388", i2c_bus, addr)
        self.device = adafruit_bmp3xx.BMP3XX_I2C(i2c_bus)
    def read(self):
        return self.device.pressure
    def read_temperature(self):
        return self.device.temperature
    def read_pressure(self):
        return self.device.pressure
#deprecated ADC
class ADS1115_myc(I2C_Sensor):
    def __init__(self, i2c_bus, address):
        super().__init__("ads1115", i2c_bus, address)
        adc = ADS1115(i2c_bus)
        self.chan1 = AnalogIn(adc, ads1x15.Pin.A0)
        self.chan2 = AnalogIn(adc, ads1x15.Pin.A1)
        self.chan3 = AnalogIn(adc, ads1x15.Pin.A2)
        self.chan4 = AnalogIn(adc, ads1x15.Pin.A3)
    def read(self):
        return self.chan1.voltage, self.chan2.voltage, self.chan3.voltage, self.chan4.voltage
    def read_channel(self, channel):
        if channel == 1:
            return self.chan1.voltage
        elif channel == 2:
            return self.chan2.voltage
        elif channel == 3:
            return self.chan3.voltage
        else:
            return self.chan4.voltage
#New ADC
class ADC_8Bit(I2C_Sensor):
    def __init__(self, name, i2c_bus, address):
        super().__init__( name, i2c_bus, address)
        self.chan_list = []
        adc = adafruit_ads7830.ads7830.ADS7830(i2c_bus, address=address, int_ref_power_down=True)
        for x in range(8):
            self.chan_list.append(AnalogIn30(adc, x))
    def read(self):
        result = []
        for chan in self.chan_list:
            result.append((chan.value * 3.3 / 65535)+0.02)
        return result 
    def read_chan(self, num):
        return (self.chan_list[num].value * 3.3 / 65535)+0.02
    def read_raw(self):
        result = []
        for chan in self.chan_list:
            result.append(chan.value)

        return result
class Thermistor:
    def __init__(self, adc, channel):
        self.adc = adc
        self.channel = channel
    def read(self):
        v_out = self.adc.read_chan(self.channel)
        # read_chan() applies a +0.02V calibration offset, so v_out can legitimately
        # reach ~3.32V when the thermistor resistance is very high (very cold / open).
        # Clamp to just under the divider rail so that case resolves to an extreme
        # cold reading instead of a math domain error.
        if not (0 < v_out < 3.32):
            raise ValueError(
                f"Thermistor channel {self.channel}: v_out={v_out!r} out of valid range (0, 3.32) - "
                "check for a disconnected sensor or bad ADC reading"
            )
        #print(v_out)
        v_out = min(v_out, 3.3 - 1e-6)
        r_therm = 10000 * v_out / (3.3 - v_out)
        temp_k = 1.0 / (1.0 / 298.15 + (1.0 / 3435) * math.log(r_therm / 10000))
        return temp_k - 273.15
class MAX31865(SPI_Sensor):
    def __init__(self, spi, cs):
        super().__init__("max31865", spi, cs)
        self.device = adafruit_max31865.MAX31865(spi, cs, wires = 3, rtd_nominal=100.0, ref_resistor=430.0)
    def read(self):
        return self.device.temperature
if __name__ == "__main__":
    spi = board.SPI()
    cs_rtd = digitalio.DigitalInOut(board.D6)
    cs_tmc1 = digitalio.DigitalInOut(board.D12)
    cs_tmc2 = digitalio.DigitalInOut(board.D25)
    cs_tmc3 = digitalio.DigitalInOut(board.D16)
    cs_tmc4 = digitalio.DigitalInOut(board.D20)
    cs_tmc5 = digitalio.DigitalInOut(board.D21)
    rtd = MAX31865(spi, cs_rtd)
    thermocouple1 = MAX31855(spi, cs_tmc1)
    thermocouple2 = MAX31855(spi, cs_tmc2)
    thermocouple3 = MAX31855(spi, cs_tmc3)
    thermocouple4 = MAX31855(spi, cs_tmc4)
    thermocouple5 = MAX31855(spi, cs_tmc5)
    print(rtd.read())
    print(thermocouple1.read())
    print(thermocouple2.read())
    print(thermocouple3.read())
    #print(thermocouple4.read())
    #print(thermocouple5.read())