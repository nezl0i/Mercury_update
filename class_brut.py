import sys
import os
import socket
from sys import platform
from time import sleep
from uart import UartSerialPort
from modbus_crc16 import crc16
from datetime import datetime
import config as cfg

try:
    from progress.bar import IncrementalBar
except ImportError:
    if platform.startswith('win'):
        os.system('py -m pip install progress')
    else:
        os.system('python3 -m pip install progress')
from progress.bar import IncrementalBar


class Exchange(UartSerialPort):
    def __init__(self):
        super().__init__()

        self.PHONE = cfg.CSD_PHONE
        self.CSD_TIMEOUT = cfg.CSD_TIMEOUT
        self.CALL = {'AT': 'AT\r', 'CBST': 'AT+CBST=71,0,1\r', 'CALL': f'ATD{self.PHONE}\r'}
        self.id = format(cfg.DEVICE_ID, '02X')

        self.timeout = cfg.UART_PORT_TIMEOUT
        self.start_passwd = cfg.START_PASSWORD
        self.stop_passwd = cfg.STOP_PASSWORD
        self.pass_mode = cfg.DEVICE_PASSWORD_MODE

        self.mode = cfg.CONNECT_MODE

        self.s = None
        self.TCP_HOST = cfg.TCP_HOST
        self.TCP_PORT = cfg.TCP_PORT
        self.TCP_TIMEOUT = cfg.TCP_TIMEOUT
        self._flag = False

        self.bar = IncrementalBar('Выполнение', max=self.stop_passwd - self.start_passwd)
        self.init()

    @property
    def flag(self):
        return self._flag

    @flag.setter
    def flag(self, var):
        self._flag = var

    def __test(self, pk):
        test = f'{pk} 00 '
        transfer = bytearray.fromhex(test + crc16(bytearray.fromhex(test)))
        sys.stdout.write(f'Тест канала связи ...\r')

        buffer = self.as_buffer(transfer)

        while buffer:
            sys.stdout.write(f'Тест канала связи - ОК.\n')
            print('-'*28)
            sleep(1)
            return True
        return False

    def _check_test(self):
        if self.__test(self.id):
            self.flag = True
        else:
            print('Нет ответа от устройства')

    def as_buffer(self, packet):
        buffer = None
        if self.mode != 2:
            self.sp.write(packet)
            buffer = self.sp.read(4)
        else:
            try:
                self.s.sendall(packet)
                buffer = self.s.recv(4)
            except socket.error:
                pass
        return buffer

    def csd_connect(self):
        self.flag = False
        self.set_time(.5)
        print(self.CSD_send(self.CALL['AT']))
        print(self.CSD_send(self.CALL['CBST']))
        self.set_time(self.CSD_TIMEOUT)
        for _ in range(3):
            calling = self.CSD_send(self.CALL['CALL'])
            print(calling)
            if calling == 'Connect OK (9600)\n':
                self.set_time(self.timeout)
                self._check_test()
        # return self.flag

    def socket_connect(self):
        self.flag = False
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('Socket successfully created')
            self.s.connect((self.TCP_HOST, self.TCP_PORT))
            self.s.settimeout(self.TCP_TIMEOUT)
            print(f'Connected to {self.TCP_HOST}:{self.TCP_PORT}\n')
            self._check_test()
        except socket.error as err:
            print(err)
            # return self.flag

    def init(self):
        if self.mode == 0:
            self._check_test()

        if self.mode == 1:
            self.csd_connect()

        if self.mode == 2:
            self.socket_connect()

    def reading(self, pk, input_pass=None):

        test = f'{pk} 01 02 {input_pass} '
        transfer = bytearray.fromhex(test + crc16(bytearray.fromhex(test)))
        sys.stdout.write(f' [Пробуем пароль - {input_pass}]\r')
        self.bar.next()

        buffer = self.as_buffer(transfer)

        while buffer:
            print(f"Ответ от устройства >> {buffer.hex(' ', -1)}\n")
            print(f'Пароль найден - {input_pass}')
            self.bar.finish()

            app_path = os.getcwd()
            path = os.path.join(app_path, 'log/password/')

            if not os.path.exists(path):
                os.makedirs(path)
                # print("Успешно создана директория %s" % path)

            dt = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f'passwd_{dt}.txt'

            with open(f'{path}{filename}', "w+") as f:
                f.write('123456')

            return True
        return False

    def brut_password(self):
        if self.flag:

            while self.start_passwd <= self.stop_passwd:

                if self.pass_mode == 'hex':
                    hex_password = ' '.join((format(int(i), '02X')) for i in str(self.start_passwd).zfill(6))
                elif self.pass_mode == 'ascii':
                    hex_password = ' '.join((format(ord(i), '02X')) for i in str(self.start_passwd).zfill(6))
                else:
                    print('Pass_mode is None..')
                    return

                if self.reading(self.id, hex_password):
                    return
                if str(self.start_passwd)[3:] == '000':
                    print(' [Пауза 3 сек...]')
                    sleep(3)
                    self._check_test()
                # start_passwd += 2 if str(start_passwd)[5] == '9' else 1
                self.start_passwd += 1
