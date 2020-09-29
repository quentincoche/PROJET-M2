# -*- coding: utf-8 -*-
"""
Created on Thu May 31 14:55:02 2018

@author: Marin COR
Editée avec la version 3.6.6 de Python (64bits) compatible 3.7.0
Executable réalisée avec le module pyinstaller (pyinstaller -F Camera_1.py)
Réutilisation et modification autorisées
"""
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
import argparse
import datetime
import time

class Application():
    cam0 = int(input("Port de périphérique USB de la caméra : "))
    def __init__(self, output_path = "./"):
         """ Initialise l'application en utilisant OpenCV + Tkinter. Affiche le stream vidéo
            dans une fenêtre Tkinter (et enregistre les photos) """       
         #Capture vidéo
         self.cap0 = cv2.VideoCapture(self.cam0) # Acquisition du flux vidéo des périphériques
                  
         self.cap0.set(3, 1920) # Redéfinition de la taille du flux
         self.cap0.set(4, 1080) # Max (1920 par 1080)
         
         self.output_path = output_path  # chemin de la sortie de la photo

         #Edition de l'interface
         self.window = tk.Tk()  #Réalisation de la fenêtre principale
         self.window.wm_title("Goniomètre") # Nom de la fenêtre
         self.window.config(background="#FFFFFF") # Couleur de la fenêtre
         self.window.protocol('WM_DELETE_WINDOW', self.destructor) # Fonction associé à la fermeture de la fenêtre
         
         self.Menu() # Lance la fonction menu
         self.video_loop() # Lance la fonction video_loop

#########
    def Menu(self):
        for c in self.window.winfo_children(): # Permet de nettoyer l'affichage
            c.destroy()
        self.display1 = tk.Label(self.window)  # Initialisation de l'écran 1
        self.display1.grid(row=0, column=0, columnspan=4, padx=10)
         
        self.display30 = tk.Label(self.window)
        self.display30.grid(row=1, column=0, rowspan=4)

        self.affich=0 # Initialisation de la variable  de sélection des fenêtres
         
        #Bouton de fermeture de la fenêtre
        bouton_quit=tk.Button(self.window, text="Fermer", command=self.destructor)
        bouton_quit.grid(row=8, column=4)


        self.Frame1=tk.Frame(self.window, borderwidth=2, relief='groove') # Initialisation des cadres contenants les différents boutons
        self.Frame1.grid(row=1, column=1, rowspan=4, padx=5, pady=5)
        self.c0=tk.IntVar()
        self.Frame2=tk.Frame(self.window, borderwidth=2, relief='groove')
        self.Frame2.grid(row=1, column=2, rowspan=4, padx=5, pady=5)
        self.c0=tk.IntVar()
        
	# Création d'espaces permettant une cohérence spatiale des cadres
        labelSpace1=tk.Label(self.Frame1, text="")
        labelSpace1.grid(row=0, column=0)
        labelSpace2=tk.Label(self.Frame1, text="")
        labelSpace2.grid(row=1, column=0)
        labelSpace5=tk.Label(self.Frame2, text="")
        labelSpace5.grid(row=0, column=0)
        labelSpace6=tk.Label(self.Frame2, text="")
        labelSpace6.grid(row=1, column=0)
		
        #Label du cadre de choix des grandes images
        label0=tk.Label(self.Frame1, text="Choix Image :")
        label0.grid(row=0, column=1)
        
	#Bouton à cocher permettant de basculer un flux précis dans la fenêtre principale
        bouton=tk.Button(self.Frame1, text="Couleur", command=self.affich0)
        bouton.grid(row=2, column=1)
        bouton=tk.Button(self.Frame1, text="Dérivées", command=self.affich1)
        bouton.grid(row=3, column=1)
		
		# Label du cadre de choix des images à faire basculer en plein écran
        label0=tk.Label(self.Frame2, text="Agrandissement Image :")
        label0.grid(row=0, column=1)
    
		# Bouton à cocher permettant de basculer un flux précis en plein écran
        self.up0, self.up4 = 0,0
        boutonf=tk.Button(self.Frame2, text="Couleur", command=self.upscreen0)
        boutonf.grid(row=2, column=1)
        boutonf=tk.Button(self.Frame2, text="Dérivées", command=self.upscreen4)
        boutonf.grid(row=3, column=1)

        labelSpace=tk.Label(self.window, text="") # Créer un espace avant la suite de l'interface
        labelSpace.grid(row=5, column=0, columnspan=7, rowspan=2)

        # Créer un bouton qui lorsqu'il est pressé, va enregistrer l'image affiché
        btn = tk.Button(self.window, text="Capture !", command=self.take_snapshot)
        btn.grid(row=6, column=0, rowspan=3, ipadx=50, ipady=10)
         
        #Sélection de l'image à capturer
        self.Frame5=tk.Frame(self.window, borderwidth=2, relief='groove')
        self.Frame5.grid(row=6, column=1, rowspan=3, columnspan=2)
        self.c0=tk.IntVar()

        label_check0=tk.Label(self.Frame5, text="Images à enregistrer")
        label_check0.grid(row=0, column=0)
        
        #Bouton à cocher permettant de sélectionner l'image à enregistrer
        self.coch0,self.coch1=0,0
        bouton_selection = tk.Checkbutton(self.Frame5, text="Couleur", command=self.choice0)
        bouton_selection.grid(row=1, column=0)
        bouton_selection = tk.Checkbutton(self.Frame5, text="Dérivées", command=self.choice1)
        bouton_selection.grid(row=2, column=0)
        
#########         
# fonction permettant de sélectionner l'affichage principale
    def affich0(self):
        self.affich=0
    
    def affich1(self):
        self.affich=1
        
#########
     #Fonction définissant l'image à enregistrer   
    def choice0(self):
        self.coch0=1
    
    def choice1(self):
        self.coch1=1


#########
    # Fonction permettant de placer un flux en plein écran
    def upscreen0(self):
        self.up0=1
        for c in self.window.winfo_children(): # permet de nettoyer l'affichage de window
            c.destroy()
        self.disp0 = tk.Label(self.window) 	#permet de mettre d'aposer le flux dans toute la fenêtre
        self.disp0.grid(row=0, column=0)
        bouton_menu=tk.Button(self.window, text="Menu", command=self.Menu) # Bouton permettant le retour au menu
        bouton_menu.grid(row=0, column=1)

    def upscreen4(self):
        self.up4=1
        for c in self.window.winfo_children():
            c.destroy()
        self.disp2 = tk.Label(self.window)
        self.disp2.grid(row=0, column=0)
        bouton_menu=tk.Button(self.window, text="Menu", command=self.Menu)
        bouton_menu.grid(row=0, column=1)

#########
    def video_loop(self):
        """ Récupère les images de la vidéo et l'affiche dans Tkinter"""
        ok0, frame0 = self.cap0.read() # lecture des images de la vidéo
        self.frame0 = frame0 #transformation de la variable en variable exploitable par toutes les fonctions
        
        cv2image0 = cv2.cvtColor(self.frame0, cv2.COLOR_BGR2RGBA) # converti les couleurs du BGR vers le RGB 
        
        self.im0 = Image.fromarray(cv2image0) # Convertit l'image pour PIL      
        
    #Opération sur les images
        imgtest0 = cv2.cvtColor(self.frame0, cv2.COLOR_BGR2GRAY)# Converti les images du BGR vers le blanc/noir
        
        sobelx0 = cv2.Sobel(imgtest0,cv2.CV_64F,1,0,ksize=5) # Dérivée selon x de la première imagegrad according to x
        sobely0 = cv2.Sobel(imgtest0,cv2.CV_64F,0,1,ksize=5) # Dérivée selon y de la première image
        
        laplacian0=cv2.add(sobelx0,sobely0)
        self.iml0 = Image.fromarray(laplacian0) # Transforme la variable
        
        if self.up0==1: # Permet de redéfinir la taille de l'affichage qui va être mis en plein écran
            self.imag0=self.im0.resize((1440,810))
            imtk0 = ImageTk.PhotoImage(image=self.imag0)
            self.disp0.imgtk = imtk0
            self.disp0.config(image=imtk0)
        elif self.up4==1:
            self.imagl0=self.iml0.resize((1440,810))
            imtkl0 = ImageTk.PhotoImage(image=self.imagl0)
            self.disp2.imgtk = imtkl0
            self.disp2.config(image=imtkl0)
        else:
            # étape permettant de redéfinir les tailles d'image en vue de changer les fenêtres
            self.img0=self.im0.resize((960,540)) 
                
            if self.affich==1:
                self.img0=self.im0.resize((320,180))
                self.imgl0=self.iml0.resize((960,540)) #Redéfini les tailles d'image pour changer le cadre
                 
            else:
                self.imgl0=self.iml0.resize((320,180))
                        
            imgtk0 = ImageTk.PhotoImage(image=self.img0) # Converti l'image pour Tkinter
            imgtkl0 = ImageTk.PhotoImage(image=self.imgl0) #Transforme l'image pour Tkinter
        
            if self.affich==1:#Inversion des cadres en vue de repositionner les différents streams
                temp=imgtk0
                imgtk0=imgtkl0
                imgtkl0=temp
                        
            self.display1.imgtk = imgtk0 # ancrer imgtk afin qu'il ne soit pas supprimé par garbage-collector
            self.display1.config(image=imgtk0) # Montre l'image

            self.display30.imgtk = imgtkl0 #On répète l'opération pour chaque flux
            self.display30.config(image=imgtkl0)
        
        self.window.after(10, self.video_loop) # rappel la fonction après 10 millisecondes
           
    def take_snapshot(self):
        """ Prends une photo et la sauvegarde dans le même dossier que le programme """
        ts = datetime.datetime.now() # récupère le temps actuel
        
        if self.coch0==1:
            filename = "Couleur0_{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # Construction du nom
            p = os.path.join(self.output_path, filename)  # construit le chemin de sortie
            self.im0.save(p, "PNG")  # Sauvegarde l'image sous format png
            print("[INFO] saved {}".format(filename))
        if self.coch1==1:
            filename1 = "Dérivées0_{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  
            p1 = os.path.join(self.output_path, filename1)
            self.iml0 = self.iml0.convert('RGB') # Converti l'image en couleur, n'a pas d'intérêt en soi
            self.iml0.save(p1, "PNG")            # mais permet d'éviter les conflits d'enregistrement
            print("[INFO] saved {}".format(filename1))
        

    def destructor(self):
        """ Détruit les racines objet et arrête l'acquisition de toutes les sources """
        print("[INFO] closing...")
        self.window.destroy() # Ferme la fenêtre
        self.cap0.release()  # lâche le flux vidéo
        cv2.destroyAllWindows()  # Pas nécessaire mais plus sûr
        print ("")
        print("Ecrit et produit par Marin COR, 01/08/2018") # Statut du programme
        print("Réutilisation et modification autorisées")
        time.sleep(5)


###############################################################################       
# Construit l'analyse des arguments et les analysent
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", default="./", #Ecrit le chemin de sortie des images sauvegardées
help="path to output directory to store snapshots (default: current folder")
args = vars(ap.parse_args())

# start the app
print("[INFO] starting...")
pba = Application(args["output"])
pba.window.mainloop() #Boucle la classe
