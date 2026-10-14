import serial

ser = serial.Serial("/dev/serial0", 9600, timeout=1)

ser.write(b"hiii")
response = ser.read(4)  
print(f"sent: hiii")
print(f"received: {response}")
ser.close()
