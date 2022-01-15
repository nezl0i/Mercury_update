import os
import sys
from ex_protocol import ExchangeProtocol

if sys.platform.startswith('win'):
    from colors import WinColors
    c = WinColors()
else:
    from colors import Colors
    c = Colors()

protocol = None


def clear():
    os.system('clear')
    print()


def error():
    print(f'{c.FAIL}Не верно указан параметр{c.END}\n')


def logo():
    clear()
    print(f'''  
                  /##      /##                                                            
                 | ###    /###                                                            
                 | ####  /####  /######   /######   /###### / ##   /##  /######  /##   /##
                 | ## ##/## ## /##__  ## /##__  ## /##_____/| ##  | ## /##__  ##| ##  | ##
                 | ##  ###| ##| ########| ##  \__/| ##      | ##  | ##| ##  \__/| ##  | ## {c.GREEN}
                 | ##\  # | ##| ##_____/| ##      | ##      | ##  | ##| ##      | ##  | ##
                 | ## \/  | ##|  #######| ##      |  #######|  ######/| ##      |  #######
                 |__/     |__/ \_______/|__/       \_______/ \______/ |__/       \____  ##
                                                                                 /##  | ##
                                                                                 | ######/
                                                                                 \______/ {c.END} \n''')


def main_menu():

    fmt = '{:30}{}'
    center = '{:>45}'

    logo()

    print(fmt.format('[0] Установить время', '[9]  Чтение шунта'))
    print(fmt.format('[1] Сброс регистров энергии', '[10] Запись шунта'))
    print(fmt.format('[2] Прочитать дескриптор', '[11] Запись показаний'))
    print(fmt.format('[3] Вектора прерываний', '[12] Обновление ПО'))
    print(fmt.format('[4] Прочитать пароли', '[13] Записать серийный номер'))
    print(fmt.format('[5] Изменить протокол', ''))
    print(fmt.format('[6] Сменить пароль', ''))
    print(fmt.format('[7] Журналы событий', ''))
    print(fmt.format('[8] Запись в память', ''))
    print()
    print(center.format(f'[100]{c.FAIL} Выход{c.END}'))
    print()

    try:
        ans = int(input(f'{c.GREEN}Enter a choice: ~# {c.END}'))
        choice(ans)()
        ready = input('Продолжить? (y/n): ')
        to_answer = ('y', 'yes', 'д', 'да')
        if ready in to_answer:
            main_menu()
        else:
            sys.exit()
    except ValueError:
        pass
    except KeyboardInterrupt:
        pass
    except KeyError:
        main_menu()


def choice(tmp):
    global protocol
    if tmp == 100:
        sys.exit()
    elif tmp == 7:
        return events
    else:
        if not isinstance(protocol, ExchangeProtocol):
            protocol = ExchangeProtocol()

        return {
            tmp == 0: protocol.time_set,
            tmp == 1: protocol.clear_meters,
            tmp == 2: protocol.descriptor,
            tmp == 3: protocol.get_vectors,
            tmp == 4: protocol.get_password,
            tmp == 5: protocol.set_spodes,
            tmp == 6: protocol.set_passwd,
            # tmp == 7: events,
            tmp == 8: protocol.write_memory,
            tmp == 9: protocol.read_shunt,
            tmp == 10: protocol.write_shunt,
            tmp == 11: protocol.write_meters,
            tmp == 12: protocol.update_firmware,
            tmp == 13: protocol.write_serial_and_date
        }[True]


def events():

    fmt = '{:60}{}'
    center = '{:>65}'

    logo()

    print(fmt.format('[1] Время включения/выключения прибора', '[14] Время превышения лимита энергии по тарифу 4'))
    print(fmt.format('[2] Время коррекции часов прибора', '[15] Время коррекции параметров контроля за превышением лимита мощности'))
    print(fmt.format('[3] Время включения/выключения фазы 1', '[16] Время коррекции параметров контроля за превышением лимита энергии'))
    print(fmt.format('[4] Время включения/выключения фазы 2', '[17] Время коррекции параметров учета технических потерь'))
    print(fmt.format('[5] Время включения/выключения фазы 3', '[18] Время вскрытия/закрытия прибора '))
    print(fmt.format('[6] Время начала/окончания превышения лимита мощности', '[19] Время и код перепрограммирования прибора'))
    print(fmt.format('[7] Время коррекции тарифного расписания', '[20] Время и код слова состояния прибора'))
    print(fmt.format('[8] Время коррекции расписания праздничных дней', '[21] Время коррекции расписания утренних и вечерних максимумов мощности'))
    print(fmt.format('[9] Время сброса регистров накопленной энергии', '[22] Время сброса массива значений максимумов мощности'))
    print(fmt.format('[10] Время инициализации массива средних мощностей', '[23] Время включения/выключения тока фазы 1'))
    print(fmt.format('[11] Время превышения лимита энергии по тарифу 1', '[24] Время включения/выключения тока фазы 2'))
    print(fmt.format('[12] Время превышения лимита энергии по тарифу 2', '[25] Время включения/выключения тока фазы 3'))
    print(fmt.format('[13] Время превышения лимита энергии по тарифу 3', '[26] Время начала/окончания магнитного воздействия'))
    print(fmt.format('', '[27] Все'))
    print()
    print(center.format(f'[100]{c.FAIL} Назад{c.END}'))
    print()
    global protocol
    try:
        ans = int(input(f'{c.GREEN}Номер журнала: ~# {c.END}'))
        if ans == 27:
            ans = None
        if ans == 100:
            main_menu()
        else:
            if not isinstance(protocol, ExchangeProtocol):
                protocol = ExchangeProtocol()
        protocol.get_event(number=ans, position=None),
        ready = input('Продолжить? (y/n): ')
        to_answer = ('y', 'yes', 'д', 'да')
        if ready in to_answer:
            main_menu()
        else:
            sys.exit()
    except ValueError:
        pass
    except KeyboardInterrupt:
        pass
    except KeyError:
        main_menu()


if __name__ == '__main__':

    main_menu()


