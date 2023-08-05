import sensor, image, time

##串口通信所要引用的库
from pyb import UART

# UART 3, and baudrate.
uart = UART(3, 19200)

clock = time.clock()


while True:
    try:
        clock.tick()
        uart.write(bytes('h', 'utf-8'))
        if uart.any():
            ret = uart.read(2) # 读取2个字节的数据
            if ret == 'ok':
                uart.write(bytes('stop', 'utf-8'))
    except Exception as e:
        print("Error:", e)
