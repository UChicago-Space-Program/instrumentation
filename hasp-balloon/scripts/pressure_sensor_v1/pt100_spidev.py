import time, spidev

# MAX31865 registers
REG_CONFIG  = 0x00
REG_RTD_MSB = 0x01
REG_RTD_LSB = 0x02
REG_FAULT   = 0x07

# config bits
BIAS     = 0x80
MODEAUTO = 0x40
WIRE3    = 0x10
FAULTCLR = 0x02
FILT50   = 0x01

RREF = 430.0      # Adafruit PT100 board
R0   = 100.0      # PT100 nominal at 0C

# Callendar–Van Dusen (PT100)
A = 3.9083e-3
B = -5.775e-7

def r8(spi, reg):
    return spi.xfer2([reg & 0x7F, 0x00])[1]

def w8(spi, reg, val):
    spi.xfer2([(reg | 0x80) & 0xFF, val & 0xFF])

def read_rtd_raw(spi):
    msb = r8(spi, REG_RTD_MSB)
    lsb = r8(spi, REG_RTD_LSB)
    raw15 = ((msb << 8) | lsb) >> 1
    fault_lsb = lsb & 0x01
    fault = r8(spi, REG_FAULT)
    return raw15, fault_lsb, fault

def raw_to_ohms(raw15):
    return (raw15 / 32768.0) * RREF

def ohms_to_temp_c(R):
    # Solve R = R0*(1 + A*T + B*T^2) for T (valid for T >= 0C; good enough for room temp)
    # B*T^2 + A*T + (1 - R/R0) = 0
    c = 1.0 - (R / R0)
    disc = A*A - 4*B*c
    if disc < 0:
        return float("nan")
    T = (-A + (disc ** 0.5)) / (2*B)
    return T

spi = spidev.SpiDev()
spi.open(0, 0)            # spidev0.0 = CE0 (you confirmed this is the working CS)
spi.max_speed_hz = 1000000
spi.mode = 0b01           # MAX31865 uses SPI mode 1

cfg = BIAS | MODEAUTO | WIRE3 | FAULTCLR | FILT50
w8(spi, REG_CONFIG, cfg)
time.sleep(0.2)           # let first conversion settle

print("CONFIG readback:", hex(r8(spi, REG_CONFIG)))

while True:
    raw15, fault_lsb, fault = read_rtd_raw(spi)
    R = raw_to_ohms(raw15)
    T = ohms_to_temp_c(R)

    print(f"raw={raw15:5d}  R={R:8.3f} Ω  T={T:7.2f} C  faultLSB={fault_lsb} fault=0x{fault:02X}")
    time.sleep(1)
