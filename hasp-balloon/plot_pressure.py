#import board
#import busio
#import HSC_pressure
import time
import csv
import os
import matplotlib.pyplot as plt
from datetime import datetime
import u6
import numpy as np
from scipy import interpolate

#i2c = busio.I2C(board.SCL, board.SDA)
#hsc = HSC_pressure.HSC(i2c, addr=0x28, p_min=0.0, p_max=1.0)
x = []
y2 = []
y3 = []
y4 = []
y5 = []
y6 = []

plt.ion()  
fig, ax = plt.subplots()
plt.show(block=False)
csv_filename = f"pressure_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
csv_path = os.path.join(os.path.dirname(__file__), csv_filename)

with open(csv_path, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "v_out", "readings", "temp2", "temp3", "temp4", "temp5", "temp6"])

print(f"Logging to: {csv_path}")
#print(f"{'Timestamp':<25} {'Pressure (bar)':<18} {'Temperature (°C)'}")
#print("-" * 65)

volt_channels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
volt_channels = [0, 2,  4,  6, 8, 10]
all_ain = np.arange(0, 14)

a = u6.U6()

Resistance_Curve = np.array([85.423, 60.781, 43.65, 31.629, 23.118, 17.04,
    12.649, 9.4864, 7.1545, 5.4479, 4.1732, 3.2256, 2.5147, 1.9763,
    1.5649, 1.2481, 1.0, 0.80956, 0.65726, 0.53697, 0.44169, 0.36534,
    0.30327, 0.25313, 0.21271, 0.17962, 0.15219, 0.12949, 0.11067,
    0.094952, 0.08178, 0.07069, 0.061383, 0.053486, 0.04673, 0.040955,
    0.036006, 0.031747, 0.028097, 0.024935, 0.022176, 0.019772, 0.017683]) * 1000.0
Temperature_Curve = np.linspace(-55, 155, 43)
r_to_temp = interpolate.interp1d(Resistance_Curve, Temperature_Curve)

def returnvolt(ain = all_ain):
    """
    Function that returns voltages of specified AIN. If no AIN are specified, it returns the voltages of all AIN, 0-13.

    Inputs:
        ain: list of AIN numbers. default is all AIN
    
    Outputs:
        v_out: all voltages read
    """
    v_out = []
    for i in ain:
        v_out.append(a.getAIN(i, gainIndex=0, settlingFactor=0, differential=True))

    for j in range(len(ain)):
        print(f"AIN{ain[j]}: {v_out[j]} Volts")

    return v_out, ain


def returntemp(v_out, ain):
    v_in = 5.05 #V, measured experimentally
    r1 = [3260., 3260., 3260., 3270., 3280., 3280., 3270., 3260., 3280., 3270.]
    avg_r1 = np.mean(r1)
    r2 = []

    for i in range(4):
        r2.append((r1[i]*(v_out[i]/v_in)) / (1 - (v_out[i]/v_in)))

    r_conv = np.array(r2)/1000.

    Resistance_Curve = np.array(
            [
                85.423,
                60.781,
                43.65,
                31.629,
                23.118,
                17.04,
                12.649,
                9.4864,
                7.1545,
                5.4479,
                4.1732,
                3.2256,
                2.5147,
                1.9763,
                1.5649,
                1.2481,
                1.0,
                0.80956,
                0.65726,
                0.53697,
                0.44169,
                0.36534,
                0.30327,
                0.25313,
                0.21271,
                0.17962,
                0.15219,
                0.12949,
                0.11067,
                0.094952,
                0.08178,
                0.07069,
                0.061383,
                0.053486,
                0.04673,
                0.040955,
                0.036006,
                0.031747,
                0.028097,
                0.024935,
                0.022176,
                0.019772,
                0.017683,
            ]
        )
    Temperature_Curve = np.linspace(-55, 155, 43)

    x = Temperature_Curve
    y = Resistance_Curve
    f = interpolate.interp1d(y, x)

    def temp(resistance):
        """
        Given resistance, outputs temperature.
        """
        return f(resistance)

    temperature = temp(r_conv)
    #for i in range(len(r_conv)):
    #    print(f"Temperature of AIN{ain[i]}: {temperature[i]} C")
    #    print(f"Temperature of AIN{ain[i]}: {((temperature[i])*(9/5))+32} F")
    #    print()
    temperature = np.append(temperature, [v_out[4]])
    
    return temperature

while True:
    try:
        #pressure, temperature = hsc.p_and_t
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        vout, ain = returnvolt(volt_channels) 
        #temps = returntemp(vout, volt_channels)
        v_diff1 = vout[0]
        v_diff2 = vout[1]
        v_diff3 = vout[2]
        v_diff4 = vout[3]
        v_diff5 = vout[4]
        v_diff6 = vout[5]
        r = 680
        ref = 5
        ther1 = r * v_diff1 / (ref- v_diff1)
        ther2 = r * v_diff2 / (ref - v_diff2)
        ther3 = r * v_diff3 / (ref - v_diff3)
        ther4 = r * v_diff4 / (ref - v_diff4)
        ther5 = r * v_diff5 / (ref - v_diff5)
        ther6 = r * v_diff6 / (ref - v_diff6)
        

        r_vals = np.array([ther1, ther2, ther3, ther4, ther5, ther6]) 

        
        temp1, temp2, temp3, temp4, temp5, temp6 = r_to_temp(r_vals)

        print(temp1)
        print(temp2)
        print(temp3)
        print(temp4)
        print(temp5)
        print(temp6)

        
        #print(f"{timestamp:<25} {pressure:<18.4f} {temperature:.2f} {vout[4]}")
        #print(f"temp of 1: {temps[0]}, temp of 6: {temps[3]} ")

        
        with open(csv_path, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, vout, [ther1, ther2, ther3, ther4, ther5, ther6], temp2, temp3, temp4, temp5, temp6])

        

        

        x.append(timestamp)
        y2.append(temp2)
        y3.append(temp3)
        y4.append(temp4)
        y5.append(temp5)
        y6.append(temp6)
        

        ax.clear()
        ax.plot(x, y2, color='g', linestyle='solid',  label='Temp 2')
        ax.plot(x, y3, color='b', linestyle='solid',  label='Temp 3')
        ax.plot(x, y4, color='m', linestyle='solid',  label='Temp 4')
        ax.plot(x, y5, color='y', linestyle='solid',  label='Temp 5')
        ax.plot(x, y6, color='r', linestyle='solid',  label='Temp 6')
        ax.set_xlabel('Time')
        ax.set_ylabel('Temperature (°C)')
        ax.set_title('Live Temperature', fontsize=20)
        ax.set_xticklabels([])
        ax.grid()
        ax.legend()
        plt.tight_layout()
        plt.pause(0.1)  

        time.sleep(1.0)

    except KeyboardInterrupt:
        print(f"\nLogging stopped. Data saved to: {csv_path}")
        break
    except Exception as e:
        print(f"Error reading sensor: {e}")
        time.sleep(1.0)


