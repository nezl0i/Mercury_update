import sys
import serial
from serial.serialutil import SerialException


class UartSerialPort:
    def __init__(self, port_name, port_timeout):
        try:
            self.sp = serial.Serial(
                port=port_name,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=port_timeout
            )
        except SerialException:
            print('Port not opened or port no available.')
            self.sp = None
            sys.exit()

    def __str__(self):
        return f'Port {self.sp.port} open' if self.sp else 'Port not opened or port no available'

    def write(self, data):
        try:
            return self.sp.write(data)
        except AttributeError:
            return False

    def read(self, count):
        try:
            return self.sp.read(count)
        except AttributeError:
            return False
