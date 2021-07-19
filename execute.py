class Execute:

    # =============== 1-й байт варианта исполнения ==============
    @staticmethod
    def byte_11(tmp):
        return {
            tmp == "00": "0,2S",
            tmp == "01": "0,5S",
            tmp == "10": "1,0",
            tmp == "11": "2,0",
        }[True]

    @staticmethod
    def byte_12(tmp):
        return {
            tmp == "00": "0,2",
            tmp == "01": "0,5",
            tmp == "10": "1,0",
            tmp == "11": "2,0",
        }[True]

    @staticmethod
    def byte_13(tmp):
        return {
            tmp == "00": "57,7В",
            tmp == "01": "230В",
        }[True]

    @staticmethod
    def byte_14(tmp):
        return {
            tmp == "00": "5А",
            tmp == "01": "1А",
            tmp == "10": "10А"
        }[True]

    # =============== 2-й байт варианта исполнения ==============
    @staticmethod
    def byte_21(tmp):
        return {
            tmp == "0": "2",
            tmp == "1": "1"
        }[True]

    @staticmethod
    def byte_22(tmp):
        return {
            tmp == "0": "-20 C",
            tmp == "1": "-40 C"
        }[True]

    @staticmethod
    def byte_23(tmp):
        return {
            tmp == "0": "Нет",
            tmp == "1": "Есть"
        }[True]

    @staticmethod
    def byte_24(tmp):
        return {
            tmp == "0": "3",
            tmp == "1": "1"
        }[True]

    @staticmethod
    def byte_25(tmp):
        return {
            tmp == "0000": "5000 имп/кВт∙ч",
            tmp == "0001": "2500 имп/кВт∙ч",
            tmp == "0010": "1250 имп/кВт∙ч",
            tmp == "0011": "500 имп/кВт∙ч",
            tmp == "0100": "1000 имп/кВт∙ч",
            tmp == "0101": "250 имп/кВт∙ч"
        }[True]

    # =============== 3-й байт варианта исполнения ==============
    @staticmethod
    def byte_31(tmp):
        return {
            tmp == "0": "С учетом знака",
            tmp == "1": "По модулю"
        }[True]

    @staticmethod
    def byte_32(tmp):
        return {
            tmp == "0": "Внешний",
            tmp == "1": "Внутренний"
        }[True]

    @staticmethod
    def byte_33(tmp):
        return {
            tmp == "00": "A+R+",
            tmp == "01": "A+"
        }[True]

    @staticmethod
    def byte_34(tmp):
        return {
            tmp == "0001": "Вариант 1",
            tmp == "0010": "Вариант 2",
            tmp == "0011": "Вариант 3",
            tmp == "0100": "Вариант 4",
        }[True]

    # =============== 4-й байт варианта исполнения ==============
    @staticmethod
    def byte_41(tmp):
        return {
            tmp == "0": "65,5x8",
            tmp == "1": "131x8"
        }[True]

    @staticmethod
    def byte_42(tmp):
        return {
            tmp == "0": "Нет",
            tmp == "1": "Есть"
        }[True]

    @staticmethod
    def byte_43(tmp):
        return {
            tmp == "0": "Нет",
            tmp == "1": "Есть"
        }[True]

    @staticmethod
    def byte_44(tmp):
        return {
            tmp == "0": "Нет",
            tmp == "1": "Есть"
        }[True]

    @staticmethod
    def byte_45(tmp):
        return {
            tmp == "00": "CAN",
            tmp == "01": "RS-485",
            tmp == "10": "Резерв",
            tmp == "11": "Нет",
        }[True]

    @staticmethod
    def byte_46(tmp):
        return {
            tmp == "0": "Нет",
            tmp == "1": "Есть"
        }[True]

    @staticmethod
    def byte_47(tmp):
        return {
            tmp == "0": "Нет",
            tmp == "1": "Есть"
        }[True]

    # =============== 7-й байт варианта исполнения ==============
    @staticmethod
    def byte_71(tmp):
        return {
            tmp == "0000": "Не используется",
            tmp == "0001": "5000 имп/кВт∙ч",
            tmp == "0010": "2500 имп/кВт∙ч",
            tmp == "0011": "1250 имп/кВт∙ч",
            tmp == "0100": "500 имп/кВт∙ч",
            tmp == "0101": "1000 имп/кВт∙ч",
            tmp == "0110": "250 имп/кВт∙ч"
        }[True]
