import sys
import serial
from serial.serialutil import SerialException
import serial.tools.list_ports
import config as cfg

# sudo nano /etc/udev/rules.d/50-myusb.rules
# KERNEL=="ttyUSB[0-9]*",MODE="0666"
# KERNEL=="ttyACM[0-9]*",MODE="0666"


class UartSerialPort:
    def __init__(self):
        if cfg.CONNECT_MODE == 2:
            return
        else:
            self.list_port()
            try:
                self.sp = serial.Serial(
                    port=cfg.UART_PORT,
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=cfg.UART_PORT_TIMEOUT
                )
            except SerialException:
                print(f'Port {cfg.UART_PORT} not opened or port no available.')
                self.sp = None
                sys.exit()

            self.data = ''

    def __str__(self):
        return f'Port {self.sp.port} open' if self.sp else 'Port not opened or port no available'

    # def write(self, data):
    #     try:
    #         return self.sp.write(data)
    #     except AttributeError:
    #         return False
    #
    # def read(self, count):
    #     try:
    #         return self.sp.read(count)
    #     except AttributeError:
    #         return False

    @staticmethod
    def list_port():
        ports = [port for port in serial.tools.list_ports.comports()]
        print('=' * 28, 'Default ports', '=' * 28)
        for port in ports:
            print(f'{port}')
        print('='*71, '\n')

#   =========== From CSD terminal settings ================

    def CSD_send(self, string):
        send_string = bytearray(string, encoding='ascii')
        self.sp.write(send_string)
        print(f'Send command: {send_string.decode()}')
        self.data = self.CSD_read()
        return self.data

    def CSD_read(self):
        self.data = self.sp.readall()
        if 'OK' in self.data.decode():
            return 'OK'
        elif 'CONNECT' in self.data.decode():
            return 'Connect OK (9600)\n'
        elif 'BUSY' in self.data.decode():
            return 'BUSY\n'
        return 'ERROR\n'

    def set_time(self, val):
        self.sp.timeout = val
        return

    def clear(self):
        self.sp.flushInput()
        self.sp.flushOutput()
