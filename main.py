import xml.etree.ElementTree as ET
from substation import Substation
from switchgear import Switchgear
from powerEquipment import PowerTransformer, PowerTransformerWinding, Line, Feeder, Generator, ShuntReactor, BusbarConnectivity
from connectivityNode import ConnectivityNode
from breaker import Breaker
import json


if __name__ == '__main__':
    with open('settings.json') as f:
        settings_file = json.load(f)

    db_host = settings_file['db_host']
    db_user = settings_file['db_user']
    db_password = settings_file['db_password']
    db_name = settings_file['db_name']
    db_port = settings_file['db_port']




    ns = {'': 'http://www.iec.ch/61850/2003/SCL',
          'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
          'ekra1': 'http://www.dev.ekra.ru',
          'sxy': 'http://www.iec.ch/61850/2003/SCLcoordinates'}
    tree = ET.parse('2020-06-06-Zaria-2007B-V0-R001.scd')
    root = tree.getroot()

    # найдем энергообъект в SCl файле
    for sub  in root.findall('Substation', ns):
        try:
            substation = Substation(sub.attrib['desc'])
        except KeyError:
            substation = Substation(sub.attrib['name'])

    # Найдем все РУ в SCL файле
    switchgears = {}
    for sw in root.iter('{'+ns['']+'}'+'VoltageLevel'):
        try:
            voltage = sw.find('Voltage',  ns)
            switchgear = Switchgear(sw.attrib['desc'], sw.attrib['name'], substation, voltage.text, voltage.attrib['unit'], voltage.attrib['multiplier'])
            switchgear.getOrCreateBaseVoltage(db_host, db_user, db_password, db_name, db_port)
            switchgears[switchgear.nameSCL] = switchgear

        except KeyError:
            voltage = sw.find('Voltage', ns)
            switchgear = Switchgear(sw.attrib['name'], sw.attrib['name'], substation, voltage.text, voltage.attrib['unit'], voltage.attrib['multiplier'])
            switchgear.getOrCreateBaseVoltage(db_host, db_user, db_password, db_name, db_port)
            switchgears[switchgear.nameSCL] = switchgear


    # создадим структуру данных для хранения Присоединений (обмоток трансформатора) и соответствующих узлов соединений
    equipment_cn_dict = {}

    # Найдем все силовые трансформаторы в SCL файле
    power_transformers = {}
    transformerWindincCNs = {} # узлы подключения обмоток силовых трансформаторов
    for pt in root.iter('{' + ns[''] + '}' + 'PowerTransformer'):
        try:
            transformer = PowerTransformer(pt.attrib['desc'], substation)
            power_transformers[transformer.name] = transformer
        except KeyError:
            transformer = PowerTransformer(pt.attrib['name'], substation )
            power_transformers[transformer.name] = transformer
        # для каждого трансформатора создадим обмотки
        for ptw in pt.findall('TransformerWinding', ns):
            try:
                try:
                    winding = PowerTransformerWinding(ptw.attrib['desc'], transformer, switchgears[ptw.find('Terminal', ns).attrib['voltageLevelName']])
                    transformer.windings.append(winding)
                except KeyError:
                    winding = PowerTransformerWinding(ptw.attrib['name'], transformer, switchgears[ptw.find('Terminal', ns).attrib['voltageLevelName']])
                    transformer.windings.append(winding)
                equipment_cn_dict[winding] = []
            except AttributeError:
                pass
            for terminal in ptw.findall('Terminal', ns):
                cn = ConnectivityNode(terminal.attrib['cNodeName'], terminal.attrib['connectivityNode'])
                transformerWindincCNs[cn.pathName] = cn
                #print("Bay name: {}, VoltageLevelName: {}".format(terminal.attrib['bayName'], terminal.attrib['voltageLevelName']))
                # определим всё силовое оборудование для присоединений, к которым подключены обмотки трансформаторов
                for bay in root.iter('{' + ns[''] + '}' + 'Bay'):
                    if terminal.attrib['bayName'] == bay.attrib['name']:
                        for connNode in bay.findall('ConnectivityNode', ns):
                            cn = ConnectivityNode(connNode.attrib['name'], connNode.attrib['pathName'])
                            equipment_cn_dict[winding].append(cn)

    # Найдем все присоединения для ЛЭП
    # ЛЭП определяется по наличию в присоединении оборудования с типом IFL
    lines = {}
    for bay in root.iter('{' + ns[''] + '}' + 'Bay'):
        for condEquip in bay.findall('ConductingEquipment', ns):
            #print('Equipment name: {}, Equipment type: {}'.format(condEquip.attrib['name'], condEquip.attrib['type']))
            if condEquip.attrib['type'] in ('IFL'):
                line = Line(bay.attrib['desc'], substation, switchgears[condEquip.find('Terminal', ns).attrib['voltageLevelName']])
                lines[line.name]= line
                equipment_cn_dict[line] = []
                for terminal in bay.findall('ConnectivityNode', ns):
                    cn = ConnectivityNode(terminal.attrib['name'], terminal.attrib['pathName'])
                    equipment_cn_dict[line].append(cn)

    # Найдем все присоединения для фидеров
    # фидер определяется по наличию в присоединении оборудования с типом CAB или LIN
    feeders = {}
    for bay in root.iter('{' + ns[''] + '}' + 'Bay'):
        for condEquip in bay.findall('ConductingEquipment', ns):
            # print('Equipment name: {}, Equipment type: {}'.format(condEquip.attrib['name'], condEquip.attrib['type']))
            if condEquip.attrib['type'] in ('CAB', 'LIN'):
                feeder = Feeder(bay.attrib['desc'], substation,
                            switchgears[condEquip.find('Terminal', ns).attrib['voltageLevelName']])
                feeders[feeder.name] = feeder
                equipment_cn_dict[feeder] = []
                for terminal in bay.findall('ConnectivityNode', ns):
                    cn = ConnectivityNode(terminal.attrib['name'], terminal.attrib['pathName'])
                    equipment_cn_dict[feeder].append(cn)

    # Найдем все присоединения для генераторов
    # генератор определяется по наличию в присоединении оборудования с типом GEN
    generators = {}
    for bay in root.iter('{' + ns[''] + '}' + 'Bay'):
        for condEquip in bay.findall('ConductingEquipment', ns):
            # print('Equipment name: {}, Equipment type: {}'.format(condEquip.attrib['name'], condEquip.attrib['type']))
            if condEquip.attrib['type'] in ('GEN'):
                gen = Generator(bay.attrib['desc'], substation,
                                switchgears[condEquip.find('Terminal', ns).attrib['voltageLevelName']])
                generators[gen.name] = gen
                equipment_cn_dict[gen] = []
                for terminal in bay.findall('ConnectivityNode', ns):
                    cn = ConnectivityNode(terminal.attrib['name'], terminal.attrib['pathName'])
                    equipment_cn_dict[gen].append(cn)

    # Найдем все присоединения для шунтирующих реакторов
    # шунтирующий реактор определяется по наличию в присоединении оборудования с типом CAP, EFN, PSH, REA, RRC, TCR
    shunt_reactors = {}
    for bay in root.iter('{' + ns[''] + '}' + 'Bay'):
        for condEquip in bay.findall('ConductingEquipment', ns):
            # print('Equipment name: {}, Equipment type: {}'.format(condEquip.attrib['name'], condEquip.attrib['type']))
            if condEquip.attrib['type'] in ('CAP', 'EFN', 'PSH', 'REA', 'RRC', 'TCR'):
                react = ShuntReactor(bay.attrib['desc'], substation,
                                switchgears[condEquip.find('Terminal', ns).attrib['voltageLevelName']])
                shunt_reactors[react.name] = react
                equipment_cn_dict[react] = []
                for terminal in bay.findall('ConnectivityNode', ns):
                    cn = ConnectivityNode(terminal.attrib['name'], terminal.attrib['pathName'])
                    equipment_cn_dict[react].append(cn)


    # Найдем все присоединения для ШСВ
    # ШСВ определяется по наличию в присоединению выключателя и отсутствию оборудования других типов
    # дополнительно нужно проверить, что к найденному присоединению ШСВ не подключено силовых трансформаторов
    busbarConnectivities = {}
    for bay in root.iter('{' + ns[''] + '}' + 'Bay'):
        flag = True  # флаг наличия оборудования других типов
        bayCNs={}
        for cn in bay.findall('ConnectivityNode', ns):
            connNode = ConnectivityNode(cn.attrib['name'], cn.attrib['pathName'])
            if connNode.pathName in transformerWindincCNs.keys():
                flag = False
        for condEquip in bay.findall('ConductingEquipment', ns):
            if condEquip.attrib['type'] in ('CAP', 'EFN', 'PSH', 'REA', 'RRC', 'TCR', 'GEN', 'CAB', 'LIN', 'IFL'):
                flag = False
        for condEquip in bay.findall('ConductingEquipment', ns):
            if condEquip.attrib['type'] in ('CBR') and flag:
                busConn = BusbarConnectivity(bay.attrib['desc'], substation,
                                     switchgears[condEquip.find('Terminal', ns).attrib['voltageLevelName']])
                busbarConnectivities[busConn.name] = busConn
                equipment_cn_dict[busConn] = []
                for terminal in bay.findall('ConnectivityNode', ns):
                    cn = ConnectivityNode(terminal.attrib['name'], terminal.attrib['pathName'])
                    equipment_cn_dict[busConn].append(cn)


    # найдем все выключатели
    breakers = {}
    for bay in root.iter('{' + ns[''] + '}' + 'Bay'):
        for condEquip in bay.findall('ConductingEquipment', ns):
            if condEquip.attrib['type'] in ('CBR'):
                br = Breaker(condEquip.attrib['desc'], substation)
                breakers[br.name] = br
                # теперь необходимо связать выключатели с присоединениями
                for terminal in condEquip.findall('Terminal', ns):
                    cn = ConnectivityNode(terminal.attrib['cNodeName'], terminal.attrib['connectivityNode'])
                    for eq in equipment_cn_dict.keys():
                        for i in equipment_cn_dict[eq]:
                            if cn.__eq__(i):
                                br.connectedEquipment.append(eq)

    # Вывод структуры силового оборудования ПС
    print(substation.__str__())

    for sw in switchgears.keys():
        print(switchgears[sw].__str__())

    for t in power_transformers.keys():
        print(power_transformers[t].__str__())
        for w in power_transformers[t].windings:
            print(w.__str__())

    for l in lines:
        print(lines[l].__str__())

    for f in feeders.keys():
        print(feeders[f].__str__())

    for b in breakers.keys():
        print(breakers[b].__str__())

