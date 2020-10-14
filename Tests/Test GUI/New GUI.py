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
from threading import Thread
import time #Bibliothèque permettant d'utiliser l'heure de l'ordinateur
import datetime #Bibliothèque permettant de récupérer la date
import os #Bibliothèque permettant de communiquer avec l'os et notamment le "path"
import numpy as np #Bibliothèque de traitement des vecteurs et matrice
import matplotlib.pyplot as plt #Bibliothèque d'affichage mathématiques
from statistics import mean
import oneCameraCapture
import Img_Traitement


#####################################################################
#                                                                   #
#           Programme d'interfaçage de faisceaux                    #
#                                                                   #
#####################################################################


# La Classe Fenetre contient l'ensemble du programme #


class Fenetre(Thread):

    def __init__(self): #Fonction d'initialisation du programme

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

        self.display()
        self.flux_cam()
        self.Interface() #Lance la fonction Interface
        self.t1.update()
        

    def Interface(self):
        """ Fonction permettant de créer l'interface dans laquelle sera placé toutes les commandes et visualisation permettant d'utiliser le programme """
        
        #commandes gauche
        self.cmdleft = tk.Frame(self.window,padx=5,pady=5,bg="red")
        self.cmdleft.grid(row=1,column=0, sticky='NSEW')
        self.cmdleft.grid_columnconfigure(0, weight=1)
        self.cmdleft.grid_rowconfigure(0, weight=1)
        btncap = tk.Button(self.cmdleft,text="Capture",command=self.t1.capture)
        btncap.grid(row=0,column=0,sticky="nsew")
        btnquit = tk.Button(self.cmdleft,text="Quitter",command = self.destructor)
        btnquit.grid(row=1,column=0,sticky="nsew")
        
        #commandes superieures
        self.cmdup = tk.Frame(self.window,padx=5,pady=5,bg="blue")
        self.cmdup.grid(row=0,column=1, sticky="NSEW")
        self.cmdup.grid_columnconfigure(0, weight=1)
        self.cmdup.grid_rowconfigure(0, weight=1)
        btnvideo = tk.Button(self.cmdup,text="Traitement video", command=self.t1.video_tool)
        btnvideo.grid(row=0,column=0,sticky="nsew")
        btnexp = tk.Button(self.cmdup,text="Réglage auto temps exp", command=self.t1.exp)
        btnexp.grid(row=0,column=1,sticky="nsew")

    def display(self):
        #cadre video
        self.display1 = tk.Canvas(self.window,bg="green")  # Initialisation de l'écran 1
        self.display1.grid(row=1,column=1,sticky="NSEW")
        self.display1.grid_columnconfigure(0,weight=1)
        self.display1.grid_rowconfigure(0,weight=1)

    def flux_cam(self):
        self.t1=camera(self.window, self.display1) #boucle la fonction d'acquisition de la caméra
        self.t1.start()
    
    def destructor(self):
        """ Détruit les racines objet et arrête l'acquisition de toutes les sources """
        print("[INFO] closing...")
        self.window.destroy() # Ferme la fenêtre



class camera(Thread):

    def __init__(self, window, display1, output_path = "./"):
        Thread.__init__(self)
        self.output_path = output_path  # chemin de sortie de la photo
        self.window=window
        self.display1=display1
        self.vid = oneCameraCapture.cameraCapture()
        self.trmt = Img_Traitement.Traitement()

        self.delay=15


    def update(self):
        #Get a frame from cameraCapture
        self.frame0 = self.vid.getFrame() #This is an array
        self.frame=cv2.flip(self.frame0,0)

        #https://stackoverflow.com/questions/48121916/numpy-resize-rescale-image/48121996
        frame = cv2.resize(self.frame, dsize=(1000, 600), interpolation=cv2.INTER_CUBIC)

        #OpenCV bindings for Python store an image in a NumPy array
        #Tkinter stores and displays images using the PhotoImage class
        # Use PIL (Pillow) to convert the NumPy ndarray to a PhotoImage
        self.photo = ImageTk.PhotoImage(image = Img.fromarray(frame))
        self.display1.create_image(500,300,image=self.photo)

        self.window.after(self.delay, self.update)

    def capture(self):
        """ Fonction permettant de capturer une image et de l'enrigistré avec l'horodatage """
        ts = datetime.datetime.now()
        filename = "image_{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # Construction du nom
        p = os.path.join(self.output_path, filename)  # construit le chemin de sortie
        self.frame.save(p, "PNG")  # Sauvegarde l'image sous format png
        print("[INFO] saved {}".format(filename))

    def video_tool(self):
        thread2 = self.trmt.traitement(self.frame)
        thread2.start()

    def exp(self):
        self.exposure=self.vid.auto_exposure()

    

        

root = Fenetre()
root.window.mainloop() # Lancement de la boucle principale