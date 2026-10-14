from hasp_lib import sensor, image, gpio_expander
from hasp_lib.gpio_expander import GpioExpander
from hasp_lib.sensor import *
from hasp_lib.image import Camera
from hasp_lib.pops import Pops
from hasp_lib.hasp_comms import hasp_comms
from hasp_lib.pumps import Pump
from hasp_lib.solenoid import Solenoid
from hasp_lib.heater import Heater
from hasp_lib.telem2 import Telem
from hasp_lib.plunger import Plunger
import RPi.GPIO as GPIO
import board
import busio
import digitalio
import time

if __name__ == "__main__":

    thermocouples_present = True
    camera_1_present = True
    camera_2_present = True
    bmp_present = True
    gpio_expander_present = True
    tmc2_present = True
    thermal_manual_control = False


    print("Starting UCSP PASCAL Payload")
    at_altitude = False
    manual_control = False

    ### SETUP DATA PROTOCOLS
    #telem setup
    telem = Telem()

    spi = board.SPI()
    
    cs_tmc = digitalio.DigitalInOut(board.D16)
    cs_rtd = digitalio.DigitalInOut(board.D6)
    #more cs pins
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    if gpio_expander_present:
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
    sol_gpio_open = 19
    sol_gpio_close = 13
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(sol_gpio_open, GPIO.OUT)
    GPIO.setup(sol_gpio_close, GPIO.OUT)
    GPIO.output(sol_gpio_open, GPIO.LOW)
    GPIO.output(sol_gpio_close, GPIO.LOW)

    step = 17
    dir = 27
    en = 23

    sol_relay = 24

    GPIO.setup(sol_relay, GPIO.OUT)
    

    


    GPIO.setup(26, GPIO.OUT)
    #serial comms setup
    pops = Pops(115200, "/dev/ttyAMA2")
    
    hasp_balloon = hasp_comms(4800, "/dev/ttyAMA0")

    #servo setup
    plunger1 = Plunger(step, dir, en)

    #camera setup
    if camera_1_present:
        cam = Camera(0, 0x0409)
        cam.start()
    if camera_2_present:        
        cam_alt = Camera(1, 0xF1F4)
        cam_alt.start()
    

    #adc setup
    if thermocouples_present:
        adc1 = ADC_8Bit("adc1", i2c_bus, 0x48)
        adc2 = ADC_8Bit("adc2", i2c_bus, 0x49)
        adc3 = ADC_8Bit("adc3", i2c_bus, 0x4A) 
        adc4 = ADC_8Bit("adc4", i2c_bus, 0x4B)


    
    thermocouple1 = MAX31855(spi, cs_tmc)
    rtd = MAX31865(spi, cs_rtd)

    image_tlm_flag = False
    
    #thermocouple setup


    if thermocouples_present:
        thm0 = Thermistor(adc1, 0)
        thm1 = Thermistor(adc1, 1) 
        thm2 = Thermistor(adc1, 2)
        thm3 = Thermistor(adc1, 3)
        thm4 = Thermistor(adc1, 4) # panel south
        thm5 = Thermistor(adc1, 5) # panel north
        thm6 = Thermistor(adc1, 6) # l1 therm2
        thm7 = Thermistor(adc1, 7) # 
        thm8 = Thermistor(adc2, 0) # l2 north
        thm9 = Thermistor(adc2, 1)  #panel top 
        thm10 = Thermistor(adc2, 2) #panel east
        thm11 = Thermistor(adc2, 3) # panel west
        thm12 = Thermistor(adc2, 4) #pump south
        thm13 = Thermistor(adc2, 5) #l2 south
        thm14 = Thermistor(adc2, 6) #pump North
        thm15 = Thermistor(adc2, 7) #pump middle
        thm16 = Thermistor(adc3, 0) 
        thm17 = Thermistor(adc3, 1)
        thm18 = Thermistor(adc3, 2)
        thm19 = Thermistor(adc3, 3)
        thm20 = Thermistor(adc3, 4)
        thm21 = Thermistor(adc3, 5)
        thm22 = Thermistor(adc3, 6)
        thm23 = Thermistor(adc3, 7)
        thm24 = Thermistor(adc4, 0) #POPS
        thm25 = Thermistor(adc4, 1) #l1 therm 1
        thm26 = Thermistor(adc4, 2) # 24 V
        thm27 = Thermistor(adc4, 3) # 12 V
        thm28 = Thermistor(adc4, 4) # 5 V
        thm29 = Thermistor(adc4, 5) # 6 V
        thm30 = Thermistor(adc4, 6) #broken
        thm31 = Thermistor(adc4, 7) #broken

        


    sol = Solenoid(sol_gpio_open, sol_gpio_close)

    #heater setup
    if gpio_expander_present:
        moudi1_heater = Heater(gpio_ex, 2, 2, 1) #with tbd thermocouple
        moudi2_heater = Heater(gpio_ex, 1, 6, 2) # with tbd thermodcouple
        north_heater = Heater(gpio_ex, 2, 0, 3) 
        south_heater = Heater(gpio_ex, 2, 1, 4)

    #bmp setup

    if bmp_present:
        bmp = BMP388(i2c_bus, 0x77)

    

    #pops.turn_on()
    telem.set_ppps(10, 1)
    print(pops.get_state())
    if gpio_expander_present:
        pumps_and_ids = [(pump1, 1), (pump2, 2), (pump3, 3), (pump4, 4), (pump5, 5), (pump6, 6), (pump7, 7), (pump8, 8), (pump9, 9)]
    img_val = 0
    tlm_count = 0

    time.sleep(5)
    GPIO.output(sol_relay, GPIO.HIGH)
    while True:
        
        category, val = hasp_balloon.read()
        if category == "command":
            print("reading command")
            if val[0] == 1 and val[1] == 28:
                thermal_manual_control = not thermal_manual_control
                #pass
            elif val[0] == 19 and val[1] == 60:
                #cam.capture("pic" + str(img_val) + ".jpg")
                if camera_1_present:
                    cam.prepare_image("pic" + str(img_val) + ".jpg")
                    print("photo captured")
                    cam.send_all(hasp_balloon)
                    img_val += 1 
            elif val[0] == 21 and val[1] == 12:
                print("got here")
                states = [(moudi1_heater, moudi1_heater.get_state()), (moudi2_heater, moudi2_heater.get_state()), (north_heater, north_heater.get_state()), (south_heater, south_heater.get_state())]
                print("u[date telem]")
                moudi1_heater.turn_off()
                telem.set_heater(1, 0)
                moudi2_heater.turn_off()
                telem.set_heater(2, 0)
                north_heater.turn_off()
                telem.set_heater(3, 0)
                south_heater.turn_off()
                telem.set_heater(4, 0)
                print("heaters off")
                plunger1.open()
                telem.set_ppps(11, 1)
                print("plunger opened")
                sol.open_solenoid()
                print("opened solenoid")
                telem.set_ppps(12, 1)
                print("set pump telem")
                time.sleep(0.5)
                if gpio_expander_present:
                    for pumpx, id in pumps_and_ids:
                        print("running")
                        pumpx.turn_on()
                        telem.set_ppps(id, 1)
                for device, state in states:
                    if state == 1:
                        device.turn_on()
                    elif state == 0:
                        device.turn_off()
                    telem.set_heater(device.get_id(), state)
                print("solenoids open, plunger open, and pumps on")
            elif val[0] == 2 and val[1] == 28:
                
                states = [(moudi1_heater, moudi1_heater.get_state()), (moudi2_heater, moudi2_heater.get_state()), (north_heater, north_heater.get_state()), (south_heater, south_heater.get_state())]
                if gpio_expander_present:
                    for pumpx, id in pumps_and_ids:
                        pumpx.turn_off()
                        telem.set_ppps(id, 0)
                
                moudi1_heater.turn_off()
                telem.set_heater(1, 0)
                moudi2_heater.turn_off()
                telem.set_heater(2, 0)
                north_heater.turn_off()
                telem.set_heater(3, 0)
                south_heater.turn_off()
                telem.set_heater(4, 0)
                print("heaters off")
                sol.close_solenoid()
                telem.set_ppps(12, 0)
                plunger1.close()
                telem.set_ppps(11, 0)
                for device, state in states:
                    if state == 1:
                        device.turn_on()
                    elif state == 0:
                        device.turn_off()
                    telem.set_heater(device.get_id(), state)
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
                if gpio_expander_present:
                    pump1.toggle()
                    st = pump1.get_state()
                    telem.set_ppps(1, st)
                print("Pump 1 set to: " + str(st)) 
            elif val[0] == 134 and val[1] == 28:
                if gpio_expander_present:
                    pump2.toggle()
                    st = pump2.get_state()
                    telem.set_ppps(2, st)
                print("Pump 2 set to: " + str(st))
            elif val[0] == 35 and val[1] == 92:
                if gpio_expander_present:
                    pump3.toggle()
                    st = pump3.get_state()
                    telem.set_ppps(3, st)
                print("Pump 3 set to: " + str(st))
            elif val[0] == 24 and val[1] == 12:
                if gpio_expander_present:
                    pump4.toggle()
                    st = pump4.get_state()
                    telem.set_ppps(4, st)
                print("Pump 4 set to: " + str(st))
            elif val[0] == 135 and val[1] == 44:
                if gpio_expander_present:
                    pump5.toggle()
                    st = pump5.get_state()
                    telem.set_ppps(5, st)
                print("Pump 5 set to: " + str(st))
            elif val[0] == 33 and val[1] == 44:
                if gpio_expander_present:
                    pump6.toggle()
                    st = pump6.get_state()
                    telem.set_ppps(6, st)
                print("Pump 6 set to: " + str(st))
            elif val[0] == 116 and val[1] == 124:
                if gpio_expander_present:
                    pump7.toggle()
                    st = pump7.get_state()
                    telem.set_ppps(7, st)
                print("Pump 7 set to: " + str(st))
            elif val[0] == 115 and val[1] == 124:
                if gpio_expander_present:
                    pump8.toggle()
                    st = pump8.get_state()
                    telem.set_ppps(8, st)
                print("Pump 8 set to: " + str(st))
            elif val[0] == 117 and val[1] == 124:
                if gpio_expander_present:
                    pump9.toggle()
                    st = pump9.get_state()
                    telem.set_ppps(9, st)
                print("Pump 9 set to: " + str(st))
            elif val[0] == 31 and val[1] == 236:
                states = [(moudi1_heater, moudi1_heater.get_state()), (moudi2_heater, moudi2_heater.get_state()), (north_heater, north_heater.get_state()), (south_heater, south_heater.get_state())]
                moudi1_heater.turn_off()
                telem.set_heater(1, 0)
                moudi2_heater.turn_off()
                telem.set_heater(2, 0)
                north_heater.turn_off()
                telem.set_heater(3, 0)
                south_heater.turn_off()
                telem.set_heater(4, 0)
                print("heaters off")
                plunger1.open()
                telem.set_ppps(11, 1)
                for device, state in states:
                    if state == 1:
                        device.turn_on()
                    elif state == 0:
                        device.turn_off()
                    telem.set_heater(device.get_id(), state)
                print("Plunger open")
            elif val[0] == 47 and val[1] == 236:
                if camera_2_present:
                    cam_alt.prepare_image("pic_alt" + str(img_val)  + ".jpg")
                    print("photo captured")
                    cam_alt.send_all(hasp_balloon)
                    img_val += 1
            elif val[0] == 119 and val[1] == 124:
                if camera_2_present:
                    cam_alt.prepare_image("pic_alt" + str(img_val)  + ".jpg")
                    print("photo captured cam 1 not sending")
                    img_val += 1
                if camera_2_present:
                    cam_alt.prepare_image("pic_alt" + str(img_val)  + ".jpg")
                    print("photo captured cam 2 not sending")
                    img_val += 1
            elif val[0] == 120 and val[1] == 124:
                if manual_control == True:
                    manual_control = False
                    print("manual control off")
                elif manual_control == False:
                    manual_control = True
                    print("manual control on")
                telem.set_manual_control(manual_control)
            elif val[0] == 118 and val[1] == 124:
                states = [(moudi1_heater, moudi1_heater.get_state()), (moudi2_heater, moudi2_heater.get_state()), (north_heater, north_heater.get_state()), (south_heater, south_heater.get_state())]
                moudi1_heater.turn_off()
                telem.set_heater(1, 0)
                moudi2_heater.turn_off()
                telem.set_heater(2, 0)
                north_heater.turn_off()
                telem.set_heater(3, 0)
                south_heater.turn_off()
                telem.set_heater(4, 0)
                print("heaters off")
                plunger1.close()
                telem.set_ppps(11, 0)
                for device, state in states:
                    if state == 1:
                        device.turn_on()
                    elif state == 0:
                        device.turn_off()
                    telem.set_heater(device.get_id(), state)
                print("plunger closed")
            elif val[0] == 118 and val[1] == 140:
                if gpio_expander_present:
                    moudi1_heater.turn_on()
                    telem.set_heater(1, 1)
                    moudi2_heater.turn_on()
                    telem.set_heater(2, 1)
                    north_heater.turn_on()
                    telem.set_heater(3, 1)
                    south_heater.turn_on()
                    telem.set_heater(4, 1)
                print("heaters on")
            elif val[0] == 96 and val[1] == 140:
                if gpio_expander_present:
                    moudi1_heater.turn_off()
                    telem.set_heater(1, 0)
                    moudi2_heater.turn_off()
                    telem.set_heater(2, 0)
                    north_heater.turn_off()
                    telem.set_heater(3, 0)
                    south_heater.turn_off()
                    telem.set_heater(4, 0)
                print("heaters off")

            elif val[0] == 49 and val[1] == 12:
                sol.close_solenoid()
                telem.set_ppps(12, 0)
                print("solenoid closed")
            
            print("here")
        elif category == "gps":
            telem.set_timestamp(val[0])
            # set gps to val in telemetry
            if val[1] >= 36000 and not manual_control and not at_altitude:
                sol.open_solenoid()
                telem.set_ppps(12, 1)
                time.sleep(0.5)
                if gpio_expander_present:
                    states = [(moudi1_heater, moudi1_heater.get_state()), (moudi2_heater, moudi2_heater.get_state()), (north_heater, north_heater.get_state()), (south_heater, south_heater.get_state())]
                    moudi1_heater.turn_off()
                    telem.set_heater(1, 0)
                    moudi2_heater.turn_off()
                    telem.set_heater(2, 0)
                    north_heater.turn_off()
                    telem.set_heater(3, 0)
                    south_heater.turn_off()
                    telem.set_heater(4, 0)
                print("heaters off")
                plunger1.open()
                telem.set_ppps(11, 1)
                if gpio_expander_present:
                    for pumpx, id in pumps_and_ids:
                        pumpx.turn_on()
                        telem.set_ppps(id, 1)
                for device, state in states:
                    if state == 1:
                        device.turn_on()
                    elif state == 0:
                        device.turn_off()
                    telem.set_heater(device.get_id(), state)

                #pops.turn_off()
                telem.set_ppps(10, 0)
                at_altitude = True
            elif val[1] >= 36000:
                at_altitude = True
            elif val[1] <= 36000 and not manual_control and at_altitude:
                
                states = [(moudi1_heater, moudi1_heater.get_state()), (moudi2_heater, moudi2_heater.get_state()), (north_heater, north_heater.get_state()), (south_heater, south_heater.get_state())]
                if gpio_expander_present:
                    moudi1_heater.turn_off()
                    telem.set_heater(1, 0)
                    moudi2_heater.turn_off()
                    telem.set_heater(2, 0)
                    north_heater.turn_off()
                    telem.set_heater(3, 0)
                    south_heater.turn_off()
                    telem.set_heater(4, 0)
                print("heaters off")
                if gpio_expander_present:
                    for pumpx, id in pumps_and_ids:
                        pumpx.turn_off()
                        telem.set_ppps(id, 0)
                at_altitude = False
                sol.close_solenoid()
                telem.set_ppps(12, 0)
                plunger1.close()
                telem.set_ppps(11, 0)

                #pops.turn_on()
                telem.set_ppps(10, 1)

                for device, state in states:
                    if state == 1:
                        device.turn_on()
                    elif state == 0:
                        device.turn_off()
                    telem.set_heater(device.get_id(), state)
            elif val[1] <= 36000:
                at_altitude = False
        if thermocouples_present and gpio_expander_present:
            for thmx, heaterx, id in zip([thm0, thm1, thm2, thm3, thm4, thm5, thm6, thm7, thm8, thm9, thm10, thm11, thm12, thm13, thm14, thm15, thm16, thm17, thm18, thm19, thm20, thm21, thm22, thm23, thm24, thm25, thm26, thm27, thm28, thm29, thm30, thm31, thermocouple1, rtd], [None, None, None, None, None, None, None, None, None, None, None, None, south_heater, None, north_heater, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, moudi2_heater, moudi1_heater], range(0,34)):
                try:
                    temp = thmx.read()
                except:
                    print("error reading id : " + str(id))
                    continue
                if id < 32:
                    telem.set_therms(id, int(round(temp * 10)))
                    
                else:
                    telem.set_therms(id, temp)
                
                #print(temp)
                if heaterx is not None and not thermal_manual_control:
                    if temp < -10 and heaterx.get_state() == 0:
                        heaterx.turn_on()
                        telem.set_heater(heaterx.get_id(), 1)
                    elif temp > 10 and heaterx.get_state() == 1:
                        heaterx.turn_off()
                        telem.set_heater(heaterx.get_id(), 0)



                if id == 24:
                    if temp >= 60:
                        #pops.turn_off()
                        print("pops is overheating and turning off")

        if bmp_present:
            telem.set_ambient_pressure(bmp.read_pressure())
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            telem.set_motherboard_temp(int(float(f.read()) / 1000.0))



        
        #dt, status, p_count, p_con, amb_press, on_temp, sample_flow, laser_temp, ext_temp = pops.read()
        #if dt is not None:
        #    telem.set_pops_data(dt, status, p_count, p_con, amb_press, on_temp, sample_flow, laser_temp, ext_temp)
        if tlm_count == 10:
            hasp_balloon.write_ptx(telem.make_tlm_packet())
            telem.printer()
            tlm_count = 0
        else:
            tlm_count += 1
