import re

pattern = re.compile(r'\w\w')


class Command:
    def __init__(self, dev_id, access, passwd, phone, param):
        self.id = dev_id
        self._access = access
        self.passwd = passwd
        self.phone = phone
        self.param = param

        self.COMMAND = {
            'TEST': [self.id, '00'],
            'OPEN_SESSION': [self.id, '01', self._access, self.passwd],
            'CLOSE_SESSION': [self.id, '02'],
            'GET_IDENTIFIER': [self.id, '08 05'],
            'GET_SERIAL': [self.id, '08 00'],
            'GET_EXECUTION': [self.id, '08 01 00'],
            'GET_DESCRIPTOR': [self.id, '06 04 1A 04 02'],
            'GET_VECTORS': [self.id, '06 04', self.param],
            'UPDATE_FIRMWARE': [self.id, '07 05', self.param],
            'GET_PASSWD': [self.id, '06 02', self.param],
            'SET_PASSWD': [self.id, '03 1F', self.param],
            'SET_SPODES': [self.id, '03 12', self.param],
            'GET_EVENT': [self.id, '04', self.param],
            'SET_DATA': [self.id, '07', self.param],
            'SET_METERS': [self.id, '07 02', self.param],
            'GET_SHUNT': [self.id, '06 04', self.param],
            'SET_SHUNT': [self.id, '07 01 F4 00 0A', self.param]
            # ID ",0x07,0x01,0xF4,0x00,0x0A," rez_1 "," rez_2 "," rez_3 "," rez_4 ",0x00,0x00,0x00,0x00,0x00,0x00"
        }

        self.HARDWARE = {
            '81A3': 'MSP430F67771', '8190': 'MSP430F6768', '8191': 'MSP430F6769', '8195': 'MSP430F6778',
            '8196': 'MSP430F6779', '819F': 'MSP430F67681', '81A0': 'MSP430F67691', '81A4': 'MSP430F67781',
            '81A5': 'MSP430F67791', '821E': 'MSP430F6768A', '821F': 'MSP430F6769A', '8223': 'MSP430F6778A',
            '8224': 'MSP430F6779A', '822D': 'MSP430F67681A', '822E': 'MSP430F67691A',
            '8232': 'MSP430F67781A', '8233': 'MSP430F67791A', 'None': 'None'
        }

        self.CALL = {
            'AT': 'AT\r',
            'CBST': 'AT+CBST=71,0,1\r',
            'CALL': f'ATD{self.phone}\r'
        }

    @staticmethod
    def get(tmp):
        return {
            tmp == "00": "OK",
            tmp == "01": "Недопустимая команда или параметр",
            tmp == "02": "Внутренняя ошибка счетчика",
            tmp == "03": "Недостаточен уровень для удовлетворения запроса",
            tmp == "04": "Внутренние часы счетчика уже корректировались в течение текущих суток",
            tmp == "05": "Не открыт канал связи"
            # bool(pattern.match(tmp)): "Ошибка"
        }[True]
