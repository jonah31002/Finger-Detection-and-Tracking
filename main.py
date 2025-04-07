# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 15:40:34 2023

@author: ess305
"""

import tkinter as tk
import tkinter.ttk as ttk
import cv2
from PIL import Image, ImageTk
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

hand_hist = None
calibration = False
start = False
record = False
paused = False
neuron_record = []
time_record = []
traverse_point = []
total_rectangle = 9
total_neuron_number = 10
hand_rect_one_x = None
hand_rect_one_y = None
dx = []
dy = []

hand_rect_two_x = None
hand_rect_two_y = None
is_hand_hist_created = False

def draw_circles(frame, traverse_point):
    if len(traverse_point) < 10:
        return(cv2.circle(frame, traverse_point[-1], int(5 - (5 * 0 * 3) / 100), [0, 255, 255], -1))
    else:
        layer1 = cv2.circle(frame, traverse_point[-1], int(5 - (5 * 5 * 3) / 100), [0, 255, 255], -1)
        layer2 = cv2.circle(layer1, traverse_point[-2], int(5 - (5 * 4 * 3) / 100), [0, 255, 255], -1)
        layer3 = cv2.circle(layer2, traverse_point[-3], int(5 - (5 * 3 * 3) / 100), [0, 255, 255], -1)
        layer4 = cv2.circle(layer3, traverse_point[-4], int(5 - (5 * 2 * 3) / 100), [0, 255, 255], -1)
        layer5 = cv2.circle(layer4, traverse_point[-5], int(5 - (5 * 1 * 3) / 100), [0, 255, 255], -1)
        return(layer5)    

def neuron_index(angle, neuron_number):
    global dx, dy
    
    single_angle = 360.0 / neuron_number
    neuron = np.arange(0, 360, single_angle)
    angle_for_dx = neuron + (single_angle/2)
    dx = np.cos(angle_for_dx * np.pi / 180. )
    dy = np.sin(angle_for_dx * np.pi / 180. )
    
    for i in range(len(neuron)):
        if neuron[i] <= angle < neuron[i]+single_angle:
            print(i)
            return i
            
def farthest_point(defects, contour, centroid):
    if defects is not None and centroid is not None:
        s = defects[:, 0][:, 0]
        cx, cy = centroid

        x = np.array(contour[s][:, 0][:, 0], dtype=np.float64)
        y = np.array(contour[s][:, 0][:, 1], dtype=np.float64)

        xp = cv2.pow(cv2.subtract(x, cx), 2)
        yp = cv2.pow(cv2.subtract(y, cy), 2)
        dist = cv2.sqrt(cv2.add(xp, yp))

        dist_max_i = np.argmax(dist)

        if dist_max_i < len(s):
            farthest_defect = s[dist_max_i]
            farthest_point = tuple(contour[farthest_defect][0])
            return farthest_point
        else:
            return None

def centroid(max_contour):
    moment = cv2.moments(max_contour)
    if moment['m00'] != 0:
        cx = int(moment['m10'] / moment['m00'])
        cy = int(moment['m01'] / moment['m00'])
        return cx, cy
    else:
        return None

def contours(hist_mask_image):
    gray_hist_mask_image = cv2.cvtColor(hist_mask_image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_hist_mask_image, 0, 255, 0)
    cont, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return cont

def hist_masking(frame, hist):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    dst = cv2.calcBackProject([hsv], [0, 1], hist, [0, 180, 0, 256], 1)

    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    cv2.filter2D(dst, -1, disc, dst)

    ret, thresh = cv2.threshold(dst, 150, 255, cv2.THRESH_BINARY)

    # thresh = cv2.dilate(thresh, None, iterations=5)

    thresh = cv2.merge((thresh, thresh, thresh))

    return cv2.bitwise_and(frame, thresh)

def manage_image_opr(frame, hand_hist):
    hist_mask_image = hist_masking(frame, hand_hist)

    hist_mask_image = cv2.erode(hist_mask_image, None, iterations=2)
    hist_mask_image = cv2.dilate(hist_mask_image, None, iterations=2)

    contour_list = contours(hist_mask_image)
    max_cont = max(contour_list, key=cv2.contourArea)

    cnt_centroid = centroid(max_cont)
    cv2.circle(frame, cnt_centroid, 5, [255, 0, 255], -1) # 桃紅色

    if max_cont is not None:
        hull = cv2.convexHull(max_cont, returnPoints=False)
        defects = cv2.convexityDefects(max_cont, hull)
        far_point = farthest_point(defects, max_cont, cnt_centroid)
        # print("Centroid : " + str(cnt_centroid) + ", farthest Point : " + str(far_point)) # 中心點和最遠點
        cv2.circle(frame, far_point, 5, [0, 0, 255], -1) # 紅色
        if len(traverse_point) < 20:
            traverse_point.append(far_point)
            index = 0
        else:
            vector = (int(traverse_point[-1][0]-traverse_point[0][0]), int(traverse_point[0][1]-traverse_point[-1][1])) # 兩點之間的向量
            if math.sqrt(vector[0]*vector[0] + vector[1]*vector[1]) == 0:
                theta = 0.0
            else:
                cosine_theta = abs(vector[0]/math.sqrt(vector[0]*vector[0] + vector[1]*vector[1]))
                theta = math.degrees(math.acos(cosine_theta))
            if vector[1] > 0:
                if vector[0] > 0:
                    angle = theta
                    #print(theta)
                else:
                    angle = 180.0 - theta
                    #print(angle)
            else:
                if vector[0] > 0:
                    angle = 360.0 - theta
                    #print(angle)
                else:
                    angle = 180.0 + theta
                    #print(angle)
            index = neuron_index(angle, total_neuron_number)
            traverse_point.pop(0)
            traverse_point.append(far_point)
            
        return(index, draw_circles(frame, traverse_point))

def hand_histogram(frame):
    global hand_rect_one_x, hand_rect_one_y

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    roi = np.zeros([90, 10, 3], dtype=hsv_frame.dtype)

    for i in range(total_rectangle):
        roi[i * 10: i * 10 + 10, 0: 10] = hsv_frame[hand_rect_one_x[i]:hand_rect_one_x[i] + 10,
                                          hand_rect_one_y[i]:hand_rect_one_y[i] + 10]

    hand_hist = cv2.calcHist([roi], [0, 1], None, [180, 256], [0, 180, 0, 256])
    return cv2.normalize(hand_hist, hand_hist, 0, 255, cv2.NORM_MINMAX)

def reconstruct():
    global neuron_record, dx, dy
    
    for i, widget in enumerate(frame3.winfo_children()):
        if i == 1:
            widget.destroy()
    
    fig = plt.figure()
    initial_point = [0, 0]
    
    for i in neuron_record:
        plt.arrow(initial_point[0], initial_point[1], dx[i], dy[i], width = 0.05)
        initial_point = [initial_point[0]+dx[i], initial_point[1]+dy[i]]
    canvas = FigureCanvasTkAgg(fig, master=frame3)  
    canvas.draw()
  
    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().place(relx=0.5, rely=0.5, anchor="center")

def submit1():
    labelF4_2.config(text="Completed")

def submit2():
    global total_neuron_number
    
    labelF4_4.config(text="Completed")
    total_neuron_number = int(neuron_var.get())    

def pause():
    global paused
    
    labelF2_1.config(text = 'Paused')
    labelF2_2.config(text = '')
    labelF2_3.config(text = '')
    labelF2_4.config(text = '')
    labelF2_5.config(text = '')
    labelF2_6.config(text = '')
    labelF2_7.config(text = '')
    labelF2_8.config(text = '')
    labelF2_9.config(text = '')
    labelF2_10.config(text = '')
    labelF2_11.config(text = '')
    labelF2_12.config(text = '')
    labelF2_13.config(text = '')
    labelF2_14.config(text = '')
    labelF2_15.config(text = '')
    labelF2_16.config(text = '')
    labelF2_17.config(text = '')
    labelF2_18.config(text = '')
    labelF2_19.config(text = '')
    labelF2_20.config(text = '')
    paused = True

def save():
    global neuron_record, total_neuron_number, time_record
    
    np.savetxt(name_var.get()+"_order.csv", neuron_record, delimiter = ",", fmt = "%i")
    matrix = np.zeros((total_neuron_number, len(neuron_record)))
    for i in range(len(neuron_record)):
        matrix[neuron_record[i], i] = 1
    np.savetxt(name_var.get()+"_spike_matrix.csv", matrix, delimiter = ",", fmt = "%i")
    np.savetxt(name_var.get()+"_time_record.csv", time_record, delimiter = ",", fmt = "%f")

def record():
    global record
    
    labelF2_1.config(text = '')
    record = True

def start():
    global start
    
    labelF2_1.config(text = '')
    start = True

def calibrate():
    global calibration, hand_hist
    
    calibration = True
    
    _, frame = camera.read()
    frame = cv2.flip(frame, 1)
    hand_hist = hand_histogram(frame)
    labelF2_1.config(text = 'Completed', font="Arial 20 bold")

def reset():
    global calibration, start, record, neuron_record, paused, time_record
    
    calibration = False
    start = False
    record = False
    paused = False
    neuron_record = []
    time_record = []
    labelF2_1.config(text = '')
    labelF2_2.config(text = '')
    labelF2_3.config(text = '')
    labelF2_4.config(text = '')
    labelF2_5.config(text = '')
    labelF2_6.config(text = '')
    labelF2_7.config(text = '')
    labelF2_8.config(text = '')
    labelF2_9.config(text = '')
    labelF2_10.config(text = '')
    labelF2_11.config(text = '')
    labelF2_12.config(text = '')
    labelF2_13.config(text = '')
    labelF2_14.config(text = '')
    labelF2_15.config(text = '')
    labelF2_16.config(text = '')
    labelF2_17.config(text = '')
    labelF2_18.config(text = '')
    labelF2_19.config(text = '')
    labelF2_20.config(text = '')

def draw_rect(frame):
    rows, cols, _ = frame.shape
    global total_rectangle, hand_rect_one_x, hand_rect_one_y, hand_rect_two_x, hand_rect_two_y

    hand_rect_one_x = np.array(
        [6 * rows / 20, 6 * rows / 20, 6 * rows / 20, 9 * rows / 20, 9 * rows / 20, 9 * rows / 20, 12 * rows / 20,
         12 * rows / 20, 12 * rows / 20], dtype=np.uint32)

    hand_rect_one_y = np.array(
        [9 * cols / 20, 10 * cols / 20, 11 * cols / 20, 9 * cols / 20, 10 * cols / 20, 11 * cols / 20, 9 * cols / 20,
         10 * cols / 20, 11 * cols / 20], dtype=np.uint32)

    hand_rect_two_x = hand_rect_one_x + 10
    hand_rect_two_y = hand_rect_one_y + 10

    for i in range(total_rectangle):
        cv2.rectangle(frame, (hand_rect_one_y[i], hand_rect_one_x[i]),
                      (hand_rect_two_y[i], hand_rect_two_x[i]),
                      (0, 255, 0), 1) # 綠色

    return frame

def video_loop():
    global hand_hist, is_hand_hist_created
    
    # Reset
    if calibration == False and start == False and record == False and paused == False:
        _, frame = camera.read()
        frame = cv2.flip(frame, 1)
        frame = draw_rect(frame)
    
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        imgV = cv2.resize(cv2image, fitted_size)
        current_image = Image.fromarray(imgV)
        imgtk = ImageTk.PhotoImage(image=current_image)
        labelF1.imgtk = imgtk
        labelF1.configure(image=imgtk)
    
    # Start finger tracking
    if start == True and paused == False:
        _, frame = camera.read()
    
        frame = cv2.flip(frame, 1)
        _, frame = manage_image_opr(frame, hand_hist)
    
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        imgV = cv2.resize(cv2image, fitted_size)
        current_image = Image.fromarray(imgV)
        imgtk = ImageTk.PhotoImage(image=current_image)
        labelF1.imgtk = imgtk
        labelF1.configure(image=imgtk)
    
    # Show neuron history
    if record == True and paused == False:
        _, frame = camera.read()
    
        frame = cv2.flip(frame, 1)
        index, frame = manage_image_opr(frame, hand_hist)
        if index is not None:
            neuron_record.append(index)
            time_record.append(time.time()*1000)
    
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        imgV = cv2.resize(cv2image, fitted_size)
        current_image = Image.fromarray(imgV)
        imgtk = ImageTk.PhotoImage(image=current_image)
        labelF1.imgtk = imgtk
        labelF1.configure(image=imgtk)
        if len(neuron_record) > 20:
            labelF2_1.configure(text="{}".format(neuron_record[-1]), font="Arial 20 bold")
            labelF2_2.configure(text="{}".format(neuron_record[-2]), font="Arial 20 bold")
            labelF2_3.configure(text="{}".format(neuron_record[-3]), font="Arial 20 bold")
            labelF2_4.configure(text="{}".format(neuron_record[-4]), font="Arial 20 bold")
            labelF2_5.configure(text="{}".format(neuron_record[-5]), font="Arial 20 bold")
            labelF2_6.configure(text="{}".format(neuron_record[-6]), font="Arial 20 bold")
            labelF2_7.configure(text="{}".format(neuron_record[-7]), font="Arial 20 bold")
            labelF2_8.configure(text="{}".format(neuron_record[-8]), font="Arial 20 bold")
            labelF2_9.configure(text="{}".format(neuron_record[-9]), font="Arial 20 bold")
            labelF2_10.configure(text="{}".format(neuron_record[-10]), font="Arial 20 bold")
            labelF2_11.configure(text="{}".format(neuron_record[-11]), font="Arial 20 bold")
            labelF2_12.configure(text="{}".format(neuron_record[-12]), font="Arial 20 bold")
            labelF2_13.configure(text="{}".format(neuron_record[-13]), font="Arial 20 bold")
            labelF2_14.configure(text="{}".format(neuron_record[-14]), font="Arial 20 bold")
            labelF2_15.configure(text="{}".format(neuron_record[-15]), font="Arial 20 bold")
            labelF2_16.configure(text="{}".format(neuron_record[-16]), font="Arial 20 bold")
            labelF2_17.configure(text="{}".format(neuron_record[-17]), font="Arial 20 bold")
            labelF2_18.configure(text="{}".format(neuron_record[-18]), font="Arial 20 bold")
            labelF2_19.configure(text="{}".format(neuron_record[-19]), font="Arial 20 bold")
            labelF2_20.configure(text="{}".format(neuron_record[-20]), font="Arial 20 bold")
        
    root.after(1, video_loop)

# - cap - 

camera = cv2.VideoCapture(0)
camera_frame_width  = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
camera_frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
camera_fps = int(camera.get(cv2.CAP_PROP_FPS))

# - tk -

root = tk.Tk()
root.title("opencv + tkinter")
app_win_width = int(0.9 * root.winfo_screenwidth()) # set main window size (depending on the screen)
app_win_height = int(0.6 * root.winfo_screenheight())

screen_width = root.winfo_screenwidth() # get screen dimensions
screen_height = root.winfo_screenheight()

app_win_x = int((screen_width - app_win_width)/2) # set coordinates of the main window so that it 
app_win_y = int((screen_height - app_win_height)/2) # would be located in the middle of the screen

#create and place the frames
frame1 = tk.Frame(root, background="black", width=int(app_win_width/4), height=app_win_height)
frame2 = tk.Frame(root, background="white", width=int(app_win_width/9), height=app_win_height)
frame3 = tk.Frame(root, background="black", width=int(app_win_width/4), height=app_win_height)
frame4 = tk.Frame(root, background="white", width=int(app_win_width/8), height=app_win_height)

frame1.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew")
frame2.grid(row=0, column=2, rowspan=2, sticky="nsew")
frame3.grid(row=0, column=3, columnspan=2, rowspan=2, sticky="nsew")
frame4.grid(row=0, column=5, rowspan=2, sticky="nsew")

root.grid_columnconfigure(0, weight=1) # column 0 的寬度為基礎
root.grid_columnconfigure(1, weight=1) # column 1 的寬度和 column 0 相同
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(4, weight=1)
root.grid_columnconfigure(5, weight=1)
root.grid_rowconfigure(0, weight=1) # row 0 的高度為基礎
root.grid_rowconfigure(1, weight=1) # row 1 的高度和 row 0 相同

#set the geometry of the main window
root.geometry("{}x{}+{}+{}".format(app_win_width, app_win_height, app_win_x, app_win_y)) 
root.resizable(width=0, height=0)

# create labels in frames
frame1.grid_propagate(0) # labels and other widgets in frame don't change the size of the frame
frame1.grid()

labelF1 = tk.Label(frame1)
labelF1.place(relx=0.5, rely=0.5, anchor="center")

frame2.grid_propagate(0)
frame1.grid()

labelF2_1 = tk.Label(frame2, background = "white")
labelF2_1.grid()

labelF2_2 = tk.Label(frame2, background = "white")
labelF2_2.grid()

labelF2_3 = tk.Label(frame2, background = "white")
labelF2_3.grid()

labelF2_4 = tk.Label(frame2, background = "white")
labelF2_4.grid()

labelF2_5 = tk.Label(frame2, background = "white")
labelF2_5.grid()

labelF2_6 = tk.Label(frame2, background = "white")
labelF2_6.grid()

labelF2_7 = tk.Label(frame2, background = "white")
labelF2_7.grid()

labelF2_8 = tk.Label(frame2, background = "white")
labelF2_8.grid()

labelF2_9 = tk.Label(frame2, background = "white")
labelF2_9.grid()

labelF2_10 = tk.Label(frame2, background = "white")
labelF2_10.grid()

labelF2_11 = tk.Label(frame2, background = "white")
labelF2_11.grid()

labelF2_12 = tk.Label(frame2, background = "white")
labelF2_12.grid()

labelF2_13 = tk.Label(frame2, background = "white")
labelF2_13.grid()

labelF2_14 = tk.Label(frame2, background = "white")
labelF2_14.grid()

labelF2_15 = tk.Label(frame2, background = "white")
labelF2_15.grid()

labelF2_16 = tk.Label(frame2, background = "white")
labelF2_16.grid()

labelF2_17 = tk.Label(frame2, background = "white")
labelF2_17.grid()

labelF2_18 = tk.Label(frame2, background = "white")
labelF2_18.grid()

labelF2_19 = tk.Label(frame2, background = "white")
labelF2_19.grid()

labelF2_20 = tk.Label(frame2, background = "white")
labelF2_20.grid()

frame3.grid_propagate(0)
frame3.grid()

frame4.grid_propagate(0)
frame4.grid()

labelF4_1 = ttk.Label(frame4, text='Participant')
labelF4_1.grid(column=0, row=0, sticky="nsew")

name_var = tk.StringVar()
name_entry = ttk.Entry(frame4, textvariable=name_var)
name_entry.grid(column=1, row=0, sticky="nsew")
name_entry.focus()

submit_btn = ttk.Button(frame4, text='Submit', command=submit1)
submit_btn.grid(column=2, row=0, sticky="nsew")

labelF4_2 = tk.Label(frame4, bg='#fff', fg='#f00')
labelF4_2.grid(column=0, row=1, columnspan=3, sticky="nsew")
labelF4_2.config(fg="#FF0000")

labelF4_3 = ttk.Label(frame4, text='Total Nuron Number:')
labelF4_3.grid(column=0, row=2, sticky="nsew")

neuron_var = tk.StringVar()
neuron_var.set("10")
neuron_entry = ttk.Entry(frame4, textvariable=neuron_var)
neuron_entry.grid(column=1, row=2, sticky="nsew")
neuron_entry.focus()

submit2_btn = ttk.Button(frame4, text='Submit', command=submit2)
submit2_btn.grid(column=2, row=2, sticky="nsew")

labelF4_4 = tk.Label(frame4, bg='#fff', fg='#f00')
labelF4_4.grid(column=0, row=3, columnspan=3, sticky="nsew")

# assing functions to buttons
reset_btn = ttk.Button(frame1, text="Reset", command=reset)
reset_btn.place(relx=0.15, rely=0.9, anchor="center")

calibration_btn = ttk.Button(frame1, text="Calibration", command=calibrate)
calibration_btn.place(relx=0.32, rely=0.9, anchor="center")

start_btn = ttk.Button(frame1, text="Start", command=start)
start_btn.place(relx=0.5, rely=0.9, anchor="center")

record_btn = ttk.Button(frame1, text="Record", command=record)
record_btn.place(relx=0.68, rely=0.9, anchor="center")

paused_btn = ttk.Button(frame1, text="Pause", command=pause)
paused_btn.place(relx=0.85, rely=0.9, anchor="center")

save_btn = ttk.Button(frame2, text="Save", command=save)
save_btn.place(relx=0.5, rely=0.9, anchor="center")

reconstruct_btn = ttk.Button(frame3, text="Reconstruct", command=reconstruct)
reconstruct_btn.place(relx=0.5, rely=0.9, anchor="center")

root.update() # to create window and correctly calculate sizes

# get camera feed and frame size
width_relation  = camera_frame_width/frame1.winfo_width()
heigth_relation = camera_frame_height/frame1.winfo_height()

# define the size of the video frame so that the video would fit into the frame of the main window
if width_relation > 1 and width_relation > heigth_relation:
    fitted_size = (int(camera_frame_width/width_relation), int(camera_frame_height/width_relation))
elif heigth_relation > 1 and heigth_relation > width_relation:
    fitted_size = (int(camera_frame_width/heigth_relation), int(camera_frame_height/heigth_relation))
else:
    fitted_size = (camera_frame_width, camera_frame_height)

video_loop()

root.mainloop()

camera.release()
cv2.destroyAllWindows()
