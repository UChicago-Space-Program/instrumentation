#!/usr/bin/env python3
"""
dual_ssc_read.py
Read two Honeywell TruStability SSC SPI pressure sensors:
  CS4 (GPIO4)  → SSCMRNN160KASA3  (0–160 kPa absolute)
  CS5 (GPIO5)  → SSCMRRN002NDSA3  (±2 inH₂O differential)
"""

import time
import spidev
import RPi.GPIO as GPIO

# ── GPIO chip selects (BCM) ────────────────────────────────────────────────
# If GPIO4 conflicts with the 1-Wire overlay change CS4_GPIO to e.g. 6
CS4_GPIO = 17   # SSCMRNN160KASA3
CS5_GPIO = 27  # SSCMRRN002NDSA3

# ── SPI settings ──────────────────────────────────────────────────────────
SPI_BUS  = 0
SPI_DEV  = 0       # CE0 pin is NOT used as CS; no_cs=True handles it
SPI_HZ   = 400_000 # 400 kHz — safe within Honeywell's 50–800 kHz spec
SPI_MODE = 0       # CPOL=0, CPHA=0 (sample on rising edge)

# ── Transfer function: 10 %–90 % of 2^14 ─────────────────────────────────
OUT_MIN = 1638
OUT_MAX = 14745

# ── Pressure ranges ───────────────────────────────────────────────────────
P1_MIN_KPA =   0.0   # SSCMRNN160KASA3: 0 to 160 kPa absolute
P1_MAX_KPA = 160.0

P2_MIN_KPA =  -0.498 # SSCMRRN002NDSA3: ±2 inH₂O ≈ ±0.498 kPa differential
P2_MAX_KPA =  +0.498

INH2O_PER_KPA = 4.01463  # 1 kPa ≈ 4.01463 inH₂O


# ── Protocol helpers ──────────────────────────────────────────────────────

def parse_ssc_4bytes(b):
    """
    Honeywell SSC 4-byte SPI frame:
      Byte 0: [S1 S0 P13 P12 P11 P10 P9 P8]
      Byte 1: [P7 P6 P5 P4 P3 P2 P1 P0]
      Byte 2: T[10:3]
      Byte 3: T[2:0] in top 3 bits; bottom 5 bits unused
    """
    b0, b1, b2, b3 = b
    status   = (b0 >> 6) & 0x03
    p_counts = ((b0 & 0x3F) << 8) | b1
    t_counts = (b2 << 3) | (b3 >> 5)
    return status, p_counts, t_counts


def pressure_kpa(counts, p_min, p_max):
    return ((counts - OUT_MIN) * (p_max - p_min) / (OUT_MAX - OUT_MIN)) + p_min


def temperature_c(t_counts):
    # Honeywell Eq. 3: T = (200 × Output / 2047) − 50
    return (200.0 * t_counts / 2047.0) - 50.0


STATUS_TEXT = {0: "OK", 1: "CMD", 2: "STALE", 3: "DIAG"}


# ── Hardware setup ────────────────────────────────────────────────────────

def gpio_setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(CS4_GPIO, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(CS5_GPIO, GPIO.OUT, initial=GPIO.HIGH)


def spi_setup():
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEV)
    spi.max_speed_hz = SPI_HZ
    spi.mode        = SPI_MODE
    spi.no_cs       = True  # we drive CS lines ourselves
    return spi


def read_sensor(spi, cs_gpio, nbytes=4):
    GPIO.output(cs_gpio, GPIO.LOW)
    time.sleep(3e-6)                  # t_HDSS: SS↓ to first SCLK edge
    rx = spi.xfer2([0x00] * nbytes)  # MOSI ignored; clocks data out on MISO
    GPIO.output(cs_gpio, GPIO.HIGH)
    time.sleep(3e-6)                  # bus free time before next SS
    return rx


# ── Main loop ─────────────────────────────────────────────────────────────

def main():
    gpio_setup()
    spi = spi_setup()

    print("Honeywell SSC dual-sensor reader")
    print(f"  CS4 GPIO{CS4_GPIO} → SSCMRNN160KASA3 (0–160 kPa abs)")
    print(f"  CS5 GPIO{CS5_GPIO} → SSCMRRN002NDSA3 (±2 inH₂O diff)")
    print(f"  SPI mode={SPI_MODE}  {SPI_HZ//1000} kHz\n")

    try:
        while True:
            # Sensor 1 — absolute pressure
            raw1 = read_sensor(spi, CS4_GPIO)
            st1, pc1, tc1 = parse_ssc_4bytes(raw1)
            p1 = pressure_kpa(pc1, P1_MIN_KPA, P1_MAX_KPA)
            t1 = temperature_c(tc1)

            # Sensor 2 — differential pressure
            raw2 = read_sensor(spi, CS5_GPIO)
            st2, pc2, tc2 = parse_ssc_4bytes(raw2)
            p2    = pressure_kpa(pc2, P2_MIN_KPA, P2_MAX_KPA)
            p2_h2o = p2 * INH2O_PER_KPA
            t2 = temperature_c(tc2)

            print(
                f"S1[{STATUS_TEXT.get(st1,'?')}] raw={pc1:5d}  "
                f"P={p1:8.3f} kPa  T={t1:6.2f}°C  | {raw1}"
            )
            print(
                f"S2[{STATUS_TEXT.get(st2,'?')}] raw={pc2:5d}  "
                f"P={p2:+8.4f} kPa  ({p2_h2o:+7.3f} inH₂O)  T={t2:6.2f}°C  | {raw2}"
            )
            print("-" * 80)
            time.sleep(0.25)

    except KeyboardInterrupt:
        pass
    finally:
        spi.close()
        GPIO.cleanup()
        print("\nClean exit.")


if __name__ == "__main__":
    main()
