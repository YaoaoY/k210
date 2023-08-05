# Untitled - By: Yaoyao - 周四 8月 3 2023

import sensor, image, time, lcd

from machine import UART #串口库函数
from Maix import GPIO
from fpioa_manager import fm # GPIO重定向函数（引脚映射


fm.register(GPIO.GPIOHS10, fm.fpioa.UART1_TX)
fm.register(GPIO.GPIOHS11, fm.fpioa.UART1_RX)

uart = UART(UART.UART1, 115200, 8, None, 1, timeout=1000, read_buf_len=4096)


lcd.init(freq=15000000)
sensor.reset()                      # Reset and initialize the sensor. It will
                                    # run automatically, call sensor.run(0) to stop
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.set_windowing((176,176))
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
#sensor.set_auto_whitebal(False) # turn this off..
sensor.set_auto_exposure(True, 80)#在这里调节曝光度，调节完可以比较清晰地看清激光点
#sensor.set_contrast(1) #设置对比度范围为[-2,+2]
sensor.set_auto_gain(False)#图像变暗，识别更准确！
sensor.set_brightness(-1) #摄像头亮度，范围为[-2,+2]
#水平方向翻转
sensor.set_hmirror(True)
# 垂直方向翻转
sensor.set_vflip(True)
clock = time.clock()                # Create a clock object to track the FPS.


clock = time.clock()
green_threshold=[(90, 100, -85, 29, 3, 90)]
red_threshold = [(60, 255, -20, 20, -20, 20)]
#red_threshold = [(44, 93, 7, 45, -8, 14)]


#识别激光点代码
def color_blob(threshold):

    blobs = img.find_blobs(threshold,x_stride=1, y_stride=1, area_threshold=0, pixels_threshold=0,merge=False,margin=1)

    if len(blobs)>=1 :#有色块
        # Draw a rect around the blob.
        b = blobs[0]
        #img.draw_rectangle(b[0:4]) # rect
        cx = b[5]
        cy = b[6]
        for i in range(len(blobs)-1):
            #img.draw_rectangle(b[0:4],color = (0,255,0)) # rect
            cx = blobs[i][5]+cx
            cy = blobs[i][6]+cy
        cx=int(cx/len(blobs))
        cy=int(cy/len(blobs))
        img.draw_cross(cx, cy,color = (255,0,0)) # cx, cy

        return int(cx), int(cy)
    return -1, -1 #表示没有找到


while(True):
    clock.tick()
    img = sensor.snapshot()
    img.draw_cross((90,90),color = (0,0,255),size = 10, thickness=1)
    cx, cy = color_blob(red_threshold)
    dot_str = str(cx) + ',' + str(cy)+'+'
    uart.write( "@" + dot_str + "!")  # 使用换行符作为消息的结束，方便 Arduino 一次读取一个坐标
    #time.sleep_ms(20)
    #print("@" + dot_str + "!")
    #print("cx:",cx,"cy",cy)
    img.draw_circle(cx, cy, 5, color=127, thickness=2)
    lcd.display(img, x_scale=1, y_scale=1)

