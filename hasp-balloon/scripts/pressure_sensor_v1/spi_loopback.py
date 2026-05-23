import spidev

spi = spidev.SpiDev()
spi.open(0, 0)          # spidev0.0 (CE0)
spi.max_speed_hz = 500000
spi.mode = 0

tx = [0xDE, 0xAD, 0xBE, 0xEF, 0x01, 0x23]
rx = spi.xfer2(tx)

print("TX:", [hex(x) for x in tx])
print("RX:", [hex(x) for x in rx])
print("PASS" if rx == tx else "FAIL")

spi.close()
