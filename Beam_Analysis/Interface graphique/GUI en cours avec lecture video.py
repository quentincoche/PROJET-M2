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


#La Classe Fenetre contient l'ensemble du programme

class Fenetre():
    cam0 = int(input("Port de périphérique USB de la caméra : "))
    propre=input('Veux-tu avoir une image propre (True/False) : ')
    def __init__(self, output_path = "./"): #Fonction d'initialisation du programme

        self.output_path = output_path  # chemin de sortie de la photo

        """Initialisation de la camera"""
        self.cap0 = cv2.VideoCapture(self.cam0) # Acquisition du flux vidéo des périphériques
        self.temp_exp=50.0 #Définition d'un temps d'exposition volontairement faible qui sera ajuster ensuite
        self.auto_exposure() #Lance le programme d'auto-exposition
        self.cap0.set(3, 5472) # Redéfinition de la taille du flux
        self.cap0.set(4, 3648) # Max (5472 par 3648)
        self.cap0.set(cv2.CAP_PROP_AUTO_EXPOSURE,0.75) #On utilise pas l'auto-exposition d'opencv
        
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
        #Fonction permettant de créer l'interface dans laquelle sera placé toutes les commandes et visualisation permettant d'utiliser le programme
        
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
        # Détruit les racines objet et arrête l'acquisition de toutes les sources
        print("[INFO] closing...")
        self.window.destroy() # Ferme la fenêtre

    def auto_exposure(self):
        #Fonction d''auto-exposition uniquement pour la caméra Basler actuellement

        self.cap0.release()  # lâche le flux vidéo
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())    #récupère la caméra par le biais de la bibliothèque Pylon
        self.camera.Open() #Ouvre la communication avec la caméra
        self.camera.ExposureTime.SetValue(self.temp_exp) #établi le temps d'exposition
        self.camera.ExposureAuto.SetValue('Off')#Continuous, SingleFrame
        self.camera.AcquisitionMode.SetValue('SingleFrame') #Utilise la caméra en mode photo
        
        exp_ok=False #Variable permettant de définir l'état de l'ajustement de l'exposition
        
        max=self.max_photo() #variable du max d'intensité de l'image

        while exp_ok == False: #Définit l'augmentation ou la diminution des valeurs d'exposition en fonction du max d'intensité de l'image
            if max<=150:
                self.temp_exp=self.temp_exp*2.
                max=self.max_photo()
                print(self.temp_exp)
            elif max >=250 :
                self.temp_exp=self.temp_exp/1.6
                max=self.max_photo()
                print(self.temp_exp)
            elif self.temp_exp>=40000.0:
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
        self.camera.Close() #Ferme la communication avec la caméra
        self.cap0 = cv2.VideoCapture(self.cam0) #Lance l'acquisition avec le module opencv
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
        if self.propre=="True":
            self.nettoyage()
        self.im0 = Img.fromarray(self.frame) # Convertit l'image pour PIL    
        self.img0=self.im0.resize((960,540))
        imgtk0 = ImageTk.PhotoImage(image=self.img0) # Converti l'image pour Tkinter
        self.display1.imgtk = imgtk0 # ancrer imgtk afin qu'il ne soit pas supprimé par garbage-collector
        self.display1.config(image=imgtk0) # Montre l'image
        self.histogram()

        self.window.after(10, self.video_loop) # rappel la fonction après 10 millisecondes

    def histogram(self):
        hist = cv2.calcHist([self.frame],[0],None,[256],[0,256])
        # Plot de hist.
        plt.plot(hist)
        plt.xlim([0,256])
        #Affichage.
        plt.show()
        return

    def capture(self):
        ts = datetime.datetime.now()
        filename = "image_{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # Construction du nom
        p = os.path.join(self.output_path, filename)  # construit le chemin de sortie
        self.im0.save(p, "PNG")  # Sauvegarde l'image sous format png
        print("[INFO] saved {}".format(filename))

    def nettoyage(self):
        #Test d'amélioration de l'image par binarisation d'Otsu
        print(self.propre)
        if self.propre=="False" :
            raise Exception()
        else :
            self.frame=cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            self.blur = cv2.GaussianBlur(self.frame,(5,5),0)
            ret3,self.frame = cv2.threshold(self.blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return
        


root = Fenetre()
root.window.mainloop() # Lancement de la boucle principale

 