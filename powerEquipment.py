import uuid

class PowerTransformer(object):
    def __init__(self, name, substation):
        self.id = uuid.uuid4()
        self.name = name
        self.short_name = name
        self.substation = substation
        self.windings = []


    def __str__(self):
        return 'PowerTransformer name: {}'.format(str(self.name))

class PowerTransformerWinding(object):
    def __init__(self, name, power_transformer, switchgear):
        self.id = uuid.uuid4()
        self.name = name
        self.short_name = name
        self.power_transformer = power_transformer
        self.switchgear = switchgear
        self.I_nom = 1000
        self.side = 1


    def __str__(self):
        return "Winding name: {}, Connected switchgear: {}".format(str(self.name), str(self.switchgear.name))


class Line(object):
    def __init__(self, name, substation, switchgear):
        self.id = uuid.uuid4()
        self.name = name
        self.short_name = name
        self.I_nom = 1000
        self.substation = substation
        self.switchgear = switchgear

    def __str__(self):
        return "Line name: {}, Connected switchgear: {}".format(str(self.name), str(self.switchgear.name))

class Feeder(object):
    def __init__(self,  name, substation, switchgear):
        self.id = uuid.uuid4()
        self.name = name
        self.short_name = name
        self.I_nom = 1000
        self.type = 1
        self.substation = substation
        self.switchgear = switchgear

    def __str__(self):
        return "Feeder name: {}, Connected switchgear: {}".format(str(self.name), str(self.switchgear.name))

class Generator(object):
    def __init__(self,  name, substation, switchgear):
        self.id = uuid.uuid4()
        self.name = name
        self.short_name = name
        self.I_nom = 1000
        self.type = 3
        self.substation = substation
        self.switchgear = switchgear

    def __str__(self):
        return "Generator name: {}, Connected switchgear: {}".format(str(self.name), (self.switchgear.name))

class ShuntReactor(object):
    def __init__(self,  name, substation, switchgear):
        self.id = uuid.uuid4()
        self.name = name
        self.short_name = name
        self.I_nom = 1000
        self.type = 2
        self.substation = substation
        self.switchgear = switchgear

    def __str__(self):
        return "ShuntReactor name: {}, Connected switchgear: {}".format(str(self.name), (self.switchgear.name))

class BusbarConnectivity(object):
    def __init__(self,  name, substation, switchgear):
        self.id = uuid.uuid4()
        self.name = name
        self.short_name = name
        self.I_nom = 1000
        self.type = 4
        self.substation = substation
        self.switchgear = switchgear

    def __str__(self):
        return "BusbarConnectivity name: {}, Connected switchgear: {}".format(str(self.name), (self.switchgear.name))