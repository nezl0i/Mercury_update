from ex_protocol import ExchangeProtocol

if __name__ == "__main__":

    protocol = ExchangeProtocol()

    # ==================== DEFAULT =========================
    # protocol.list_port()  # Список доступных портов
    # protocol.read_identifier()  # Чтение ID прибора учета
    # protocol.read_serial()  # Чтение серийного номера ПУ
    # protocol.execution()  # Вариант исполнения
    # =====================================================

    # protocol.descriptor()  # Дескриптор
    # protocol.get_vectors()  # Вектора прерываний
    # protocol.update_firmware()  # Обновление ПО
    # protocol.get_password()  # Чтение паролей
    # protocol.set_spodes()  # Изменение протокола (СПОДЭС, Меркурий)
    # protocol.get_event()  # Чтение журналов событий
    # protocol.set_passwd()    # Запись нового пароля
    # protocol.write_memory()  # Запись в память
    # protocol.write_meters()  # Запись показаний
    # protocol.write_shunt()  # Запись шунта
    # protocol.read_shunt()  # Чтение шунта
    # protocol.write_serial_and_date()  # Запись серийного номера и даты выпуска
    # protocol.clear_meters()  # Сброс регистров накопленной энергии
    # protocol.time_set()  # Установка времени
