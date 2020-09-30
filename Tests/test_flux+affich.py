import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
import argparse
import datetime
import time

class Application():
    def __init__(self, output_path = "./"):
        """ Initialise l'application en utilisant OpenCV + Tkinter. Affiche le stream vidéo
            dans une fenêtre Tkinter (et enregistre les photos) """       
        #Capture vidéo
        self.cap0 = cv2.VideoCapture(0) # Acquisition du flux vidéo des périphériques
                  
        self.cap0.set(3, 1920) # Redéfinition de la taille du flux
        self.cap0.set(4, 1080) # Max (1920 par 1080)
        self.output_path = output_path  # chemin de la sortie de la photo
        #Edition de l'interface
        self.window = tk.Tk()  #Réalisation de la fenêtre principale
        self.window.wm_title("Analyseur de faisceaux") # Nom de la fenêtre
        self.window.config(background="#FFFFFF") # Couleur de la fenêtre
        self.window.protocol('WM_DELETE_WINDOW', self.destructor) # Fonction associé à la fermeture de la fenêtre
        
        self.Menu() # Lance la fonction menu
        self.video_loop() # Lance la fonction video_loop
    
    def Menu(self):
        for c in self.window.winfo_children(): # Permet de nettoyer l'affichage
            c.destroy()
        self.display1 = tk.Label(self.window)  # Initialisation de l'écran 1
        self.display1.grid(row=0, column=0, columnspan=4, padx=10)


        #Bouton de fermeture de la fenêtre
        bouton_quit=tk.Button(self.window, text="Fermer", command=self.destructor)
        bouton_quit.grid(row=8, column=4)

        self.c0=tk.IntVar()

         # Créer un bouton qui lorsqu'il est pressé, va enregistrer l'image affiché
        btn = tk.Button(self.window, text="Capture !", command=self.take_snapshot)
        btn.grid(row=6, column=0, rowspan=3, ipadx=50, ipady=10)


    def video_loop(self):
        """ Récupère les images de la vidéo et l'affiche dans Tkinter"""
        ok0, frame0 = self.cap0.read() # lecture des images de la vidéo
        self.frame0 = frame0 #transformation de la variable en variable exploitable par toutes les fonctions
        
        self.im0 = Image.fromarray(self.frame0) # Convertit l'image pour PIL    
        self.img0=self.im0.resize((960,540))
        imgtk0 = ImageTk.PhotoImage(image=self.img0) # Converti l'image pour Tkinter
        self.display1.imgtk = imgtk0 # ancrer imgtk afin qu'il ne soit pas supprimé par garbage-collector
        self.display1.config(image=imgtk0) # Montre l'image

        self.window.after(10, self.video_loop) # rappel la fonction après 10 millisecondes


    def take_snapshot(self):
        """ Prends une photo et la sauvegarde dans le même dossier que le programme """
        ts = datetime.datetime.now() # récupère le temps actuel
        filename = "Image_{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # Construction du nom
        p = os.path.join(self.output_path, filename)  # construit le chemin de sortie
        self.im0.save(p, "PNG")  # Sauvegarde l'image sous format png
        print("[INFO] saved {}".format(filename))

    def destructor(self):
        """ Détruit les racines objet et arrête l'acquisition de toutes les sources """
        print("[INFO] closing...")
        self.window.destroy() # Ferme la fenêtre
        self.cap0.release()  # lâche le flux vidéo
        cv2.destroyAllWindows()  # Pas nécessaire mais plus sûr


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