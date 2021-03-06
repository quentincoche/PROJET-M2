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
from PIL import Image as Img #Bibliothèque de traitement d'image
from PIL import ImageTk #Transformation d'image pour l'affichage de tkinter
import numpy as np #Bibliothèque de traitement des vecteurs et matrice
import cv2 #Bibliothèque d'interfaçage de caméra et de traitement d'image
import tkinter as tk #Bibliothèque d'affichage graphique
from tkinter import filedialog
from tkinter import StringVar, ttk
from tkinter import IntVar
from tkinter import DoubleVar
from tkinter import RIDGE
from tkinter import tix
from threading import Thread #Bibliothèque de multithreading pour optimiser le fonctionnement
import os #Bibliothèque permettant de communiquer avec l'os et notamment le "path"
from pathlib import Path #Bibliothèque de gestion du path
import datetime #Bibliothèque permettant de récupérer la date
from matplotlib.figure import Figure #Bibliothèque de figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)

import oneCameraCapture_q as oneCameraCapture
import opencv_module_q as OpenCam
import Img_Traitement_q as Img_Traitement



# La Classe Fenetre contient l'ensemble du programme #
class Fenetre(Thread):

    def __init__(self): #Fonction d'initialisation du programme
        
        Thread.__init__(self) #Lance la classe dans un thread

        """Edition de nom de variable associé aux autres fichiers du programme"""
        try :
            self.vid = oneCameraCapture.cameraCapture() #test si la caméra est basler
            self.basler=True
        except :
            try :
                self.cam=OpenCam.openCamera() #Pour toutes les autres camera
                self.basler=False
            except :
                print("Need camera troubleshooting") #Surement pas de caméra
                exit()

        self.trmt = Img_Traitement.Traitement() #Lance l'initalisation de la classe traitement
        self.output_path = Path.cwd()  #Chemin de sortie de la photo

        """"Edition de l'interface"""
        self.window = tix.Tk()  #Réalisation de la fenêtre principale
        self.window.state('zoomed') #Lance le GUI en plein écran
         
        self.window.title("Beam analyzer Python")
        self.window.config(background="#FFFFFF") #Couleur de la fenêtre
        self.window.protocol('WM_DELETE_WINDOW', self.destructor) #La croix de la fenetre va fermer le programme
        
        """"definition des proportions pour les frames"""
        self.window.grid_columnconfigure(1, weight=3)
        self.window.grid_columnconfigure(2,weight=2)
        self.window.grid_rowconfigure(1, weight=3)
        self.window.grid_rowconfigure(2, weight=3)
        
        """Definition de certaines variables nécessaires au demarrage de l'interface"""
        #Variables pour la taille des pixels des caméras
        self.size_pixel_height = DoubleVar()
        self.size_pixel_width = DoubleVar()

        #Variables d'affichage des figures
        self.choix_fig_XY = IntVar()
        self.choix_fig_XY = 0

        #Variable choix du filtre de binarisation
        self.choix_filtre = IntVar()
        self.choix_filtre = 1

        #Variables du barycentre de l'image
        self.cX = IntVar()
        self.cY = IntVar()

        #Variables du fit ellipse
        self.ellipse_width = IntVar()
        self.ellipse_height = IntVar()
        self.ellipse_angle =IntVar()

        #Variables du fit gauss
        self.titre_gauss1=StringVar()
        self.titre_gauss2=StringVar()
        self.gauss_amp1=StringVar()
        self.gauss_mean1=StringVar()
        self.gauss_stddev1=StringVar()
        self.gauss_amp2=StringVar()
        self.gauss_mean2=StringVar()
        self.gauss_stddev2=StringVar()

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
        self.Bx=0
        self.By=0
        self.H=False

        #Variable denoise
        self.noise=0

        #Appel de toutes les fonctions permettant l'affichage de notre programme
        self.display()
        #self.plot()
        self.Interface() #Lance la fonction Interface
        self.flux_cam()

        #detection du nombre de pixels par pouce: utile pour l'affichage des plots
        self.dpi = self.cadre_plots.winfo_fpixels('1i')
        try:    
            self.pixel_size = self.vid.pixel_size
        except:
            pass
        
    #########################
    #   Partie Interface    # 
    #########################       

    def Interface(self):
        """ Fonction permettant de créer l'interface dans laquelle sera placé toutes les commandes et visualisation permettant d'utiliser le programme """
        
        #COMMANDES GAUCHE
            #Taille de la zone des boutons
        self.cmdleft = tk.Frame(self.window,padx=5,pady=5,bg="gray",relief = RIDGE)
        self.cmdleft.grid(row=1, rowspan=2,column=0, sticky='NSEW')

            #Bouton snapshot
        self.FrameCapture=tk.Frame(self.cmdleft, borderwidth=2, relief='groove')
        self.FrameCapture.grid(row=0, column=0, sticky="nsew")

        label_snap=tk.Label(self.FrameCapture, text="Choix enregistrement :")
        label_snap.grid(row=0, column=0, sticky="nsew")

        self.coch0, self.coch1, self.coch2, self.coch3, self.coch4 =0,0,0,0,0

        bouton_selection = tk.Checkbutton(self.FrameCapture, text="Preview", command=self.choice0)
        bouton_selection.grid(row=1, column=0)
        bouton_selection = tk.Checkbutton(self.FrameCapture, text="Traité", command=self.choice1)
        bouton_selection.grid(row=2, column=0)
        bouton_selection = tk.Checkbutton(self.FrameCapture, text="Plot", command=self.choice2)
        bouton_selection.grid(row=3, column=0)
        bouton_selection = tk.Checkbutton(self.FrameCapture, text="Coordonnées", command=self.choice3)
        bouton_selection.grid(row=4, column=0)
        bouton_selection = tk.Checkbutton(self.FrameCapture, text="Données Plot", command=self.choice4)
        bouton_selection.grid(row=5, column=0)


            #Bouton capture
        btncap = tk.Button(self.cmdleft,text="Enregistrer",command=self.capture)
        btncap.grid(row=1,column=0,sticky="nsew")

        labelSpace2=tk.Label(self.cmdleft, text='', bg='gray')
        labelSpace2.grid(row=2,column=0)

            #Liste selection du plot
        selection_plot=tk.Label(self.cmdleft,text="Sellectionnez Fit",bg="gray")
        selection_plot.grid(row=3,column=0,sticky="nsew")
        liste_plots =["Choix","Fit XY","Fit axes ellipse","Fit Gaussien 2D"]
        self.liste_combobox = ttk.Combobox(self.cmdleft,values=liste_plots)
        self.liste_combobox.grid(row=4,column=0,sticky="nsew")
        self.liste_combobox.current(0)
        self.liste_combobox.bind("<<ComboboxSelected>>",self.choix_figure) 

            #tracé du profil (par defaut XY)
        btnprofiles = tk.Button(self.cmdleft,text="Profils",command=self.plot)
        btnprofiles.grid(row=5,column=0,sticky="nsew")

        btn_stpprof = tk.Button(self.cmdleft, text="Stop Profils", command=self.stop_profil)
        btn_stpprof.grid(row=6, column=0, sticky="nsew")

        labelSpace3=tk.Label(self.cmdleft, text='', bg='gray')
        labelSpace3.grid(row=7,column=0)       

            #Bouton alignement de faisceaux
        btnalign = tk.Button(self.cmdleft, text='Alignement de faisceaux', command=self.alignement)
        btnalign.grid(row=8, column=0, sticky="nsew")

            #Bouton hold de faisceaux
        btnhold = tk.Button(self.cmdleft, text='Hold', command=self.hold)
        btnhold.grid(row=9, column=0, sticky="nsew")

            #Bouton arrêt alignement
        btn_stopalign = tk.Button(self.cmdleft, text='Arrêt alignement', command=self.arret_align)
        btn_stopalign.grid(row=10, column=0, sticky="nsew")

        labelSpace=tk.Label(self.cmdleft, text='', bg='gray')
        labelSpace.grid(row=11,column=0)

        btn_M2 = tk.Button(self.cmdleft, text='Fit M²',command=self.M2)
        btn_M2.grid(row=12, column=0, sticky="nsew")


        labelSpace=tk.Label(self.cmdleft, text='', bg='gray')
        labelSpace.grid(row=13,column=0)

            #Bouton quitter
        btnquit = tk.Button(self.cmdleft,text="Quitter",command = self.destructor)
        btnquit.grid(row=14,column=0,sticky="nsew")

        #COMMANDES SUPERIEURES
            #Taille de la zone de commande
        self.cmdup = tk.Frame(self.window,padx=5,pady=5,bg="gray")
        self.cmdup.grid(row=0,column=1, sticky="NSEW")

            #Bouton traitement vidéo
        btnvideo = tk.Button(self.cmdup,text="Traitement video", command=self.video_tool)
        btnvideo.grid(row=0,column=0,sticky="nsew")

            #Bouton auto-exposition
        btnexp = tk.Button(self.cmdup,text="Réglage auto temps exp", command=self.exp)
        btnexp.grid(row=0,column=1,sticky="nsew")

        labelSpace5=tk.Label(self.cmdup, text='  ', bg='gray')
        labelSpace5.grid(row=0,column=2)

            #Choix du filtre
        selection_filtre=tk.Label(self.cmdup,text="Selectionnez Filtre",bg="gray")
        selection_filtre.grid(row=0,column=3,sticky="nse")
        liste_filtres =["Otsu","Adaptatif","I/e²"]
        self.liste_combobox2 = ttk.Combobox(self.cmdup,values=liste_filtres)
        self.liste_combobox2.grid(row=0,column=4,sticky="nse")
        self.liste_combobox2.current(0)
        self.liste_combobox2.bind("<<ComboboxSelected>>",self.choose_filter)

            #Denoise
        btnNoise = tk.Button(self.cmdup,text="Denoise image", command=self.DeNoise)
        btnNoise.grid(row=0,column=5,sticky="nsew")
        

        #### Affichage de l'aide quand on survole les bouttons ####

        b = tk.tix.Balloon(self.window,bg="gray")
        b.bind_widget(btnquit,balloonmsg='Quitte le logiciel')
        b.bind_widget(btnalign,balloonmsg='Permet de mémoriser la position du barycentre du faisceau au moment de la pression, puis d\'afficher\n la position en temps réel du barycentre pour aligner un deuxième faisceau avec le premier')
        b.bind_widget(btnexp,balloonmsg='Réglage automatique du temps d\'exposition après pression du bouton')
        b.bind_widget(btnvideo,balloonmsg='Lance le traitement d\'image.\
            \n Permet de détecter plus ou moins grossièrement selon la méthode de\n seuillage la forme de l\'ellipse ainsi que la position du barycentre de limage croppée')
        b.bind_widget(self.liste_combobox,balloonmsg='Choix du fit à afficher :\n\
             -Fit XY -> fit gaussien selon les axes X et Y \n\
             -Fit axes ellipse -> fit gaussien selon les axes de l\'ellipse (grand et petit axes)\n\
             -Fit gauss2D -> fit gaussien sur les deux dimensions \n Appuyer sur le bouton Profils pour afficher les graphes')
        b.bind_widget(self.liste_combobox2,balloonmsg='Choix de la technique de seuillage du faisceau :\n\
             -Otsu -> binarisation selon l\'algorithme Otsu \n\
             -Adaptatif -> \n\
             -I/e² -> les pixels inférieurs à la valeur de Imax/e² sont mis à zero ')
        #b.bind_widget(button2, balloonmsg='Self-destruct button',statusmsg='Press this button and it will destroy itself')
        return

    def display(self):

        self.display1 = tk.Canvas(self.window, borderwidth=4,bg="white",relief="ridge")  # Initialisation de l'écran 1
        self.display1.grid(row=1,column=1,sticky="NSEW")        #cadre video
        self.Screen_x = self.display1.winfo_width()
        self.Screen_y = self.display1.winfo_height()

        #cadre traitement
        self.title_display2 = tk.Label(self.window,text="Fit ellipse",borderwidth=4,bg="gray",relief="ridge")
        self.title_display2.grid(row=0,column=2,sticky="NSEW")
        self.display2 = tk.Canvas(self.window, width=self.Screen2_x/2, height=self.Screen2_y/2,bg="white",relief="ridge")  # Def de l'écran 2
        self.display2.grid(row=1,column=2,sticky="NSEW")
        self.Screen2_x = self.display2.winfo_width()
        self.Screen2_y = self.display2.winfo_height()

        #cadre plots fits
        self.display_plots_title = tk.Label(self.window,text="affichage graphes de fit",borderwidth=4,bg="gray",relief="ridge")
        self.display_plots_title.grid(row=3,column=1, sticky="NSEW")
        self.cadre_plots = tk.Frame(self.window,borderwidth=4,bg="white",relief="ridge")
        self.cadre_plots.grid(row=2,column=1,columnspan=1,sticky="NSEW")


        ##zone affichage résultats##

        self.fsize = 12 #Taille de la police pour l'affichage
        
        self.results = tk.Frame(self.window,padx=5,pady=5,bg="gray") #définit la frame
        self.results.grid(row=2,rowspan=2,column=2,sticky="NSEW") #place la frame

        #barycentres
        self.label01 = tk.Label(self.results,text="barycentre X = ",font=(None,self.fsize)).grid(row=0,column=0,sticky="nsew")
        self.label001 = tk.Label(self.results,text="\u03BCm",font=(None,self.fsize)).grid(row=0,column=2,sticky="nsew")
        self.label1 = tk.Label(self.results,textvariable=self.cX,font=(None,self.fsize)).grid(row=0,column=1,sticky="nsew")
        self.label02 = tk.Label(self.results,text="barycentre Y = ",font=(None,self.fsize)).grid(row=1,column=0,sticky="nsew")
        self.label002 = tk.Label(self.results,text="\u03BCm",font=(None,self.fsize)).grid(row=1,column=2,sticky="nsew")
        self.label2 = tk.Label(self.results,textvariable=self.cY,font=(None,self.fsize)).grid(row=1,column=1,sticky="nsew")
        
        #parametres ellipse
        self.label03 = tk.Label(self.results,text="Grand axe ellipse = ",font=(None,self.fsize)).grid(row=2,column=0,sticky="nsew")
        self.label003 = tk.Label(self.results,text="\u03BCm",font=(None,self.fsize)).grid(row=2,column=2,sticky="nsew")
        self.label3 = tk.Label(self.results,textvariable=self.ellipse_width,font=(None,self.fsize)).grid(row=2,column=1,sticky="nsew")
        self.label04 = tk.Label(self.results,text="Petit axe ellipse = ",font=(None,self.fsize)).grid(row=3,column=0,sticky="nsew")
        self.label004 = tk.Label(self.results,text="\u03BCm",font=(None,self.fsize)).grid(row=3,column=2,sticky="nsew")
        self.label4 = tk.Label(self.results,textvariable=self.ellipse_height,font=(None,self.fsize)).grid(row=3,column=1,sticky="nsew")
        self.label05 = tk.Label(self.results,text="Angle ellipse = ",font=(None,self.fsize)).grid(row=4,column=0,sticky="nsew")
        self.label005 = tk.Label(self.results,text="°",font=(None,self.fsize)).grid(row=4,column=2,sticky="nsew")
        self.label5 = tk.Label(self.results,textvariable=self.ellipse_angle,font=(None,self.fsize)).grid(row=4,column=1,sticky="nsew")
        

        #Paramètre gaussienne
        self.labelg10=tk.Label(self.results,textvariable=self.titre_gauss1,font=(None,self.fsize)).grid(row=5,column=0,sticky="nsew")
        self.labelg11 = tk.Label(self.results,textvariable=self.gauss_amp1,font=(None,self.fsize)).grid(row=5,column=1,sticky="nsew")
        self.labelg111 = tk.Label(self.results,text="\u03BCm",font=(None,self.fsize)).grid(row=5,column=2,sticky="nsew")
        self.labelg12 = tk.Label(self.results,textvariable=self.gauss_mean1,font=(None,self.fsize)).grid(row=6,column=1,sticky="nsew")
        self.labelg121 = tk.Label(self.results,text="\u03BCm",font=(None,self.fsize)).grid(row=6,column=2,sticky="nsew")
        self.labelg13 = tk.Label(self.results,textvariable=self.gauss_stddev1,font=(None,self.fsize)).grid(row=7,column=1,sticky="nsew")
        self.labelg131 = tk.Label(self.results,text="\u03BCm",font=(None,self.fsize)).grid(row=7,column=2,sticky="nsew")
        self.labelg01=tk.Label(self.results,textvariable=self.titre_gauss2,font=(None,self.fsize)).grid(row=8,column=0,sticky="nsew")
        self.labelg02 = tk.Label(self.results,textvariable=self.gauss_amp2,font=(None,self.fsize)).grid(row=8,column=1,sticky="nsew")
        self.labelg021 = tk.Label(self.results,text="\u03BCm",font=(None,self.fsize)).grid(row=8,column=2,sticky="nsew")
        self.labelg03 = tk.Label(self.results,textvariable=self.gauss_mean2,font=(None,self.fsize)).grid(row=9,column=1,sticky="nsew")
        self.labelg031 = tk.Label(self.results,text="\u03BCm",font=(None,self.fsize)).grid(row=9,column=2,sticky="nsew")
        self.labelg04 = tk.Label(self.results,textvariable=self.gauss_stddev2,font=(None,self.fsize)).grid(row=10,column=1,sticky="nsew")
        self.labelg120=tk.Label(self.results,textvariable="",font=(None,self.fsize)).grid(row=6,column=0,sticky="nsew")
        self.labelg130=tk.Label(self.results,textvariable="",font=(None,self.fsize)).grid(row=7,column=0,sticky="nsew")
        self.labelg030=tk.Label(self.results,textvariable="",font=(None,self.fsize)).grid(row=9,column=0,sticky="nsew")
        self.labelg040=tk.Label(self.results,textvariable="",font=(None,self.fsize)).grid(row=10,column=0,sticky="nsew")
        return

    def M2(self):

        """Variables à initialiser"""
       

        """"Edition de l'interface"""
        self.windowM2 = tix.Tk()  #Réalisation de la fenêtre pour le calcul du M²
        #self.windowM2.state('zoomed') #Lance le GUI en plein écran
         
        self.windowM2.title("Calcul du M²")
        self.windowM2.config(background="#FFFFFF") #Couleur de la fenêtre

        """Définition des frames"""
        self.cmdM2 = tk.Frame(self.windowM2,padx=5,pady=5,bg="gray",relief = RIDGE)
        self.cmdM2.grid(row=1,column=0,sticky="nsw")
        
        self.central = tk.Frame(self.windowM2,padx=5,pady=5,bg="white",relief = RIDGE)
        self.central.grid(row=1,column=1,sticky="nsew")

        """Définition des boutons et zones de saisie"""
        self.labelSpace = tk.Label(self.cmdM2, text='  ', bg='gray')
        self.labelSpace.grid(row=0,column=0)

        self.labellambda = tk.Label(self.cmdM2,text='Longueur d\'onde du faisceau (en nm)',bg="gray")
        self.labellambda.grid(row=1,column=0)
        self.entrylambda = tk.Entry(self.cmdM2)
        self.entrylambda.grid(row=2,column=0)

        self.labelSpace = tk.Label(self.cmdM2, text='  ', bg='gray')
        self.labelSpace.grid(row=3,column=0)

        self.labelz0 = tk.Label(self.cmdM2,text='Position du waist (en mm)',bg="gray")
        self.labelz0.grid(row=4,column=0)
        self.entryz0 = tk.Entry(self.cmdM2)
        self.entryz0.grid(row=5,column=0)

        self.labelSpace = tk.Label(self.cmdM2, text='  ', bg='gray')
        self.labelSpace.grid(row=6,column=0)

        self.labelw0 = tk.Label(self.cmdM2,text='diamètre waist (en µm)',bg="gray")
        self.labelw0.grid(row=7,column=0)
        self.entryw0 = tk.Label(self.cmdM2,text=self.ellipse_width.get())
        self.entryw0.grid(row=8,column=0)

        self.labelSpace = tk.Label(self.cmdM2, text='  ', bg='gray')
        self.labelSpace.grid(row=9,column=0)

        self.membutton= tk.Button(self.cmdM2,text="OK", command=self.memorise)
        self.membutton.grid(row=10,column=0)

        return 

    def destructor(self):
        """ Détruit les racines objet et arrête l'acquisition de toutes les sources """
        print("[INFO] closing...")
        self.window.quit()
        self.window.destroy() # Ferme la fenêtre
        return

    def destructorM2(self):
        """ Détruit les racines objet et arrête l'acquisition de toutes les sources """
        print("[INFO] closing...")
        self.windowM2.quit()
        self.windowM2.destroy() # Ferme la fenêtre
        return

    #Fonction définissant l'image à enregistrer   
    def choice0(self):
        self.coch0=1
        return
    
    def choice1(self):
        self.coch1=1
        return
 
    def choice2(self):
        self.coch2=1
        return

    def choice3(self):
        self.coch3=1
        return
 
    def choice4(self):
        self.coch4=1
        return

    def alignement(self):
        """Fonction pour alignement de faisceaux"""
        self.align=True
        return
    
    def arret_align(self):
        """Fonction d'arrêt de l'alignement"""
        self.align=False
        self.titre_gauss1.set("")
        self.titre_gauss2.set("")
        self.gauss_amp1.set(0)
        self.gauss_amp2.set(0)
        return

    def stop_profil(self):
        """Fonction permettant d'enlever le plots"""
        for widget in self.cadre_plots.winfo_children():
                widget.destroy()
                self.titre_gauss1.set("")
                self.titre_gauss2.set("")
                self.gauss_1.set(0)
                self.gauss_2.set(0)

    def hold(self):
        self.H=True
        self.Bx=self.baryX
        self.By=self.baryY
        return

    def DeNoise(self):
        self.noise=1
        return

    def memorise(self):
        self.lambda0 = float(self.entrylambda.get())*10**-9
        self.w0 = float(self.ellipse_width.get())*10**-6
        self.z0 = float(self.entryz0.get())*10**-3
        print("lambda = ",self.lambda0,"z0 = ",self.z0)
        self.mesuresM2()
        return

    def memoMeasures(self):
        Measures = np.zeros(7)
        Measures[0] = float(self.measure1.get())
        Measures[1] = float(self.measure2.get())
        Measures[2] = float(self.measure3.get())
        Measures[3] = float(self.measure4.get())
        Measures[4] = float(self.measure5.get())
        Measures[5] = float(self.measure6.get())
        Measures[6] = float(self.measure7.get())
        print(Measures)
        params = self.abc_fit(self.positions, Measures, self.lambda0)
        self.labelSpace = tk.Label(self.central, text='  ', bg='white')
        self.labelSpace.grid(row=10,column=1)
        self.title = tk.Label(self.central,text="Resultats du fit M2 (d0, z0, Theta, M2, zR) : ", bg='gray')
        self.title.grid(row=11,column = 1)
        self.affichparams = tk.Label(self.central,text=params, bg='gray')
        self.affichparams.grid(row=11,column = 2)
        return

    def mesuresM2(self):
        """Définition des zones d'affichage des z"""
        self.labeltitlez = tk.Label(self.central, text=' z (en mm) ', bg='gray')
        self.labeltitlez.grid(row=0,column=0)
        self.labeltitlew = tk.Label(self.central, text=' w (en µm) ', bg='gray')
        self.labeltitlew.grid(row=0,column=2)

        self.positions = np.zeros(7)
        rows=0
        Zr = np.pi * self.w0*self.w0 / self.lambda0
        delta = 2* Zr / 7
        n = -3
        line=0
        for line in range(7):
            rows=rows+1
            self.positions[line] = self.z0 + n*delta
            pos = tk.Label(self.central,text=self.positions[line])
            pos.grid(row=rows, column=0)
            space = tk.Label(self.central,text =" ")
            space.grid(row=rows, column=1)
            
            line=line+1
            n=n+1
        #Zones d'entrées indexées pour ranger les valeurs par la suite
        self.measure1 = tk.Entry(self.central)
        self.measure1.grid(row=1, column=2)
        self.measure2 = tk.Entry(self.central)
        self.measure2.grid(row=2, column=2)
        self.measure3 = tk.Entry(self.central)
        self.measure3.grid(row=3, column=2)
        self.measure4 = tk.Entry(self.central)
        self.measure4.grid(row=4, column=2)
        self.measure5 = tk.Entry(self.central)
        self.measure5.grid(row=5, column=2)
        self.measure6 = tk.Entry(self.central)
        self.measure6.grid(row=6, column=2)
        self.measure7 = tk.Entry(self.central)
        self.measure7.grid(row=7, column=2)

        self.labelSpace = tk.Label(self.central, text='  ', bg='white')
        self.labelSpace.grid(row=8,column=2)

        #Bouton OK
        self.membutton= tk.Button(self.central,text="OK", command=self.memoMeasures)
        self.membutton.grid(row=9,column=2)


    #####################
    #   Partie Camera   # 
    #####################

    def flux_cam(self):
        """Lance la fonction d'affichage de la preview  dans un thread"""
        self.t1=Thread(target=self.update(), args=(self.window, self.display1, self.Screen_x, self.Screen_y)) #boucle la fonction d'acquisition de la caméra
        self.t1.start()
        return
    
    def update(self):
        """Affichage de la preview"""
        #Get a frame from cameraCapture
        ratio=1

        #Récupère le flux basler si elle communique
        if self.basler==True:
            self.frame0 = self.vid.getFrame() #This is an array

        #Sinon récupère le flux opencv
        else :
            try :
                self.frame0 = self.cam.capture()
                cam_rat=False
            except :
                print("Problem to get an image") #Impossible de récuperer le flux de la caméra
                tk.messagebox.showerror("Problem to get an image") #Affichage d'un message d'erreur
                exit()

        self.frame=cv2.normalize(self.frame0, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1) #Convertit l'image en 8bits pour en permettre l'affichage sur tous les écrans
        frame=self.frame

        #Fonction d'alignement
        if self.align == True :
            test=True
            try :
                self.baryX
            except AttributeError: #Si le traitement d'image n'a pas été fait avant l'appui sur le bouton
                test=False
                self.align = False
                tk.messagebox.showerror("Alignement impossible", "Il faut traiter le premier faisceau pour permettre l'alignement. \n Pour cela cliquez sur le bouton traitement après ce message.")
            if self.H == False:
                if test == True:
                    #Dessine une croix sur l'écran pour permettre alignement
                
                    cv2.line(frame, (self.baryX, 0), (self.baryX, frame.shape[0]), (255, 0, 0), 3)#Dessine une croix sur le barycentre de l'image
                    cv2.line(frame, (0, self.baryY), (frame.shape[1], self.baryY), (255, 0, 0), 3)
            else:
                if test==True:
                    cv2.line(frame, (self.Bx, 0), (self.Bx, frame.shape[0]), (255, 0, 0), 3)#Dessine une croix sur le barycentre de l'image
                    cv2.line(frame, (0, self.By), (frame.shape[1], self.By), (255, 0, 0), 3)
                    otsu = cv2.GaussianBlur(frame,(5,5),0) #Met un flou gaussien
                    ret3,otsu = cv2.threshold(otsu,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
                    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
                    img_cls = cv2.morphologyEx(otsu, cv2.MORPH_CLOSE, kernel)
                    img_opn = cv2.morphologyEx(img_cls, cv2.MORPH_OPEN, kernel)
                    contours, hierarchy = cv2.findContours(otsu,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:1]
                    for c in contours:
                        M = cv2.moments(c)
                        if M["m00"] != 0:
                            self.cX = int(M["m10"] / M["m00"])
                            self.cY = int(M["m01"] / M["m00"])
                        else:
                            self.cX, self.cY = 0, 0
                    cv2.line(frame, (self.cX, 0), (self.cX, frame.shape[0]), (255, 0, 0), 1)#Dessine une croix sur le barycentre de l'image
                    cv2.line(frame, (0, self.cY), (frame.shape[1], self.cY), (255, 0, 0), 1)
                    self.titre_gauss1.set("X aligne :")
                    self.titre_gauss2.set("Y aligne :")
                    self.gauss_amp1.set(self.cX * self.pixel_size)
                    self.gauss_amp2.set(self.cY * self.pixel_size)

        #Get display size
        self.Screen_x = self.display1.winfo_width()
        self.Screen_y = self.display1.winfo_height()

        #Récupère le ratio d'affichage de la frame
        r = float(self.Screen_x/self.Screen_y)

        #Get picture ratio from Camera
        if self.basler==True :
            ratio = self.vid.ratio
        elif self.basler==False:
            ratio = self.cam.ratio

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

    def video_tool(self):
        self.t2 = Thread(target=self.disp_traitement)
        self.t2.start()

    def disp_traitement(self):
        if self.noise==1:
            self.frame= cv2.fastNlMeansDenoising( self.frame , None , 10 , 7 , 21)
            self.noise=0
        else :
            pass
        self.frame2, self.ellipse, self.baryX, self.baryY, self.choix_fig_XY = self.trmt.traitement(self.frame,self.choix_filtre)
        self.affich_traitement()
        return
    
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
        self.cX.set("{:.2f}".format(self.baryX * self.pixel_size))
        self.cY.set("{:.2f}".format(self.baryY * self.pixel_size) )
        self.ellipse_width.set("{:.2f}".format(int(self.ellipse[1][1]) * self.pixel_size)) #3 lignes pour extraction des données du tuple ellipse
        self.ellipse_height.set("{:.2f}".format(int(self.ellipse[1][0]) * self.pixel_size))
        self.ellipse_angle.set("{:.2f}".format(int(self.ellipse[2])))
        return

    def exp(self):
        """Lance la fonction d'auto expo de la classe onCameraCapture suite à la pression d'un bouton"""
        try :
            self.vid.auto_exposure()
        except :
            try :
                self.cam.auto_exposure()
            except :
                print("Exposure Problem")
                tk.messagebox.showerror("Problème d'exposition")
                pass
        return

    def choix_figure(self, parameter):
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

    def choose_filter(self,parameter):
        selection = self.liste_combobox2.get()
        if selection =="Otsu":
            self.choix_filtre=1
        if selection =="Adaptatif":
            self.choix_filtre=2
        if selection =="I/e²":
            self.choix_filtre=3
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
            self.fig_width = self.cadre_plots.winfo_width() 
            self.fig_height = self.cadre_plots.winfo_height()
                
            if self.choix_fig == 1 :
                self.fig_XY, x, y = self.trmt.trace_profil(self.dpi,self.fig_width,self.fig_height, self.pixel_size)
                self.titre_gauss1.set("Gaussienne X :")
                self.titre_gauss2.set("Gaussienne Y :")
                self.gauss_amp1.set('Amplitude: {:.3f} +\- {:.3f}'.format(x[0]* self.pixel_size, np.sqrt(x[3][0])* self.pixel_size))
                self.gauss_mean1.set('Mean: {:.3f} +\- {:.3f}'.format(x[1]* self.pixel_size, np.sqrt(x[3][1])* self.pixel_size))
                self.gauss_stddev1.set('Standard Deviation: {:.3f} +\- {:.3f}'.format(x[2]* self.pixel_size, np.sqrt(x[3][2])* self.pixel_size))
                self.gauss_amp2.set('Amplitude: {:.3f} +\- {:.3f}'.format(y[0]* self.pixel_size, np.sqrt(y[3][0])* self.pixel_size))
                self.gauss_mean2.set('Mean: {:.3f} +\- {:.3f}'.format(y[1]* self.pixel_size, np.sqrt(y[3][1])* self.pixel_size))
                self.gauss_stddev2.set('Standard Deviation: {:.3f} +\- {:.3f} µm'.format(y[2]* self.pixel_size, np.sqrt(y[3][2])* self.pixel_size))
            if self.choix_fig == 2 :
                self.fig_XY, g, p= self.trmt.trace_ellipse(self.dpi,self.fig_width,self.fig_height, self.pixel_size)
                self.titre_gauss1.set("Gaussienne ellipse G :")
                self.titre_gauss2.set("Gaussienne ellipse P :")
                self.gauss_amp1.set('Amplitude: {:.3f} +\- {:.3f}'.format(g[0]* self.pixel_size, np.sqrt(g[3][0])* self.pixel_size))
                self.gauss_mean1.set('Mean: {:.3f} +\- {:.3f}'.format(g[1]* self.pixel_size, np.sqrt(g[3][1])* self.pixel_size))
                self.gauss_stddev1.set('Standard Deviation: {:.3f} +\- {:.3f}'.format(g[2]* self.pixel_size, np.sqrt(g[3][2])* self.pixel_size))
                self.gauss_amp2.set('Amplitude: {:.3f} +\- {:.3f}'.format(p[0]* self.pixel_size, np.sqrt(p[3][0])* self.pixel_size))
                self.gauss_mean2.set('Mean: {:.3f} +\- {:.3f}'.format(p[1]* self.pixel_size, np.sqrt(p[3][1])* self.pixel_size))
                self.gauss_stddev2.set('Standard Deviation: {:.3f} +\- {:.3f} µm'.format(p[2]* self.pixel_size, np.sqrt(p[3][2])* self.pixel_size))
            if self.choix_fig == 3 :
                self.fig_XY, d = self.trmt.plot_2D(self.dpi,self.fig_width,self.fig_height)
                self.titre_gauss1.set("Gaussienne 2D :")
                self.titre_gauss2.set("")
                self.gauss_amp1.set('Amplitude: {:.3f} +\- {:.3f}'.format(d[0]* self.pixel_size, np.sqrt(d[6][0])* self.pixel_size))
                self.gauss_mean1.set('Mean x: {:.3f} +\- {:.3f}'.format(d[1]* self.pixel_size, np.sqrt(d[6][1])* self.pixel_size))
                self.gauss_stddev1.set('Mean y: {:.3f} +\- {:.3f}'.format(d[2]* self.pixel_size, np.sqrt(d[6][1])* self.pixel_size))
                self.gauss_amp2.set('Standard Deviation x: {:.3f} +\- {:.3f}'.format(d[3]* self.pixel_size, np.sqrt(d[6][2])* self.pixel_size))
                self.gauss_mean2.set('Standard Deviation y: {:.3f} +\- {:.3f}'.format(d[4]* self.pixel_size, np.sqrt(d[6][2])* self.pixel_size))
                self.gauss_stddev2.set('Theta: {:.3f} °'.format(d[5]))

        #cadre affichage profils
        self.disp_XY = FigureCanvasTkAgg(self.fig_XY, self.cadre_plots)
        self.toolbar = NavigationToolbar2Tk(self.disp_XY, self.cadre_plots,pack_toolbar=False)
        self.toolbar.grid(row=0,column=0)
        self.toolbar.update()    
        self.cadre_disp_XY = self.disp_XY.get_tk_widget()
        self.cadre_disp_XY.grid(row=1,column=0,sticky="NSEW")
        return self.fig_XY

    def abc_fit(self,z, d, lambda0):
    
        # Return beam parameters for beam diameter measurements.

        # Follows ISO 11146-1 section 9 and uses the standard `polyfit` routine
        # in `numpy` to find the coefficients `a`, `b`, and `c`.

        # d(z)**2 = a + b*z + c*z**2

        # These coefficients are used to determine the beam parameters using
        # equations 25-29 from ISO 11146-1.

        # Unfortunately, standard error propagation fails to accurately determine
        # the standard deviations of these parameters.  Therefore the error calculation
        # lines are commented out and only the beam parameters are returned.

        # Args:
        #     z: axial position of beam measurement [m]
        #     d: beam diameter [m]
        # Returns:
        #     d0: beam waist diameter [m]
        #     z0: axial location of beam waist [m]
        #     M2: beam propagation parameter [-]
        #     Theta: full beam divergence angle [radians]
        #     zR: Rayleigh distance [m]
    
        nlfit, _nlpcov = np.polyfit(z, d**2, 2, cov=True)

        # unpack fitting parameters
        c, b, a = nlfit


        z0 = -b/(2*c)
        Theta = np.sqrt(c)
        disc = np.sqrt(4*a*c-b*b)/2
        M2 = np.pi/4/lambda0*disc
        d0 = disc / np.sqrt(c)
        zR = disc/c
        params = [d0, z0, Theta, M2, zR]

        # unpack uncertainties in fitting parameters from diagonal of covariance matrix
        #c_std, b_std, a_std = [np.sqrt(_nlpcov[j, j]) for j in range(nlfit.size)]
        #z0_std = z0*np.sqrt(b_std**2/b**2 + c_std**2/c**2)
        #d0_std = np.sqrt((4*c**2*a_std)**2 + (2*b*c*b_std)**2 + (b**2*c_std)**2) / (8*c**2*d0)
        #Theta_std = c_std/2/np.sqrt(c)
        #zR_std = np.sqrt(4*c**4*a_std**2 + b**2*c**2*b_std**2 + (b**2-2*a*c)**2*c_std**2)/(4*c**3) / zR
        #M2_std = np.pi**2 * np.sqrt(4*c**2*a_std**2 + b**2*b_std**2 + 4*a**2*c_std**2)/(64*lambda0**2) / M2
        #errors = [d0_std, z0_std, M2_std, Theta_std, zR_std]
        return params

    def capture(self):
        """ Fonction permettant de capturer une image et de l'enregistrer avec l'horodatage """
        ts = datetime.datetime.now()
        try:
            os.mkdir('Snapshot') #Créer un dossier snapshot pour les images
        except OSError:
            pass
        path=self.output_path.joinpath('Save') #défini le path pour les images
        #print(path)
        while True :

            if self.coch0==1: #Enregistrement de la preview
                filename = "preview_{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # Construction du nom
                image = Img.fromarray(self.frame) #Création de l'image à partir de l'array
                #Boîte de dialogue de la sauvegarde
                S=filedialog.asksaveasfile (mode='w', title="Enregistrer sous",initialdir = path, defaultextension=".jpg", initialfile=filename, filetypes = (("JPEG files","*.jpg"),("all files","*.*")))
                image.save(S) #Sauvegarde
                S.close() #Fermeture de la boîte de dialogue
                print("[INFO] saved {}".format(filename))

            if self.coch1==1:#Enregistrement du traitement
                try :
                    self.photo2 
                    filename_2 = "treatment_{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
                    image2 = Img.fromarray(self.frame2)
                    S2=filedialog.asksaveasfile (mode='w', title="Enregistrer sous",initialdir = path, defaultextension=".jpg", initialfile=filename_2, filetypes = (("JPEG files","*.jpg"),("all files","*.*")))
                    image2.save(S2)
                    S2.close()
                    print("[INFO] saved {}".format(filename_2))
                except:
                    tk.messagebox.showerror("Save Problem", "Problème de traitement")
                    break

            if self.coch2==1:#Enregistrement des graphs
                if self.choix_fig != 0 :
                    filename_xy = "plot_{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
                    S3=filedialog.asksaveasfile (mode='w', title="Enregistrer sous",initialdir = path, defaultextension=".jpg", initialfile=filename_xy, filetypes = (("JPEG files","*.jpg"),("all files","*.*")))
                    self.fig_XY.savefig("plot", dpi=1200) #Sauvegarde du plot en 1200dpi
                    Im=Img.open("plot.png") #Transformation en image
                    im = Im.convert("RGB") #Convertion vers JPEG
                    im.save(S3)
                    S3.close()
                    print("[INFO] saved {}".format(filename_xy))
                else:
                    tk.messagebox.showerror("Save Problem", "Problème de Plots")
                    break

            if self.coch3==1:#Enregistrement des coordonnées
                try :
                    self.photo2
                    coord = "coordonnées_{}.txt".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
                    S4=filedialog.asksaveasfile (mode='w', title="Enregistrer sous",initialdir = path, defaultextension=".txt", initialfile=coord, filetypes = (("Text files","*.txt"),("all files","*.*")))
                    #Création d'un tuple à partir des données affichées
                    tup=("Barycentre X = ", str(self.cX.get()), " \u03BCm", "\n", "Barycentre Y = ", str(self.cY.get()), " \u03BCm", "\n\n", "Grand axe ellipse = ", str(self.ellipse_width.get()), " \u03BCm", "\n", "Petit axe ellipse = ", str(self.ellipse_height.get()), " \u03BCm", "\n", "Angle ellipse = ", str(self.ellipse_angle.get()), " °")
                    file=''.join(tup)
                    S4.write(file)
                    S4.close()
                    print("[INFO] saved {}".format(coord))
                except:
                    tk.messagebox.showerror("Save Problem", "Problème de traitement")
                    break

            if self.coch4==1:#Enregistrement des données pour les gauss 1D
                if self.choix_fig == 1 or self.choix_fig ==2 :
                    plot = "PlotData_{}.txt".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
                    S5=filedialog.asksaveasfile (mode='w', title="Enregistrer sous",initialdir = path, defaultextension=".txt", initialfile=plot, filetypes = (("Text files","*.txt"),("all files","*.*")))
                    tup2=(str(self.titre_gauss1.get()), "\n", str(self.gauss_amp1.get()), " µm", "\n", str(self.gauss_mean1.get()), " µm", "\n", str(self.gauss_stddev1.get()), " µm", "\n\n", str(self.titre_gauss2.get()), "\n", str(self.gauss_amp2.get()), " µm", "\n", str(self.gauss_mean2.get()), " µm", "\n", str(self.gauss_stddev2.get()), " µm")
                    file2=''.join(tup2)
                    S5.write(file2)
                    S5.close()
                    print("[INFO] saved {}".format(plot))

                if self.choix_fig == 3:#Enregistrement des données pour les gauss 2D
                    plot = "PlotData_{}.txt".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
                    S5=filedialog.asksaveasfile (mode='w', title="Enregistrer sous",initialdir = path, defaultextension=".txt", initialfile=plot, filetypes = (("Text files","*.txt"),("all files","*.*")))
                    tup2=(str(self.titre_gauss1.get()), "\n", str(self.gauss_amp1.get()), " µm", "\n", str(self.gauss_mean1.get()), " µm", "\n", str(self.gauss_stddev1.get()), " µm", "\n", str(self.gauss_amp2.get()), " µm", "\n", str(self.gauss_mean2.get()), " µm", "\n", str(self.gauss_stddev2.get()), " °")
                    file2=''.join(tup2)
                    S5.write(file2)
                    S5.close()
                    print("[INFO] saved {}".format(plot))

                else:
                    tk.messagebox.showerror("Save Problem", "Problème de Plots")
                    break

        self.coch0, self.coch1, self.coch2, self.coch3, self.coch4 =0,0,0,0,0
        return


root = Fenetre()
root.window.mainloop() # Lancement de la boucle principale