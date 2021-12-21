import sys
import argparse
from ex_protocol import ExchangeProtocol

if sys.platform.startswith('win'):
    from colors import WinColors
    c = WinColors()
else:
    from colors import Colors
    c = Colors()


def create_parser():
    argv_parser = argparse.ArgumentParser()
    argv_parser.add_argument('-p', '--port', default='/dev/ttyUSB0')  # СОМ порт
    argv_parser.add_argument('-t', '--timeout', type=float, default=.5)  # Системный таймаут
    argv_parser.add_argument('-i', '--number', type=int, default=40)  # Идентификатор счетчика
    argv_parser.add_argument('-l', '--level', type=int, default=2)  # Уровень доступа (1-USER,2-ADMIN)
    argv_parser.add_argument('-pwd', '--password', type=str, default='222222')  # Пароль пользователя
    argv_parser.add_argument('-f', '--file', default='update/FIRMWARE_2019_(90_C5_B8_82).txt')  # Файл прошивки
    argv_parser.add_argument('-m', '--mode', default=1)  # Режим: 0-"RS-485", 1-"CSD", 2-"TCP/IP"
    argv_parser.add_argument('-ph', '--phone', default='+79886222987')  # Номер для CSD соединения
    argv_parser.add_argument('-pm', '--pass_mode', default='hex')   # Кодировка пароля
    return argv_parser


parser = create_parser().parse_args(sys.argv[1:])

port = parser.port
target_id = parser.number
target_password = parser.password
target_access = parser.level
port_timeout = parser.timeout
file = parser.file
mode = parser.mode
phone = parser.phone
pass_mode = parser.pass_mode

protocol = ExchangeProtocol(
    port,
    port_timeout,
    identifier=target_id,
    password=target_password,
    access=target_access,
    mode=mode,
    phone=phone,
    pass_mode=pass_mode,
    file=file
)

if __name__ == "__main__":

    # protocol.list_port()  # Список доступных портов
    protocol.test_channel()  # Тест канала связи
    protocol.open_session()  # Открытие канала связи
    protocol.read_identifier()  # Чтение ID прибора учета
    protocol.read_serial()  # Чтение серийного номера ПУ
    protocol.execution()  # Вариант исполнения
    protocol.descriptor()  # Дескриптор
    protocol.get_vectors()  # Вектора прерываний
    # protocol.update_firmware()  # Обновление ПО
    # protocol.get_password()  # Чтение паролей
    # protocol.close_session()  # Закрытие канала связи
    # protocol.set_spodes(0, 0, 300, 120)  # Изменение протокола (СПОДЭС, Меркурий)
    # protocol.get_event(number=None, position=None)  # Чтение журналов событий
    # protocol.set_passwd('222222', 'hex')    # Запись нового пароля
    # protocol.write_memory(2, '00 4F', 6, '01 01 01 01 01 01')
