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
import oneCameraCapture
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
        self.vid = oneCameraCapture.cameraCapture()

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

        self.Screen_x = 1200
        self.Screen_y = 800

        self.Interface() #Lance la fonction Interface
        self.delay=15
        #self.vid.__init__()
        #self.update() #boucle la fonction d'acquisition de la caméra
    
##########################################    
    def Interface(self):
        """ Fonction permettant de créer l'interface dans laquelle sera placé toutes les commandes et visualisation permettant d'utiliser le programme """
        
        #commandes gauche
        self.cmdleft = tk.Frame(self.window,padx=5,pady=5,bg="red")
        self.cmdleft.grid(row=1,column=0, sticky='NSEW')
        self.cmdleft.grid_columnconfigure(0, weight=1)
        self.cmdleft.grid_rowconfigure(0, weight=1)
        btncap = tk.Button(self.cmdleft,text="Capture",command=self.capture)
        btncap.grid(row=0,column=0,sticky="nsew")
        btnquit = tk.Button(self.cmdleft,text="Quitter",command = self.destructor)
        btnquit.grid(row=1,column=0,sticky="nsew")
        
        #commandes superieures
        self.cmdup = tk.Frame(self.window,padx=5,pady=5,bg="blue")
        self.cmdup.grid(row=0,column=1, sticky="NSEW")
        self.cmdup.grid_columnconfigure(0, weight=1)
        self.cmdup.grid_rowconfigure(0, weight=1)
        btnvideo = tk.Button(self.cmdup,text="Afficher video")
        btnvideo.grid(row=0,column=0,sticky="nsew")
        btnexp = tk.Button(self.cmdup,text="Réglage auto temps exp", command=self.vid.auto_exposure)
        btnexp.grid(row=0,column=1,sticky="nsew")

        #cadre video
        
        self.display1 = tk.Canvas(self.window, width=self.Screen_x,height=self.Screen_y, bg="green")  # Initialisation de l'écran 1
        self.display1.bind("<Configure>",self.auto_size)
        self.display1.grid(row=1,column=1,sticky="NSEW")
        self.display1.grid_columnconfigure(0,weight=1)
        self.display1.grid_rowconfigure(0,weight=1)

        
    
##########################################    
    
    def destructor(self):
        """ Détruit les racines objet et arrête l'acquisition de toutes les sources """
        print("[INFO] closing...")
        self.window.destroy() # Ferme la fenêtre

    def auto_size(self,event):
        """redimensionnement de l'image pour correspondre à la taille de la fenêtre"""
        frame = self.vid.getFrame() #This is an array
        try:
            self.display1.delete(self.display1.image)
        except:
            pass
        self.photo=cv2.resize(frame,dsize=(event.width,event.height), interpolation=cv2.INTER_CUBIC) 
        #OpenCV bindings for Python store an image in a NumPy array
        #Tkinter stores and displays images using the PhotoImage class
        # Use PIL (Pillow) to convert the NumPy ndarray to a PhotoImage
        self.photo = ImageTk.PhotoImage(image = Img.fromarray(frame))
        self.display1.create_image(event.width/2,event.height/2,image=self.photo)

        self.window.after(self.delay, self.auto_size)
    # def update(self):
    #     #Get a frame from cameraCapture
    #     frame = self.vid.getFrame() #This is an array
    #     #https://stackoverflow.com/questions/48121916/numpy-resize-rescale-image/48121996
    #     frame = cv2.resize(frame, dsize=(Screen_x, Screen_Y), interpolation=cv2.INTER_CUBIC)

    #     #OpenCV bindings for Python store an image in a NumPy array
    #     #Tkinter stores and displays images using the PhotoImage class
    #     # Use PIL (Pillow) to convert the NumPy ndarray to a PhotoImage
    #     self.photo = ImageTk.PhotoImage(image = Img.fromarray(frame))
    #     self.display1.create_image(500,300,image=self.photo)

    #     self.window.after(self.delay, self.update)

    def capture(self):
        """ Fonction permettant de capturer une image et de l'enrigistré avec l'horodatage """
        ts = datetime.datetime.now()
        filename = "image_{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # Construction du nom
        p = os.path.join(self.output_path, filename)  # construit le chemin de sortie
        self.im0.save(p, "PNG")  # Sauvegarde l'image sous format png
        print("[INFO] saved {}".format(filename))

    def nettoyage(self):
        """ Test d'amélioration de l'image par binarisation d'Otsu """
        i,j=0,0
        #print(self.propre)
        if self.propre=="False" :
            raise Exception() #Quitte la fonction si la valeur est fausse, 2eme sécurité
        else :
            img_gris=cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)  #Transforme l'image en noir/blanc
            width = int(self.frame.shape[1]*0.5) #Redimensionne l'image pour plus de rapidité (flux réel)
            height = int(self.frame.shape[0]*0.5)
            dim = (width, height)
            self.gray = cv2.resize(img_gris,dim, interpolation = cv2.INTER_AREA) #Redimensionne l'image pour plus de rapidité (flux réel)
            self.blur = cv2.GaussianBlur(self.gray,(5,5),0) #Mets un flou gaussien
            ret3,self.otsu = cv2.threshold(self.blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) #Applique le filtre d'Otsu
            data1 = np.asarray(self.gray) #Récupère la matrice de l'image initiale
            data2 = np.asarray(self.otsu) #Récupère la matrice de l'image filtrée
            for i in range (data2.shape[0]): #Interverti les pixels blancs de la deuxième matrice par ceux nuancés de la première
                for j in range (data2.shape[1]):
                    if data2[i,j]==255 :
                        data2[i,j]=data1[i,j]
            self.frame=data2 #Nouvelle image dont le fond est filtré en fonction de l'intensité du reste de l'image

            #Remet l'image en RGB pour y dessiner toutes les formes par la suite et en couleur
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_GRAY2RGB)
            
            # find contours in the binary image
            contours, hierarchy = cv2.findContours(self.otsu,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
            for c in contours:
            # calculate moments for each contour
                M = cv2.moments(c)

            # calculate x,y coordinate of center
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                else:
                    cX, cY = 0, 0

                #Dessine un cercle sur tous les blobs de l'image (formes blanches)
                cv2.circle(self.frame, (cX, cY), 2, (0, 0, 255), -1)

                # permet de fit une ellipse sur toutes les formes identifiés sur l'image
                if len(c) < 5:
                    break
                ellipse = cv2.fitEllipse(c)
                thresh = cv2.ellipse(self.frame,ellipse,(0,255,0),1)
                
            M=cv2.moments(self.otsu)
            # calculate x,y coordinate of center
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            # dessine les contours des formes qu'il a identifiés
            cv2.drawContours (self.frame, contours, 3, (255,215,0), 3)
            
            #Dessine une croix sur le barycentre de l'image
            cv2.line(self.frame, (cX, 0), (cX, height), (255, 0, 0), 1)
            cv2.line(self.frame, (0, cY), (width, cY), (255, 0, 0), 1)

        return        


root = Fenetre()
root.window.mainloop() # Lancement de la boucle principale