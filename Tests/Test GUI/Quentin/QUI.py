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
import oneCameraCapture_q as oneCameraCapture
import Img_Traitement_q as Img_Traitement


#####################################################################
#                                                                   #

#           Programme d'interfaçage de faisceaux                    #
#                                                                   #
#####################################################################


# La Classe Fenetre contient l'ensemble du programme #


class Fenetre(Thread):

    def __init__(self, output_path = "./"): #Fonction d'initialisation du programme

        Thread.__init__(self)

        self.vid = oneCameraCapture.cameraCapture()
        self.trmt = Img_Traitement.Traitement()
        self.output_path = output_path  # chemin de sortie de la photo

        """"Edition de l'interface"""
        self.window = tk.Tk()  #Réalisation de la fenêtre principale
        self.window.geometry("920x613") #taille de la fenetre
         
        self.window.title("Beam analyzer Python")
        self.window.config(background="#FFFFFF") # Couleur de la fenêtre
        self.window.protocol('WM_DELETE_WINDOW', self.destructor) #La croix de la fenetre va fermer le programme

        """"definition des proportions pour les frames"""
        #self.window.grid_columnconfigure(0, weight=1)
        #self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=3)
        self.window.grid_columnconfigure(2,weight=2)
        self.window.grid_rowconfigure(1, weight=5)
        
        """Definition de certaines variables nécessaires au demarrage de l'interface"""
        self.cX = IntVar()
        self.cY = IntVar()
        self.ellipse_width = DoubleVar()
        self.ellipse_height = DoubleVar()
        self.ellipse_angle =DoubleVar()
        self.Screen_x = 1500
        self.Screen_y = 1000
        self.Screen2_x = 750
        self.Screen2_y = 750
        self.delay=15
        self.frame2=[]

        self.display()
        self.Interface() #Lance la fonction Interface
        self.flux_cam()


    #########################
    #   Partie Interface    # 
    #########################       


    def Interface(self):
        """ Fonction permettant de créer l'interface dans laquelle sera placé toutes les commandes et visualisation permettant d'utiliser le programme """
        
        #commandes gauche
        self.cmdleft = tk.Frame(self.window,padx=5,pady=5,bg="gray")
        self.cmdleft.grid(row=1,column=0, sticky='NSEW')
        btncap = tk.Button(self.cmdleft,text="Capture",command=self.capture)
        btncap.grid(row=0,column=0,sticky="nsew")
        btnquit = tk.Button(self.cmdleft,text="Quitter",command = self.destructor)
        btnquit.grid(row=1,column=0,sticky="nsew")
        
        #commandes superieures
        self.cmdup = tk.Frame(self.window,padx=5,pady=5,bg="gray")
        self.cmdup.grid(row=0,column=1, sticky="NSEW")
        btnvideo = tk.Button(self.cmdup,text="Traitement video", command=self.video_tool)
        btnvideo.grid(row=0,column=0,sticky="nsew")
        btnexp = tk.Button(self.cmdup,text="Réglage auto temps exp", command=self.exp)
        btnexp.grid(row=0,column=1,sticky="nsew")

    def display(self):
        #cadre video
        self.display1 = tk.Canvas(self.window, width=self.Screen_x,height=self.Screen_y)  # Initialisation de l'écran 1
        self.display1.grid(row=1,column=1,sticky="NSW")
        self.Screen_x = self.display1.winfo_width()
        self.Screen_y = self.display1.winfo_height()

        #cadre traitement
        self.title_display2 = tk.Label(self.window,text="Fit ellipse",bg="gray")
        self.title_display2.grid(row=0,column=2,sticky="NSEW")
        self.display2 = tk.Canvas(self.window, width=self.Screen2_x, height=self.Screen2_y, bg="green")  # Initialisation de l'écran 1
        self.display2.grid(row=1,column=2,sticky="NSE")
        self.Screen2_x = self.display2.winfo_width()
        self.Screen2_y = self.display2.winfo_height()

        #zone affichage résultats
        self.results = tk.Frame(self.window,padx=5,pady=5,bg="gray")
        self.results.grid(row=2,column=2,sticky="NSE")
        #barycentres
        self.label01 = tk.Label(self.results,text="barycentre X = ")
        self.label01.grid(row=0,column=0,sticky="nsew")
        self.label1 = tk.Label(self.results,textvariable=self.cX)
        self.label1.grid(row=0,column=1,sticky="nsew")
        self.label02 = tk.Label(self.results,text="barycentre Y = ")
        self.label02.grid(row=1,column=0,sticky="nsew")
        self.label2 = tk.Label(self.results,textvariable=self.cY)
        self.label2.grid(row=1,column=1,sticky="nsew")
        
        #parametres ellipse
        self.label03 = tk.Label(self.results,text="Grand axe ellipse = ")
        self.label03.grid(row=2,column=0,sticky="nsew")
        self.label3 = tk.Label(self.results,textvariable=self.ellipse_width)
        self.label3.grid(row=2,column=1,sticky="nsew")
        self.label04 = tk.Label(self.results,text="Petit axe ellipse = ")
        self.label04.grid(row=3,column=0,sticky="nsew")
        self.label4 = tk.Label(self.results,textvariable=self.ellipse_height)
        self.label4.grid(row=3,column=1,sticky="nsew")
        self.label05 = tk.Label(self.results,text="Angle ellipse = ")
        self.label05.grid(row=4,column=0,sticky="nsew")
        self.label5 = tk.Label(self.results,textvariable=self.ellipse_angle)
        self.label5.grid(row=4,column=1,sticky="nsew")

    def destructor(self):
        """ Détruit les racines objet et arrête l'acquisition de toutes les sources """
        print("[INFO] closing...")
        self.window.destroy() # Ferme la fenêtre


    #####################
    #   Partie Camera   # 
    #####################


    def flux_cam(self):
        self.t1=Thread(target=self.update(), args=(self.window, self.display1, self.Screen_x, self.Screen_y)) #boucle la fonction d'acquisition de la caméra
        self.t1.start()

    def update(self):
        #Get a frame from cameraCapture
        self.frame0 = self.vid.getFrame() #This is an array
        self.frame=cv2.flip(self.frame0,0)

        #Get display size
        self.Screen_x = self.display1.winfo_width()
        self.Screen_y = self.display1.winfo_height()
        r = float(self.Screen_x/self.Screen_y)

        #Get a frame from cameraCapture
        ratio = self.vid.ratio
        #keep ratio
        if r > ratio:
            self.Screen_x = int(round(self.display1.winfo_height()*ratio))
        elif r < ratio:
            self.Screen_y = int(round(self.display1.winfo_width()/ratio))

        frame = cv2.resize(self.frame, dsize=(self.Screen_x,self.Screen_y), interpolation=cv2.INTER_AREA)

        #OpenCV bindings for Python store an image in a NumPy array
        #Tkinter stores and displays images using the PhotoImage class
        # Use PIL (Pillow) to convert the NumPy ndarray to a PhotoImage
        self.photo = ImageTk.PhotoImage(image = Img.fromarray(frame))
        self.display1.create_image(self.Screen_x/2,self.Screen_x/(2*ratio),image=self.photo)

        self.window.after(self.delay, self.update)

    def capture(self):
        """ Fonction permettant de capturer une image et de l'enrigistré avec l'horodatage """
        ts = datetime.datetime.now()
        filename = "image_{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # Construction du nom
        p = os.path.join(self.output_path, filename)  # construit le chemin de sortie
        self.frame.save(p, "PNG")  # Sauvegarde l'image sous format png
        print("[INFO] saved {}".format(filename))

    def video_tool(self):
        self.t2 = Thread(target=self.disp_traitement)
        self.t2.start()

    def disp_traitement(self):
        self.frame2, self.ellipse, self.baryX, self.baryY = self.trmt.traitement(self.frame)
        self.affich_traitement()
    
    def affich_traitement(self):
        #Get display size
        self.Screen2_x = self.display2.winfo_width()
        self.Screen2_y = self.display2.winfo_height()
        r = float(self.Screen2_x/self.Screen2_y)

        #Get a frame from cameraCapture
        ratio = self.frame2.shape[1]/self.frame2.shape[0]
        #keep ratio
        if r > ratio:
            self.Screen2_x = int(round(self.display2.winfo_height()*ratio))
        elif r < ratio:
            self.Screen2_y = int(round(self.display2.winfo_width()/ratio))

        frame = cv2.resize(self.frame2, dsize=(self.Screen2_x,self.Screen2_y), interpolation=cv2.INTER_AREA)
        self.photo2 = ImageTk.PhotoImage(image = Img.fromarray(frame))
        self.display2.create_image(self.Screen2_x/2,self.Screen2_x/(2*ratio),image=self.photo2)

        #pour affichage des parametres
        self.cX.set(self.baryX)
        self.cY.set(self.baryY)
        self.ellipse_width.set(int(self.ellipse[1][1]))
        self.ellipse_height.set(int(self.ellipse[1][0]))
        self.ellipse_angle.set(int(self.ellipse[2]))
        self.window.after(self.delay, self.affich_traitement)

    def exp(self):
        self.exposure=self.vid.auto_exposure()

    

        

root = Fenetre()
root.window.mainloop() # Lancement de la boucle principale