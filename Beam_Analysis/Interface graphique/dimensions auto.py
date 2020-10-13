#!/usr/bin/python
# -*- coding: utf-8 -*-
 
from tkinter import *
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
 
class Application:
    def __init__(self):
        self.root=Tk()
        self.image = cv2.imread('C:/Users/Optique/Documents/GitHub/PROJET-M2/Beam_Analysis/Interface graphique/image.png',0)
        #cv2.imshow('fenetre',self.image)
        self.x, self.y = self.image.shape
        self.can = Canvas(self.root,width=self.x,height=self.y,bg='white')
        self.can.bind("<Configure>",self.resize)
        self.can.pack(expand=Y,fill=BOTH)
 
    def resize(self,event):
        try:
            self.can.delete(self.can.image)
        except:
            pass
        self.img = self.image.resize((event.width,event.height))
        self.mon_image = ImageTk.PhotoImage(self.img)
        self.can.image = self.can.create_image(0, 0, image=self.mon_image, anchor=NW)
 
app=Application()
app.root.mainloop()