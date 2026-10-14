import serial
class Serial_Port:
	def __init__(self, baud_rate, port):
		self.baud_rate = baud_rate
		self.port = port
		self._seri = serial.Serial(port=port, baudrate=baud_rate, timeout=0.1)
	def read(self):
		pass
	def close(self):
		self._seri.close()
	
	def __enter__(self):
		return self
  
	def __exit__(self, *args):
		self.close()
  
  



