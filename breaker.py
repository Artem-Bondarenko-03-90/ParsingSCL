import uuid

class Breaker(object):
    def __init__(self, name, substation):
        self.id = uuid.uuid4()
        self.name = name
        self.short_name = name
        self.control_phases = 2
        self.in_transit_time = 0.1
        self.out_transit_time = 0.1
        self.substation = substation
        self.position_a = 2
        self.position_b = 2
        self.position_c = 2
        self.status = 2
        self.connectedEquipment = []

    def __str__(self):
        return "Breaker name: {}".format(str(self.name))