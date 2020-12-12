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
        self.temp_exp=50.0
        self.acquisition()
    
    def acquisition(self):
        self.camera.Open()
        #self.camera.ExposureAuto.SetValue('On')#Continuous, SingleFrame
        #self.auto_exposure()
        self.camera.PixelFormat.SetValue('Mono8')
        self.camera.AcquisitionMode.SetValue('Continuous') #SingleFrame
        self.camera.GainAuto.SetValue("Continuous")
        self.camera.AcquisitionFrameRate.SetValue(60.0)
        #self.camera.ExposureTime.SetValue(self.temp_exp)
        # Grabing Continusely (video) with minimal delay
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
        self.converter = pylon.ImageFormatConverter()
        
        
        while self.camera.IsGrabbing():
            self.grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if self.grabResult.GrabSucceeded():
                # Access the image data
                self.image = self.converter.Convert(self.grabResult)
                self.img = self.image.GetArray()
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
        print("Max photo :", self.max_photo())
        print(self.img)
        
       
    #def ending_acquisition(self):
        # Releasing the resource    
        self.camera.StopGrabbing()
        self.camera.Close()
        cv2.destroyAllWindows()
        
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
        self.camera.StopGrabbing()
        self.camera.AcquisitionMode.SetValue('SingleFrame')
        self.camera.ExposureTime.SetValue(self.temp_exp)
        self.camera.StartGrabbing()
        converter = pylon.ImageFormatConverter()
        grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        photo=converter.Convert(grabResult)
        pht=photo.GetArray()
        max_photo=np.amax(pht)
        photo.Release()
        self.camera.StopGrabbing()
        return(max_photo)

Camera()