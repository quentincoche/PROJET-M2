'''
A simple Program for grabing video from basler camera and converting it to opencv img.
Tested on Basler acA1300-200uc (USB3, linux 64bit , python 3.5)

'''
from pypylon import pylon
import cv2

class Camera():
    
    def __init__(self):
        # conecting to the first available camera
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.camera.Open()
        #self.temp_exp=16.0
        #self.acquisition()
    
    def acquisition(self):
        self.camera.AcquisitionMode.SetValue('Continuous') #SingleFrame
        self.camera.PixelFormat.SetValue('Mono12')
        self.camera.GainAuto.SetValue("Continuous")
        self.camera.AcquisitionFrameRate.SetValue(60.0)
        self.camera.ExposureAuto.SetValue('Continuous')#Continuous, SingleFrame
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
                self.camera.ExposureTime.SetValue(self.temp_exp)
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