# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 12:05:39 2023

@author: ess305
"""

import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from cv2 import cv2

# --- constants --- (PEP8: UPPER_CASE_NAMES)

#FPS = 25

# --- classes --- (PEP8: CamelCaseNames)

# ... empty ...

# --- functions --- (PEP8: lower_case_names)

def video_to_mainwin():
    """Getting a video frame, resizing it for the main window and placing it into the frame 2."""

    if not paused:
        chk, frame = cap.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        imgV = cv2.resize(cv2image, fitted_size) 
        img = Image.fromarray(imgV)
        imgtk = ImageTk.PhotoImage(image=img)
        labelF2.imgtk = imgtk
        labelF2.configure(image=imgtk)

    # run it again after `1000/FPS` milliseconds
    #mainwin.after(int(1000/FPS), video_to_mainwin)
    mainwin.after(int(1000/cap_fps), video_to_mainwin)

def set_pause(event):
    global paused
    
    paused = True
    labelF1.config(text = 'Paused')

def unset_pause(event):
    global paused
    
    paused = False
    labelF1.config(text = '') 
    
# --- main ---- (PEP8: lower_case_names)
    
paused = False  # default value at start

# - cap - 

cap = cv2.VideoCapture(0)
cap_frame_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap_frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cap_fps = int(cap.get(cv2.CAP_PROP_FPS))

# - tk -

mainwin = tk.Tk()  # create main window

app_win_width = int(0.6 * mainwin.winfo_screenwidth()) # set main window size (depending on the screen)
app_win_height = int(0.5 * mainwin.winfo_screenheight())

screen_width = mainwin.winfo_screenwidth() # get screen dimensions
screen_height = mainwin.winfo_screenheight()

app_win_x = int((screen_width - app_win_width)/2) # set coordinates of the main window so that it 
app_win_y = int((screen_height - app_win_height)/2) # would be located in the middle of the screen

#create and place the frames
frame1 = tk.Frame(mainwin, background="white", width=int(app_win_width/2), height=app_win_height)
frame2 = tk.Frame(mainwin, background="black", width=int(app_win_width/2), height=app_win_height)

frame1.grid(row=0, column=0, sticky="nsew")   # PEP8: without spaces around `=`
frame2.grid(row=0, column=1, sticky="nsew")   # PEP8: without spaces around `=`

mainwin.grid_columnconfigure(0, weight=1)   # PEP8: without spaces around `=`
mainwin.grid_columnconfigure(1, weight=1)   # PEP8: without spaces around `=`
mainwin.grid_rowconfigure(0, weight=1)

#set the geometry of the main window
mainwin.geometry("{}x{}+{}+{}".format(app_win_width, app_win_height, app_win_x, app_win_y)) 
mainwin.resizable(width=0, height=0)

# create labels in frames
frame2.grid_propagate(0) # labels and other widgets in frame don't change the size of the frame
frame2.grid()

labelF2 = tk.Label(frame2)
labelF2.place(relx=0.5, rely=0.5, anchor="center")

frame1.grid_propagate(0)

labelF1 = tk.Label(frame1, background = "white")
labelF1.grid()

mainwin.update() # to create window and correctly calculate sizes

# get camera feed and frame size
width_relation  = cap_frame_width/frame2.winfo_width()
heigth_relation = cap_frame_height/frame2.winfo_height()


# define the size of the video frame so that the video would fit into the frame of the main window
if width_relation > 1 and width_relation > heigth_relation:
    fitted_size = (int(cap_frame_width/width_relation), int(cap_frame_height/width_relation))
elif heigth_relation > 1 and heigth_relation > width_relation:
    fitted_size = (int(cap_frame_width/heigth_relation), int(cap_frame_height/heigth_relation))
else:
    fitted_size = (cap_frame_width, cap_frame_height)

# assing functions to buttons
mainwin.bind("p", set_pause)
mainwin.bind("c", unset_pause)

# star video
video_to_mainwin()

# start tkinter mainloop (event loop)
mainwin.mainloop()

# - end -

cap.release()