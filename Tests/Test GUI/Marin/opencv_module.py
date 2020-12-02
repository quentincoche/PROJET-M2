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
        self.pixel_max = 255
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 6400)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 4800)
        self.cap.set(5,30)
        w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(w,h)
        #self.auto_exposure()


    def capture(self):
        # Capture frame-by-frame
        ret, frame = self.cap.read()
        self.width, self.height = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        #print(self.width, self.height)
        self.ratio = float(self.width/self.height)


        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #self.cap.release()
        
        return gray

    def auto_exposure(self):
        """ Fonction d'auto-exposition uniquement pour la caméra Basler actuellement """
        self.temp_exp =-12

        exp_ok=False #Variable permettant de définir l'état de l'ajustement de l'exposition
        
        max=self.max_photo() #variable du max d'intensité de l'image
        #print(max)

        while exp_ok == False: #Définit l'augmentation ou la diminution des valeurs d'exposition en fonction du max d'intensité de l'image
            if max<=self.pixel_max - 25:
                if self.temp_exp>=0:
                    exp_ok=True
                    print('Exp time too big')
                    break
                else :
                    self.temp_exp=self.temp_exp+2
                    max=self.max_photo()
                    #print(max)
                    self.cap.set(cv2.CAP_PROP_EXPOSURE, self.temp_exp)
            elif max >=self.pixel_max :
                if self.temp_exp<=-13:
                    exp_ok=True
                    print('Exp time too short')
                    break
                else: 
                    self.temp_exp=self.temp_exp-1
                    max=self.max_photo()
                    #print(max)
                    self.cap.set(cv2.CAP_PROP_EXPOSURE, self.temp_exp)
            else:
                exp_ok=True
                break
        
        self.cap.set(cv2.CAP_PROP_EXPOSURE, self.temp_exp)
            
        print("Exposure time ", self.temp_exp)
        print("valeur max de pixel", max)
        return
    
    def max_photo(self):
        """" Fonction permettant de retourner le max d'intensité sur l'image """
        self.cap.set(cv2.CAP_PROP_EXPOSURE, self.temp_exp)
        ret, image = self.cap.read()
        frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        img=cv2.blur(frame,(5,5))
        max_photo=np.amax(img) #cherche la valeur max de la matrice

        return max_photo #Renvoie la valeur du max