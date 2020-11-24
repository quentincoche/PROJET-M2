import os

os.environ["PYLON_CAMEMU"] = "3"
import pypylon
from pypylon import genicam
from pypylon import pylon
import sys
import time
import cv2
import numpy as np
import tkinter as tk

class cameraCapture(tk.Frame):
    def __init__(self):
        t=time.time()
        self.img0 = []
        nodeFile = "NodeMap.pfs"
        self.windowName = 'title'
        self.temp_exp = 100.0

        try:
            # Create an instant camera object with the camera device found first.
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            self.camera.Open() #Ouvre la communication avec la caméra
            self.Model = self.camera.GetDeviceInfo().GetModelName()

            if self.Model == "acA1920-40uc":
                self.camera.PixelFormat.SetValue('Mono8')
                self.tps_exp_min = 50 
                self.pixel_size = 5.86 #microns (pixels carrés sur les baslers)
                self.pixel_max = 255

            elif self.Model == "acA5472-17um":
                self.camera.PixelFormat.SetValue('Mono12')
                self.tps_exp_min = 50 
                self.pixel_size = 2.4 #microns (pixels carrés sur les baslers)
                self.pixel_max = 4095

            else :
                print("Camera non reconnue")

            self.width = self.camera.Width.GetValue()
            self.height = self.camera.Height.GetValue()
            self.ratio = float(self.width/self.height)

            pylon.FeaturePersistence.Save(nodeFile, self.camera.GetNodeMap())

            # Print the model name of the camera.
            print("Using device ", self.camera.GetDeviceInfo().GetModelName())
            #print("Exposure time ", self.camera.ExposureTime.GetValue())
            #print("Pixels formats :", self.camera.PixelFormat.Symbolics)
            

            self.auto_exposure() #This line HAS TO STAY HERE :')         

            # converting to opencv bgr format
            self.converter = pylon.ImageFormatConverter()
            self.converter.OutputPixelFormat = pylon.PixelType_Mono16
            self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

            # According to their default configuration, the cameras are
            # set up for free-running continuous acquisition.
            #Grabbing continuously (video) with minimal delay
            #self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        except genicam.GenericException as e:
            # Error handling
            print("An exception occurred.", e.GetDescription())
            exitCode = 1

        temps=time.time()-t
        print("Temps acquisition caméra  : ", temps)

    def getFrame(self):
        try:
            self.grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException) #Récupère tous les flux de la caméra

            if self.grabResult.GrabSucceeded():
                image = self.converter.Convert(self.grabResult) # Access the openCV image data
                self.img0 = image.GetArray()
            else:
                print("Error: ", self.grabResult.ErrorCode)
    
            self.grabResult.Release()
            return self.img0
            
        except genicam.GenericException as e:
            # Error handling
            print("An exception occurred.", e.GetDescription())
            exitCode = 1

    def auto_exposure(self):
        """ Fonction dauto-exposition uniquement pour la caméra Basler actuellement """
        self.camera.Close()
        self.camera.Open()  #Need to open camera before can use camera.ExposureTime
        self.temp_exp =500
        self.camera.ExposureAuto.SetValue('Off')#Continuous, SingleFrame
        self.camera.ExposureTime.SetValue(self.temp_exp) #établi le temps d'exposition
        self.camera.AcquisitionMode.SetValue('Continuous') #Utilise la caméra en mode photo
        
        exp_ok=False #Variable permettant de définir l'état de l'ajustement de l'exposition
        
        max=self.max_photo() #variable du max d'intensité de l'image
        #print(max)

        while exp_ok == False: #Définit l'augmentation ou la diminution des valeurs d'exposition en fonction du max d'intensité de l'image
            if max<=self.pixel_max - 25:
                if self.temp_exp>=10000000.0:
                    exp_ok=True
                    print('Exp time too big')
                    break
                else :
                    self.temp_exp=self.temp_exp*2.
                    max=self.max_photo()
                    #print(max)
                    self.camera.ExposureTime.SetValue(self.temp_exp)
            elif max >=self.pixel_max :
                if self.temp_exp<=self.tps_exp_min:
                    exp_ok=True
                    print('Exp time too short')
                    break
                else: 
                    self.temp_exp=self.temp_exp/1.3
                    max=self.max_photo()
                    #print(max)
                    self.camera.ExposureTime.SetValue(self.temp_exp)
            else:
                exp_ok=True
                break
        
        self.camera.ExposureTime.SetValue(self.temp_exp)
        self.camera.StopGrabbing() #Arrête l'acquisition d'information de la caméra
        self.camera.Close() #Ferme la communication avec la caméra
        self.camera.Open()  #Need to open camera before can use camera.ExposureTime
            
        self.camera.ExposureTime.SetValue(self.temp_exp)
        print("Exposure time ", self.camera.ExposureTime.GetValue())
        print("valeur max de pixel", max)
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        return
    
    def max_photo(self):
        """" Fonction permettant de retourner le max d'intensité sur l'image """
        self.camera.StopGrabbing() #Arrête l'acquisition d'information de la caméra
        self.camera.AcquisitionMode.SetValue('SingleFrame') #Utilise la caméra en mode photo
        self.camera.ExposureTime.SetValue(self.temp_exp)
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) #Permet la récupération des infos de la caméra
        grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException) #Récupère tous les flux de la caméra
        pht=grabResult.GetArray() #Transforme l'image en matrice
        img=cv2.blur(pht,(5,5))
        max_photo=np.amax(img) #cherche la valeur max de la matrice
        grabResult.Release() #Relache le flux
        self.camera.StopGrabbing() #Arrête l'acquisition d'information de la caméra
        return max_photo #Renvoie la valeur du max

if __name__ == "__main__":
    testWidget = cameraCapture()
    while testWidget.camera.IsGrabbing():
        #input("Press Enter to continue...")
        testWidget.getFrame()

        #If window has been closed using the X button, close program
        # getWindowProperty() returns -1 as soon as the window is closed
        if cv2.getWindowProperty(testWidget.windowName, 0) < 0:
            cv2.destroyAllWindows()
            break
        if testWidget.k == 27: #If press ESC key
            print('ESC')
            cv2.destroyAllWindows()
            break