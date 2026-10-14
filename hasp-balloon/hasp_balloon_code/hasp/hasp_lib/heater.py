from .pumps import Pump
class Heater(Pump):
    def __init__(self, gpio_ex, bank, pin, id):
        super().__init__(gpio_ex, bank, pin)
        self.id = id
    def get_id(self):
        return self.id


