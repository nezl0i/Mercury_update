import sys
import argparse
from ex_protocol import ExchangeProtocol
from colors import Colors

c = Colors()
check_out = []


def create_parser():
    argv_parser = argparse.ArgumentParser()
    argv_parser.add_argument('-p', '--port', default='/dev/ttyUSB0')  # СОМ порт
    argv_parser.add_argument('-t', '--timeout', type=float, default=5)  # Время ожидания ответа
    argv_parser.add_argument('-i', '--number', type=int, default=39)  # Идентификатор счетчика
    argv_parser.add_argument('-s', '--sys_timeout', type=float, default=.5)  # Системный таймаут
    argv_parser.add_argument('-l', '--level', type=int, default=2)  # Уровень доступа (1-USER,2-ADMIN)
    argv_parser.add_argument('-pwd', '--password', type=str, default='252696')  # Пароль пользователя
    argv_parser.add_argument('-f', '--file', default='update/firmware.txt')  # Файл прошивки
    argv_parser.add_argument('-m', '--mode', default=0)  # Режим: 0-"RS-485", 1-"CSD", 2-"TCP/IP"
    argv_parser.add_argument('-ph', '--phone', default='+79898503741')  # Номер для CSD соединения
    return argv_parser


parser = create_parser().parse_args(sys.argv[1:])

port = parser.port
target_id = parser.number
target_password = parser.password
target_access = parser.level
port_sys_timeout = parser.sys_timeout
port_timeout = parser.timeout
file = parser.file
mode = parser.mode
phone = parser.phone

protocol = ExchangeProtocol(
    port,
    port_sys_timeout,
    identifier=target_id,
    password=target_password,
    access=target_access,
    mode=mode,
    phone=phone,
    file=file
)


if __name__ == "__main__":

    #  Тест канала связи
    protocol.test_channel()

    #   Открытие канала связи
    protocol.open_session()

    #   Закрытие канала связи
    # protocol.close_session()

    #   Чтение ID прибора учета
    # protocol.read_identifier()

    #   Чтение серийного номера ПУ
    protocol.read_serial()

    #   Вариант исполнения
    protocol.execution()

    #  Дескриптор
    # protocol.descriptor()

    #   Вектора прерываний
    # protocol.get_vectors()

    # =============================================
    #           Обновление ПО
    # =============================================
    # protocol.update_firmware()

    #   Чтение паролей
    protocol.get_password()
