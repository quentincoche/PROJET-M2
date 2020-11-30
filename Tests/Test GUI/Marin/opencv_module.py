import sys
import os
import time
import numpy as np
import cv2
from PIL import Image as Img #Bibliothèque de traitement d'image
from PIL import ImageTk
import tkinter as tk


class openCamera():

    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Cannot open camera")
            exit()


    def capture(self):
        # Capture frame-by-frame
        ret, self.frame = self.cap.read()
        self.width, self.height = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        #print(self.width, self.height)
        self.ratio = float(self.width/self.height)


        # Our operations on the frame come here
        self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        
        return self.gray
    

