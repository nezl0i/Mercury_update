import os
import sys
from ex_protocol import ExchangeProtocol
from class_brut import Exchange

if sys.platform.startswith('win'):
    from colors import WinColors
    c = WinColors()
else:
    from colors import Colors
    c = Colors()

protocol = None
findpass = None


def clear():
    if sys.platform.startswith('win'):
        os.system('cls')
    else:
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


def _menu():
    fmt = '{:30}{}'
    center = '{:>45}'

    logo()

    print(fmt.format('[1] Установить время', '[10] Чтение шунта'))
    print(fmt.format('[2] Сброс регистров энергии', '[11] Запись шунта'))
    print(fmt.format('[3] Прочитать дескриптор', '[12] Запись показаний'))
    print(fmt.format('[4] Вектора прерываний', '[13] Обновление ПО'))
    print(fmt.format('[5] Прочитать пароли', '[14] Записать серийный номер'))
    print(fmt.format('[6] Сменить пароль', '[15] Очистить журнал'))
    print(fmt.format('[7] Сменить протокол', '[16] Брут паролей'))
    print(fmt.format('[8] Журналы событий', ''))
    print(fmt.format('[9] Запись в память', ''))
    print()
    print(center.format(f'[0]{c.FAIL} Выход{c.END}'))
    print()


def _event_menu():
    fmt = '{:60}{}'
    center = '{:>65}'

    logo()

    print(fmt.format('[1] Время включения/выключения прибора', '[14] Время превышения лимита энергии по тарифу 4'))
    print(fmt.format('[2] Время коррекции часов прибора',
                     '[15] Время коррекции параметров контроля за превышением лимита мощности'))
    print(fmt.format('[3] Время включения/выключения фазы 1',
                     '[16] Время коррекции параметров контроля за превышением лимита энергии'))
    print(
        fmt.format('[4] Время включения/выключения фазы 2', '[17] Время коррекции параметров учета технических потерь'))
    print(fmt.format('[5] Время включения/выключения фазы 3', '[18] Время вскрытия/закрытия прибора '))
    print(fmt.format('[6] Время начала/окончания превышения лимита мощности',
                     '[19] Время и код перепрограммирования прибора'))
    print(fmt.format('[7] Время коррекции тарифного расписания', '[20] Время и код слова состояния прибора'))
    print(fmt.format('[8] Время коррекции расписания праздничных дней',
                     '[21] Время коррекции расписания утренних и вечерних максимумов мощности'))
    print(fmt.format('[9] Время сброса регистров накопленной энергии',
                     '[22] Время сброса массива значений максимумов мощности'))
    print(
        fmt.format('[10] Время инициализации массива средних мощностей', '[23] Время включения/выключения тока фазы 1'))
    print(fmt.format('[11] Время превышения лимита энергии по тарифу 1', '[24] Время включения/выключения тока фазы 2'))
    print(fmt.format('[12] Время превышения лимита энергии по тарифу 2', '[25] Время включения/выключения тока фазы 3'))
    print(fmt.format('[13] Время превышения лимита энергии по тарифу 3',
                     '[26] Время начала/окончания магнитного воздействия'))
    print(fmt.format('', '[27] Все'))
    print()
    print(center.format(f'[0]{c.FAIL} Назад{c.END}'))
    print()


def main_menu():

    _menu()

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
    if tmp == 0:
        sys.exit()
    elif tmp == 8:
        return events
    elif tmp == 15:
        return clear_events
    elif tmp == 16:
        return brut
    else:
        if not isinstance(protocol, ExchangeProtocol):
            protocol = ExchangeProtocol()

        return {
            tmp == 1: protocol.time_set,
            tmp == 2: protocol.clear_meters,
            tmp == 3: protocol.descriptor,
            tmp == 4: protocol.get_vectors,
            tmp == 5: protocol.get_password,
            tmp == 6: protocol.set_passwd,
            tmp == 7: protocol.set_spodes,
            # tmp == 8: events,
            tmp == 9: protocol.write_memory,
            tmp == 10: protocol.read_shunt,
            tmp == 11: protocol.write_shunt,
            tmp == 12: protocol.write_meters,
            tmp == 13: protocol.update_firmware,
            tmp == 14: protocol.write_serial_and_date
        }[True]


def events():
    global protocol

    _event_menu()

    try:
        ans = int(input(f'{c.GREEN}Номер журнала: ~# {c.END}'))
        if ans == 27:
            ans = None
        if ans == 0:
            main_menu()

        if not isinstance(protocol, ExchangeProtocol):
            protocol = ExchangeProtocol()

        protocol.get_event(number=ans, position=None),
        ready = input('Продолжить? (y/n): ')
        to_answer = ('y', 'yes', 'д', 'да')
        if ready in to_answer:
            events()
        else:
            sys.exit()
    except ValueError:
        pass
    except KeyboardInterrupt:
        pass
    except KeyError:
        main_menu()


def clear_events():
    global protocol

    _event_menu()

    try:
        ans = input(f'{c.GREEN}Номер журнала: ~# {c.END}')
        if ans == '27':
            ans = None
        if ans == '0':
            main_menu()

        pos = input(f'{c.GREEN}Номер записи (1-10, 11-Все): ~# {c.END}')
        if pos == '11':
            pos = None

        if not isinstance(protocol, ExchangeProtocol):
            protocol = ExchangeProtocol()
        protocol.clear_event(journal=ans, number=pos),
        ready = input('Продолжить? (y/n): ')
        to_answer = ('y', 'yes', 'д', 'да')
        if ready in to_answer:
            clear_events()
        else:
            sys.exit()
    except ValueError:
        pass
    except KeyboardInterrupt:
        pass
    except KeyError:
        main_menu()


def brut():
    global findpass

    if not isinstance(findpass, Exchange):
        findpass = Exchange()
    else:
        del findpass
        findpass = Exchange()

    findpass.brut_password()
    ready = input('Продолжить? (y/n): ')
    to_answer = ('y', 'yes', 'д', 'да')
    if ready in to_answer:
        main_menu()
    else:
        sys.exit()


if __name__ == '__main__':

    main_menu()


