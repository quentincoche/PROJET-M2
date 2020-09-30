# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 09:22:21 2020

@author: Optique
"""
from pypylon import pylon
from PIL import Image as Img
from PIL import ImageTk
from tkinter import *
import cv2
import tkinter as tk
import time
import numpy as np


class Fenetre():
    cam0 = int(input("Port de périphérique USB de la caméra : "))
    def __init__(self, output_path = "./"):

        """Initialisation de la camera"""
        self.cap0 = cv2.VideoCapture(self.cam0) # Acquisition du flux vidéo des périphériques
        self.temp_exp=50.0
        self.auto_exposure()
        self.cap0.set(3, 5472) # Redéfinition de la taille du flux
        self.cap0.set(4, 3648) # Max (1920 par 1080)
        self.cap0.set(cv2.CAP_PROP_AUTO_EXPOSURE,0.75)
        
        """"Edition de l'interface"""
        self.window = tk.Tk()  #Réalisation de la fenêtre principale
        self.window.geometry("920x613")
         
        self.window.title("Beam analyzer Python")
        self.window.config(background="#FFFFFF") # Couleur de la fenêtre
        self.window.protocol('WM_DELETE_WINDOW', self.destructor)

        """"definition des proportions pour les frames"""
        #self.window.grid_columnconfigure(0, weight=1)
        #self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=8)
        self.window.grid_rowconfigure(1, weight=8)


        self.Interface() #Lance la fonction Interface
        self.video_loop()
    
##########################################    
    def Interface(self):
        #commandes gauche
        self.cmdleft = tk.Frame(self.window,padx=5,pady=5,bg="red")
        self.cmdleft.grid(row=1,column=0, sticky='NSEW')
        self.cmdleft.grid_columnconfigure(0, weight=1)
        self.cmdleft.grid_rowconfigure(0, weight=1)
        btnquit = tk.Button(self.cmdleft,text="Quitter",command = self.destructor)
        btnquit.grid(row=0,column=0,sticky="nsew")

        #commandes superieures
        self.cmdup = tk.Frame(self.window,padx=5,pady=5,bg="blue")
        self.cmdup.grid(row=0,column=1, sticky="NSEW")
        self.cmdup.grid_columnconfigure(0, weight=1)
        self.cmdup.grid_rowconfigure(0, weight=1)
        btnvideo = tk.Button(self.cmdup,text="Afficher video")
        btnvideo.grid(row=0,column=0,sticky="nsew")

        #cadre video
        self.display1 = tk.Label(self.window,padx=5,pady=5,bg="green")  # Initialisation de l'écran 1
        self.display1.grid(row=1,column=1,sticky="NSEW")
        self.display1.grid_columnconfigure(0,weight=1)
        self.display1.grid_rowconfigure(0,weight=1)

        
    
##########################################    
    
    def destructor(self):
        # Détruit les racines objet et arrête l'acquisition de toutes les sources
        print("[INFO] closing...")
        self.window.destroy() # Ferme la fenêtre

    def auto_exposure(self):
        self.cap0.release()  # lâche le flux vidéo
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.camera.Open()
        self.camera.ExposureTime.SetValue(self.temp_exp)
        self.camera.ExposureAuto.SetValue('Off')#Continuous, SingleFrame
        self.camera.AcquisitionMode.SetValue('SingleFrame')
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
        self.camera.Close()
        self.cap0 = cv2.VideoCapture(self.cam0)
        return
                
    def max_photo(self):
        self.camera.ExposureTime.SetValue(self.temp_exp)
        self.camera.StartGrabbing()
        grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        pht=grabResult.GetArray()
        max_photo=np.amax(pht)
        grabResult.Release()
        self.camera.StopGrabbing()
        return max_photo

    def video_loop(self):
        """ Récupère les images de la vidéo et l'affiche dans Tkinter"""
        ok0, frame0 = self.cap0.read() # lecture des images de la vidéo
        self.frame0 = frame0 #transformation de la variable en variable exploitable par toutes les fonctions
        self.frame=cv2.flip(self.frame0,0)
        self.im0 = Img.fromarray(self.frame) # Convertit l'image pour PIL    
        self.img0=self.im0.resize((960,540))
        imgtk0 = ImageTk.PhotoImage(image=self.img0) # Converti l'image pour Tkinter
        self.display1.imgtk = imgtk0 # ancrer imgtk afin qu'il ne soit pas supprimé par garbage-collector
        self.display1.config(image=imgtk0) # Montre l'image

        self.window.after(10, self.video_loop) # rappel la fonction après 10 millisecondes



root = Fenetre()
root.window.mainloop() # Lancement de la boucle principale