from w1thermsensor import W1ThermSensor

sensor = W1ThermSensor()
print("DS18B20:", sensor.get_temperature(), "C")
