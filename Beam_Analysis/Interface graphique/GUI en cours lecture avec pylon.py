# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 09:22:21 2020

@author: Optique
"""
from pypylon import pylon #Bibliothèque Basler d'interfaçage de la caméra
from PIL import Image as Img #Bibliothèque de traitement d'image
from PIL import ImageTk
from tkinter import * #Bibliothèque de GUI
import cv2 #Bibliothèque d'interfaçage de caméra et de traitement d'image
import tkinter as tk
import time #Bibliothèque permettant d'utiliser l'heure de l'ordinateur
import datetime #Bibliothèque permettant de récupérer la date
import os #Bibliothèque permettant de communiquer avec l'os et notamment le "path"
import numpy as np #Bibliothèque de traitement des vecteurs et matrice
import matplotlib.pyplot as plt #Bibliothèque d'affichage mathématiques

#####################################################################
#                                                                   #
#           Programme d'interfaçage de faisceaux                    #
#                                                                   #
#####################################################################


# La Classe Fenetre contient l'ensemble du programme #

class Fenetre():
    def __init__(self, output_path = "./"): #Fonction d'initialisation du programme

        self.output_path = output_path  # chemin de sortie de la photo

        """Initialisation de la camera"""
        
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.temp_exp=50.0
        self.camera.Open()
        self.camera.ExposureAuto.SetValue('Off')#Continuous, SingleFrame
        #self.auto_exposure()
        self.camera.PixelFormat.SetValue('Mono12')
        self.camera.AcquisitionMode.SetValue('Continuous') #SingleFrame
        self.camera.GainAuto.SetValue("Continuous")
        self.camera.AcquisitionFrameRate.SetValue(60.0)
        self.camera.ExposureTime.SetValue(self.temp_exp)
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
        self.converter = pylon.ImageFormatConverter()
        
        """"Edition de l'interface"""
        self.window = tk.Tk()  #Réalisation de la fenêtre principale
        self.window.geometry("920x613") #taille de la fenetre
         
        self.window.title("Beam analyzer Python")
        self.window.config(background="#FFFFFF") # Couleur de la fenêtre
        self.window.protocol('WM_DELETE_WINDOW', self.destructor) #La croix de la fenetre va fermer le programme

        """"definition des proportions pour les frames"""
        #self.window.grid_columnconfigure(0, weight=1)
        #self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=8)
        self.window.grid_rowconfigure(1, weight=8)


        self.Interface() #Lance la fonction Interface
        self.video_loop() #lance la fonction d'acquisition de la caméra
    
##########################################    
    def Interface(self):
        """ Fonction permettant de créer l'interface dans laquelle sera placé toutes les commandes et visualisation permettant d'utiliser le programme """
        
        #commandes gauche
        self.cmdleft = tk.Frame(self.window,padx=5,pady=5,bg="red")
        self.cmdleft.grid(row=1,column=0, sticky='NSEW')
        self.cmdleft.grid_columnconfigure(0, weight=1)
        self.cmdleft.grid_rowconfigure(0, weight=1)
        btnquit = tk.Button(self.cmdleft,text="Quitter",command = self.destructor)
        btnquit.grid(row=1,column=0,sticky="nsew")
        btncap = tk.Button(self.cmdleft,text="Capture",command=self.capture)
        btncap.grid(row=0,column=0,sticky="nsew")

        #commandes superieures
        self.cmdup = tk.Frame(self.window,padx=5,pady=5,bg="blue")
        self.cmdup.grid(row=0,column=1, sticky="NSEW")
        self.cmdup.grid_columnconfigure(0, weight=1)
        self.cmdup.grid_rowconfigure(0, weight=1)
        btnvideo = tk.Button(self.cmdup,text="Afficher video")
        btnvideo.grid(row=0,column=0,sticky="nsew")
        btnexp = tk.Button(self.cmdup,text="Réglage auto temps exp",command=self.auto_exposure)
        btnexp.grid(row=0,column=1,sticky="nsew")

        #cadre video
        self.display1 = tk.Label(self.window,padx=5,pady=5,bg="green")  # Initialisation de l'écran 1
        self.display1.grid(row=1,column=1,sticky="NSEW")
        self.display1.grid_columnconfigure(0,weight=1)
        self.display1.grid_rowconfigure(0,weight=1)

        
    
##########################################    
    
    def destructor(self):
        """ Détruit les racines objet et arrête l'acquisition de toutes les sources """
        print("[INFO] closing...")
        self.window.destroy() # Ferme la fenêtre

    def auto_exposure(self):
        """ Fonction d''auto-exposition uniquement pour la caméra Basler actuellement """
        self.camera.AcquisitionMode.SetValue('SingleFrame') #Utilise la caméra en mode photo
        exp_ok=False #Variable permettant de définir l'état de l'ajustement de l'exposition
        
        max=self.max_photo() #variable du max d'intensité de l'image

        while exp_ok == False: #Définit l'augmentation ou la diminution des valeurs d'exposition en fonction du max d'intensité de l'image
            if max<=150:
                self.temp_exp=self.temp_exp*2.
                max=self.max_photo()
                print(self.temp_exp)
                self.camera.ExposureTime.SetValue(self.temp_exp)
            elif max >=250 :
                self.temp_exp=self.temp_exp/1.8
                max=self.max_photo()
                print(self.temp_exp)
                self.camera.ExposureTime.SetValue(self.temp_exp)
            elif self.temp_exp>=40000.0:
                exp_ok=True
                print('Exp time too big')
                break
            elif self.temp_exp<=100:
                exp_ok=True
                print('Exp time too short')
                break
            else:
                exp_ok=True
                break
        return
                
    def max_photo(self):
        """" Fonction permettant de retourner le max d'intensité sur l'image """
        self.camera.ExposureTime.SetValue(self.temp_exp)
        self.camera.StartGrabbing() #Permet la récupération des infos de la caméra
        grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException) #Récupère tous les flux de la caméra
        pht=grabResult.GetArray() #Transforme l'image en matrice
        max_photo=np.amax(pht) #cherche la valeur max de la matrice
        grabResult.Release() #Relache le flux
        self.camera.StopGrabbing() #Arrête l'acquisition d'information de la caméra
        return max_photo #Renvoie la valeur du max

    def video_loop(self):
        while self.camera.IsGrabbing():
            self.grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if self.grabResult.GrabSucceeded():
                # Access the image data
                self.image = self.converter.Convert(self.grabResult)
                self.img = self.image.GetArray()
            self.grabResult.Release()

    def capture(self):
        """ Fonction permettant de capturer une image et de l'enrigistré avec l'horodatage """
        ts = datetime.datetime.now()
        filename = "image_{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # Construction du nom
        p = os.path.join(self.output_path, filename)  # construit le chemin de sortie
        self.im0.save(p, "PNG")  # Sauvegarde l'image sous format png
        print("[INFO] saved {}".format(filename))
        


root = Fenetre()
root.window.mainloop() # Lancement de la boucle principale