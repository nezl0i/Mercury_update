import sys
from datetime import datetime
from time import sleep
from colors import Colors
from modbus_crc16 import crc16
from uart import UartSerialPort

c = Colors()


def repeat(func):
    def wrapper_repeat(*args, **kwargs):
        for _ in range(3):
            current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
            check, get_hex, tmp = func(*args, **kwargs)
            print(f'[{current_time}] :{c.BLUE} >>', get_hex, c.END)
            if check:
                print(f'[{current_time}] :{c.FAIL} <<', tmp, c.END)
                return check, get_hex, tmp
            sleep(2)
        print(f'{c.WARNING}Нет ответа от устройства.{c.END}')
        sys.exit()
    return wrapper_repeat


class ExchangeProtocol(UartSerialPort):
    def __init__(self, port_name, port_timeout, password='111111', identifier=0, access=1):
        super().__init__(port_name, port_timeout)
        self.__password = ' '.join((format(int(i), '02X')) for i in password)
        self.__id = format(identifier, '02X')
        self._access = format(access, '02X')
        self.buffer = ''
        self.param = ''
        self.hex_out = []

        self.COMMAND = {'TEST': [self.id, '00'],
                        'OPEN_SESSION': [self.id, '01', self._access, self.passwd],
                        'CLOSE_SESSION': [self.id, '02'],
                        'GET_IDENTIFIER': [self.id, '08 05'],
                        'GET_SERIAL': [self.id, '08 00'],
                        'GET_EXECUTION': [self.id, '08 01 00'],
                        'GET_DESCRIPTOR': [self.id, '06 04 1A 04 02'],
                        'GET_VECTORS': [self.id, '06 04', self.param],
                        'GET_FIRMWARE': [self.id, '07 05', self.param]}

    def clear(self):
        return self.hex_out.clear()

    @property
    def passwd(self):
        if len(self.__password.split(' ')) != 6:
            print(f'{c.WARNING}Пароль не должен превышать 6 знаков.{c.END}')
            sys.exit()
            # self.__password = self.__password[:17]
        return self.__password

    @property
    def id(self):
        if int(self.__id, 16) > 254:
            print(f'{c.WARNING}Введен неверный ID прибора учета.{c.END}')
            sys.exit()
        return self.__id

    @repeat
    def exchange(self, command_name, count, param=''):
        tmp_buffer = ''
        self.clear()
        if param:
            self.COMMAND[command_name].pop()
            self.COMMAND[command_name].append(param)
        data = ' '.join(list(map(lambda var: var, self.COMMAND[command_name])))
        transfer = bytearray.fromhex(data + ' ' + crc16(bytearray.fromhex(data)))
        get_hex_line = ' '.join(format(x, '02x') for x in transfer)
        self.write(transfer)
        self.buffer = self.read(count)
        while self.buffer:
            if len(self.buffer) == count:
                tmp_buffer = self.buffer.hex(' ', -1)
                return True, get_hex_line, tmp_buffer
            break
        return False, get_hex_line, tmp_buffer

    def update_firmware(self, file):
        hi_address = ''
        lo_address = ''
        arg_value = ''
        with open(file) as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith('@'):
                arg_value = '02'
                hex_line = line[1:].rstrip()
                if len(hex_line) < 5:
                    hi_address = f'0{hex_line[:1]}'
                    lo_address = f'{hex_line[1:]}0' if len(hex_line[1:]) == 1 else f'{hex_line[1:]}'
                else:
                    hi_address = f'{hex_line[:2]}'
                    lo_address = f'{hex_line[2:4]}'

            elif line.startswith('q'):
                send_command = f'12 0F 3C 0F FC 10'
                a = self.exchange('GET_FIRMWARE', 4, param=send_command)
                self.hex_out.append(a[2])
                return self.hex_out
            else:
                send_command = f'{arg_value} {hi_address} {lo_address} {line.rstrip()}'
                a = self.exchange('GET_FIRMWARE', 4, param=send_command)
                self.hex_out.append(a[2])
                if lo_address == 'FF':
                    hi_address = format(int(hi_address, 16) + 1, "02X")
                    lo_address = '00'
                    arg_value = '00'
                else:
                    lo_address = format(int(lo_address, 16) + 1, "02X")
                    arg_value = '00'

    def test_channel(self):
        self.hex_out.append(self.exchange('TEST', 4)[2])
        return self.hex_out

    def open_session(self):
        self.hex_out.append(self.exchange('OPEN_SESSION', 4)[2])
        return self.hex_out

    def close_session(self):
        self.hex_out.append(self.exchange('CLOSE_SESSION', 4)[2])
        return self.hex_out

    def read_identifier(self):
        self.hex_out.append(self.exchange('GET_IDENTIFIER', 5)[2])
        return self.hex_out

    def read_serial(self):
        self.hex_out.append(self.exchange('GET_SERIAL', 10)[2])
        return self.hex_out

    def execution(self):
        self.hex_out.append(self.exchange('GET_EXECUTION', 27)[2])
        return self.hex_out

    def descriptor(self):
        self.hex_out.append(self.exchange('GET_DESCRIPTOR', 5)[2])
        return self.hex_out

    def get_firmware(self, file):
        return self.update_firmware(file)

    def get_vectors(self):
        vectors = []
        param = ['F1 C0 10', 'F1 D0 10', 'F1 E0 10', 'F1 F0 10']
        for i in range(len(param)):
            a = self.exchange('GET_VECTORS', 19, param=param[i])
            vectors.append(a[2])
        return vectors
