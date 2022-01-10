import json
import os
import re

path = os.path.join("meters", "meters.json")
meter = json.load(open(path, encoding='utf8'))


def _reverse(lst):
    for el in lst:
        el[0], el[1], el[2], el[3] = el[1], el[0], el[3], el[2]
    n_lst = [' '.join(x) for x in lst]
    return n_lst


def _reverse2(lst):
    n_lst = []
    for item in lst:
        for el in item:
            el[0], el[1], el[2], el[3] = el[1], el[0], el[3], el[2]
        n_lst.append([' '.join(x) for x in item])
    return n_lst


def _format(json_path, lst, cf):
    count_lst = []
    for j in range(len(lst)):
        count_lst.append([
            re.findall(r'\w\w', format(int(''.join(str("{:.3f}".format(x * cf)).split('.'))), '08X'))
            for x in json_path[lst[j]]
        ])
    return count_lst


def _offset(mem_offset, lst):
    count_lst = []
    for m in range(5):
        count_lst.append(
            f'{format(mem_offset, "04X")[:2]} {format(mem_offset, "04X")[2:]} 10 {lst[0][m]} {lst[1][m]} {lst[2][m]} {lst[3][m]}')
        mem_offset += 0x11
    return count_lst


# ===========================================================================================================
def EnergyReset(k):
    count_lst = []
    ap, am, pp, pm = _reverse2(_format(meter, ['A+', 'A-', 'R+', 'R-'], k))

    offset = 0x0000
    for i in range(4):
        count_lst.append(f'{format(offset, "04X")[:2]} {format(offset, "04X")[2:]} 10 {ap[i]} {am[i]} {pp[i]} {pm[i]}')
        offset += 0x11
    return count_lst


# ===========================================================================================================
def EnergyPhase(k):
    count_lst = []
    phase_a, phase_b, phase_c = _reverse2(_format(meter, ['PhaseA', 'PhaseB', 'PhaseC'], k))

    offset = 0x092A
    for i in range(4):
        count_lst.append(
            f'{format(offset, "04X")[:2]} {format(offset, "04X")[2:]} 0C {phase_a[i]} {phase_b[i]} {phase_c[i]}')
        offset += 0x0D
    return count_lst


# ===========================================================================================================
def EnergyYear(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['Year_A+', 'Year_A-', 'Year_R+', 'Year_R-'], k))

    return _offset(0x0200, [ap, am, pp, pm])


# ===========================================================================================================
def EnergyOldYear(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['Year_old_A+', 'Year_old_A-', 'Year_old_R+', 'Year_old_R-'], k))

    return _offset(0x0255, [ap, am, pp, pm])


# ===========================================================================================================
def EnergyJanuary(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['January_A+', 'January_A-', 'January_R+', 'January_R-'], k))

    return _offset(0x02AA, [ap, am, pp, pm])


# ===========================================================================================================
def EnergyFebruary(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['February_A+', 'February_A-', 'February_R+', 'February_R-'], k))

    return _offset(0x02FF, [ap, am, pp, pm])


# ===========================================================================================================
def EnergyMarch(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['March_A+', 'March_A-', 'March_R+', 'March_R-'], k))

    return _offset(0x0354, [ap, am, pp, pm])


# ===========================================================================================================
def EnergyApril(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['April_A+', 'April_A-', 'April_R+', 'April_R-'], k))

    return _offset(0x03A9, [ap, am, pp, pm])


# ===========================================================================================================
def EnergyMay(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['May_A+', 'May_A-', 'May_R+', 'May_R-'], k))

    return _offset(0x03FE, [ap, am, pp, pm])


# ===========================================================================================================
def EnergyJune(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['June_A+', 'June_A-', 'June_R+', 'June_R-'], k))

    return _offset(0x0453, [ap, am, pp, pm])


# ===========================================================================================================
def EnergyJuly(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['July_A+', 'July_A-', 'July_R+', 'July_R-'], k))

    return _offset(0x04A8, [ap, am, pp, pm])


# ===========================================================================================================
def EnergyAugust(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['August_A+', 'August_A-', 'August_R+', 'August_R-'], k))

    return _offset(0x04FD, [ap, am, pp, pm])


# ===========================================================================================================
def EnergySeptember(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['September_A+', 'September_A-', 'September_R+', 'September_R-'], k))

    return _offset(0x0552, [ap, am, pp, pm])


# ===========================================================================================================
def EnergyOctober(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['October_A+', 'October_A-', 'October_R+', 'October_R-'], k))

    return _offset(0x05A7, [ap, am, pp, pm])


# ===========================================================================================================
def EnergyNovember(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['November_A+', 'November_A-', 'November_R+', 'November_R-'], k))

    return _offset(0x05FC, [ap, am, pp, pm])


# ===========================================================================================================
def EnergyDecember(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['December_A+', 'December_A-', 'December_R+', 'December_R-'], k))

    return _offset(0x0651, [ap, am, pp, pm])


# ===========================================================================================================
def EnergyDay(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['Day_A+', 'Day_A-', 'Day_R+', 'Day_R-'], k))

    return _offset(0x06A6, [ap, am, pp, pm])


# ===========================================================================================================
def EnergyOldDay(k):
    ap, am, pp, pm = _reverse2(_format(meter, ['Day_A+', 'Day_A-', 'Day_R+', 'Day_R-'], k))

    return _offset(0x06FB, [ap, am, pp, pm])
