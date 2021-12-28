import sys
from ex_protocol import ExchangeProtocol


if sys.platform.startswith('win'):
    from colors import WinColors
    c = WinColors()
else:
    from colors import Colors
    c = Colors()


protocol = ExchangeProtocol()

if __name__ == "__main__":

    # protocol.list_port()  # Список доступных портов
    protocol.read_identifier()  # Чтение ID прибора учета
    protocol.read_serial()  # Чтение серийного номера ПУ
    protocol.execution()  # Вариант исполнения
    protocol.descriptor()  # Дескриптор
    protocol.get_vectors()  # Вектора прерываний
    # protocol.update_firmware()  # Обновление ПО
    # protocol.get_password()  # Чтение паролей
    # protocol.set_spodes(0, 0, 300, 120)  # Изменение протокола (СПОДЭС, Меркурий)
    # protocol.get_event(number=None, position=None)  # Чтение журналов событий
    # protocol.set_passwd('222222', 'hex')    # Запись нового пароля
    # protocol.write_memory(2, '00 4F', 6, '01 01 01 01 01 01')
