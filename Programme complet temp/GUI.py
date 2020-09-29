# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 09:22:21 2020

@author: Optique
"""

import tkinter as tk 
#import cv2
from tkinter import Tk
import time
from objet_camera import *
cam = Camera()
class Application():
    
    def __init__(self, output_path = "./"):
        
        #Edition de l'interface
         self.window = tk.Tk()  #Réalisation de la fenêtre principale
         self.window.title("Beam analyzer Python")
         self.window.config(background="#FFFFFF") # Couleur de la fenêtre
         self.window.protocol('WM_DELETE_WINDOW', self.destructor)
        #affichage d'une image sur la fenetre video
        
         
         self.Interface() # Lance la fonction Interface
         #self.video_loop() # Lance la fonction video_loop
    
    
##########################################    
    def Interface(self):
        for c in self.window.winfo_children():
            c.destroy()
        self.display1 = tk.Label(self.window)  # Initialisation de l'écran 1
        self.display1.grid(row=2, column=2, columnspan=4, padx=10)
        
        # Initialisation du cadre Menu contenant les différents boutons
        self.Frame1 = tk.Frame(self.window, borderwidth=2, relief='flat')
        self.Frame1.grid(row=2, column=1, rowspan=1, padx=5, pady=5)
        titre = tk.Label(self.Frame1, text="Menu")
        titre.grid(row=0)
        self.c0=tk.IntVar()
        
        #Boutons du menu
        bouton_coupes = tk.Button(self.Frame1, text="Coupes XY", relief="groove")
        bouton_coupes.grid(row=1)
        bouton_fit_ellipse = tk.Button(self.Frame1, text="Fit ellipse", relief="groove")
        bouton_fit_ellipse.grid(row=2)
        bouton_Gauss2D = tk.Button(self.Frame1, text="Fit Gauss 2D", relief="groove")
        bouton_Gauss2D.grid(row=3)
        bouton_toto = tk.Button(self.Frame1, text="toto", relief="groove")
        bouton_toto.grid(row=4)
        bouton_titi = tk.Button(self.Frame1, text="titi", relief="groove")
        bouton_titi.grid(row=5)
        bouton_tata = tk.Button(self.Frame1, text="tata", relief="groove")
        bouton_tata.grid(row=6)
        bouton_align = tk.Button(self.Frame1,text="Alignement", relief="groove")
        bouton_align.grid(row=7)
        bouton_hold = tk.Button(self.Frame1, text="HOLD", relief="groove")
        bouton_hold.grid(row=8)
        bouton_quit=tk.Button(self.Frame1, text="Fermer", command=self.destructor)
        bouton_quit.grid(row=11, column=0)
        
        #Initialisation du bandeau pour lancer la video/faire une capture...
        self.Frame2 = tk.Frame(self.window, relief = "flat")
        self.Frame2.grid(row=1, column=2)
        
        #Boutons du bandeau
        bouton_affichvideo = tk.Button(self.Frame2, text="Affichage video", relief="groove", command=cam.acquisition())
        bouton_affichvideo.grid(row=1, column=1)
        bouton_capture = tk.Button(self.Frame2, text="Capture", relief="groove")
        bouton_capture.grid(row=1, column=2)
        self.auto = tk.IntVar()
        check_expo = tk.Checkbutton(self.Frame2, text="auto exposition", variable=self.auto, onvalue = 1, offvalue = 0)
        check_expo.grid(row=1, column=3)
        
        
        #Initialisation de la Frame coupe X
        self.Frame3 = tk.Frame(self.window, relief = "flat")
        self.Frame3.grid(row=1, column=3)
        
            
##########################################     
    #def streaming(self):
        
    
##########################################    
    #def video_loop(self):
        
    
##########################################    
    
    def destructor(self):
        # Détruit les racines objet et arrête l'acquisition de toutes les sources
        print("[INFO] closing...")
        self.window.destroy() # Ferme la fenêtre
        time.sleep(5)





root = Application()

root.window.mainloop() # Lancement de la boucle principale
