from .serial_handler import Serial_Port
import RPi.GPIO as GPIO
class Pops(Serial_Port):
    def __init__(self, baud_rate, port):
        super().__init__(baud_rate, port)
        self.state = 0
    def toggle(self):

        if self.state == 0:
            GPIO.output(26, GPIO.HIGH)
            self.state = 1
        elif self.state == 1:
            GPIO.output(26, GPIO.LOW)
            self.state = 0
    def turn_on(self):
        GPIO.output(26, GPIO.HIGH)
        self.state = 1
    def turn_off(self):
        GPIO.output(26, GPIO.LOW)
        self.state = 0
    def read(self):
        no_data = (None, None, None, None, None, None, None, None, None)
        last_record = None
        data = self._seri.readline()
        while data:
            fields = data.decode(errors="ignore").split(",")
            for i, field in enumerate(fields):
                if field.endswith("POPS"):
                    last_record = fields[i:]
            data = self._seri.readline()
        if last_record is None:
            return no_data
        try:
            return last_record[3], last_record[5], last_record[7], last_record[9], last_record[14], last_record[15], last_record[19], last_record[21], last_record[24]
        except IndexError:
            return no_data
    def get_state(self):
        return self.state

if __name__ == "__main__":
    pops = Pops(9600, "/dev/serial0")
    print(pops.read())
