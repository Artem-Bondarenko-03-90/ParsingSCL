import uuid

class Substation(object):
    def __init__(self, name):
        self.name = name
        self.short_name = name
        self.id = uuid.uuid4()

    def __str__(self):
        return "Substation name: {}, id: {}".format(str(self.name), str(self.id))