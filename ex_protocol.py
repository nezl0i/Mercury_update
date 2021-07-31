import sys
from sys import platform
from datetime import datetime
from time import sleep
from modbus_crc16 import crc16
from uart import UartSerialPort
import execute
import event_log as log

if platform.startswith('win'):
    from colors import WinColors
    c = WinColors()
else:
    from colors import Colors
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
            sleep(1)
        print(f'{c.WARNING}Нет ответа от устройства.{c.END}')
        sys.exit()

    return wrapper_repeat


def get_out(tmp):
    return {
        tmp == "00": "OK",
        tmp == "01": "Недопустимая команда или параметр",
        tmp == "02": "Внутренняя ошибка счетчика",
        tmp == "03": "Недостаточен уровень для удовлетворения запроса",
        tmp == "04": "Внутренние часы счетчика уже корректировались в течение текущих суток",
        tmp == "05": "Не открыт канал связи"
    }[True]


class ExchangeProtocol(UartSerialPort):
    __slots__ = ('port_name', 'port_timeout', 'password', 'identifier', 'access', 'mode', 'file', '__password',
                 '__id', '_access', 'buffer', 'param', 'hex_out', 'phone', 'call_flag', 'CALL', 'COMMAND',
                 'hardware', 'device', 'tmp_event', 'pass_mode')

    def __init__(self, port_name, port_timeout, password='111111', identifier=0, access=1, mode=0, phone='', file='',
                 pass_mode='hex'):
        super().__init__(port_name, port_timeout)
        self.pass_mode = pass_mode

        if self.pass_mode == 'hex':
            self.__password = ' '.join((format(int(i), '02X')) for i in password)
        elif self.pass_mode == 'ascii':
            self.__password = ' '.join((format(ord(i), '02X')) for i in password)
        else:
            print('No pass_mode.')
            sys.exit()

        self.__id = format(identifier, '02X')
        self._access = format(access, '02X')
        self.mode = mode
        self.phone = phone
        self.file = file

        self.param = ''
        self.call_flag = False
        self.device = ''

        self.CALL = {'AT': 'AT\r',
                     'CBST': 'AT+CBST=71,0,1\r',
                     'CALL': f'ATD{self.phone}\r'
                     }

        self.hardware = {'81A3': 'MSP430F67771', '8190': 'MSP430F6768', '8191': 'MSP430F6769', '8195': 'MSP430F6778',
                         '8196': 'MSP430F6779', '819F': 'MSP430F67681', '81A0': 'MSP430F67691', '81A4': 'MSP430F67781',
                         '81A5': 'MSP430F67791', '821E': 'MSP430F6768A', '821F': 'MSP430F6769A', '8223': 'MSP430F6778A',
                         '8224': 'MSP430F6779A', '822D': 'MSP430F67681A', '822E': 'MSP430F67691A',
                         '8232': 'MSP430F67781A', '8233': 'MSP430F67791A', 'None': 'None'
                         }

        self.COMMAND = {'TEST': [self.id, '00'],
                        'OPEN_SESSION': [self.id, '01', self._access, self.passwd],
                        'CLOSE_SESSION': [self.id, '02'],
                        'GET_IDENTIFIER': [self.id, '08 05'],
                        'GET_SERIAL': [self.id, '08 00'],
                        'GET_EXECUTION': [self.id, '08 01 00'],
                        'GET_DESCRIPTOR': [self.id, '06 04 1A 04 02'],
                        'GET_VECTORS': [self.id, '06 04', self.param],
                        'GET_FIRMWARE': [self.id, '07 05', self.param],
                        'GET_PASSWD': [self.id, '06 02', self.param],
                        'SET_PASSWD': [self.id, '03 1F', self.param],
                        'SET_SPODES': [self.id, '03 12', self.param],
                        'GET_EVENT': [self.id, '04', self.param]
                        }

    def set_id(self, var):
        self.__id = var

    def set_device(self, var):
        self.device = var

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

    @property
    def level(self):
        return self._access

    @repeat
    def exchange(self, command_name, count, param=''):
        if self.mode == 1:
            print(self.CSD_send(self.CALL['AT']))
            print(self.CSD_send(self.CALL['CBST']))
            self.set_time(10)
            for _ in range(3):
                calling = self.CSD_send(self.CALL['CALL'])
                print(calling)
                if calling == 'Connect OK (9600)\n':
                    self.call_flag = True
                    break
            if self.call_flag:
                self.mode = 0
            else:
                sys.exit()

        if param:
            self.COMMAND[command_name].pop()
            self.COMMAND[command_name].append(param)
        data = ' '.join(list(map(lambda var: var, self.COMMAND[command_name])))
        transfer = bytearray.fromhex(data + ' ' + crc16(bytearray.fromhex(data)))
        print_line = ' '.join(format(x, '02x') for x in transfer)
        self.write(transfer)
        buffer = self.read(count)
        while buffer:
            if len(buffer) == count:
                return True, print_line, buffer.hex(' ', -1)
            break
        return False, print_line, buffer.hex(' ', -1)

    def update_firmware(self):
        hi_address = ''
        lo_address = ''
        arg_value = ''
        with open(self.file) as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith('@'):
                arg_value = '02'
                hex_line = line[1:].rstrip()

                if hex_line[0].isdigit():
                    hi_address = format(int(hex_line[:2], 16), "02X")
                    lo_address = format(int(hex_line[2:4], 16), "02X")
                else:
                    hi_address = format(int(hex_line[0], 16), "02X")
                    lo_address = format(int(hex_line[1:3], 16), "02X")

            elif line.startswith('q'):
                send_command = f'12 0F 3C 0F FC 10'
                out = self.exchange('GET_FIRMWARE', 4, param=send_command)[2].split(' ')
                if out[1] == '00':
                    print(f'{c.GREEN}Обновление выполнено успешно!{c.END}')
                else:
                    print(f'{c.FAIL}Не удалось выполнить обновление...{c.END}')
                return
            else:
                send_command = f'{arg_value} {hi_address} {lo_address} {line.rstrip()}'
                self.exchange('GET_FIRMWARE', 4, param=send_command)
                if lo_address == 'FF':
                    hi_address = format(int(hi_address, 16) + 1, "02X")
                    lo_address = '00'
                    arg_value = '00'
                else:
                    lo_address = format(int(lo_address, 16) + 1, "02X")
                    arg_value = '00'

    def test_channel(self):
        out = self.exchange('TEST', 4)[2].split(' ')
        print(f'{c.GREEN}Тест канала связи - '
              f'{get_out(out[1])}{c.END}\n')
        return

    def open_session(self):
        out = self.exchange('OPEN_SESSION', 4)[2].split(' ')
        print(f'{c.GREEN}Открытие канала связи - '
              f'{get_out(out[1])}{c.END}\n')
        return

    def close_session(self):
        out = self.exchange('CLOSE_SESSION', 4)[2].split(' ')
        print(f'{c.GREEN}Закрытие канала связи - '
              f'{get_out(out[1])}{c.END}\n')
        return

    def read_identifier(self):
        out = self.exchange('GET_IDENTIFIER', 5)[2].split(' ')
        id_result = int(out[2], 16)
        print(f'{c.GREEN}Идентификатор ПУ - {id_result}{c.END}\n')
        return

    def read_serial(self):
        out = self.exchange('GET_SERIAL', 10)[2].split(' ')
        tmp_check_out = list(map(lambda x: str(int(x, 16)).zfill(2), out))
        result = ''.join(tmp_check_out[1:5])
        self.set_device(result)
        work_data = '.'.join(tmp_check_out[5:8])
        print(f'{c.GREEN}Серийный номер - {self.device}\n'
              f'Дата выпуска - {work_data}{c.END}\n')
        return

    def execution(self):
        var = self.exchange('GET_EXECUTION', 27)[2].split(' ')
        tmp_serial = list(map(lambda x: str(int(x, 16)).zfill(2), var[1:5]))
        tmp_data = list(map(lambda x: str(int(x, 16)).zfill(2), var[5:8]))
        tmp_version = list(map(lambda x: str(int(x, 16)).zfill(2), var[8:11]))
        tmp_revision = list(map(lambda x: str(int(x, 16)).zfill(2), var[19:21]))
        self.set_device(''.join(tmp_serial))
        data = '.'.join(tmp_data)
        version = '.'.join(tmp_version)
        revision = '.'.join(tmp_revision)
        crc_po = f"{''.join(var[17:19]).upper()}"

        byte_1 = format(int(var[11], 16), "08b")
        byte_2 = format(int(var[12], 16), "08b")
        byte_3 = format(int(var[13], 16), "08b")
        byte_4 = format(int(var[14], 16), "08b")
        byte_5 = format(int(var[15], 16), "08b")
        byte_6 = format(int(var[16], 16), "08b")
        byte_7 = format(int(var[21], 16), "08b")
        # byte_8 = format(int(check_out[22], 16), "08b")

        return execute.print_exec(self.device, data, version, revision, crc_po, byte_1, byte_2,
                                  byte_3, byte_4, byte_5, byte_6, byte_7)

    def descriptor(self):
        out = self.exchange('GET_DESCRIPTOR', 5)[2].split(' ')
        desc = f'{out[2]}{out[1]}'
        print(f'{c.GREEN}Дескриптор ПУ - {desc}\n'
              f'Микроконтроллер - {self.hardware[desc]}{c.END}\n')
        return

    def get_vectors(self):
        var = []
        param = ['F1 C0 10', 'F1 D0 10', 'F1 E0 10', 'F1 F0 10']
        for i in range(len(param)):
            var.append(' '.join(self.exchange('GET_VECTORS', 19, param=param[i])[2].split(' ')[1:16]))
        print(f'{c.GREEN}Вектора прерываний:')
        print(*var, c.END, sep='\n')
        return

    def get_password(self):
        var = []
        param = ['00 4F 06', '00 48 06']
        for i in range(len(param)):
            var.append(self.exchange('GET_PASSWD', 9, param=param[i])[2].split(' ')[1:7])
        for i, el in enumerate(var, 1):
            passwd = ''.join(map(lambda x: str(int(x, 16)), el))
            if len(passwd) == 6:
                print(f'{c.GREEN}Пароль {i} уровня- {passwd} (HEX){c.END}')
            else:
                passwd = ''.join(map(lambda x: bytearray.fromhex(x).decode(), el))
                print(f"{c.GREEN}Пароль {i} уровня- {''.join(passwd)} (ASCII){c.END}")
        print('\n')
        return

    def set_spodes(self, channel, value, byte_timeout, active_time):
        """
        :param channel: 0 – оптопорт, 1 – встроенный, 2 – левый канал, 3 – правый канал
        :param value: 0 – «Меркурий», 1 – «СПОДЭС»
        :param byte_timeout: Межсимвольный таймаут
        :param active_time: Таймаут неактивности
        :return: Result
        """
        interface = {0: "Оптопорт", 1: "Встроенный", 2: "Левый канал", 3: "Правый канал"}
        default_protocol = {0: "Меркурий", 1: "СПОДЭС"}
        ch = format(channel, '02X')
        val = format(value, '02X')
        lo_byte_timeout = format(byte_timeout, '04X')[:2]
        hi_byte_timeout = format(byte_timeout, '04X')[2:]
        act_time = format(active_time, '02X')

        param = f'{ch} {val} 00 {hi_byte_timeout} {lo_byte_timeout} {act_time}'
        out = self.exchange('SET_SPODES', 4, param=param)[2].split(' ')
        print(f'{c.GREEN}Интерфейс - "{interface[channel]}"\n'
              f'Протокол - "{default_protocol[value]}"\n'
              f'Межсимвольный таймаут - {byte_timeout}\n'
              f'Тайиаут неактивности - {active_time}\n'
              f'Выполнение - {get_out(out[1])}{c.END}\n')
        return

    def get_event(self, number=None, position=None):
        """
        :param number: Номер журнала (1-26), None - читать все журналы
        :param position: Номер записи (1-10), None - читать все записи
        :return: Результат
        """

        list_all = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '0A', '0B', '0C', '0D',
                    '0E', '0F', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1A']
        list_0 = ['07', '08', '09', '0A', '0B', '0C', '0D', '0E', '0F', '10', '11', '15', '16']
        param = None
        pos = None
        tmp_key = []
        tmp_out = []
        tmp_event = []
        flag = 1

        if number is not None and position is None:
            if 0 < number <= 26:
                param = format(number, '02X')
                flag = 3
            else:
                print('Некорректный номер журнала')
                sys.exit()

        elif number is not None and position is not None:
            if 0 < number <= 26 and 0 < position <= 10:
                position -= 1
                param = format(number, '02X')
                pos = format(position, '02X')
                flag = 4
            else:
                print('Некорректный введен номер параметра')
                sys.exit()
        elif number is None and position is not None:
            if 0 < position <= 10:
                position -= 1
                pos = format(position, '02X')
                flag = 2
            else:
                print('Некорректный номер записи')
                sys.exit()

        for i in range(len(list_all)):
            key = list_all[i]
            tmp_out.clear()
            count = 9 if list_all[i] in list_0 else 15

            if flag == 1:
                print(f'{c.GREEN}[ {log.event(key)} ]{c.END}')
                for j in range(10):
                    index = format(j, '02X')
                    tmp_out.append(self.exchange('GET_EVENT', count, param=f'{key} {index}')[2])
            elif flag == 2:
                print(f'{c.GREEN}[ {log.event(key)} ]{c.END}')
                tmp_out.append(self.exchange('GET_EVENT', count, param=f'{key} {pos}')[2])
            elif flag == 3:
                print(f'{c.GREEN}[ {log.event(param)} ]{c.END}')
                count = 9 if param in list_0 else 15
                for j in range(10):
                    index = format(j, '02X')
                    tmp_out.append(self.exchange('GET_EVENT', count, param=f'{param} {index}')[2])
                tmp_event.append(tmp_out[:])
                tmp_key.append(param)
                break
            elif flag == 4:
                print(f'{c.GREEN}[ {log.event(param)} ]{c.END}')
                count = 9 if param in list_0 else 15
                tmp_out.append(self.exchange('GET_EVENT', count, param=f'{param} {pos}')[2])
                tmp_event.append(tmp_out[:])
                tmp_key.append(key)
                break
            tmp_event.append(tmp_out[:])
            tmp_key.append(key)
        event_dict = dict(zip(tmp_key, tmp_event))
        return log.print_log(event_dict)

    def set_passwd(self, pwd, md):
        if md == 'hex':
            tmp_pass = ' '.join((format(int(i), '02X')) for i in pwd)
        elif md == 'ascii':
            tmp_pass = ' '.join((format(ord(i), '02X')) for i in pwd)
        else:
            print('Bad password mode (use "hex" or "ascii").')
            sys.exit()
        out = self.exchange('SET_PASSWD', 4, param=f'{self.level} {self.passwd} {tmp_pass}')[2].split(' ')
        print(f'{c.GREEN}Изменение пароля  - '
              f'{get_out(out[1])}{c.END}\n')
        return
