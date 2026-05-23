import time, spidev

REG_CONFIG   = 0x00
REG_RTD_MSB  = 0x01
REG_RTD_LSB  = 0x02
REG_FAULT    = 0x07

# config bits
BIAS     = 0x80
MODEAUTO = 0x40
WIRE3    = 0x10
FAULTCLR = 0x02
FILT50   = 0x01

RREF = 430.0  # PT100 Adafruit board

def r8(spi, reg):
    return spi.xfer2([reg & 0x7F, 0x00])[1]

def w8(spi, reg, val):
    spi.xfer2([(reg | 0x80) & 0xFF, val & 0xFF])

def read_rtd(spi):
    msb = r8(spi, REG_RTD_MSB)
    lsb = r8(spi, REG_RTD_LSB)
    raw15 = ((msb << 8) | lsb) >> 1
    fault_lsb = lsb & 0x01
    return raw15, fault_lsb, msb, lsb

def raw_to_ohms(raw15):
    return (raw15 / 32768.0) * RREF

spi = spidev.SpiDev()
spi.open(0, 0)              # CE0
spi.max_speed_hz = 1000000
spi.mode = 0b01             # MAX31865 mode 1

cfg = BIAS | MODEAUTO | WIRE3 | FAULTCLR | FILT50
w8(spi, REG_CONFIG, cfg)
time.sleep(0.1)

print("CONFIG readback:", hex(r8(spi, REG_CONFIG)))

for i in range(20):
    raw15, fault_lsb, msb, lsb = read_rtd(spi)
    fault = r8(spi, REG_FAULT)
    ohms = raw_to_ohms(raw15)
    print(f"[{i:02d}] RTD msb=0x{msb:02X} lsb=0x{lsb:02X} raw={raw15:5d} ohms={ohms:8.3f} faultLSB={fault_lsb} faultReg=0x{fault:02X}")
    time.sleep(0.5)

spi.close()

# asdasoidja
