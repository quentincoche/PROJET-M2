# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 09:22:21 2020

@author: Optique
"""
from pypylon import pylon #Bibliothèque Basler d'interfaçage de la caméra
from PIL import Image as Img #Bibliothèque de traitement d'image
from PIL import ImageTk
import cv2 #Bibliothèque d'interfaçage de caméra et de traitement d'image
import tkinter as tk
from tkinter import (ttk,IntVar,DoubleVar,StringVar,Entry)
from tkinter import BOTH, LEFT, FLAT, SUNKEN, RAISED, GROOVE, RIDGE
from threading import Thread
import time #Bibliothèque permettant d'utiliser l'heure de l'ordinateur
import datetime #Bibliothèque permettant de récupérer la date
import os #Bibliothèque permettant de communiquer avec l'os et notamment le "path"
from pathlib import Path
import numpy as np #Bibliothèque de traitement des vecteurs et matrice
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)
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
        self.output_path = output_path  #Chemin de sortie de la photo

        """"Creation de la fenetre principale : window"""
        self.window = tk.Tk()  #Réalisation de la fenêtre principale
        self.window.state('zoomed')
         
        self.window.title("Beam analyzer Python")
        self.window.config(background="#FFFFFF") #Couleur de la fenêtre
        self.window.protocol('WM_DELETE_WINDOW', self.destructor) #La croix de la fenetre va fermer le programme
        
        """"definition des proportions pour les frames"""
        self.window.grid_columnconfigure(1, weight=3)
        self.window.grid_columnconfigure(2,weight=2)
        self.window.grid_rowconfigure(1, weight=3)
        self.window.grid_rowconfigure(2, weight=3)
        
        """Definition de certaines variables nécessaires au demarrage de l'interface"""

        #choix de la figure à plotter (0 = figure vide, par défaut)
        self.choix_fig_XY = IntVar()
        self.choix_fig_XY = 0
        self.choix_fig=0

        #variables du barycentre et de l'ellipse opencv
        self.cX = DoubleVar()
        self.cY = DoubleVar()
        self.ellipse_width = DoubleVar()
        self.ellipse_height = DoubleVar()
        self.ellipse_angle =DoubleVar()

        #Variables du fit ellipse
        self.ellipse_width = DoubleVar()
        self.ellipse_height = DoubleVar()
        self.ellipse_angle =DoubleVar()
        self.titre_gauss1=StringVar()
        self.titre_gauss2=StringVar()
        self.gauss_1=DoubleVar()
        self.gauss_2=DoubleVar()

        #init variables taille d'ecran
        self.Screen_x = 1500
        self.Screen_y = 1000
        self.Screen2_x = 750
        self.Screen2_y = 750

        #delai d'actualisation de l'interface
        self.delay=15

        self.frame2=[]
        self.align=False
        
        
        #Demarrage des instances dans le bon ordre
        self.display() #lance les espaces d'affichage
        self.Interface() #Lance la fonction Interface
        self.flux_cam() #debut de la capture video

        #detection du nombre de pixels par pouce: utile pour l'affichage des plots
        self.dpi = self.cadre_plots.winfo_fpixels('1i')
        self.pixel_size = self.vid.pixel_size
        
        

    #########################
    #   Partie Interface    # 
    #########################       


    def Interface(self):
        """ Fonction permettant de créer l'interface dans laquelle sera placé toutes les commandes et visualisation permettant d'utiliser le programme """
        
        #commandes gauche
        self.cmdleft = tk.Frame(self.window,padx=5,pady=5,bg="gray",relief = RIDGE) #definition de la frame
        self.cmdleft.grid(row=1,column=0,rowspan=2, sticky='NSEW') #place la Frame

        #Zone sélection de la partie a capturer
        self.FrameCapture=tk.Frame(self.cmdleft, borderwidth=2, relief='groove')
        self.FrameCapture.grid(row=0, column=0, sticky="nsew")

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

        #Boutton capture
        btncap = tk.Button(self.cmdleft,text="Capture",command=self.capture)
        btncap.grid(row=1,column=0,sticky="nsew")

        labelSpace1=tk.Label(self.cmdleft, text='', bg='gray')
        labelSpace1.grid(row=2,column=0)   

        #Liste selection du plot
        selection_plot=tk.Label(self.cmdleft,text="Selectionnez Fit",bg="gray")
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

        labelSpace2=tk.Label(self.cmdleft, text='', bg='gray')
        labelSpace2.grid(row=7,column=0) 

        #Bouton alignement de faisceaux
        btnalign = tk.Button(self.cmdleft, text='Alignement de faisceaux', command=self.alignement)
        btnalign.grid(row=8, column=0, sticky="nsew")
        #Bouton arrêt alignement
        btn_stopalign = tk.Button(self.cmdleft, text='Arrêt alignement', command=self.arret_align)
        btn_stopalign.grid(row=9, column=0, sticky="nsew")

        labelSpace3=tk.Label(self.cmdleft, text='', bg='gray')
        labelSpace3.grid(row=10,column=0)   

        #Boutton pour quitter l'appli
        btnquit = tk.Button(self.cmdleft,text="Quitter",command = self.destructor)
        btnquit.grid(row=11,column=0,sticky="nsew")
           
        
        #commandes superieures
        self.cmdup = tk.Frame(self.window,borderwidth=4,relief="ridge",bg="gray") #définition de la frame
        self.cmdup.grid(row=0,column=1, sticky="NSEW") #place la frame

        btnvideo = tk.Button(self.cmdup,text="Traitement video", command=self.video_tool)
        btnvideo.grid(row=0,column=0,sticky="nsew")
        btnexp = tk.Button(self.cmdup,text="Réglage auto temps exp", command=self.exp)
        btnexp.grid(row=0,column=1,sticky="nsew")
        

    def display(self):
        #cadre video
        self.display1 = tk.Canvas(self.window, borderwidth=4,bg="gray",relief="ridge")  # Définition de l'écran 1
        self.display1.grid(row=1,column=1,sticky="NSEW")
        self.Screen_x = self.display1.winfo_width()
        self.Screen_y = self.display1.winfo_height()

        #cadre traitement
        self.title_display2 = tk.Label(self.window,text="Fit ellipse",borderwidth=4,bg="gray",relief="ridge")
        self.title_display2.grid(row=0,column=2,sticky="NSEW")
        self.display2 = tk.Canvas(self.window, width=self.Screen2_x/2, height=self.Screen2_y/2,bg="gray",relief="ridge")  # Def de l'écran 2
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
        self.labelg10=tk.Label(self.results,textvariable=self.titre_gauss1)
        self.labelg10.grid(row=5,column=0,sticky="nsew")
        self.labelg11 = tk.Label(self.results,textvariable=self.gauss_1)
        self.labelg11.grid(row=5,column=1,sticky="nsew")
        self.labelg01=tk.Label(self.results,textvariable=self.titre_gauss2)
        self.labelg01.grid(row=6,column=0,sticky="nsew")
        self.labelg12 = tk.Label(self.results,textvariable=self.gauss_2)
        self.labelg12.grid(row=6,column=1,sticky="nsew")





    def destructor(self):
        """ Détruit les racines objet et arrête l'acquisition de toutes les sources """
        print("[INFO] closing...")
        #self.fig_XY.clear()
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
        for widget in self.cadre_plots.winfo_children():
                widget.destroy()
                self.titre_gauss1.set("")
                self.titre_gauss2.set("")
                self.gauss_1.set(0)
                self.gauss_2.set(0)


    #####################
    #   Partie Camera   # 
    #####################


    def flux_cam(self):
        self.t1=Thread(target=self.update(), args=(self.window, self.display1, self.Screen_x, self.Screen_y)) #boucle la fonction d'acquisition de la caméra
        self.t1.start()

    def update(self):

        """Affichage de la preview"""
        #Get a frame from cameraCapture
        self.frame0 = self.vid.getFrame() #This is an array
        self.frame0=cv2.normalize(self.frame0, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1)
        self.frame=cv2.flip(self.frame0,0)

        if self.align == True :
            test=True
            try :
                self.baryX
            except AttributeError:
                test=False
                self.align = False
                tk.messagebox.showerror("Alignement impossible", "Il faut traiter le premier faisceau pour permettre l'alignement. \n Pour cela cliquez sur le bouton traitement après ce message.")
            if test == True:
                cv2.line(self.frame, (self.baryX, 0), (self.baryX, self.frame.shape[0]), (255, 0, 0), 3)#Dessine une croix sur le barycentre de l'image
                cv2.line(self.frame, (0, self.baryY), (self.frame.shape[1], self.baryY), (255, 0, 0), 3)

        #Get display size
        self.Screen_x = self.display1.winfo_width()
        self.Screen_y = self.display1.winfo_height()
        r = float(self.Screen_x/self.Screen_y)

        #Get picture ratio from oneCameraCapture
        ratio = self.vid.ratio
        #keep ratio
        if r > ratio:
            self.Screen_x = int(round(self.display1.winfo_height()*ratio))
        elif r < ratio:
            self.Screen_y = int(round(self.display1.winfo_width()/ratio))

        #resize the picture
        frame = cv2.resize(self.frame, dsize=(self.Screen_x,self.Screen_y), interpolation=cv2.INTER_AREA)

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
        filename = "image_{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # Construction du nom
        p = os.path.join(self.output_path, filename)  # construit le chemin de sortie
        self.frame.save(p, "PNG")  # Sauvegarde l'image sous format png
        print("[INFO] saved {}".format(filename))

    def video_tool(self):
        self.t2 = Thread(target=self.disp_traitement)
        self.t2.start()

    def disp_traitement(self):
        self.frame2, self.ellipse, self.baryX, self.baryY, self.choix_fig_XY = self.trmt.traitement(self.frame)
        self.affich_traitement()
        GP1, GP2, PP1, PP2 = self.trmt.points_ellipse()
        print("GP1=",GP1,"GP2=", GP2, "PP1=",PP1, "PP2=",PP2)
    
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
        self.cX.set(self.baryX * self.pixel_size)
        self.cY.set(self.baryY * self.pixel_size) 
        self.ellipse_width.set(int(self.ellipse[1][1]) * self.pixel_size) #3 lignes pour extraction des données du tuple ellipse
        self.ellipse_height.set(int(self.ellipse[1][0]) * self.pixel_size)
        self.ellipse_angle.set(int(self.ellipse[2]))

        #Conversion en microns
        # self.cX = self.cX * self.pixel_size
        # self.cY = self.cY * self.pixel_size
        # self.ellipse_width = self.ellipse_width * self.pixel_size
        # self.ellipse_height = self.ellipse_height * self.pixel_size
        # self.ellipse_angle = self.ellipse_angle * self.pixel_size

    def exp(self):
        """Lance la fonction d'auto expo de la classe onCameraCapture suite à la pression d'un bouton"""
        self.exposure=self.vid.auto_exposure()

    def px2m(self,param):
        #Convertit les données en pixels vers microns
        param_um = param * self.pixel_size
        return param



    def choix_figure(self,param):
        selection = self.liste_combobox.get()
        if selection =="Choix":
            choix_fig=0
        if selection =="Fit XY":
            choix_fig=1
        if selection =="Fit axes ellipse":
            choix_fig=2
        if selection =="Fit Gaussien 2D":
            choix_fig=3
        self.choix_fig_XY=choix_fig
        return self.choix_fig_XY

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
        if self.choix_fig_XY > 0:
            self.fig_width = self.cadre_plots.winfo_width() 
            self.fig_height = self.cadre_plots.winfo_height()
        if self.choix_fig_XY == 1 :
            self.fig_XY, x, y = self.trmt.trace_profil(self.dpi,self.fig_width,self.fig_height)
            self.titre_gauss1.set("Gaussienne X :")
            self.titre_gauss2.set("Gaussienne Y :")
            self.gauss_1.set(x)
            self.gauss_2.set(y)
        if self.choix_fig_XY == 2 :
            self.fig_XY, g, p = self.trmt.trace_ellipse(self.dpi,self.fig_width,self.fig_height)
            self.titre_gauss1.set("Gaussienne ellipse G :")
            self.titre_gauss2.set("Gaussienne ellipse P :")
            self.gauss_1.set(g)
            self.gauss_2.set(p)
        if self.choix_fig_XY == 3 :
            self.fig_XY, d = self.trmt.plot_2D(self.dpi,self.fig_width,self.fig_height)
            self.titre_gauss1.set("Gaussienne 2D :")
            self.titre_gauss2.set("")
            self.gauss_1.set(d)
            self.gauss_2.set(0)

        #cadre affichage profils
        self.disp_XY = FigureCanvasTkAgg(self.fig_XY, self.cadre_plots)
        self.toolbar = NavigationToolbar2Tk(self.disp_XY, self.cadre_plots)#,pack_toolbar=False)
        self.toolbar.grid(row=0,column=0)
        self.toolbar.update()    
        self.cadre_disp_XY = self.disp_XY.get_tk_widget()
        self.cadre_disp_XY.grid(row=1,column=0,sticky="NSEW")
        
        return self.fig_XY

    

        

root = Fenetre()
root.window.mainloop() # Lancement de la boucle principale