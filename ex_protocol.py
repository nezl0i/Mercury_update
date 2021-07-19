import sys
from datetime import datetime
from time import sleep
from colors import Colors
from modbus_crc16 import crc16
from uart import UartSerialPort
from execute import Execute

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


class ExchangeProtocol(UartSerialPort):
    __slots__ = ('port_name', 'port_timeout', 'password', 'identifier', 'access', 'mode', 'file', '__password',
                 '__id', '_access', 'buffer', 'param', 'hex_out', 'phone', 'call_flag', 'CALL', 'COMMAND', 'var',
                 'hardware')

    def __init__(self, port_name, port_timeout, password='111111', identifier=0, access=1, mode=0, phone='', file=''):
        super().__init__(port_name, port_timeout)
        self.__password = ' '.join((format(int(i), '02X')) for i in password)
        self.__id = format(identifier, '02X')
        self._access = format(access, '02X')
        self.buffer = ''
        self.param = ''
        self.hex_out = []
        self.var = []
        self.mode = mode
        self.phone = phone
        self.call_flag = False
        self.file = file

        self.CALL = {
            'AT': 'AT\r',
            'CBST': 'AT+CBST=71,0,1\r',
            'CALL': f'ATD{self.phone}\r'
        }

        self.hardware = {'81A3': 'MSP430F67771', '8190': 'MSP430F6768', '8191': 'MSP430F6769', '8195': 'MSP430F6778',
                         '8196': 'MSP430F6779', '819F': 'MSP430F67681', '81A0': 'MSP430F67691', '81A4': 'MSP430F67781',
                         '81A5': 'MSP430F67791', '821E': 'MSP430F6768A', '821F': 'MSP430F6769A', '8223': 'MSP430F6778A',
                         '8224': 'MSP430F6779A', '822D': 'MSP430F67681A', '822E': 'MSP430F67691A',
                         '8232': 'MSP430F67781A', '8233': 'MSP430F67791A', 'None': 'None'}

        self.COMMAND = {'TEST': [self.id, '00'],
                        'OPEN_SESSION': [self.id, '01', self._access, self.passwd],
                        'CLOSE_SESSION': [self.id, '02'],
                        'GET_IDENTIFIER': [self.id, '08 05'],
                        'GET_SERIAL': [self.id, '08 00'],
                        'GET_EXECUTION': [self.id, '08 01 00'],
                        'GET_DESCRIPTOR': [self.id, '06 04 1A 04 02'],
                        'GET_VECTORS': [self.id, '06 04', self.param],
                        'GET_FIRMWARE': [self.id, '07 05', self.param]
                        }

    def clear(self):
        return self.hex_out.clear()

    @staticmethod
    def get_out(tmp):
        return {
            tmp == "00": "OK",
            tmp == "01": "Недопустимая команда или параметр",
            tmp == "02": "Внутренняя ошибка счетчика",
            tmp == "03": "Недостаточен уровень для удовлетворения запроса",
            tmp == "04": "Внутренние часы счетчика уже корректировались в течение текущих суток",
            tmp == "05": "Не открыт канал связи"
        }[True]

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
        if self.mode == 1:

            print(self.CSD_send(self.CALL['AT']))
            print(self.CSD_send(self.CALL['CBST']))
            self.set_time(10)
            for _ in range(3):
                calling = self.CSD_send(self.CALL['CALL'])
                print(calling)
                if calling == 'Connect OK (9600)':
                    self.call_flag = True
                    break
            if self.call_flag:
                self.mode = 0
            else:
                sys.exit()

        tmp_buffer = ''
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
                if len(hex_line) < 5:
                    hi_address = f'0{hex_line[:1]}'
                    lo_address = f'{hex_line[1:]}0' if len(hex_line[1:]) == 1 else f'{hex_line[1:]}'
                else:
                    hi_address = f'{hex_line[:2]}'
                    lo_address = f'{hex_line[2:4]}'

            elif line.startswith('q'):
                send_command = f'12 0F 3C 0F FC 10'
                # a = self.exchange('GET_FIRMWARE', 4, param=send_command)
                self.hex_out.append(self.exchange('GET_FIRMWARE', 4, param=send_command)[2])
                for el in self.hex_out:
                    self.var = el.split(' ')
                if self.var[1] == '00':
                    print(f'{c.GREEN}Обновление выполнено успешно!{c.END}')
                else:
                    print(f'{c.FAIL}Не удалось выполнить обновление...{c.END}')
                self.clear()
                return
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
        for el in self.hex_out:
            self.var = el.split(' ')
        print(f'{c.GREEN}Тест канала связи - {self.get_out(self.var[1])}{c.END}\n')
        self.clear()
        return

    def open_session(self):
        self.hex_out.append(self.exchange('OPEN_SESSION', 4)[2])
        for el in self.hex_out:
            self.var = el.split(' ')
        print(f'{c.GREEN}Открытие канала связи - {self.get_out(self.var[1])}{c.END}\n')
        self.clear()
        return

    def close_session(self):
        self.hex_out.append(self.exchange('CLOSE_SESSION', 4)[2])
        for el in self.hex_out:
            self.var= el.split(' ')
        print(f'{c.GREEN}Закрытие канала связи - {self.get_out(self.var[1])}{c.END}\n')
        self.clear()
        return

    def read_identifier(self):
        self.hex_out.append(self.exchange('GET_IDENTIFIER', 5)[2])
        for el in self.hex_out:
            self.var = el.split(' ')
        id_result = int(self.var[2], 16)
        print(f'{c.GREEN}Идентификатор ПУ - {id_result}{c.END}\n')
        self.clear()
        return

    def read_serial(self):
        self.hex_out.append(self.exchange('GET_SERIAL', 10)[2])
        for el in self.hex_out:
            self.var = el.split(' ')
        tmp_check_out = list(map(lambda x: str(int(x, 16)).zfill(2), self.var))
        serial_result = ''.join(tmp_check_out[1:5])
        work_data = '.'.join(tmp_check_out[5:8])
        print(f'{c.GREEN}Серийный номер - {serial_result}\nДата выпуска - {work_data}{c.END}\n')
        self.clear()
        return

    def execution(self):
        self.hex_out.append(self.exchange('GET_EXECUTION', 27)[2])
        for el in self.hex_out:
            self.var = el.split(' ')
        tmp_serial = list(map(lambda x: str(int(x, 16)).zfill(2), self.var[1:5]))
        tmp_data = list(map(lambda x: str(int(x, 16)).zfill(2), self.var[5:8]))
        tmp_version = list(map(lambda x: str(int(x, 16)).zfill(2), self.var[8:11]))
        tmp_revision = list(map(lambda x: str(int(x, 16)).zfill(2), self.var[19:21]))
        serial = ''.join(tmp_serial)
        data = '.'.join(tmp_data)
        version = '.'.join(tmp_version)
        revision = '.'.join(tmp_revision)
        crc_po = f"{''.join(self.var[17:19]).upper()}"

        byte_1 = format(int(self.var[11], 16), "08b")
        byte_2 = format(int(self.var[12], 16), "08b")
        byte_3 = format(int(self.var[13], 16), "08b")
        byte_4 = format(int(self.var[14], 16), "08b")
        byte_5 = format(int(self.var[15], 16), "08b")
        byte_6 = format(int(self.var[16], 16), "08b")
        byte_7 = format(int(self.var[21], 16), "08b")
        # byte_8 = format(int(check_out[22], 16), "08b")
        print(f'{c.GREEN}Серийный номер - {serial}\n'
              f'Дата выпуска - {data}\n'
              f'Версия ПО - {version}\n'
              f'Ревизия ПО - {revision}\n'
              f'CRC ПО - {crc_po}\n'
              f'Класс точности А+ : {Execute.byte_11(byte_1[:2])}\n'
              f'Класс точности R+ : {Execute.byte_12(byte_1[2:4])}\n'
              f'Номинальное напряжение : {Execute.byte_13(byte_1[4:6])}\n'
              f'Номинальный ток : {Execute.byte_14(byte_1[6:])}\n'
              f'Число направлений : {Execute.byte_21(byte_2[0])}\n'
              f'Температурный диапазон : {Execute.byte_22(byte_2[1])}\n'
              f'Учет профиля средних мощностей : {Execute.byte_23(byte_2[2])}\n'
              f'Число фаз : {Execute.byte_24(byte_2[3])}\n'
              f'Постоянная счетчика : {Execute.byte_25(byte_2[4:])}\n'
              f'Суммирование фаз : {Execute.byte_31(byte_3[0])}\n'
              f'Тарификатор : {Execute.byte_32(byte_3[1])}\n'
              f'Тип счетчика : {Execute.byte_33(byte_3[2:4])}\n'
              f'Номер варианта исполнения : {Execute.byte_34(byte_3[4:])}\n'
              f'Память №3 : {Execute.byte_41(byte_4[0])}\n'
              f'Модем PLC : {Execute.byte_42(byte_4[1])}\n'
              f'Модем GSM : {Execute.byte_43(byte_4[2])}\n'
              f'Оптопорт : {Execute.byte_44(byte_4[3])}\n'
              f'Интерфейс 1: {Execute.byte_45(byte_4[4:6])}\n'
              f'Внешнее питание : {Execute.byte_46(byte_4[6])}\n'
              f'Эл.пломба верхней крышки : {Execute.byte_47(byte_4[7])}\n'
              f'Флаг наличия встроенного реле : {Execute.byte_47(byte_5[0])}\n'
              f'Флаг наличия подсветки ЖКИ : {Execute.byte_47(byte_5[1])}\n'
              f'Флаг потарифного учета максимумов мощности : {Execute.byte_47(byte_5[2])}\n'
              f'Флаг наличия эл.пломбы защитной крышки : {Execute.byte_47(byte_5[3])}\n'
              f'Интерфейс 2 : {Execute.byte_47(byte_5[4])}\n'
              f'Встроенное питание интерфейса 1 : {Execute.byte_47(byte_5[5])}\n'
              f'Контроль ПКЭ : {Execute.byte_47(byte_5[6])}\n'
              f'Пофазный учет энергии А+ : {Execute.byte_47(byte_5[7])}\n'
              f'Флаг измерения тока в нуле : {Execute.byte_47(byte_6[0])}\n'
              f'Флаг расширенного перечня массивов : {Execute.byte_47(byte_6[1])}\n'
              f'Флаг протокола IEC 61107 : {Execute.byte_47(byte_6[2])}\n'
              f'Модем PLC2 : {Execute.byte_47(byte_6[3])}\n'
              f'Флаг наличия профиля 2 : {Execute.byte_47(byte_6[4])}\n'
              f'Флаг наличия пломбы модульного отсека : {Execute.byte_47(byte_6[5])}\n'
              f'Флаг переключения тарифов внешним напряжением : {Execute.byte_47(byte_6[6])}\n'
              f'Реле управ-ния внешн.устр-ми откл. нагрузки : {Execute.byte_47(byte_6[7])}\n'
              f'Постоянная имп. и оптических выходов : {Execute.byte_71(byte_7[0:4])}\n'
              f'Флаг измерения провалов и перенапряжений : {Execute.byte_47(byte_7[4])}\n'
              f'Флаг тарифного учета R1-R4 : {Execute.byte_47(byte_7[5])}\n'
              f'Флаг КПК : {Execute.byte_47(byte_7[6])}\n'
              f'Флаг массива профилей : {Execute.byte_47(byte_7[7])}{c.END}\n'

              )
        self.clear()
        return

    def descriptor(self):
        self.hex_out.append(self.exchange('GET_DESCRIPTOR', 5)[2])
        for el in self.hex_out:
            self.var = el.split(' ')
        desc = f'{self.var[2]}{self.var[1]}'
        print(f'{c.GREEN}Дескриптор ПУ - {desc}{c.END}')
        print(f'{c.GREEN}Микроконтроллер - {self.hardware[desc]}{c.END}\n')
        self.clear()
        return

    def get_vectors(self):
        param = ['F1 C0 10', 'F1 D0 10', 'F1 E0 10', 'F1 F0 10']
        for i in range(len(param)):
            self.hex_out.append(self.exchange('GET_VECTORS', 19, param=param[i])[2])
        print(f'{c.GREEN}Вектора прерываний:{c.END}')
        for el in self.hex_out:
            print(f'{c.GREEN}{el[3:50]}{c.END}')
        print('\n')
        self.clear()
        return
