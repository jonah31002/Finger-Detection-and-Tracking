# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 14:08:06 2023

@author: ess305
"""

from tkinter import *

window = Tk()
window.geometry("200x300")

def evaluate(event):
    thetext = StringVar()
    labeloutput = Label(app, textvariable = thetext)
    n = e.get()
    thetext.set(n)
    labeloutput.grid()
    e.delete(0, 'end') # Here we remove text inside the entry

app = Frame(window)
app.pack()

e = Entry(window)
e.pack()

b = Button(window, text="Return", command=lambda: evaluate(None)) # Here we have a lambda to pass None to the event
b.pack()

window.bind("<Return>", evaluate)

mainloop()

#%% 
from tkinter import *

win = Tk()                         # create the window

labels = []                        # no labels

                                   # index for method grid()
rowIndex = 2                       # Set to 2 because of the
                                   # buttons and the entry.
                                   # this variable is used to increment
                                   # the y position of the labels so that
                                   # they are drawn one after the other,
                                   # and not on top of each other.

def add_label():
    global labels, text, rowIndex
    labels.append(Label(win, text=text.get())) # append a label object to the list
    rowIndex += 1                  # increment the y position

                                   # draw the added label
    labels[-1]\
            .grid(columnspan=2,    # for align in the middle.
                  row=rowIndex,    # y position specific to this label
                  pady=5)

def delete_all_labels():
    global labels
    for label in labels:           # delete all the labels
        label.grid_forget()        # one by one

    rowIndex = 2                   # reset the vars
    labels = []                    #

label=Label(win, text="Type the text :")
label.grid(column=0, row=0, padx=5)

text = Entry(win)                  # add the entry
text.grid(column=1, row=0, padx=5)
text.focus()                       # focus in entry

Button(win, text="Create new label", command=add_label)\
            .grid(column=0, row=1, padx=5)
Button(win, text="Delete all the labels", command=delete_all_labels)\
            .grid(column=1, row=1, padx=5)

win.mainloop()

#%%
#Import the tkinter library
from tkinter import *
import time
#Create an instance of the canvas
win = Tk()

#Select the title of the window
win.title("tutorialspoint.com")

#Define the geometry of the window
win.geometry("600x400")
#Define the clock which
def clock():
   hh= time.strftime("%I")
   mm= time.strftime("%M")
   ss= time.strftime("%S")
   day=time.strftime("%A")
   ap=time.strftime("%p")
   time_zone= time.strftime("%Z")
   my_lab.config(text= hh + ":" + mm +":" + ss)
   my_lab.after(1000,clock)

   my_lab1.config(text=time_zone+" "+ day)
#Update the Time
def updateTime():
   my_lab.config(text= "New Text")

#Creating the label with text property of the clock
my_lab= Label(win,text= "",font=("sans-serif", 56), fg= "red")
my_lab.pack(pady=20)
my_lab1= Label(win, text= "", font=("Helvetica",20), fg= "blue")
my_lab1.pack(pady= 10)

#Calling the clock function
clock()
#Keep Running the window

win.mainloop()

#%% 
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def remove_plot():
    w.pack_forget()   # here you remove the widget from the tk window
    # w.destroy()


if __name__ == '__main__':

    # data
    x, y = [1, 2, 3, 4], [1, 4, 9, 16]

    # matplotlib stuff
    figure1 = plt.Figure(figsize=(6, 5), dpi=100)
    ax1 = figure1.add_subplot(111)
    ax1.plot(x, y)
    ax1.set_title('Country Vs. GDP Per Capita')

    # tkinter stuff
    root = tk.Tk()

    bar1 = FigureCanvasTkAgg(figure1, root)
    w = bar1.get_tk_widget()
    w.pack(side=tk.LEFT, fill=tk.BOTH)   # here you insert the widget in the tk window
    button_delete = tk.Button(root, text='Remove Plot', command=remove_plot)
    button_delete.place(height=30, width=100, rely=0.02, relx=0.4)   # place is an odd choice of geometry manager, you will have to adjust it every time the title changes

    root.mainloop()