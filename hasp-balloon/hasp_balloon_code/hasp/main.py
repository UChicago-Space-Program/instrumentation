from hasp_lib import sensor, image, gpio_expander
from hasp_lib.gpio_expander import GpioExpander
from hasp_lib.sensor import *
from hasp_lib.image import Camera
from hasp_lib.pops import Pops
from hasp_lib.hasp_comms import hasp_comms
from hasp_lib.pumps import Pump
from hasp_lib.solenoid import Solenoid
from hasp_lib.heater import Heater
from hasp_lib.telem import Telem
from hasp_lib.plunger import Plunger
import RPi.GPIO as GPIO
import board
import busio
import digitalio
import time

if __name__ == "__main__":
    print("Starting UCSP PASCAL Payload")
    at_altitude = False
    manual_control = False

    ### SETUP DATA PROTOCOLS
    #telem setup
    telem = Telem()

    spi = board.SPI()
    cs_rtd = digitalio.DigitalInOut(board.D6)
    """cs_tmc1 = digitalio.DigitalInOut(board.D25)
    cs_tmc2 = digitalio.DigitalInOut(board.D12)
    cs_tmc3 = digitalio.DigitalInOut(board.D16)
    cs_tmc4 = digitalio.DigitalInOut(board.D20)
    cs_tmc5 = digitalio.DigitalInOut(board.D21)"""
    #more cs pins
    i2c_bus = busio.I2C(board.SCL, board.SDA)

    gpio_ex = GpioExpander(i2c_bus, 0x20)
    #gpio_ex.config_io(1, 0, 0) # config pin 0 gpio bus 1 to be an output
    
    #pump setup

    pump1 = Pump(gpio_ex, 1, 0)
    pump2 = Pump(gpio_ex, 1, 1)
    pump3 = Pump(gpio_ex, 1, 2)
    pump4 = Pump(gpio_ex, 1, 3)
    pump5 = Pump(gpio_ex, 1, 4)
    pump6 = Pump(gpio_ex, 1, 5)
    pump7 = Pump(gpio_ex, 2, 5)
    pump8 = Pump(gpio_ex, 2, 6)
    pump9 = Pump(gpio_ex, 2, 7)


    #gpio setup
    sol_gpio_open = 13
    sol_gpio_close = 19
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(sol_gpio_open, GPIO.OUT)
    GPIO.setup(sol_gpio_close, GPIO.OUT)

    step = 17
    dir = 27

    


    GPIO.setup(26, GPIO.OUT)
    #serial comms setup
    pops = Pops(9600, "/dev/ttyAMA2")
    hasp_balloon = hasp_comms(4800, "/dev/ttyAMA0")

    #servo setup
    plunger1 = Plunger(step, dir)

    #camera setup
    cam = Camera()
    cam.start()
    cur_img = None

    #adc setup
    adc1 = ADC_8Bit("adc1", i2c_bus, 0x48)
    adc2 = ADC_8Bit("adc2", i2c_bus, 0x49)
    adc3 = ADC_8Bit("adc3", i2c_bus, 0x4A)
    adc4 = ADC_8Bit("adc4", i2c_bus, 0x4B)

    #rtd setup
    rtd = MAX31865(spi, cs_rtd)

    image_tlm_flag = False
    
    #thermocouple setup

    """tmc1 = MAX31855(spi, cs_tmc1)
    tmc2 = MAX31855(spi, cs_tmc2)
    tmc3 = MAX31855(spi, cs_tmc3)
    tmc4 = MAX31855(spi, cs_tmc4)
    tmc5 = MAX31855(spi, cs_tmc5)"""
    thm1 = Thermistor(adc1, 0)
    thm2 = Thermistor(adc1, 2)
    thm3 = Thermistor(adc1, 4)
    thm4 = Thermistor(adc1, 6)
    thm5 = Thermistor(adc3, 4)
    thm6 = Thermistor(adc2, 0)
    thm7 = Thermistor(adc2, 2)
    thm8 = Thermistor(adc2, 6)
    thm9 = Thermistor(adc3, 0)
    thm10 = Thermistor(adc3, 2)
    thm11 = Thermistor(adc3, 6)
    thm12 = Thermistor(adc4, 0)
    thm13 = Thermistor(adc4, 2)
    thm14 = Thermistor(adc4, 6)
    thm15 = Thermistor(adc4, 4)


    sol = Solenoid(sol_gpio_open, sol_gpio_close)

    #heater setup
    heater1 = Heater(gpio_ex, 1, 6)
    heater2 = Heater(gpio_ex, 1, 7)
    heater3 = Heater(gpio_ex, 2, 4)
    heater4 = Heater(gpio_ex, 2, 3)
    heater5 = Heater(gpio_ex, 2, 2)

    #bmp setup

    bmp = BMP388(i2c_bus, 0x77)

    

    #pops.turn_on()
    #telem.set_ppps(10, 1)

    pumps_and_ids = [(pump1, 1), (pump2, 2), (pump3, 3), (pump4, 4), (pump5, 5), (pump6, 6), (pump7, 7), (pump8, 8), (pump9, 9)]
    img_val = 0

    while True:
        category, val = hasp_balloon.read()
        if category == "command":
            print("reading command")
            if val[0] == 1 and val[1] == 28:
                #todo reset computer
                
                pass
            elif val[0] == 19 and val[1] == 60:
                #cam.capture("pic" + str(img_val) + ".jpg")
                cam.prepare_image("pic" + str(img_val) + ".jpg")
                print("photo captured")
                img_val += 1 
            elif val[0] == 21 and val[1] == 12:
                print("got here")
                sol.open_solenoid()
                print("openednsolenoid")
                telem.set_ppps(12, 1)
                print("u[date telem]")
                #plunger1.open()
                print("plunger opened")
                telem.set_ppps(11, 1)
                print("set pump telem")
                for pumpx, id in pumps_and_ids:
                    print("running")
                    pumpx.turn_on()
                    telem.set_ppps(id, 1)
                print("solenoids open, plunger open, and pumps on")
            elif val[0] == 2 and val[1] == 28:
                sol.close_solenoid()
                telem.set_ppps(12, 0)
                #plunger1.close()
                telem.set_ppps(11, 0)
                for pumpx, id in pumps_and_ids:
                    pumpx.turn_off()
                    telem.set_ppps(id, 0)
                print("solenoid closed, plunger closed, and pumps off")
            elif val[0] == 80 and val[1] == 12:
                pops.toggle()
                st = pops.get_state()
                telem.set_ppps(10, st)
                print("Pops: " + str(st))
            elif val[0] == 5 and val[1] == 156:
                sol.open_solenoid()
                telem.set_ppps(12, 1)
                print("solenoid open")
            elif val[0] == 3 and val[1] == 12:
                pump1.toggle()
                st = pump1.get_state()
                telem.set_ppps(1, st)
                print("Pump 1 set to: " + str(st)) 
            elif val[0] == 134 and val[1] == 28:
                pump2.toggle()
                st = pump2.get_state()
                telem.set_ppps(2, st)
                print("Pump 2 set to: " + str(st))
            elif val[0] == 35 and val[1] == 92:
                pump3.toggle()
                st = pump3.get_state()
                telem.set_ppps(3, st)
                print("Pump 3 set to: " + str(st))
            elif val[0] == 24 and val[1] == 12:
                pump4.toggle()
                st = pump4.get_state()
                telem.set_ppps(4, st)
                print("Pump 4 set to: " + str(st))
            elif val[0] == 135 and val[1] == 44:
                pump5.toggle()
                st = pump5.get_state()
                telem.set_ppps(5, st)
                print("Pump 5 set to: " + str(st))
            elif val[0] == 33 and val[1] == 44:
                pump6.toggle()
                st = pump6.get_state()
                telem.set_ppps(6, st)
                print("Pump 6 set to: " + str(st))
            elif val[0] == 116 and val[1] == 124:
                pump7.toggle()
                st = pump7.get_state()
                telem.set_ppps(7, st)
                print("Pump 7 set to: " + str(st))
            elif val[0] == 115 and val[1] == 124:
                pump8.toggle()
                st = pump8.get_state()
                telem.set_ppps(8, st)
                print("Pump 8 set to: " + str(st))
            elif val[0] == 117 and val[1] == 124:
                pump9.toggle()
                st = pump9.get_state()
                telem.set_ppps(9, st)
                print("Pump 9 set to: " + str(st))
            elif val[0] == 31 and val[1] == 236:
                plunger1.open()
                telem.set_ppps(11, 1)
                print("Plunger open")
            elif val[0] == 47 and val[1] == 236:
                #servo2.close()
                pass
            elif val[0] == 119 and val[1] == 124:
                print("loop reset")
                #continue
            elif val[0] == 120 and val[1] == 124:
                if manual_control == 1:
                    manual_control = 0
                    print("manual control off")
                elif manual_control == 0:
                    manual_control = 1
                    print("manual control on")
            elif val[0] == 118 and val[1] == 124:
                plunger1.close()
                telem.set_ppps(11, 0)
                print("plunger closed")
            elif val[0] == 118 and val[1] == 140:
                heater1.turn_on()
                telem.set_heater(1, 1)
                heater2.turn_on()
                telem.set_heater(2, 1)
                heater3.turn_on()
                telem.set_heater(3, 1)
                heater4.turn_on()
                telem.set_heater(4, 1)
                heater5.turn_on()
                telem.set_heater(5, 1)
                print("heaters on")
            elif val[0] == 96 and val[1] == 140:
                heater1.turn_off()
                telem.set_heater(1, 0)
                heater2.turn_off()
                telem.set_heater(2, 0)
                heater3.turn_off()
                telem.set_heater(3, 0)
                heater4.turn_off()
                telem.set_heater(4, 0)
                heater5.turn_off()
                telem.set_heater(5, 0)
                print("heaters off")

            elif val[0] == 49 and val[1] == 12:
                sol.close_solenoid()
                telem.set_ppps(12, 0)
                print("solenoid closed")
            
            print("here")
        elif category == "gps":
            # set gps to val in telemetry
            if val[1] >= 36000 and not manual_control and not at_altitude:
                sol.open_solenoid()
                telem.set_ppps(12, 1)
                #plunger1.open()
                telem.set_ppps(11, 1)
                for pumpx, id in pumps_and_ids:
                    pumpx.turn_on()
                    telem.set_ppps(id, 0)
                pops.turn_off()
                telem.set_ppps(10, 0)
                at_altitude = True
            elif val[1] <= 36000 and not manual_control and at_altitude:
                sol.close_solenoid()
                telem.set_ppps(12, 0)
                #plunger1.close()
                telem.set_ppps(11, 0)
                for pumpx, id in pumps_and_ids:
                    pumpx.turn_off()
                    telem.set_ppps(id, 0)
                pops.turn_on()
                telem.set_ppps(11, 1)
                at_altitude = False
        print("end command")
        for thmx, heaterx, id in zip([thm1, thm2, thm3, thm4, thm5, thm6, thm7, thm8, thm9, thm10, thm11, thm12, thm13, thm14, thm15], [heater1, heater2, heater3, heater4, heater5, None, None, None, None, None, None, None, None, None, None], range(1,16)):
            temp = thmx.read()
            telem.set_therms(id, int(round(temp * 10)))
            print(temp)
            if id < 6:
                if temp < -20 and heaterx.get_state() == 0 and not manual_control:
                    heaterx.turn_on()
                    telem.set_heater(id, 1)
                elif temp > 15 and heaterx.get_state() == 1 and not manual_control:
                    heaterx.turn_off()
                    telem.set_heater(id, 0)

        telem.set_ambient_pressure(bmp.read_pressure())
        telem.set_motherboard_temp(bmp.read_temperature())




        #datetime, status, counts, concentration = pops.read()

        cam.send_next_chunk(hasp_balloon)
        hasp_balloon.write(telem.make_tlm_packet())

        telem.printer()






        


        
        
        
            




        

    
