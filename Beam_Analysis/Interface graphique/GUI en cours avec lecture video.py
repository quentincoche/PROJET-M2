# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 09:22:21 2020

@author: Optique
"""

import tkinter as tk
from tkinter import *
import time

class Fenetre():
    
    def __init__(self, output_path = "./"):
        
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


         self.Interface() """Lance la fonction Interface"""
    
    
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






root = Fenetre()
root.window.mainloop() # Lancement de la boucle principale