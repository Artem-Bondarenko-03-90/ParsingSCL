
class ConnectivityNode(object):
    def __init__(self, name, pathName):
        self.name = name
        self.pathName = pathName

    def __str__(self):
        return "Node name: {}, Path: {}".format(str(self.name), str(self.pathName))

    def __eq__(self, other):
        if self.name == other.name and self.pathName == other.pathName:
            return True
        else:
            return False