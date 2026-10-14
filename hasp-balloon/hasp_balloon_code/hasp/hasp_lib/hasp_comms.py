from .serial_handler import Serial_Port
class hasp_comms(Serial_Port):
	def __init__(self, baud_rate, port):
		super().__init__(baud_rate, port)
	def read(self):
		data = self._seri.readline()
		if not data:
			return None, None
		#this is 0x24 which every gps read begins with
		if data[0] == 36:
			return "gps", (float(data.decode().split(',')[1]), float(data.decode().split(',')[9]))
			#handle gps data
		#every command begins with one
		elif data[0] == 1:
			if (data[3] & 12) == 12:
				return "command", (data[2], data[3])
			else:
				return None, None
		else:
			return None, None
	def write(self, data):
		self._seri.write(data)
	def write_ptx(self, data):
		self._seri.write(data.encode('utf-8'))
  

if __name__ == "__main__":
	hasp = hasp_comms(4800, "/dev/ttyUSB0")
	while True:
		mode, vals = hasp.read()
		if mode == "gps" and vals:
			print("time: " + str(vals[0]))
			print("altitude: " + str(vals[1]))
			print("\n\n\n")

		if mode == "command" and vals:
			print("byte 1: " + hex(vals[0]))
			print("byte 2: " + hex(vals[1]))
			print("\n\n\n")


            

