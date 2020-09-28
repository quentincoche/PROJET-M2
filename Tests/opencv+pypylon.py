'''
A simple Program for grabing video from basler camera and converting it to opencv img.
Tested on Basler acA1300-200uc (USB3, linux 64bit , python 3.5)

'''
from pypylon import pylon
import cv2
import numpy as np

class Camera():
    
    def __init__(self):
        # conecting to the first available camera
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.camera.Open()
        self.temp_exp=16.0
        self.acquisition()
    
    def acquisition(self):
        self.camera.AcquisitionMode.SetValue('Continuous') #SingleFrame
        self.camera.PixelFormat.SetValue('Mono12')
        self.camera.GainAuto.SetValue("Continuous")
        self.camera.AcquisitionFrameRate.SetValue(60.0)
        self.camera.ExposureAuto.SetValue('Off')#Continuous, SingleFrame
        self.camera.ExposureTime.SetValue(self.temp_exp)
        # Grabing Continusely (video) with minimal delay
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
        self.converter = pylon.ImageFormatConverter()
        
        
        while self.camera.IsGrabbing():
            self.grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if self.grabResult.GrabSucceeded():
                # Access the image data
                self.image = self.converter.Convert(self.grabResult)
                self.img = self.image.GetArray()
                self.auto_exposure()
                #Demande d'auto-exposition
                cv2.namedWindow('title', cv2.WINDOW_NORMAL)
                cv2.imshow('title', self.img)
                self.k = cv2.waitKey(1)
                if self.k == 27:
                    break
            self.grabResult.Release()
            
        #Printing technical data
        print("Using device ", self.camera.GetDeviceInfo().GetModelName())
        print("Matrice : ", self.grabResult.Width, " x ", self.grabResult.Height)
        print("Bit pixel : ", self.camera.PixelFormat.GetValue())
        print("Temps d'exposition : ", self.camera.ExposureTime.GetValue(), "µs")
        print("Exposition min : ",self.camera.ExposureTime.Min, "µs")
        print("Exposition max : ",self.camera.ExposureTime.Max, "µs")
        print("Gain : ", self.camera.Gain.GetValue())
        print("Frame rate : ",self.camera.AcquisitionFrameRate.GetValue())
        print(self.img)
        
       
    #def ending_acquisition(self):
        # Releasing the resource    
        self.camera.StopGrabbing()
        self.camera.Close()
        cv2.destroyAllWindows()
        
    def auto_exposure(self):
        exp_time_ok=False
        max_img=self.maximum(self.img)
        while exp_time_ok==False:
            if max_img <=3500:
                tps=round(self.camera.ExposureTime.Min*2.)
            elif max_img >=4095:
                tps=round(self.camera.ExposureTime.Min/1.5)
        else :
            exp_time_ok=True
            self.temp_exp=tps
            
        if self.temp_exp <=16:
            print("Temps d'exposition trop court")
        elif self.temp_exp>=10000000:
            print("Temps d'exposition trop haut")
        return(self.temp_exp)
    
    def maximum(self,liste):
        m=[]
        l=len(liste)
        for i in range (l):
            L=len(liste[i])
            for j in range (L):
                m.append(liste[i][j])
        print(max(m))
        return(max(m))
    
    def function(self):
        if self.camera.ExposureAuto.GetValue() == 'Off':
                x=input("Auto exposition ? (y ou n) :")
                if x=='y':
                    self.auto_exposure()
                else :
                    self.temp_exp=int(input("Temps d'exposition (µs) :"))