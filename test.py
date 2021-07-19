import sys
import argparse
from ex_protocol import ExchangeProtocol
from colors import Colors

c = Colors()
check_out = []


def create_parser():
    argv_parser = argparse.ArgumentParser()
    argv_parser.add_argument('-p', '--port', default='/dev/ttyUSB0')  # СОМ порт
    argv_parser.add_argument('-t', '--timeout', type=float, default=.1)  # Время ожидания ответа
    argv_parser.add_argument('-i', '--number', type=int, default=52)  # Идентификатор счетчика
    argv_parser.add_argument('-s', '--sys_timeout', type=float, default=.1)  # Системный таймаут
    argv_parser.add_argument('-l', '--level', type=int, default=2)  # Уровень доступа (1-USER,2-ADMIN)
    argv_parser.add_argument('-pwd', '--password', type=str, default='222222')  # Пароль пользователя
    argv_parser.add_argument('-f', '--file', default='update/firmware.txt')    # Файл прошивки
    argv_parser.add_argument('-m', '--mode', default=1)     # Режим: 0-"RS-485", 1-"CSD", 2-"TCP/IP"
    argv_parser.add_argument('-ph', '--phone', default='')      # Номер для CSD соединения
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


def get_out(tmp):
    return {
        tmp == "00": "OK",
        tmp == "01": "Недопустимая команда или параметр",
        tmp == "02": "Внутренняя ошибка счетчика",
        tmp == "03": "Недостаточен уровень для удовлетворения запроса",
        tmp == "04": "Внутренние часы счетчика уже корректировались в течение текущих суток",
        tmp == "05": "Не открыт канал связи"
    }[True]


if __name__ == "__main__":

    # =============================================
    #           Тест канала связи
    # =============================================

    for el in protocol.test_channel():
        check_out = el.split(' ')
    print(f'{c.GREEN}Тест канала связи - {get_out(check_out[1])}{c.END}')

    # =============================================
    #           Открытие канала связи
    # =============================================

    for el in protocol.open_session():
        check_out = el.split(' ')
    print(f'{c.GREEN}Открытие канала связи - {get_out(check_out[1])}{c.END}')

    # =============================================
    #           Закрытие канала связи
    # =============================================

    # for el in protocol.close_session():
    #     check_out = el.split(' ')
    # print(f'{c.GREEN}Закрытие канала связи - {get_out(check_out[1])}{c.END}')

    # =============================================
    #           Чтение ID прибора учета
    # =============================================

    for el in protocol.read_identifier():
        check_out = el.split(' ')
    id_result = int(check_out[2], 16)
    print(f'{c.GREEN}Идентификатор ПУ - {id_result}{c.END}')

    # =============================================
    #         Чтение серийного номера ПУ
    #            35310276 10.07.2018
    # =============================================

    for el in protocol.read_serial():
        check_out = el.split(' ')
    tmp_check_out = list(map(lambda x: str(int(x, 16)).zfill(2), check_out))
    serial_result = ''.join(tmp_check_out[1:5])
    work_data = '.'.join(tmp_check_out[5:8])
    print(f'{c.GREEN}Серийный номер - {serial_result}\nДата выпуска - {work_data}{c.END}')

    # =============================================
    #           Вариант исполнения
    # =============================================
    """
    Доделать расшифровку варианта исполения
    """
    print(protocol.execution())

    # =============================================
    #           Дескриптор
    # =============================================

    for el in protocol.descriptor():
        check_out = el.split(' ')
    print(f'{c.GREEN}Дескриптор ПУ - {check_out[2]}{check_out[1]}{c.END}')
    #

    # =============================================
    #           Вектора прерываний
    # =============================================

    tmp_vectors = protocol.get_vectors()
    print(f'{c.GREEN}Вектора прерываний:{c.END}')
    for el in tmp_vectors:
        print(f'{c.GREEN}{el[3:50]}{c.END}')

    # =============================================
    #           Обновление ПО
    # =============================================

    # for el in protocol.update_firmware():
    #     check_out = el.split(' ')
    # if check_out[1] == '00':
    #     print(f'{c.GREEN}Обновление выполнено успешно!{c.END}')
    # else:
    #     print(f'{c.FAIL}Не удалось выполнить обновление...{c.END}')
