from sys import platform

if platform.startswith('win'):
    from colors import WinColors
    c = WinColors()
else:
    from colors import Colors
    c = Colors()


def event(tmp):
    return {
        tmp == "00": "Чтение текущего времени",  # 8 + 3
        tmp == "01": "Время включения/выключения прибора",  # 12 + 3
        tmp == "02": "Время коррекции часов прибора",  # 12 + 3
        tmp == "03": "Время включения/выключения фазы 1",  # 12 + 3
        tmp == "04": "Время включения/выключения фазы 2",  # 12 + 3
        tmp == "05": "Время включения/выключения фазы 3",  # 12 + 3
        tmp == "06": "Время начала/окончания превышения лимита мощности",  # 12 + 3
        tmp == "07": "Время коррекции тарифного расписания",  # 6 + 3
        tmp == "08": "Время коррекции расписания праздничных дней",  # 6 + 3
        tmp == "09": "Время сброса регистров накопленной энергии",  # 6 + 3
        tmp == "0A": "Время инициализации массива средних мощностей",  # 6 + 3
        tmp == "0B": "Время превышения лимита энергии по тарифу 1",  # 6 + 3
        tmp == "0C": "Время превышения лимита энергии по тарифу 2",  # 6 + 3
        tmp == "0D": "Время превышения лимита энергии по тарифу 3",  # 6 + 3
        tmp == "0E": "Время превышения лимита энергии по тарифу 4",  # 6 + 3
        tmp == "0F": "Время коррекции параметров контроля за превышением лимита мощности",  # 6 + 3
        tmp == "10": "Время коррекции параметров контроля за превышением лимита энергии",  # 6 + 3
        tmp == "11": "Время коррекции параметров учета технических потерь",  # 6 + 3
        tmp == "12": "Время вскрытия/закрытия прибора",  # 12 + 3
        tmp == "13": "Время и код перепрограммирования прибора",  # 12 + 3
        tmp == "14": "Время и код слова состояния прибора",  # 12 + 3
        tmp == "15": "Время коррекции расписания утренних и вечерних максимумов мощности",  # 6 + 3
        tmp == "16": "Время сброса массива значений максимумов мощности",  # 6 + 3
        tmp == "17": "Время включения/выключения тока фазы 1",  # 12 + 3
        tmp == "18": "Время включения/выключения тока фазы 2",  # 12 + 3
        tmp == "19": "Время включения/выключения тока фазы 3",  # 12 + 3
        tmp == "1A": "Время начала/окончания магнитного воздействия"  # 12 + 3
    }[True]


def code(tmp):
    return {
        tmp == "": "Неизвестная операция",
        tmp == "00": "Инициализация основного массива средних мощностей (срезов)",
        tmp == "01": "Запись параметров индикации счетчика (по индицируемым тарифам)",
        tmp == "02": "Запись параметров индикации счетчика (по периодам индикации)",
        tmp == "03": "Запись параметров индикации счетчика",
        tmp == "04": "Вкл./выкл. режима «Тест 0,5 Гц»",
        tmp == "05": "Запись нового сетевого адреса счетчика",
        tmp == "06": "Инициализация дополнительного массива средних мощностей (срезов)",
        tmp == "07": "Запись байта программируемых функций",
        tmp == "08": "Фиксация данных 2",
        tmp == "09": "Запись фильтра флагов событий при инициативном выходе",
        tmp == "0A": "Неизвестная операция (Выполнена команда '03 0A')",
        tmp == "0B": "Неизвестная операция (Выполнена команда '03 0B')",
        tmp == "0C": "Установка времени",
        tmp == "0D": "Коррекция времени в пределах ±4 мин один раз в сутки",
        tmp == "0E": "Неизвестная операция (Выполнена команда '03 0E')",
        tmp == "0F": "Неизвестная операция (Выполнена команда '03 0F')",
        tmp == "10": "Запрет записи параметров по PLC1",
        tmp == "11": "Запись параметров PLC1",
        tmp == "12": "Запись параметров протокола",
        tmp == "13": "Запись параметров правого канала",
        tmp == "14": "Изменить параметры связи дополнительного интерфейса",
        tmp == "15": "Изменить параметры связи основного интерфейса 5",
        tmp == "16": "Перезапустить счетчик",
        tmp == "17": "Неизвестная операция (Выполнена команда '03 17')",
        tmp == "18": "Разрешить/запретить автоматический переход на зимнее/летнее время",
        tmp == "19": "Значения времени перехода для летнего и зимнего времени",
        tmp == "1A": "Запись серийного номера блока индикации (БИ) в память прибора учета (ПУ)",
        tmp == "1B": "Записать коэффициенты трансформации Кн и Кт",
        tmp == "1C": "Запись значения расчетного дня",
        tmp == "1D": "Записать тарифное расписание",
        tmp == "1E": "Записать расписание праздничных дней",
        tmp == "1F": "Изменить пароль",
        tmp == "20": "Неизвестная операция (Выполнена команда '03 20')",
        tmp == "21": "Неизвестная операция (Выполнена команда '03 21')",
        tmp == "22": "Запись местоположения прибора",
        tmp == "23": "Запись расписания утреннего и вечернего максимумов",
        tmp == "24": "Сброс значений массива помесячных максимумов",
        tmp == "25": "Неизвестная операция (Выполнена команда '03 25')",
        tmp == "26": "Установка времени контроля за превышением лимита мощности и параметров автовключения реле",
        tmp == "27": "Изменение постоянной счетчика",
        tmp == "28": "Неизвестная операция (Выполнена команда '03 28')",
        tmp == "29": "Неизвестная операция (Выполнена команда '03 29')",
        tmp == "2A": "Изменение режима тарификатора",
        tmp == "2B": "Неизвестная операция (Выполнена команда '03 2B')",
        tmp == "2C": "Установка лимита активной мощности",
        tmp == "2D": "Включение контроля превышения лимита активной мощности",
        tmp == "2E": "Установка лимита потребленной активной энергии",
        tmp == "2F": "Включение контроля превышения потребленной активной энергии",
        tmp == "30": "Изменение режима импульсного выхода и параметров управления нагрузкой",
        tmp == "31": "Изменение режима управления нагрузкой",
        tmp == "32": "Изменение множителя тайм-аута основного интерфейса",
        tmp == "33": "Изменение режима учета технических потерь",
        tmp == "34": "Установка значений мощностей технических потерь",
        tmp == "35": "Изменение режима светодиодного индикатора и импульсного выхода R+ по виду энергии",
        tmp == "36": "Установка допустимых значений при контроле ПКЭ",
        tmp == "37": "Установка времен усреднения значений напряжения и частоты",
        tmp == "38": "Запись в память №2"
    }[True]


def position_5(tmp):
    return {
        tmp == 0: "00",
        tmp == 1: "01",
        tmp == 2: "02",
        tmp == 3: "03",
        tmp == 4: "04",
        tmp == 5: "05",
        tmp == 6: "06",
        tmp == 7: "07"
    }[True]


def position_6(tmp):
    return {
        tmp == 0: "08",
        tmp == 1: "09",
        tmp == 2: "0A",
        tmp == 3: "0B",
        tmp == 4: "0C",
        tmp == 5: "0D",
        tmp == 6: "0E",
        tmp == 7: "0F"
    }[True]


def position_7(tmp):
    return {
        tmp == 0: "10",
        tmp == 1: "11",
        tmp == 2: "12",
        tmp == 3: "13",
        tmp == 4: "14",
        tmp == 5: "15",
        tmp == 6: "16",
        tmp == 7: "17"
    }[True]


def position_8(tmp):
    return {
        tmp == 0: "18",
        tmp == 1: "19",
        tmp == 2: "1A",
        tmp == 3: "1B",
        tmp == 4: "1C",
        tmp == 5: "1D",
        tmp == 6: "1E",
        tmp == 7: "1F"
    }[True]


def position_9(tmp):
    return {
        tmp == 0: "20",
        tmp == 1: "21",
        tmp == 2: "22",
        tmp == 3: "23",
        tmp == 4: "24",
        tmp == 5: "25",
        tmp == 6: "26",
        tmp == 7: "27"
    }[True]


def position_10(tmp):
    return {
        tmp == 0: "28",
        tmp == 1: "29",
        tmp == 2: "2A",
        tmp == 3: "2B",
        tmp == 4: "2C",
        tmp == 5: "2D",
        tmp == 6: "2E",
        tmp == 7: "2F"
    }[True]


def position_11(tmp):
    return {
        tmp == 0: "30",
        tmp == 1: "31",
        tmp == 2: "32",
        tmp == 3: "33",
        tmp == 4: "34",
        tmp == 5: "35",
        tmp == 6: "36",
        tmp == 7: "37"
    }[True]


def position_12(tmp):
    return {
        tmp == 0: "38",
        tmp == 1: "38",
        tmp == 2: "38",
        tmp == 3: "38",
        tmp == 4: "38",
        tmp == 5: "38",
        tmp == 6: "38",
        tmp == 7: "38"
    }[True]


def word_1(tmp):
    return {
        tmp == 0: "Error-01: Напряжение батареи менее 2.2 В",
        tmp == 1: "Error-02: Нарушено функционирование памяти №2",
        tmp == 2: "Error-03: Нарушено функционирование UART1",
        tmp == 3: "Error-04: Нарушено функционирование ADS",
        tmp == 4: "Error-05: Ошибка обмена с памятью №1",
        tmp == 5: "Error-06: Нарушено функционирование RTC",
        tmp == 6: "Error-07: Нарушено функционирование памяти №3",
        tmp == 7: "Error-08: "
    }[True]


def word_2(tmp):
    return {
        tmp == 0: "Error-09: Ошибка CRC ПО",
        tmp == 1: "Error-10: Ошибка CRC калибровочных коэффициентов во FLASH MSP430",
        tmp == 2: "Error-11: Ошибка CRC регистров накопленной энергии",
        tmp == 3: "Error-12: Ошибка CRC адреса прибора",
        tmp == 4: "Error-13: Ошибка CRC серийного номера",
        tmp == 5: "Error-14: Ошибка CRC пароля",
        tmp == 6: "Error-15: Ошибка CRC варианта исполнения счетчика",
        tmp == 7: "Error-16: Ошибка CRC байта тарификатора"
    }[True]


def word_3(tmp):
    return {
        tmp == 0: "Error-17: Ошибка CRC байта управления нагрузкой",
        tmp == 1: "Error-18: Ошибка CRC лимита мощности",
        tmp == 2: "Error-19: Ошибка CRC лимита энергии",
        tmp == 3: "Error-20: Ошибка CRC байта парметров UART",
        tmp == 4: "Error-21: Ошибка CRC параметров индикации (по тарифам)",
        tmp == 5: "Error-22: Ошибка CRC параметров индикации (по периодам)",
        tmp == 6: "Error-23: Ошибка CRC множителя таймаута",
        tmp == 7: "Error-24: Ошибка CRC байта программируемых флагов"
    }[True]


def word_4(tmp):
    return {
        tmp == 0: "Error-25: Ошибка CRC массива праздничных дней",
        tmp == 1: "Error-26: Ошибка CRC массива тарифного расписания",
        tmp == 2: "Error-27: Ошибка CRC массива таймера",
        tmp == 3: "Error-28: Ошибка CRC массива сезонных переходов",
        tmp == 4: "Error-29: Ошибка CRC массива местоположения прибора",
        tmp == 5: "Error-30: Ошибка CRC массива коэффициентов трансформации",
        tmp == 6: "Error-31: Ошибка CRC регистров накопления по периодам времени",
        tmp == 7: "Error-32: Ошибка CRC параметров среза"
    }[True]


def word_5(tmp):
    return {
        tmp == 0: "Error-33: Ошибка CRC регистров среза",
        tmp == 1: "Error-34: Ошибка CRC указателей журналов событий",
        tmp == 2: "Error-35: Ошибка CRC записи журнала событий",
        tmp == 3: "Error-36: Ошибка CRC регистра учета технических потерь",
        tmp == 4: "Error-37: Ошибка CRC мощностей технических потерь",
        tmp == 5: "Error-38: Ошибка CRC массива регистров накопленной энергии",
        tmp == 6: "Error-39: Ошибка CRC регистров энергии пофазного учета",
        tmp == 7: "Error-40: Флаг наступления широковещательного сообщения"
    }[True]


def word_6(tmp):
    return {
        tmp == 0: "Error-41: Ошибка CRC указателей журнала ПКЭ",
        tmp == 1: "Error-42: Ошибка CRC записи журнала ПКЭ",
        tmp == 2: "Error-43: Ошибка CRC регистров R1-R4",
        tmp == 3: "Error-44: ",
        tmp == 4: "Error-45: ",
        tmp == 5: "Error-46: ",
        tmp == 6: "Error-47: Флаг выполнения процедуры коррекции времени",
        tmp == 7: "Error-48: Напряжение батареи менее 2.65В"
    }[True]


def print_event(arg):
    for el in arg:
        var = el.split(' ')
        print(f'{c.GREEN}{".".join(var[4:7])} ({":".join(reversed(var[1:4]))})  |  '
              f'{".".join(var[10:13])} ({":".join(reversed(var[7:10]))}){c.END}')
    print('\n')


def print_event_2(arg):
    for el in arg:
        var = el.split(' ')
        print(f'{c.GREEN}{".".join(var[4:7])} ({":".join(reversed(var[1:4]))}){c.END}')
    print('\n')


def print_log(arg: dict):
    list_1 = ['01', '03', '04', '05', '17', '18', '19']
    list_2 = ['07', '08', '0F', '10', '11', '15']
    list_3 = ['0B', '0C', '0D', '0E']
    list_4 = ['09', '16']
    print('=' * 50)
    for key, val in arg.items():
        print(f'{c.WARNING}[ {event(key)} ]{c.END}')
        if key in list_1:
            print(f'{c.BLUE}   [ Включение ]          [ Отключение ]')
            print_event(val)
        elif key in list_2:
            print(f'{c.BLUE}[ Время коррекции ]')
            print_event_2(val)
        elif key in list_3:
            print(f'{c.BLUE}[ Время превышения ]')
            print_event_2(val)
        elif key == '02':
            print(f'{c.BLUE} [ До коррекции ]      [ После коррекции ]')
            print_event(val)
        elif key == '06':
            print(f'{c.BLUE}[Начало превышения]   [Окончание превышения]')
            print_event(val)
        elif key in list_4:
            print(f'{c.BLUE}[ Время сброса ]')
            print_event_2(val)
        elif key == '0A':
            print(f'{c.BLUE}[ Время инициализации ]')
            print_event_2(val)
        elif key == '1A':
            print(f'{c.BLUE}[Начало воздействия]   [Окончание воздействия]')
            print_event(val)
        elif key == '12':
            print(f'{c.BLUE}  [Время вскрытия]        [Время закрытия]')
            print_event(val)
        elif key == '13':
            function = [position_5, position_6, position_7,
                        position_8, position_9, position_10,
                        position_11, position_12]
            for el in val:
                byte_array = []
                string = el.split(' ')
                data = '.'.join(string[1:4])
                count = int(string[4])
                print(f'{c.BLUE}-{c.END}' * 50)
                print(f'{c.BLUE}Дата {data} (Количество операций - {count}){c.END}')

                for i in range(5, 13):
                    byte_array.append(format(int(string[i], 16), "08b"))
                for i in range(8):
                    func = function[i]
                    for j, k in enumerate(reversed(byte_array[i])):
                        if k == '1':
                            result = code(func(j))
                            print(f'{c.GREEN}{result}{c.END}')
            print('\n')
        elif key == '14':
            function = [word_1, word_2, word_3,
                        word_4, word_5, word_6]
            for el in val:
                byte_array = []
                string = el.split(' ')
                time = ':'.join(reversed(string[1:4]))
                data = '.'.join(string[4:7])
                print(f'{c.BLUE}-{c.END}' * 50)
                print(f'{c.BLUE}Дата {data} ({time}){c.END}')
                for i in range(7, 13):
                    byte_array.append(format(int(string[i], 16), "08b"))

                byte_array[0], byte_array[4] = byte_array[4], byte_array[0]
                byte_array[2], byte_array[3] = byte_array[3], byte_array[2]
                byte_array[1], byte_array[5] = byte_array[5], byte_array[1]

                for i in range(6):
                    func = function[i]
                    for j, k in enumerate(reversed(byte_array[i])):
                        if k == '1':
                            result = func(j)
                            print(f'{c.GREEN}{result}{c.END}')
            print('\n')
