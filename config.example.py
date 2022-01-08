# Режим соединения / 0-RS485, 1-CSD, 2-TCP
MODE = 1

# Параметры для пароля
START_PASSWORD = 100800
STOP_PASSWORD = 999999
PASS_MODE = 'hex'   # 'hex' or 'ascii'

# Идентификатор ПУ
PK = 0  # Default '0'

# Настройки Serial порта
PORT = '/dev/ttyUSB0'   # Serial port Linux-'/dev/tty' Windows-'COM1'
SERIAL_TIMEOUT = .08

# Настройки для CSD соединения
CSD_PHONE = ''  # if CSD==True
CSD_TIMEOUT = 10

# Настройки для TCP соединения
TCP_HOST = '127.0.0.1'
TCP_PORT = 8000
TCP_TIMEOUT = 7
