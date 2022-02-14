import os
import re
import sys
import json
import socket
import execute
import config as cfg
from meters import meters
from sys import platform
import event as log
from command import Command
from datetime import datetime
from modbus_crc16 import crc16
from uart import UartSerialPort

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
            check, buffer = func(*args, **kwargs)
            if check:
                if cfg.DEBUG:
                    print(f'[{current_time}] :{c.FAIL} <<', ' '.join(buffer), c.END)
                return check, buffer
            else:
                if buffer and len(buffer) != 0:
                    if cfg.DEBUG:
                        print(f'[{current_time}] :{c.FAIL} <<', ' '.join(buffer), c.END)
        print(f'{c.WARNING}Нет ответа от устройства.{c.END}')
        sys.exit()

    return wrapper_repeat


class ExchangeProtocol(UartSerialPort):

    def __init__(self):
        super().__init__()

        self.mode = cfg.CONNECT_MODE
        self.file = cfg.FIRMWARE_FILE
        self.phone = cfg.CSD_PHONE
        self.__id = format(cfg.DEVICE_ID, '02X')
        self.__access = format(cfg.DEVICE_LEVEL, '02X')
        self.__device = ''
        self.__version = None
        self.__imp = '1000'

        self.pass_mode = cfg.DEVICE_PASSWORD_MODE

        if self.pass_mode == 'hex':
            self.__password = ' '.join((format(int(i), '02X')) for i in cfg.DEVICE_PASSWORD)
        elif self.pass_mode == 'ascii':
            self.__password = ' '.join((format(ord(i), '02X')) for i in cfg.DEVICE_PASSWORD)
        else:
            print('No pass_mode.')
            sys.exit()

        self.param = ''
        self.call_flag = False
        self.s = None

        self.TCP_HOST = cfg.TCP_HOST
        self.TCP_PORT = cfg.TCP_PORT
        self.TCP_TIMEOUT = cfg.TCP_TIMEOUT

        self._init_command()
        self.init()

    @property
    def passwd(self):
        if len(self.__password.split(' ')) != 6:
            print(f'{c.WARNING}Пароль не должен превышать 6 знаков.{c.END}')
            sys.exit()
            # self.__password = self.__password[:17]
        return self.__password

    @passwd.setter
    def passwd(self, var):
        self.__password = var

    @property
    def id(self):
        if int(self.__id, 16) > 254:
            print(f'{c.WARNING}Введен неверный ID прибора учета.{c.END}')
            sys.exit()
        return self.__id

    @id.setter
    def id(self, var):
        self.__id = var

    @property
    def imp(self):
        return self.__imp

    @imp.setter
    def imp(self, var):
        self.__imp = var

    @property
    def device(self):
        return self.__device

    @device.setter
    def device(self, var):
        self.__device = var

    @property
    def access(self):
        return self.__access

    @access.setter
    def access(self, var):
        self.__access = var

    @property
    def version(self):
        return self.__version

    @version.setter
    def version(self, var):
        self.__version = var

    def init(self):
        if self.mode == 1:
            self.csd_connect()
        if self.mode == 2:
            self.socket_connect()

        self.test_channel()
        self.open_session()
        self.read_identifier()
        self.read_serial()
        self.execution()

    def _init_command(self):

        self.combine = Command(self.id, self.access, self.passwd, self.phone)

        self.CALL = self.combine.CALL
        self.HARDWARE = self.combine.HARDWARE
        self.COMMAND = self.combine.COMMAND

    def checkout(self, text, out):
        try:
            print(f'{c.GREEN}{text} - {self.combine.get(out[1])}{c.END}\n')
        except KeyError:
            print(f'{c.GREEN}{text} - Ошибка{c.END}\n')

    def csd_connect(self):
        print(self.CSD_send(self.CALL['AT']))
        print(self.CSD_send(self.CALL['CBST']))
        self.set_time(cfg.CSD_TIMEOUT)
        for _ in range(3):
            calling = self.CSD_send(self.CALL['CALL'])
            print(calling)
            if calling == 'Connect OK (9600)\n':
                self.call_flag = True
                break
        if self.call_flag:
            return
        else:
            sys.exit()

    def socket_connect(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('Socket successfully created')
        except socket.error as e:
            print(f'Socket creation failed with error as {e}')

        try:
            self.s.settimeout(self.TCP_TIMEOUT)
            print(f'Connection with {self.TCP_HOST}:{self.TCP_PORT} ...')
            self.s.connect((self.TCP_HOST, self.TCP_PORT))
            print(f'Connection OK.')
        except socket.error as err:
            print(err)
            sys.exit()
        return

    @repeat
    def exchange(self, command_name, count, param=''):
        current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
        buffer = None
        if param:
            self.COMMAND[command_name].pop()
            self.COMMAND[command_name].append(param)
        data = ' '.join(self.COMMAND[command_name])
        transfer = bytearray.fromhex(data + ' ' + crc16(bytearray.fromhex(data)))
        print_line = ' '.join(map(lambda x: format(x, '02x'), transfer))

        if cfg.DEBUG:
            print(f'[{current_time}] :{c.BLUE} >>', print_line, c.END)

        if self.mode != 2:
            self.sp.write(transfer)
            buffer = self.sp.read(count)
        else:
            try:
                self.s.sendall(transfer)
                buffer = self.s.recv(count)
            except socket.error:
                pass

        while buffer:
            if len(buffer) == count:
                return True, buffer.hex(' ', -1).split()
            return False, buffer.hex(' ', -1).split()
        return False, buffer

    def test_channel(self):
        """Тест канала связи """
        out = self.exchange('TEST', 4)[1]
        self.checkout('Тест канала связи', out)
        return

    def open_session(self):
        """Авторизация с устройством """
        out = self.exchange('OPEN_SESSION', 4)[1]
        self.checkout('Открытие канала связи', out)
        return

    def close_session(self):
        """Закрытие канала связи """
        out = self.exchange('CLOSE_SESSION', 4)[1]
        self.checkout('Закрытие канала связи', out)
        return

    def read_identifier(self):
        """Чтение идентификатора прибора (id) """
        out = self.exchange('GET_IDENTIFIER', 5)[1]
        id_result = int(out[2], 16)
        self.id = out[2]
        del self.combine
        self._init_command()
        print(f'{c.GREEN}Идентификатор ПУ - {id_result}{c.END}\n')
        return

    def read_serial(self):
        """Чтение серийного номера и даты выпуска """
        out = self.exchange('GET_SERIAL', 10)[1]
        tmp_check_out = list(map(lambda x: str(int(x, 16)).zfill(2), out))
        self.device = ''.join(tmp_check_out[1:5])
        work_data = '.'.join(tmp_check_out[5:8])
        print(f'{c.GREEN}Серийный номер - {self.device}\n'
              f'Дата выпуска - {work_data}{c.END}\n')

    @staticmethod
    def to_bit(item):
        return format(int(item, 16), "08b")

    @staticmethod
    def to_list(item):
        return list(map(lambda x: str(int(x, 16)).zfill(2), item))

    def execution(self):
        """Чтение варианта исполнения """
        var = self.exchange('GET_EXECUTION', 27)[1]
        tmp_serial = self.to_list(var[1:5])
        tmp_data = self.to_list(var[5:8])
        tmp_version = self.to_list(var[8:11])
        tmp_revision = self.to_list(var[19:21])
        self.device = ''.join(tmp_serial)
        data = '.'.join(tmp_data)
        self.version = '.'.join(tmp_version)
        revision = '.'.join(tmp_revision)
        crc_po = f"{''.join(var[17:19]).upper()}"

        byte_1 = self.to_bit(var[11])
        byte_2 = self.to_bit(var[12])
        byte_3 = self.to_bit(var[13])
        byte_4 = self.to_bit(var[14])
        byte_5 = self.to_bit(var[15])
        byte_6 = self.to_bit(var[16])
        byte_7 = self.to_bit(var[21])
        # byte_8 = format(int(check_out[22], 16), "08b")
        self.imp = execute.byte_25(byte_2[4:]).split()[0]  # Количество импульсов
        return execute.print_exec(self.device, data, self.version, revision, crc_po, byte_1, byte_2,
                                  byte_3, byte_4, byte_5, byte_6, byte_7)

    def descriptor(self):
        """Чтение дескриптора и типа микроконтроллера """
        out = self.exchange('GET_DESCRIPTOR', 5)[1]
        desc = f'{out[2]}{out[1]}'
        print(f'{c.GREEN}Дескриптор ПУ - {desc}\n'
              f'Микроконтроллер - {self.HARDWARE[desc.upper()]}{c.END}\n')
        return

    def get_vectors(self):
        """Чтение векторов прерываний """
        var = []
        param = ['F1 C0 10', 'F1 D0 10', 'F1 E0 10', 'F1 F0 10']
        for i in range(len(param)):
            var.append(' '.join(self.exchange('GET_VECTORS', 19, param=param[i])[1][1:16]))
        print(f'{c.GREEN}Вектора прерываний:')
        print(*var, c.END, sep='\n')
        return

    def get_password(self):
        """Чтение паролей """
        var = []
        param = ['00 4F 06', '00 48 06']
        for i in range(len(param)):
            var.append(self.exchange('GET_PASSWD', 9, param=param[i])[1][1:7])
        for i, el in enumerate(var, 1):
            passwd = ''.join(map(lambda x: str(int(x, 16)), el))
            if len(passwd) == 6:
                print(f'{c.GREEN}Пароль {i} уровня- {passwd} (HEX){c.END}')
            else:
                passwd = ''.join(map(lambda x: bytearray.fromhex(x).decode(), el))
                print(f"{c.GREEN}Пароль {i} уровня- {''.join(passwd)} (ASCII){c.END}")
        print('\n')
        return

    def update_firmware(self):
        hi_address = None
        lo_address = None
        arg_value = None

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
                send_command = '12 0F 3C 0F FC 10'
                out = self.exchange('UPDATE_FIRMWARE', 4, param=send_command)[1]
                if out[1] == '00':
                    print(f'{c.GREEN}Обновление выполнено успешно!{c.END}')
                else:
                    print(f'{c.FAIL}Не удалось выполнить обновление...{c.END}')
                return
            else:
                send_command = f'{arg_value} {hi_address} {lo_address} {line.rstrip()}'
                self.exchange('UPDATE_FIRMWARE', 4, param=send_command)
                if lo_address == 'FF':
                    hi_address = format(int(hi_address, 16) + 1, "02X")
                    lo_address = '00'
                    arg_value = '00'
                else:
                    lo_address = format(int(lo_address, 16) + 1, "02X")
                    arg_value = '00'

    def set_spodes(self):
        """Переключение протоколов
        """
        interface = {0: "Оптопорт", 1: "Встроенный", 2: "Левый канал", 3: "Правый канал"}
        default_protocol = {0: "Меркурий", 1: "СПОДЭС"}
        channel = int(input('Канал 0 – оптопорт, 1 – встроенный, 2 – левый, 3 – правый: '))
        value = int(input('Протокол 0 – «Меркурий», 1 – «СПОДЭС»: '))
        ch = format(channel, '02X')
        val = format(value, '02X')
        byte_timeout = int(input('межсимвольный таймаут (default 300): '))
        active_time = int(input('Таймаут неактивности (default 120): '))
        lo_byte_timeout = format(byte_timeout, '04X')[:2]
        hi_byte_timeout = format(byte_timeout, '04X')[2:]
        act_time = format(active_time, '02X')

        param = f'{ch} {val} 00 {hi_byte_timeout} {lo_byte_timeout} {act_time}'
        out = self.exchange('SET_SPODES', 4, param=param)[1]
        print(f'{c.GREEN}Интерфейс - "{interface[channel]}"\n'
              f'Протокол - "{default_protocol[value]}"\n'
              f'Межсимвольный таймаут - {byte_timeout}\n'
              f'Таймаут неактивности - {active_time}\n'
              f'Выполнение - {self.combine.get(out[1])}{c.END}\n')
        return

    def get_event(self, number=None, position=None):
        """Чтение журналов событий
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
        # else:
        #     print('Некорректный номер записи')
        #     sys.exit()

        for i in range(len(list_all)):
            key = list_all[i]
            tmp_out.clear()
            count = 9 if list_all[i] in list_0 else 15

            if flag == 1:
                print(f'{c.GREEN}[ {log.event(key)} ]{c.END}')
                for j in range(10):
                    index = format(j, '02X')
                    tmp_out.append(self.exchange('GET_EVENT', count, param=f'{key} {index}')[1])
            elif flag == 2:
                print(f'{c.GREEN}[ {log.event(key)} ]{c.END}')
                tmp_out.append(self.exchange('GET_EVENT', count, param=f'{key} {pos}')[1])
            elif flag == 3:
                print(f'{c.GREEN}[ {log.event(param)} ]{c.END}')
                count = 9 if param in list_0 else 15
                for j in range(10):
                    index = format(j, '02X')
                    tmp_out.append(list(self.exchange('GET_EVENT', count, param=f'{param} {index}')[1]))
                tmp_event.append(tmp_out[:])
                tmp_key.append(param)
                break
            elif flag == 4:
                print(f'{c.GREEN}[ {log.event(param)} ]{c.END}')
                count = 9 if param in list_0 else 15
                tmp_out.append(' '.join(self.exchange('GET_EVENT', count, param=f'{param} {pos}')[1]))
                tmp_event.append(tmp_out[:])
                tmp_key.append(key)
                break
            tmp_event.append(tmp_out[:])
            tmp_key.append(key)

        event_dict = dict(zip(tmp_key, tmp_event))
        return log.print_log(event_dict)

    def clear_event(self, journal=None, number=None):

        path = os.path.join("meters", "clear.json")
        clear_event = json.load(open(path, encoding="utf-8"))

        if journal is not None and number is None:
            for key, value in clear_event[journal].items():
                param = ' '.join(value)
                out = self.exchange('SET_METERS', 4, param=param)[1]
                self.checkout(f'Очистка журнала [{journal}], запись [{key}]', out)
        elif journal is not None and number is not None:
            param = ' '.join(clear_event[journal][number])
            out = self.exchange('SET_METERS', 4, param=param)[1]
            self.checkout(f'Очистка журнала [{journal}], запись [{number}]', out)
        elif journal is None and number is None:
            for key in clear_event.keys():
                for key2, value in clear_event[key].items():
                    param = ' '.join(value)
                    out = self.exchange('SET_METERS', 4, param=param)[1]
                    self.checkout(f'Очистка журнала [{key}], запись [{key2}]', out)
        else:
            print('Не самый лучший вариант. Попробуй другие параметры.')

    def set_passwd(self):
        """Запись паролей для текущего уровня доступа """
        pwd = input('Введите пароль: ')
        pass_mode = input('Кодировка (hex/ascii): ')
        if pass_mode == 'hex':
            tmp_pass = ' '.join((format(int(i), '02X')) for i in pwd)
        elif pass_mode == 'ascii':
            tmp_pass = ' '.join((format(ord(i), '02X')) for i in pwd)
        else:
            print('Bad password mode (use "hex" or "ascii").')
            sys.exit()
        out = self.exchange('SET_PASSWD', 4, param=f'{self.access} {self.passwd} {tmp_pass}')[1]
        self.checkout('Изменение пароля', out)
        return

    def write_memory(self):
        """Прямая запись по физическим адресам памяти
        """
        memory = format(int(input('Номер памяти: ')), '02X')
        offset = input('Адрес (через пробел "00 4f"): ')
        count = format(int(input('Количество байт: ')), '02X')
        data = input('Данные (через пробел): ')
        send_data = f'{memory} {offset} {count} {data}'
        out = self.exchange('SET_DATA', 4, param=send_data)[1]
        self.checkout('Команда записи', out)
        return

    def _param_select(self, param):
        for i in range(len(param)):
            out = self.exchange('SET_METERS', 4, param=param[i])[1]
            self.checkout('Запись показаний', out)
        return

    def write_meters(self):
        path = os.path.join("meters", "meters.json")
        meter = json.load(open(path, encoding='utf8'))
        # print(self.imp)
        if self.imp == '1000':
            k = 2
        elif self.imp == '500':
            k = 1
        else:
            k = 10

        keys = ("A+", "PhaseA", "Year_A+", "Year_old_A+", "January_A+", "February_A+", "March_A+", "April_A+",
                "May_A+", "June_A+", "July_A+", "August_A+", "September_A+", "October_A+", "November_A+",
                "December_A+", "Day_A+", "Day_old_A+")

        if keys[0] in meter:
            param = meters.EnergyReset(k)
            self._param_select(param)
            # param = meters.EnergyResetDouble(k)
            # self._param_select(param)
        if keys[1] in meter:
            param = meters.EnergyPhase(k)
            self._param_select(param)
        if keys[2] in meter:
            param = meters.EnergyYear(k)
            self._param_select(param)
        if keys[3] in meter:
            param = meters.EnergyOldYear(k)
            self._param_select(param)
        if keys[4] in meter:
            param = meters.EnergyJanuary(k)
            self._param_select(param)
        if keys[5] in meter:
            param = meters.EnergyFebruary(k)
            self._param_select(param)
        if keys[6] in meter:
            param = meters.EnergyMarch(k)
            self._param_select(param)
        if keys[7] in meter:
            param = meters.EnergyApril(k)
            self._param_select(param)
        if keys[8] in meter:
            param = meters.EnergyMay(k)
            self._param_select(param)
        if keys[9] in meter:
            param = meters.EnergyJune(k)
            self._param_select(param)
        if keys[10] in meter:
            param = meters.EnergyJuly(k)
            self._param_select(param)
        if keys[11] in meter:
            param = meters.EnergyAugust(k)
            self._param_select(param)
        if keys[12] in meter:
            param = meters.EnergySeptember(k)
            self._param_select(param)
        if keys[13] in meter:
            param = meters.EnergyOctober(k)
            self._param_select(param)
        if keys[14] in meter:
            param = meters.EnergyNovember(k)
            self._param_select(param)
        if keys[15] in meter:
            param = meters.EnergyDecember(k)
            self._param_select(param)
        if keys[16] in meter:
            param = meters.EnergyDay(k)
            self._param_select(param)
        if keys[17] in meter:
            param = meters.EnergyOldDay(k)
            self._param_select(param)

    def read_shunt(self):
        """Чтение параметров программного шунта """
        # _soft  = "2" - Меркурий-230
        # _soft  = "3" - Меркурий-231
        # _soft  = "4" - Меркурий-232
        # _soft  = "7"  - Меркурий-233
        # _soft  = "8" - Меркурий-236
        # _soft  = "9" - Меркурий-234
        # _soft  = "11" - Меркурий-231i

        _soft = int(self.version.split('.')[0], 16)
        # print(_soft)
        if _soft == 9:
            self.param = '18 70 0A'
        elif _soft == 2 or _soft == 8:
            self.param = '10 70 0A'
        elif _soft == 11:
            self.param = '10 00 0A'
        else:
            print('Тип прибора не определен.')
            return

        out = self.exchange('GET_SHUNT', 13, param=self.param)[1]
        shunt_mode = int(out[3], 16)
        event_code = int(out[4], 16)

        if event_code == 1:
            print_event_code = 'отключен'
        else:
            print_event_code = 'не отключен'

        if shunt_mode == 1:
            shunt_value = int(out[1], 16)
            percent = 100 - (100 / shunt_value)
        elif shunt_mode == 2:
            shunt_value = int(out[2], 16) + 1
            percent = 100 / shunt_value
        else:
            shunt_mode = 'не определено'
            shunt_value = 'не определено'
            percent = 0
        print(f'{c.GREEN}Текущий режим - {shunt_mode}{c.END}')
        print(f'{c.GREEN}Значение - {shunt_value}{c.END}')
        print(f'{c.GREEN}Недоучет - {percent} %{c.END}')
        print(f'{c.GREEN}Журнал "Дата и код программирования" - {print_event_code}{c.END}\n')
        return

    def write_shunt(self, code=True):

        percent = int(input('Процент недоучета: '))

        w_code = '01' if code else '00'

        if percent > 50:
            value = format(int(100 / (100 - percent)), "02X")
            self.param = f'{value} 00 01 {w_code} 00 00 00 00 00 00'
        else:
            value = format(int(100 / percent), "02X")
            self.param = f'00 {value} 02 {w_code} 00 00 00 00 00 00'
        out = self.exchange('SET_SHUNT', 4, param=self.param)[1]
        self.checkout('Команда записи шунта', out)
        return

    @staticmethod
    def two_split(tmp_str):
        b = re.findall(r'\d\d', tmp_str)
        return " ".join(map(lambda x: format(int(x), '02X'), b))

    @staticmethod
    def date_split(tmp_str):
        b = tmp_str.split(".")
        return " ".join(map(lambda x: format(int(x), '02X'), b))

    @staticmethod
    def fill(*args):
        return str(args[0]).zfill(2)

    def write_serial_and_date(self):
        """ Запись серийного номера и даты выпуска"""
        serial = input('Серийный номер: ')
        date = input('Дата выпуска (дд.мм.гг): ')
        send_serial = self.two_split(serial)
        send_date = self.date_split(date)
        self.param = f'{send_serial} {send_date} 00'
        out = self.exchange('SET_SERIAL', 4, param=self.param)[1]
        self.checkout('Команда записи серийного номера и даты выпуска', out)
        return

    def clear_meters(self):
        """ Сброс регистров накопленной энергии"""
        out = self.exchange('CLEAR_METERS', 4)[1]
        self.checkout('Сброс регистров энергии', out)
        return

    def time_get(self):
        week_day = {'01': 'Понедельник', '02': 'Вторник', '03': 'Среда',
                    '04': 'Четверг', '05': 'Пятница', '06': 'Суббота', '07': 'Воскресение'}
        device_time = self.exchange('GET_TIME', 11)[1][1:9]  # Разбить на правильное отображение
        print(f'\nВремя прибора: {".".join(list(device_time[4:7]))}'
              f' {":".join(list(device_time[:3])[::-1])}'
              f' {week_day[device_time[3]]}'
              f' {"Зима" if  device_time[7] == "01" else "Лето"}\n')

    def time_set(self):
        self.time_get()

        month = [1, 2, 3, 10, 11, 12]
        dt = datetime.now()
        seconds = self.fill(dt.second)
        minutes = self.fill(dt.minute)
        hours = self.fill(dt.hour)
        weeks = self.fill(dt.weekday()+1)
        days = self.fill(dt.day)
        months = self.fill(dt.month)
        years = str(dt.year)[-2:]
        seasons = self.fill(1 if dt.month in month else 0)
        self.param = f'{seconds} {minutes} {hours} {weeks} {days} {months} {years} {seasons}'
        out = self.exchange('SET_TIME', 4, param=self.param)[1]
        self.checkout('Запись времени', out)
        self.time_get()
        return
