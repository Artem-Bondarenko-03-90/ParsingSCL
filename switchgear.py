import uuid
import psycopg2


class Switchgear(object):
    def __init__(self, name, nameSCL, substation, voltage, unit, multiplier):
        self.name = name
        self.short_name = name
        self.id = uuid.uuid4()
        self.substation = substation
        self.base_voltage_id = None
        self.voltage = voltage
        self.unit = unit
        self.multiplier = multiplier
        self.nameSCL = nameSCL

    def __str__(self):
        return "Switchgear name: {}, nominal voltage: {}".format(str(self.name), str(self.voltage)+' '+str(self.multiplier)+str(self.unit))
    
    # метод преобразует величину напряжения в вольты
    def convertNominalVoltage(self):
        if self.multiplier == 'k':
            return int(float(self.voltage) *1000)
        elif self.multiplier == 'M':
            return int(float(self.voltage) *1000000)

    # найдем в БД АСМ соответствующую запись asm_base_voltage
    def getOrCreateBaseVoltage(self, db_host, db_user, db_password, db_name, db_port):
        connection = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port
        )
        connection.autocommit = True
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM public.asm_base_voltage WHERE nominal = "+str(self.convertNominalVoltage())+";")
                result = cursor.fetchone()
                if result != None:
                    self.base_voltage_id = result[0]
                else:
                    # здесь нужно создавать недостающие записи asm_base_voltage
                    pass
        except Exception as ex:
            print(ex)
            return None
        finally:
            if connection:
                connection.close()