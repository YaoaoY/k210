import sensor, image, lcd, time

from machine import UART #串口库函数
from Maix import GPIO
from fpioa_manager import fm # GPIO重定向函数（引脚映射


fm.register(GPIO.GPIOHS10, fm.fpioa.UART1_TX)
fm.register(GPIO.GPIOHS11, fm.fpioa.UART1_RX)

uart = UART(UART.UART1, 9600, 8, None, 1, timeout=1000, read_buf_len=4096)

lcd.init(freq=15000000)
sensor.reset()                      # Reset and initialize the sensor. It will
                                    # run automatically, call sensor.run(0) to stop
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)   # Set frame size to 160x120 分辨率的相机传感器。

sensor.set_windowing((120,120))
#水平方向翻转
sensor.set_hmirror(True)
# 垂直方向翻转
sensor.set_vflip(True)
sensor.skip_frames(time = 10000)     # Wait for settings take effect.
clock = time.clock()                # Create a clock object to track the FPS.

def detect_rect():
    center_x = 0
    center_y = 0
    for i in range(3):
        clock.tick()
        img = sensor.snapshot()
        for r in img.find_rects():
            if r.w() > 20 and r.h() > 20 and r.w() < 100 and r.w() < 100:
                img.draw_rectangle(r.rect(), color = (255, 0, 0), thickness = 2, fill = False)
                center_x += r.cx()
                center_y += r.cy()
    if center_x != 0 and center_y != 0:
        center_x = int(center_x / 3)
        center_y = int(center_y / 3)
        img.draw_rectangle((center_x-5, center_y-5, 10, 10), color = (0, 255, 0), thickness = 2, fill = False)
        center_str = str(center_x) + ',' + str(center_y)
        uart.write(center_str)
        uart.write("@")
        uart.write(center_str)
        uart.write("!")
        print("@" + center_str + "!")
        time.sleep(1)
    lcd.display(img)

flag = 0

x1 = 0
y1 = 0
x2 = 0
y2 = 0
x3 = 0
y3 = 0
x4 = 0
y4 = 0

while(True):
    clock.tick()                    # 更新FPS时钟
    img = sensor.snapshot()         # 拍摄图片并返回图像
    img.draw_cross((60,60),color = (255,0,0),size = 5, thickness=1)
    # -----矩形框部分-----
    print("寻找矩形")
    # 在图像中寻找矩形
    for r in  img.find_rects():

        # 判断矩形边长是否符合要求
        if r.w() >20  and r.h() > 20 and r.w() < 100 and r.w() < 100:

            #flag += 1
            # 在屏幕上框出矩形
            print("找到了矩形",flag)
            #img.draw_rectangle(r.rect(), color = (255, 0, 0), thickness = 2, fill = False)

            # 获取矩形角点位置
            corner = r.corners()
            ## 在屏幕上圆出矩形角点；四个角点坐标, 角点1的数组是corner[0], 坐标就是(corner[0][0],corner[0][1])
            #img.draw_circle(corner[0][0], corner[0][1], 5, color = (0, 0, 255), thickness = 2, fill = False)
            #img.draw_circle(corner[1][0], corner[1][1], 5, color = (0, 0, 255), thickness = 2, fill = False)
            #img.draw_circle(corner[2][0], corner[2][1], 5, color = (0, 0, 255), thickness = 2, fill = False)
            #img.draw_circle(corner[3][0], corner[3][1], 5, color = (0, 255, 0), thickness = 2, fill = False)

            print("左下角：",corner[0][0], corner[0][1],"，右下角 ",corner[1][0], corner[1][1],"，右上角：",corner[2][0], corner[2][1],"，左上角：",corner[3][0], corner[3][1])
            x1 += corner[0][0]
            y1 += corner[0][1]
            x2 += corner[1][0]
            y2 += corner[1][1]
            x3 += corner[2][0]
            y3 += corner[2][1]
            x4 += corner[3][0]
            y4 += corner[3][1]


           ## 将角点数据发送到STM32F41
            #uart.write(corner_str)




    # 在屏幕上显示图像，此部分会降低帧率
    lcd.display(img)
    if(flag == 3):
        x1 = x1/3
        y1 = y1/3
        x2 = x2/3
        y2 = y2/3
        x3 = x3/3
        y3 = y3/3
        x4 = x4/4
        y4 = y4/4
        # 将四个角点的坐标数据打包成一个字符串b
        corner_str = str(x1) + ',' + str(y1) + ',' + str(x2) + ',' + str(y2) + ',' + str(x3) + ',' + str(y3) + ',' + str(x4) + ',' + str(y4)
        uart.write( "@" + corner_str + "!")  # 使用换行符作为消息的结束，方便 Arduino 一次读取一个坐标
        print("@" + corner_str + "!")
        # 停止1秒钟
        time.sleep(1)

        break

    # 打印帧率
    #print(clock.fps())
