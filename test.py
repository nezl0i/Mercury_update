import sys
import argparse
from ex_protocol import ExchangeProtocol


def create_parser():
    argv_parser = argparse.ArgumentParser()
    argv_parser.add_argument('-p', '--port', default='/dev/ttyUSB0')  # СОМ порт
    argv_parser.add_argument('-t', '--timeout', type=float, default=5)  # Время ожидания ответа
    argv_parser.add_argument('-i', '--number', type=int, default=39)  # Идентификатор счетчика
    argv_parser.add_argument('-s', '--sys_timeout', type=float, default=.2)  # Системный таймаут
    argv_parser.add_argument('-l', '--level', type=int, default=2)  # Уровень доступа (1-USER,2-ADMIN)
    argv_parser.add_argument('-pwd', '--password', type=str, default='252696')  # Пароль пользователя
    argv_parser.add_argument('-f', '--file', default='')
    return argv_parser


parser = create_parser().parse_args(sys.argv[1:])

port = parser.port
target_id = parser.number
target_password = parser.password
target_access = parser.level
port_sys_timeout = parser.sys_timeout
port_timeout = parser.timeout
file = parser.file

uart = ExchangeProtocol(port, port_sys_timeout, identifier=target_id, password=target_password, access=target_access)
# print(parser)
# print(uart.id)
# print(uart.passwd)


# uart.test_channel()
uart.open_session()
# # uart.close_session()
# uart.read_identifier()
# uart.read_serial()
# uart.execution()
# uart.descriptor()
# for el in uart.get_vectors():
#     print(el)
print(uart.update_firmware(file='update/firmware.txt'))

