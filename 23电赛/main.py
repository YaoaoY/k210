import sensor, image, lcd, time

from machine import UART #串口库函数
from Maix import GPIO
from fpioa_manager import fm # GPIO重定向函数（引脚映射

fm.register(GPIO.GPIOHS10, fm.fpioa.UART1_TX)
fm.register(GPIO.GPIOHS11, fm.fpioa.UART1_RX)

uart = UART(UART.UART1, 9600, 8, None, 1, timeout=1000, read_buf_len=4096)

lcd.init() # 初始化LCD显示屏

sensor.reset()                      # 重置并初始化传感器
sensor.set_pixformat(sensor.GRAYSCALE) # 设置像素格式为RGB565（或GRAYSCALE）
sensor.set_framesize(sensor.QVGA)   # 设置帧大小为QVGA（320x240）
sensor.set_windowing((224, 224))    #
sensor.set_vflip(True)              # 垂直翻转图像（如果需要）
sensor.skip_frames(time = 2000)     # 等待设置生效
sensor.set_auto_whitebal(True)      # 设置自动白平衡
sensor.set_brightness(0)            # 设置亮度为0，以增加对比度
clock = time.clock()                # 创建一个时钟对象来跟踪FPS

while(True):
    clock.tick()                    # 更新FPS时钟
    img = sensor.snapshot()         # 拍摄图片并返回图像
    # -----矩形框部分-----
    # 在图像中寻找矩形
    for r in img.find_rects(threshold = 10000):
        # 判断矩形边长是否符合要求
        if r.w() > 20 and r.h() > 20:
            # 在屏幕上框出矩形
            img.draw_rectangle(r.rect(), color = (255, 0, 0), thickness = 2, fill = False)
            # 获取矩形角点位置
            corner = r.corners()
            # 在屏幕上圆出矩形角点；四个角点坐标, 角点1的数组是corner[0], 坐标就是(corner[0][0],corner[0][1])
            img.draw_circle(corner[0][0], corner[0][1], 5, color = (0, 0, 255), thickness = 2, fill = False)
            img.draw_circle(corner[1][0], corner[1][1], 5, color = (0, 0, 255), thickness = 2, fill = False)
            img.draw_circle(corner[2][0], corner[2][1], 5, color = (0, 0, 255), thickness = 2, fill = False)
            img.draw_circle(corner[3][0], corner[3][1], 5, color = (0, 255, 0), thickness = 2, fill = False)

            # 将四个角点的坐标数据打包成一个字符串
            corner_str = str(corner[0][0]) + ',' + str(corner[0][1]) + ',' + str(corner[1][0]) + ',' + str(corner[1][1]) + ',' + str(corner[2][0]) + ',' + str(corner[2][1]) + ',' + str(corner[3][0]) + ',' + str(corner[3][1])

           # 将角点数据发送到Arduino
            uart.write(corner_str)

            uart.write( "@" + corner_str + "!")  # 使用换行符作为消息的结束，方便 Arduino 一次读取一个坐标
            print("@" + corner_str + "!")
            # 停止1秒钟
            time.sleep(1)

            #print("左下角：",corner[0][0], corner[0][1],"，右下角 ",corner[1][0], corner[1][1],"，右上角：",corner[2][0], corner[2][1],"，左上角：",corner[3][0], corner[3][1])


    # 在屏幕上显示图像，此部分会降低帧率
    lcd.display(img)

    # 打印帧率
    #print(clock.fps())
