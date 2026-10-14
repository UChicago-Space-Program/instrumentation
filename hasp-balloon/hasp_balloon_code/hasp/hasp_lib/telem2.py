import struct
class Telem:
    def __init__(self):
        self.header = 0x0121
        self.id = 0
        self.timestamp = 0 
        self.thermistors = 0
        self.ambient_pressure = 0
        self.pump_air_flow = 0
        self.pops_particle_density = 0
        self.pops_flow_rate = 0
        self.motherboard_temp = 0
        self.voltage_reg_status = 0
        self.pumps_plunger_pops = 0
        self.pump1 = 0
        self.pump2 = 0
        self.pump3 = 0
        self.pump4 = 0
        self.pump5 = 0
        self.pump6 = 0
        self.pump7 = 0
        self.pump8 = 0
        self.pump9 = 0
        self.pops = 0
        self.plunger = 0
        self.solenoid = 0
        self.heater1 = 0
        self.heater2 = 0
        self.heater3 = 0
        self.heater4 = 0
        self.heater5 = 0
        self.heater_stat = 0
        self.red_pops_part_dens = 0
        self.checksum = 0
        self.terminator = 0x030D
        self.therm_bytes = [0] * 34
        self.therm_volts = [0] * 32
        self.air_flow_rate = 0
        self.red = 0
        self.pops_status = 0
        self.pops_dt = 0
        self.pops_p_status = 0
        self.pops_p_count = 0
        self.pops_p_con = 0
        self.pops_amb_press = 0
        self.pops_on_temp = 0
        self.pops_sample_flow = 0
        self.pops_laser_temp = 0
        self.pops_ext_temp = 0
        self.manual_control = False
    def set_ambient_pressure(self, pressure):
        self.ambient_pressure = pressure
    def set_part_dens(self, density):
        self.pops_particle_density = density
    def set_pops_flow_rate(self, pops_flow):
        self.pops_flow_rate = pops_flow
    def set_motherboard_temp(self, temp):
        self.motherboard_temp = int(temp)
    def set_voltage_reg_status(self, volt_reg_stat):
        self.voltage_reg_status = volt_reg_stat
    def set_pops_data(self, dt, status, p_count, p_con, amb_press, on_temp, sample_flow, laser_temp, ext_temp):
        self.pops_dt = dt
        self.pops_p_status = status
        self.pops_p_count = p_count
        self.pops_p_con = p_con
        self.pops_amb_press = amb_press
        self.pops_on_temp = on_temp
        self.pops_sample_flow = sample_flow
        self.pops_laser_temp = laser_temp
        self.pops_ext_temp = ext_temp
    def set_pumps_plunger_pops(self):
        self.pumps_plunger_pops = self.pump1 * (2 ** 15) + self.pump2 * (2 ** 14) + self.pump3 * (2 ** 13) + self.pump4 * (2 ** 12) + self.pump5 * (2 ** 11) + self.pump6 * (2 ** 10) + self.pump7 * (2 ** 9) + self.pump8 * (2 ** 8) + self.pump9 * (2 ** 7) + self.plunger * (2 ** 6) + self.pops * (2 ** 5) + self.solenoid * (2 ** 4)
    def set_heater_stat(self):
        self.heater_stat = self.heater1 * (2 ** 8) + self.heater2 * (2 ** 7) + self.heater3 * (2 ** 6) + self.heater4 * (2 ** 5) + self.heater5 * (2 ** 4)
    def get_heater_stat(self):
        return self.heater_stat
    def make_tlm_packet(self):
        #data = struct.pack(">HBQ64sffffhBHHf", self.header, self.id, self.timestamp, self.therm_bytes, self.ambient_pressure, self.air_flow_rate, self.pops_particle_density, self.pops_flow_rate, self.motherboard_temp, self.voltage_reg_status, self.pumps_plunger_pops, self.heater_stat, self.red_pops_part_dens)
        #therm_hex = self.therm_bytes.hex()
        self.checksum =  0xFFFF
        fields = [f"TLM,{self.header}", f"ID: {self.id}", f"Time: {self.timestamp}"]
        fields += [f"Therm{i}: {t/10.0:.1f}" for i, t in enumerate(self.therm_bytes)]
        fields += [f"Pressure: {self.ambient_pressure}", f"AirFlow: {self.air_flow_rate}",
                  f"PopsDensity: {self.pops_particle_density}", f"PopsFlow: {self.pops_flow_rate}",
                  f"MBTemp: {self.motherboard_temp}", f"VoltReg: {self.voltage_reg_status}",
                  f"Pump1: {self.pump1}", f"Pump2: {self.pump2}", f"Pump3: {self.pump3}", f"Pump4: {self.pump4}",
                  f"Pump5: {self.pump5}", f"Pump6: {self.pump6}", f"Pump7: {self.pump7}", f"Pump8: {self.pump8}", f"Pump9: {self.pump9}",
                  f"Plunger: {self.plunger}", f"Pops: {self.pops}", f"Solenoid: {self.solenoid}", f"Heater1: {self.heater1}", f"Heater2: {self.heater2}",
                  f"Heater3: {self.heater3}", f"Heater4: {self.heater4}", f"Heater5: {self.heater5}",
                  f"RedPopsDensity: {self.red_pops_part_dens}",
                  f"PopsDT: {self.pops_dt}", f"PopsStatus: {self.pops_p_status}", f"PopsCount: {self.pops_p_count}",
                  f"PopsConcentration: {self.pops_p_con}", f"PopsAmbPress: {self.pops_amb_press}", f"PopsOnTemp: {self.pops_on_temp}",
                  f"PopsSampleFlow: {self.pops_sample_flow}", f"PopsLaserTemp: {self.pops_laser_temp}", f"PopsExtTemp: {self.pops_ext_temp}",
                  f"ManualControl: {self.manual_control}",
                  f"Checksum: {self.checksum}", f"Terminator: {self.terminator}"]

        return ",".join(fields) + "\n"
    def set_ppps(self, id, new_state):
        if id == 1:
            self.pump1 = new_state
        elif id == 2:
            self.pump2 = new_state
        elif id == 3:
            self.pump3 = new_state
        elif id == 4:
            self.pump4 = new_state
        elif id == 5:
            self.pump5 = new_state
        elif id == 6:
            self.pump6 = new_state
        elif id == 7:
            self.pump7 = new_state
        elif id == 8:
            self.pump8 = new_state
        elif id == 9:
            self.pump9 = new_state
        elif id == 10:
            self.pops = new_state
        elif id == 11:
            self.plunger = new_state
        elif id == 12:
            self.solenoid = new_state
        self.set_pumps_plunger_pops()
    def set_heater(self, id, new_state):
        if id == 1:
            self.heater1 = new_state
        elif id == 2:
            self.heater2 = new_state
        elif id == 3:
            self.heater3 = new_state
        elif id == 4:
            self.heater4 = new_state
        elif id == 5:
            self.heater5 = new_state
        self.set_heater_stat()
    def set_therms(self, id, val):
        self.therm_bytes[id] = val
    def set_timestamp(self, time):
        hh = int(time) // 10000
        mm = (int(time) // 100) % 100
        ss = int(time) % 100
        self.timestamp = hh * 3600 + mm * 60 + ss

    def set_manual_control(self, val):
        self.manual_control = val

    def printer(self):
        
        print("---- HASP STATUS ----")
        print("Pumps:    " + " ".join(f"{i+1}:{v}" for i, v in enumerate([
            self.pump1, self.pump2, self.pump3, self.pump4, self.pump5,
            self.pump6, self.pump7, self.pump8, self.pump9,
        ])))
        print(f"Plunger:  {self.plunger}   Solenoid: {self.solenoid}   Pops: {self.pops}")
        print("Heaters:  " + " ".join(f"{i+1}:{v}" for i, v in enumerate([
            self.heater1, self.heater2, self.heater3, self.heater4, self.heater5,
        ])))
        print(f"Manual control: {self.manual_control}")
        print("Therms(C):" + " ".join(f"{i}:{t/10.0:.1f}\n" for i, t in enumerate(self.therm_bytes[:32])))
        print("RTD:" + str(self.therm_bytes[32]))
        print("Thermocouple:" + str(self.therm_bytes[33]))
        print(f"Pressure: {self.ambient_pressure}   Motherboard Temp: {self.motherboard_temp}")
        print(f"Voltage Reg Status: {self.voltage_reg_status}")
        print(f"Pops DT: {self.pops_dt}   Status: {self.pops_p_status}   Count: {self.pops_p_count}   Concentration: {self.pops_p_con}")
        print(f"Pops AmbPress: {self.pops_amb_press}   OnTemp: {self.pops_on_temp}   SampleFlow: {self.pops_sample_flow}   LaserTemp: {self.pops_laser_temp}   ExtTemp: {self.pops_ext_temp}")
        print("---------------------")