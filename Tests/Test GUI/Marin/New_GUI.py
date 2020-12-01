# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 09:22:21 2020

@author: Optique
"""

#####################################################################
#                                                                   #
#           Programme d'interfaçage de faisceaux                    #
#                                                                   #
#####################################################################


"""Fonctionnalités"""
#Ce programme est actuellement composé de 3 fichiers et il permet de récupérer
#le flux vidéo d'une caméra Basler et permet de l'utiliser dans le cadre d'une
#analyse de faisceau laser.
# Il permet :
#   * Afficher la preview vidéo
#   * Auto-expose l'image au démarrage et sur appuie du bouton
#   * Préviens des problèmes sur un temps d'exposition trop long ou trop court
#   * Permet d'effectuer le traitement de l'image
#       * Filtrage
#       * Détection de forme
#       * Définition automatique de ROI
#       * Crop sur ROI
#       * Fit de l'ellipse du faisceau
#       * Fit gaussien du faisceau en x et y
#       * Fit 2D Gaussien
#   * Affichage du traitement d'image
#   * Affichage des courbes


print("[INFO] starting...")
from pypylon import pylon #Bibliothèque Basler d'interfaçage de la caméra
from PIL import Image as Img #Bibliothèque de traitement d'image
from PIL import ImageTk
import numpy as np #Bibliothèque de traitement des vecteurs et matrice
import cv2 #Bibliothèque d'interfaçage de caméra et de traitement d'image
import tkinter as tk
from tkinter import ttk
from tkinter import IntVar
from tkinter import DoubleVar
from tkinter import Entry
from threading import Thread
import sys
import os #Bibliothèque permettant de communiquer avec l'os et notamment le "path"
from pathlib import Path
import time #Bibliothèque permettant d'utiliser l'heure de l'ordinateur
import datetime #Bibliothèque permettant de récupérer la date
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)
from statistics import mean
import oneCameraCapture as oneCameraCapture
import opencv_module as OpenCam
import Img_Traitement as Img_Traitement


# La Classe Fenetre contient l'ensemble du programme #

class Fenetre(Thread):

    def __init__(self, output_path = "./"): #Fonction d'initialisation du programme
        
        Thread.__init__(self)

        """Edition de nom de variable associé aux autres fichiers du programme"""
        try :
            self.vid = oneCameraCapture.cameraCapture()
        except :
            try :
                self.cam=OpenCam.openCamera()
            except :
                print("Need camera troubleshooting")
                exit()

        self.trmt = Img_Traitement.Traitement()
        self.output_path = Path.cwd()  #Chemin de sortie de la photo

        """"Edition de l'interface"""
        self.window = tk.Tk()  #Réalisation de la fenêtre principale
        self.window.state('zoomed')
         
        self.window.title("Beam analyzer Python")
        self.window.config(background="#FFFFFF") #Couleur de la fenêtre
        self.window.protocol('WM_DELETE_WINDOW', self.destructor) #La croix de la fenetre va fermer le programme
        
        """"definition des proportions pour les frames"""
        self.window.grid_columnconfigure(1, weight=3)
        self.window.grid_columnconfigure(2,weight=2)
        self.window.grid_rowconfigure(1, weight=5)
        self.window.grid_rowconfigure(2, weight=0)
        self.window.grid_rowconfigure(3, weight=0)
        self.window.grid_rowconfigure(4, weight=3)
        
        """Definition de certaines variables nécessaires au demarrage de l'interface"""
        #Variables pour la taille des pixels des caméras
        self.size_pixel_height = DoubleVar()
        self.size_pixel_width = DoubleVar()

        #Variables d'affichage des figures
        self.choix_fig_XY = IntVar()
        self.choix_fig_XY = 0

        #Variables du barycentre de l'image
        self.cX = DoubleVar()
        self.cY = DoubleVar()

        #Variables du fit ellipse
        self.ellipse_width = DoubleVar()
        self.ellipse_height = DoubleVar()
        self.ellipse_angle =DoubleVar()

        #Valeurs d'initialisation des tailles de l'affichage
        self.Screen_x = 1500
        self.Screen_y = 1000
        self.Screen2_x = 750
        self.Screen2_y = 750

        #Temps en ms entre chaque actualisation de l'interface
        self.delay=15

        #Variable de l'écran de l'image traité
        self.frame2=[]

        #Variable pour l'aligenement des faisceaux
        self.align=False
        self.choix_fig=0

        #Appel de toutes les fonctions permettant l'affichage de notre programme
        self.display()
        self.plot()
        self.Interface() #Lance la fonction Interface
        self.flux_cam()


    #########################
    #   Partie Interface    # 
    #########################       


    def Interface(self):
        """ Fonction permettant de créer l'interface dans laquelle sera placé toutes les commandes et visualisation permettant d'utiliser le programme """
        
        #commandes gauche
            #Taille de la zone des boutons
        self.cmdleft = tk.Frame(self.window,padx=5,pady=5,bg="gray")
        self.cmdleft.grid(row=1, rowspan=2,column=0, sticky='NSEW')

            #Bouton snapshot
        self.FrameCapture=tk.Frame(self.cmdleft, borderwidth=2, relief='groove')
        self.FrameCapture.grid(row=0, column=0, rowspan=3, columnspan=1, sticky="nsew")

        label_snap=tk.Label(self.FrameCapture, text="Choix enregistrement :")
        label_snap.grid(row=0, column=0, sticky="nsew")

        self.coch0, self.coch1, self.coch2, self.coch3, self.coch4 =0,0,0,0,0

        bouton_selection = tk.Checkbutton(self.FrameCapture, text="Preview", command=self.choice0)
        bouton_selection.grid(row=1, column=0)
        bouton_selection = tk.Checkbutton(self.FrameCapture, text="Traité", command=self.choice1)
        bouton_selection.grid(row=2, column=0)
        bouton_selection = tk.Checkbutton(self.FrameCapture, text="Plot X,Y", command=self.choice2)
        bouton_selection.grid(row=3, column=0)
        bouton_selection = tk.Checkbutton(self.FrameCapture, text="Plot Ellipse", command=self.choice3)
        bouton_selection.grid(row=4, column=0)
        bouton_selection = tk.Checkbutton(self.FrameCapture, text="Plot 2D", command=self.choice4)
        bouton_selection.grid(row=5, column=0)

            #Bouton capture
        btncap = tk.Button(self.cmdleft,text="Capture",command=self.capture)
        btncap.grid(row=3,column=0,sticky="nsew")

        labelSpace2=tk.Label(self.cmdleft, text='', bg='gray')
        labelSpace2.grid(row=4,column=0)

            #tracé du profil (par defaut XY)
        btnprofiles = tk.Button(self.cmdleft,text="Profils",command=self.plot)
        btnprofiles.grid(row=7,column=0,sticky="nsew")

        btn_stpprof = tk.Button(self.cmdleft, text="Stop Profils", command=self.stop_profil)
        btn_stpprof.grid(row=8, column=0, sticky="nsew")

            #Liste selection du plot
        selection_plot=tk.Label(self.cmdleft,text="Sellectionnez Fit",bg="gray")
        selection_plot.grid(row=5,column=0,sticky="nsew")
        liste_plots =["Choix","Fit XY","Fit axes ellipse","Fit Gaussien 2D"]
        self.liste_combobox = ttk.Combobox(self.cmdleft,values=liste_plots)
        self.liste_combobox.grid(row=6,column=0,sticky="nsew")
        self.liste_combobox.current(0)
        self.liste_combobox.bind("<<ComboboxSelected>>",self.choix_figure) 

        labelSpace3=tk.Label(self.cmdleft, text='', bg='gray')
        labelSpace3.grid(row=9,column=0)       

            #Bouton alignement de faisceaux
        btnalign = tk.Button(self.cmdleft, text='Alignement de faisceaux', command=self.alignement)
        btnalign.grid(row=10, column=0, sticky="nsew")

            #Bouton arrêt alignement
        btn_stopalign = tk.Button(self.cmdleft, text='Arrêt alignement', command=self.arret_align)
        btn_stopalign.grid(row=11, column=0, sticky="nsew")

        labelSpace=tk.Label(self.cmdleft, text='', bg='gray')
        labelSpace.grid(row=12,column=0)

            #Bouton quitter
        btnquit = tk.Button(self.cmdleft,text="Quitter",command = self.destructor)
        btnquit.grid(row=13,column=0,sticky="nsew")

        #commandes superieures
            #Taille de la zone de commande
        self.cmdup = tk.Frame(self.window,padx=5,pady=5,bg="gray")
        self.cmdup.grid(row=0,column=1, sticky="NSEW")

            #Bouton traitement vidéo
        btnvideo = tk.Button(self.cmdup,text="Traitement video", command=self.video_tool)
        btnvideo.grid(row=0,column=0,sticky="nsew")

            #Bouton auto-exposition
        btnexp = tk.Button(self.cmdup,text="Réglage auto temps exp", command=self.exp)
        btnexp.grid(row=0,column=1,sticky="nsew")


    def display(self):
        #cadre video
            #Position
        self.display1 = tk.Canvas(self.window, width=self.Screen_x,height=self.Screen_y,bg="white")  # Initialisation de l'écran 1
        self.display1.grid(row=1,column=1,sticky="NSW")
            #Taille
        self.Screen_x = self.display1.winfo_width()
        self.Screen_y = self.display1.winfo_height()

        #cadre traitement
            #Titre
        self.title_display2 = tk.Label(self.window,text="Fit ellipse",bg="white")
        self.title_display2.grid(row=0,column=2,sticky="NSEW")
            #Position
        self.display2 = tk.Canvas(self.window, width=self.Screen2_x, height=self.Screen2_y, bg="white")  # Initialisation de l'écran 1
        self.display2.grid(row=1, rowspan=2,column=2,sticky="NSE")
            #Taille
        self.Screen2_x = self.display2.winfo_width()
        self.Screen2_y = self.display2.winfo_height()

        #cadre plots fits
        self.display_plots_title = tk.Label(self.window,text="affichage graphes de fit",bg="white")
        self.display_plots_title.grid(row=3,column=1, sticky="NSEW")

        #zone affichage résultats
        self.results = tk.Frame(self.window,padx=5,pady=5,bg="gray")
        self.results.grid(row=3,column=2,sticky="NSE")

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
        """
        self.console = tk.Frame(self.window, padx=5, pady=5)
        self.console.grid(row=3, column=0, sticky='nsew')
        t=tk.Text(self.console)
        t.pack()
        t.insert(self.console, sys.stdout)
        """
        



    def destructor(self):
        """ Détruit les racines objet et arrête l'acquisition de toutes les sources """
        print("[INFO] closing...")
        self.window.quit()
        self.window.destroy() # Ferme la fenêtre


         #Fonction définissant l'image à enregistrer   
    def choice0(self):
        self.coch0=1
    
    def choice1(self):
        self.coch1=1
 
    def choice2(self):
        self.coch2=1
    
    def choice3(self):
        self.coch3=1

    def choice4(self):
        self.coch4=1

    def alignement(self):
        self.align=True
    
    def arret_align(self):
        self.align=False

    def stop_profil(self):
        self.cadre_plots.destroy()




    #####################
    #   Partie Camera   # 
    #####################


    def flux_cam(self):
        """Lance la fonction d'affichage de la preview  dans un thread"""
        self.t1=Thread(target=self.update(), args=(self.window, self.display1, self.Screen_x, self.Screen_y)) #boucle la fonction d'acquisition de la caméra
        self.t1.start()


    def update(self):
        """Affichage de la preview"""
        #Get a frame from cameraCapture
        try:
            self.frame0 = self.vid.getFrame() #This is an array
        except :
            try :
                self.frame0 = self.cam.capture()
            except :
                pass
        self.frame=cv2.normalize(self.frame0, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1)
        frame=self.frame
        if self.align == True :
            test=True
            try :
                self.baryX
            except AttributeError:
                test=False
                self.align = False
                tk.messagebox.showerror("Alignement impossible", "Il faut traiter le premier faisceau pour permettre l'alignement. \n Pour cela cliquez sur le bouton traitement après ce message.")
            if test == True:
                cv2.line(frame, (self.baryX, 0), (self.baryX, frame.shape[0]), (255, 0, 0), 3)#Dessine une croix sur le barycentre de l'image
                cv2.line(frame, (0, self.baryY), (frame.shape[1], self.baryY), (255, 0, 0), 3)

        #Get display size
        self.Screen_x = self.display1.winfo_width()
        self.Screen_y = self.display1.winfo_height()
        r = float(self.Screen_x/self.Screen_y)

        #Get picture ratio from oneCameraCapture
        try:
            ratio = self.vid.ratio
        except:
            try :
                ratio = self.cam.ratio
            except :
                pass
        #keep ratio
        if r > ratio:
            self.Screen_x = int(round(self.display1.winfo_height()*ratio))
        elif r < ratio:
            self.Screen_y = int(round(self.display1.winfo_width()/ratio))

        #resize the picture
        frame = cv2.resize(frame, dsize=(self.Screen_x,self.Screen_y), interpolation=cv2.INTER_AREA)

        #OpenCV bindings for Python store an image in a NumPy array
        #Tkinter stores and displays images using the PhotoImage class
        # Use PIL (Pillow) to convert the NumPy ndarray to a PhotoImage
        self.photo = ImageTk.PhotoImage(image = Img.fromarray(frame))
        self.display1.create_image(self.Screen_x/2,self.Screen_x/(2*ratio),image=self.photo)

        #recall the function after a delay
        self.window.after(self.delay, self.update)


    def capture(self):
        """ Fonction permettant de capturer une image et de l'enregistrer avec l'horodatage """
        ts = datetime.datetime.now()
        try:
            os.mkdir('Snapshot')
        except OSError:
            pass
        path=self.output_path.joinpath('Snapshot')
        print("Dossier d'enregistrement : ", path)
        
        if self.coch0==1:
            filename = "preview_{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # Construction du nom
            p = path.joinpath(filename)  # construit le chemin de sortie
            image = Img.fromarray(self.frame)
            image.save(p, "PNG")  # Sauvegarde l'image sous format png
            print("[INFO] saved {}".format(filename))
        if self.coch1==1:
            filename_2 = "treatment_{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
            p = path.joinpath(filename_2)
            image2 = Img.fromarray(self.frame2)
            image2.save(p, "PNG")
            print("[INFO] saved {}".format(filename_2))
        if self.coch2==1:
            filename_xy = "plot_xy_{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
            p = path.joinpath(filename_xy)
            self.fig_XY.savefig(p, dpi=1200)
            print("[INFO] saved {}".format(filename_xy))
        if self.coch3==1:
            filename_ellipse = "plot_ell_{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
            p = path.joinpath(filename_ellipse)
            #self.fig_XY.savefig(p, dpi=1200)
            print("[INFO] saved {}".format(filename_ellipse))
        if self.coch4==1:
            filename_2D = "plot_2D_{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
            p = path.joinpath(filename_2D)
            #self.fig_XY.savefig(p, dpi=1200)
            print("[INFO] saved {}".format(filename_ellipse))
        self.coch0, self.coch1, self.coch2, self.coch3, self.coch4 =0,0,0,0,0
        

    def video_tool(self):
        self.t2 = Thread(target=self.disp_traitement)
        self.t2.start()

    def disp_traitement(self):
        self.frame2, self.ellipse, self.baryX, self.baryY, self.choix_fig_XY = self.trmt.traitement(self.frame)
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
        self.ellipse_width.set(int(self.ellipse[1][1])) #3 lignes pour extraction des données du tuple ellipse
        self.ellipse_height.set(int(self.ellipse[1][0]))
        self.ellipse_angle.set(int(self.ellipse[2]))

        #self.window.after(self.delay, self.affich_traitement)

    def exp(self):
        """Lance la fonction d'auto expo de la classe onCameraCapture suite à la pression d'un bouton"""
        self.vid.auto_exposure()

    def choix_figure(self,param):
        selection = self.liste_combobox.get()
        #print(selection)
        if selection =="Choix":
            self.choix_fig=0
        if selection =="Fit XY":
            self.choix_fig=1
        if selection =="Fit axes ellipse":
            self.choix_fig=2
        if selection =="Fit Gaussien 2D":
            self.choix_fig=3

        return

    def plot(self):
        "choix_fig_XY = 0 quand le traitement d'image n'a pas encore été effectué, et = 1 après le traitement. le graphe apparait après pression du bouton profils"
        try :
            for widget in self.cadre_plots.winfo_children():
                widget.destroy()
        except :
            pass
        if self.choix_fig == 0:
            self.fig_XY = Figure()
        else : 
            try :
                self.photo2
            except :
                tk.messagebox.showerror("Graphiques impossibles", "Il faut traiter le faisceau pour l'affichage des graphs. \n Pour cela cliquez sur le bouton traitement après ce message.")
                self.fig_XY = Figure()
                return self.fig_XY

            self.fig_XY = Figure()
            if self.choix_fig == 1 :
                self.fig_XY = self.trmt.trace_profil()
            if self.choix_fig == 2 :
                self.fig_XY = self.trmt.trace_ellipse()
            if self.choix_fig == 3 :
                self.fig_XY = self.trmt.plot_2D()

        #cadre affichage profils
        self.cadre_plots = tk.Frame(self.window,padx=5,pady=5,bg="gray")
        self.cadre_plots.grid(row=2,column=1,columnspan=2,sticky="NSW")
        self.disp_XY = FigureCanvasTkAgg(self.fig_XY, self.cadre_plots)
        self.toolbar = NavigationToolbar2Tk(self.disp_XY, self.cadre_plots)
        self.toolbar.grid(row=0,column=0)
        self.toolbar.update()    
        self.cadre_disp_XY = self.disp_XY.get_tk_widget()
        self.cadre_disp_XY.grid(row=1,column=0)
        return self.fig_XY


root = Fenetre()
root.window.mainloop() # Lancement de la boucle principale