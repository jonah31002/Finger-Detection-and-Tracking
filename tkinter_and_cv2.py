# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 18:05:57 2023

@author: ess305
"""

from tkinter import *
import cv2
from PIL import Image, ImageTk

def take_snapshot():
    print("ABC")
    
def video_loop():
    success, img = camera.read()
    if success:
        cv2.waitKey(1)
        # 顏色轉換: 從 B(BLUE), G(GREEN), R(RED) 轉成 R(RED), G(GREEN), B(BLUE), A(ALPHA)
        cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        
        # OpenCV 轉換 PIL.Image 格式
        current_image = Image.fromarray(cv2image)
        
        # 如果要在 tkinter 中顯示圖片，必須搭配 Pillow 函式庫的 ImageTk.Photoimage 建立圖片物件，再透過 Label 或 Canvas 顯示圖片
        imgtk = ImageTk.PhotoImage(image=current_image)
        panel.imagtk = imgtk
        panel.config(image=imgtk)
        
        root.after(1, video_loop)

camera = cv2.VideoCapture(0)
root = Tk()
root.title("opencv + tkinter")

panel = Label(root)
panel.pack(padx=10, pady=10)
root.config(cursor="arrow")
btn = Button(root, text="Like!", command = take_snapshot)
btn.pack(fill="both", expand=True, padx=10, pady=10)

video_loop()

root.mainloop()

camera.release()
cv2.destroyAllWindows()
