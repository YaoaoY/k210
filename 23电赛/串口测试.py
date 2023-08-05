import sensor, image, lcd, time

from machine import UART #串口库函数
from fpioa_manager import fm # GPIO重定向函数（引脚映射

fm.register(10, fm.fpioa.UART1_TX, force=True)
fm.register(11, fm.fpioa.UART1_RX, force=True)

uart = UART(UART.UART1, 0, 8, 0, 0, timeout=1000, read_buf_len=4096)

lcd.init() # 初始化LCD显示屏

sensor.reset()                      # 重置并初始化传感器
sensor.set_pixformat(sensor.GRAYSCALE) # 设置像素格式为RGB565（或GRAYSCALE）
sensor.set_framesize(sensor.QVGA)   # 设置帧大小为QVGA（320x240）
sensor.set_windowing((224, 224))    #
sensor.set_vflip(True)              # 垂直翻转图像（如果需要）
sensor.skip_frames(time = 2000)     # 等待设置生效
sensor.set_auto_whitebal(True)      # 设置自动白平衡
sensor.set_brightness(0)            # 设置亮度为0，以增加对比度
clock = time.clock()                # 创建一个时钟对象来跟

# 将四个角点的坐标数据打包成一个字符串
corner_str = str(1 + ',' + 2 + ',' + 3 + ',' + 4 + ',' + 4 + ',' + 5 + ',' + 6 + ',' + 7)

# 将角点数据发送到Arduino
uart.write(corner_str)

uart.write( corner_str + "\n")  # 使用换行符作为消息的结束，方便 Arduino 一次读取一个坐标

#print("左下角：",corner[0][0], corner[0][1],"，右下角 ",corner[1][0], corner[1][1],"，右上角：",corner[2][0], corner[2][1],"，左上角：",corner[3][0], corner[3][1])
lcd.display(img)
