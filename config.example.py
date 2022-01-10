# Connect MODE
CONNECT_MODE = 0  # 0-RS485, 1-CSD, 2-TCP/IP

# Debug MODE
DEBUG = True

# Serial port
UART_PORT = '/dev/ttyUSB0'
UART_PORT_TIMEOUT = 1.8  # UART(0.048 - 0.5)

# TCP/IP
TCP_HOST = ''
TCP_PORT = 1
TCP_TIMEOUT = 7  # Timeout TCP(2-10)

# Device
DEVICE_ID = 30
DEVICE_LEVEL = 2
DEVICE_PASSWORD = '222222'
DEVICE_PASSWORD_MODE = 'hex'

# Update firmware
FIRMWARE_FILE = 'update/firmware.txt'

# CSD MODE
CSD_PHONE = ''
CSD_TIMEOUT = 15
