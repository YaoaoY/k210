# Hello World Example
#
# Welcome to the OpenMV IDE! Click on the green run arrow button below to run the script!
# 用于绑定激光的摄像头（激光点始终在屏幕中心处）；功能：找到该屏幕内的黑色色卡的中心点，根据另外一个K210发送来的数据，进行移动

import sensor, image, time

import ustruct # 用于快速打包和解包数据的模块。
import array #用于创建和操作数值数组的模块。

##串口通信所要引用的库
from pyb import UART

# UART 3, and baudrate.
uart = UART(3, 19200)

flag = 0

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
sensor.set_auto_whitebal(False) # turn this off.关闭自动白平衡
clock = time.clock()                # Create a clock object to track the FPS.

window_roi = (0,0,240, 240)

line_thresholds = [(25,33),(24,24),(8,25)]
track_roi = (100,100,40,40)

red_threshold  = (13, 49, 18, 64, 121, -98) # 红色激光颜色阈值
size_threshold = 2000 # 物体的大小阈值，通过调整像素面积的大小来确定。

# 定义标志变量，初始值为False
flag2= False


# 根据阈值，查找最大色块
def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob

def send_data_to_arduino(exp_x, exp_y, red_x, red_y):
    # 将四个变量打包为一个字节数组
    data = bytearray()
    data.extend(exp_x.to_bytes(2, 'little'))
    data.extend(exp_y.to_bytes(2, 'little'))
    data.extend(red_x.to_bytes(2, 'little'))
    data.extend(red_y.to_bytes(2, 'little'))

    # 将数据发送到Arduino
    uart.write(data)

#串口接收函数
def receive_data():
     tmp_data = uart.read();  #读取所有可用字符#b'a'
     return tmp_data

#得到A4纸的左上角坐标
def get_leftup_index():
    rects = img.find_rects(threshold = 10000)
     # 返回左上角坐标
    if len(rects) > 0:
        rect = rects[0]
        x, y, w, h = rect
        return x, y
    else:
        return -1,-1

def track_light(light_threshold):
     cx = cy = 0
     blobs = img.find_blobs([light_threshold])
     if blobs:
         max_blob = find_max(blobs)
         img.draw_rectangle(max_blob[0:4]) # rect
         cx = max_blob[5]
         cy = max_blob[6]
         img.draw_cross(cx, cy ) # cx, cy
     return cx, cy

def begin(red_x1, red_y1):
    #开始得到左上角坐标，并且让激光红点移动
    exp_x,exp_y = get_leftup_index()
    #激光点的坐标在中心点（固定的）
    red_x = red_x1
    red_y = red_y1
    send_data_to_arduino(exp_x, exp_y, red_x, red_y)
    #print("左上角坐标",exp_x, exp_y, red_x, red_y)


def track(red_x1,red_y1):
    #print("welcom to track")
    global flag
    #先绘制一下感兴趣区域
    img.draw_cross(120, 120,size = 8)
    #img.draw_rectangle(track_roi, color = (0, 255, 0), thickness = 1,merge = True)


    # 查找ROI区域内的线段
    line_segments = img.find_line_segments(roi=track_roi, merge_distance=10, max_theta_difference=5)

    line_num = len( line_segments)
    if(line_num >=2):
        #向单片机发送转换信号
        flag += 1
        uart.write(bytes([flag]))
    else:
        # 在图像上绘制线段
        for line in line_segments:
            img.draw_line(line.line(), color=(255, 0, 0))
            #计算预期中心点坐标并且发送给中心坐标
            exp_x = (line.x1()+line.x2())/2;
            exp_y = (line.y1()+line.y2())/2;

            #激光点的坐标在中心点（固定的）
            red_x = red_x1
            red_y = red_y1
            send_data_to_arduino(exp_x, exp_y, red_x, red_y)

     #打印直线元素的个数
    print("Number of lines detected: ", len( line_segments))

red_x1 = -1
red_y1 = -1

while(True):


    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image.
    #print(clock.fps())              # Note: OpenMV Cam runs about half as fast when connected
                                    # to the IDE. The FPS should increase once disconnected.
    sensor.set_windowing(window_roi)
    img.draw_rectangle(window_roi, color = (255, 0, 0), thickness = 1)

    #只执行一次，给arduino发送预期左上角坐标和激光所在点坐标
    if flag2 == False:
        #red_x1,red_y1 = track_light(red_threshold)
        red_x1 = 120
        red_y1 = 120
        begin(red_x1, red_y1)
        flag2 = True

    #如果接收到了arduino的返回值，则开始循迹
    ret = receive_data()
    if(ret == 'ok'):
        track(red_x1, red_y1)
