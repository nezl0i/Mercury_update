import sys
import json
from meters import meters
from sys import platform
import socket
import execute
from event import event_log as log
import config as cfg
from command.command import Command
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
            check, get_hex, buffer = func(*args, **kwargs)
            if cfg.DEBUG:
                print(f'[{current_time}] :{c.BLUE} >>', get_hex, c.END)
            if check:
                if cfg.DEBUG:
                    print(f'[{current_time}] :{c.FAIL} <<', buffer, c.END)
                return check, get_hex, buffer
            else:
                if len(buffer) != 0:
                    if cfg.DEBUG:
                        print(f'[{current_time}] :{c.FAIL} <<', buffer, c.END)
            # sleep(1)
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
        self._access = format(cfg.DEVICE_LEVEL, '02X')

        self.TCP_HOST = cfg.TCP_HOST
        self.TCP_PORT = cfg.TCP_PORT
        self.TCP_TIMEOUT = cfg.TCP_TIMEOUT

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
        self.device = ''
        self.s = None

        self.imp = '1000'

        self.combine = Command(self.id, self._access, self.passwd, self.phone, self.param)

        self.CALL = self.combine.CALL
        self.HARDWARE = self.combine.HARDWARE
        self.COMMAND = self.combine.COMMAND

        self.init()

    def checkout(self, text, out):
        print(f'{c.GREEN}{text} - {self.combine.get(out[1])}{c.END}\n')

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
            self.s.connect((self.TCP_HOST, self.TCP_PORT))
            self.s.settimeout(self.TCP_TIMEOUT)
            print(f'Connected to {self.TCP_HOST}:{self.TCP_PORT}\n')
        except socket.error as err:
            print(err)
            sys.exit()
        return

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

    def set_id(self, var):
        self.__id = var

    def set_imp(self, var):
        self.imp = var
        return self.imp

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
        buffer = None
        if param:
            self.COMMAND[command_name].pop()
            self.COMMAND[command_name].append(param)
        data = ' '.join(self.COMMAND[command_name])
        transfer = bytearray.fromhex(data + ' ' + crc16(bytearray.fromhex(data)))
        # print_line = ' '.join(format(x, '02x') for x in transfer)
        print_line = ' '.join(map(lambda x: format(x, '02x'), transfer))

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
                return True, print_line, buffer.hex(' ', -1)
            return False, print_line, buffer.hex(' ', -1)
        return False, print_line, buffer

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
                out = self.exchange('UPDATE_FIRMWARE', 4, param=send_command)[2].split(' ')
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

    def test_channel(self):
        """Тест канала связи """
        out = self.exchange('TEST', 4)[2].split()
        self.checkout('Тест канала связи', out)
        return

    def open_session(self):
        """Авторизация с устройством """
        out = self.exchange('OPEN_SESSION', 4)[2].split()
        self.checkout('Открытие канала связи', out)
        return

    def close_session(self):
        """Закрытие канала связи """
        out = self.exchange('CLOSE_SESSION', 4)[2].split()
        self.checkout('Закрытие канала связи', out)
        return

    def read_identifier(self):
        """Чтение идентификатора прибора (id) """
        out = self.exchange('GET_IDENTIFIER', 5)[2].split()
        id_result = int(out[2], 16)
        print(f'{c.GREEN}Идентификатор ПУ - {id_result}{c.END}\n')
        return

    def read_serial(self):
        """Чтение серийного номера и даты выпуска """
        out = self.exchange('GET_SERIAL', 10)[2].split()
        tmp_check_out = list(map(lambda x: str(int(x, 16)).zfill(2), out))
        result = ''.join(tmp_check_out[1:5])
        self.set_device(result)
        work_data = '.'.join(tmp_check_out[5:8])
        print(f'{c.GREEN}Серийный номер - {self.device}\n'
              f'Дата выпуска - {work_data}{c.END}\n')
        return

    def execution(self):
        """Чтение варианта исполнения """
        var = self.exchange('GET_EXECUTION', 27)[2].split()
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
        self.set_imp(execute.byte_25(byte_2[4:]).split()[0])  # Количество импульсов
        return execute.print_exec(self.device, data, version, revision, crc_po, byte_1, byte_2,
                                  byte_3, byte_4, byte_5, byte_6, byte_7)

    def descriptor(self):
        """Чтение дескриптора и типа микроконтроллера """
        out = self.exchange('GET_DESCRIPTOR', 5)[2].split()
        desc = f'{out[2]}{out[1]}'
        print(f'{c.GREEN}Дескриптор ПУ - {desc}\n'
              f'Микроконтроллер - {self.HARDWARE[desc]}{c.END}\n')
        return

    def get_vectors(self):
        """Чтение векторов прерываний """
        var = []
        param = ['F1 C0 10', 'F1 D0 10', 'F1 E0 10', 'F1 F0 10']
        for i in range(len(param)):
            var.append(' '.join(self.exchange('GET_VECTORS', 19, param=param[i])[2].split()[1:16]))
        print(f'{c.GREEN}Вектора прерываний:')
        print(*var, c.END, sep='\n')
        return

    def get_password(self):
        """Чтение паролей """
        var = []
        param = ['00 4F 06', '00 48 06']
        for i in range(len(param)):
            var.append(self.exchange('GET_PASSWD', 9, param=param[i])[2].split()[1:7])
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
        """Переключение протоколов
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
        out = self.exchange('SET_SPODES', 4, param=param)[2].split()
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

    def set_passwd(self, pwd, pass_mode):
        """Запись паролей для текущего уровня доступа
        :param pwd: Пароль
        :param pass_mode: Кодировка пароля
        :return:
        """
        if pass_mode == 'hex':
            tmp_pass = ' '.join((format(int(i), '02X')) for i in pwd)
        elif pass_mode == 'ascii':
            tmp_pass = ' '.join((format(ord(i), '02X')) for i in pwd)
        else:
            print('Bad password mode (use "hex" or "ascii").')
            sys.exit()
        out = self.exchange('SET_PASSWD', 4, param=f'{self.level} {self.passwd} {tmp_pass}')[2].split()
        self.checkout('Изменение пароля', out)
        return

    def write_memory(self, memory, offset, length, data):
        """Прямая запись по физическим адресам памяти
        :param memory: Номер памяти
        :param offset: Адрес
        :param length: Количество байт
        :param data: Данные
        :return:
        """
        mem = format(memory, '02X')
        count = format(length, '02X')
        send_data = f'{mem} {offset} {count} {data}'
        out = self.exchange('SET_DATA', 4, param=send_data)[2].split()
        self.checkout('Команда записи', out)
        return

    def _param_select(self, param):
        for i in range(len(param)):
            out = self.exchange('SET_METERS', 4, param=param[i])[2].split()
            self.checkout('Запись показаний', out)
        return

    def write_meters(self):
        path = r'meters\meters.json'
        meter = json.load(open(path, encoding='utf8'))
        if self.imp == '1000':
            mode = 'sub'
            k = 2
        elif self.imp == '500':
            mode = 'sub'
            k = 1
        else:
            mode = 'sub'
            k = 10

        keys = ["A+", "PhaseA", "Year_A+", "Year_old_A+", "January_A+", "February_A+", "March_A+", "April_A+",
                "May_A+", "June_A+", "July_A+", "August_A+", "September_A+", "October_A+", "November_A+",
                "December_A+", "Day_A+", "Day_old_A+"]

        for key in keys:
            if key in meter:
                param = meters.EnergyReset(k, mode)
                self._param_select(param)
