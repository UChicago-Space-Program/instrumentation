import time
import board
import busio
import adafruit_bmp3xx

i2c = busio.I2C(board.SCL, board.SDA)
bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)

while True:
    print(f"BMP388: {bmp.temperature:.2f} C, {bmp.pressure:.2f} hPa")
    time.sleep(1)
