# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 11:24:25 2020

@author: OPTIQUE
"""

#import numpy as np
from pypylon import pylon
import cv2
import numpy as np

class Camera():
    def __init__(self):
        #self.temp_exp=50.0
        #self.auto_exposure()
        self.cap = cv2.VideoCapture(0)
        #self.acquisition()

    def acquisition(self):
        while(True):
            # Capture image par image
            self.cap.set(3, 5472)
            self.cap.set(4, 3648)
            ret, img = self.cap.read()
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE,0.75)
            #self.cap.set(cv2.CAP_PROP_EXPOSURE, -6)
            #img25=rescale_frame(img, 10)
            # Préparation de l'affichage de l'
            img=cv2.flip(img,0)
            #cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)
            #cv2.imshow('frame',img)
            #cv2.imwrite('image.png',img)
            # Lecture fps 
            #print("FPS=",self.cap.get(cv2.CAP_PROP_FPS))
            #print("EXP=",cap.get(cv2.CAP_PROP_EXPOSURE))
            #print("size : ",cap.get(3)," x ",cap.get(4))
            #print("size= ",cap.get(cv2.CAP_PROP_FRAME_WIDTH)," x ",cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            # affichage et saisie d'un code clavier
            #if cv2.waitKey(1) & 0xFF == 27:
                #break   
        # Ne pas oublier de fermer le flux et la fenetre
        self.cap.release()
        #cv2.destroyAllWindows()
        print('ok')
        return img
    
    def auto_exposure(self):
        exp_ok=False
        max=self.max_photo()
        while exp_ok == False:
            if max<=200:
                self.temp_exp=self.temp_exp*2.
                max=self.max_photo()
                print(self.temp_exp)
            elif max >=255:
                self.temp_exp=self.temp_exp/1.6
                max=self.max_photo()
                print(self.temp_exp)
            elif self.temp_exp>=10000000.0:
                exp_ok=True
                print('Exp time too big')
                break
            elif self.temp_exp<=16.0:
                exp_ok=True
                print('Exp time too short')
                break
            else:
                exp_ok=True
                break
                
    def max_photo(self):
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.camera.Open()
        self.camera.ExposureAuto.SetValue('Off')#Continuous, SingleFrame
        self.camera.AcquisitionMode.SetValue('SingleFrame')
        self.camera.ExposureTime.SetValue(self.temp_exp)
        self.camera.StartGrabbing()
        #converter = pylon.ImageFormatConverter()
        grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        #photo=converter.Convert(grabResult)
        pht=grabResult.GetArray()
        max_photo=np.amax(pht)
        grabResult.Release()
        self.camera.StopGrabbing()
        self.camera.Close()
        return max_photo