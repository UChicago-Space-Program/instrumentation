import time
import busio
import digitalio
import board
import adafruit_max31865
from .gpio_expander import config_io, set_gpio, get_gpio

#think about this!!!!!!

#SPI - PT100
spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)
rtd = adafruit_max31865.MAX31865(spi, cs, wires = 3, rtd_nominal=100.0, ref_resistor=430.0)

# output for heaters
addr = 0x27


def turn_on_heaters(i2c_bus):
    get_gpio(i2c_bus, 1, 0, 0, 1)

def turn_off_heaters(i2c_bus):
    set_gpio(i2c_bus, 1, 0, 0, 0)
    
def pid_controller(setpoint, pv, kp, ki, kd, previous_error, integral, dt):
    error = setpoint - pv
    integral += error * dt
    derivative = (error - previous_error) / dt
    control = kp * error + ki * integral + kd * derivative
    return control, error, integral

def pwm(control, dt, i2c_bus):
    rate = control / 25
    print("heating!", rate)
    for i in range(2):
        turn_on_heaters(i2c_bus)
        time.sleep(0.05 * rate)
        turn_off_heaters(i2c_bus)
        time.sleep(0.05 * (1-rate))

def main():
    setpoint = 35  # Desired setpoint
    pv = 0  # Initial process variable
    kp = 1  # Proportional gain
    ki = 0.05  # Integral gain
    kd = 0.1  # Derivative gain
    previous_error = 0
    integral = 0
    dt = 0.1  # Time step

    time_steps = []
    pv_values = []
    control_values = []
    setpoint_values = []

    while True:  # Simulate for 100 time steps
        pv = rtd.temperature # in real life replace this with sensor data
        print("current temp:", pv)
        control, error, integral = pid_controller(setpoint, pv, kp, ki, kd, previous_error, integral, dt)
        #pv += control * dt  # Update process variable based on control output (simplified) in real life run heaters for this time
        previous_error = error

        #time_steps.append(i * dt)
        pv_values.append(pv)
        control_values.append(control)
        setpoint_values.append(setpoint)
        print(control)
        if control > 0:
            #print("heating!")
            pwm(control, dt, i2c_bus)
        #heaters.value=False


if __name__ == "__main__":
    main()
