    # -*- coding: utf-8 -*-
"""
Created on Wen Oct 14 10:27:21 2020

@author: Optique
"""
    
import os    
import cv2 #Bibliothèque d'interfaçage de caméra et de traitement d'image
import numpy as np #Bibliothèque de traitement des vecteurs et matrice
import math
import matplotlib.pyplot as plt #Bibliothèque d'affichage mathématiques
from matplotlib.figure import Figure 
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import rcParams
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from scipy.optimize import curve_fit
import astropy.io.fits as fits
from astropy import modeling
from skimage.draw import line
import statistics
from statistics import mean
import time #Bibliothèque permettant d'utiliser l'heure de l'ordinateur

rcParams.update({'figure.autolayout': True})

class Traitement():
    
    def traitement(self, img):
        gray=cv2.normalize(img, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1)
        img_trait, img_bin=self.binarisation(gray)
        self.img = img_trait
        img100, ellipse, cX, cY=self.calcul_traitement(img_trait, img_bin)
        choix_fig = 1
        return img100, ellipse, cX, cY, choix_fig


    def binarisation(self,img):
        """ Filtrage de l'image et binarisation de celle-ci"""
        kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10,10))

        otsu = cv2.GaussianBlur(img,(5,5),0) #Met un flou gaussien
        ret3,otsu = cv2.threshold(otsu,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) #Applique le filtre d'Otsu
        img_opn = cv2.morphologyEx(otsu, cv2.MORPH_OPEN, kernel)
        #frame= cv2.fastNlMeansDenoising( img , None , 10 , 7 , 21)

        return img, img_opn



    def calcul_traitement(self,frame, otsu):
        """ Amélioration de l'image par binarisation d'Otsu """

        #Remet l'image en RGB pour y dessiner toutes les formes par la suite et en couleur
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        
        M=cv2.moments(otsu)
        # calculate x,y coordinate of center
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        print('barycentre : ', cX, ',', cY)

        # find contours in the binary image
        contours, hierarchy = cv2.findContours(otsu,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key = cv2.contourArea, reverse = True)[:1]

        for c in contours:
            # permet de fit une ellipse sur toutes les formes identifiés sur l'image
            if len(c) < 5:
                break
            
            area = cv2.contourArea(c)
            if area <= 1000:  # skip ellipses smaller then 
                continue

            # calculate moments for each contour
            M = cv2.moments(c)

        # calculate x,y coordinate of center
            if M["m00"] != 0:
                self.cX = int(M["m10"] / M["m00"])
                self.cY = int(M["m01"] / M["m00"])
            else:
                self.cX, self.cY = 0, 0

            #Dessine un cercle sur tous les blobs de l'image (formes blanches)
            cv2.circle(frame, (self.cX, self.cY), 2, (0, 0, 255), -1)

            #Fit une ellipse sur le(s) faisceau(x)
            self.ellipse = cv2.fitEllipse(c)
            thresh = cv2.ellipse(frame,self.ellipse,(0,255,0),1)
            print('Ellipse : ', self.ellipse)

            
            #Fit un rectangle sur la zone d'intérêt pour la zoomer par la suite
            self.x,self.y,self.w,self.h = cv2.boundingRect(c)
            #rectangle = cv2.rectangle(frame,(self.x,self.y),(self.x+self.w,self.y+self.h),(0,175,175),1)
            print('Rectangle : Position = ', self.x,',',self.y,'; Size = ',self.w,',',self.h)

        #Dessine les formes sur l'image
        cv2.line(frame, (self.cX, 0), (self.cX, frame.shape[0]), (255, 0, 0), 1)#Dessine une croix sur le barycentre de l'image
        cv2.line(frame, (0, self.cY), (frame.shape[1], self.cY), (255, 0, 0), 1)

        crop_img = self.crop(frame)
        self.crop_img = self.crop(self.img)

        return crop_img, self.ellipse, cX, cY

    def crop(self,frame):
        """ Fonction qui crop le centre d'intérêt à 2 fois sa taille"""

        X=self.x-math.ceil(self.w/2)
        Y=self.y-math.ceil(self.h/2)
        self.W=2*self.w
        self.H=2*self.h
        
        if X<0:
            X=0
            off_x=self.x-X
            self.W=self.w+2*off_x
        if Y<0:
            Y=0
            off_y=self.y-Y
            self.H=self.h+2*off_y
        if X+self.W>frame.shape[1]:
            W=frame.shape[1]-(X+self.w)
            X=X+self.w-W
        if Y+self.H>frame.shape[0]:
            self.H=frame.shape[0]-(Y+self.h)
            Y=Y+self.h-self.H

        crop_img = frame[Y:Y+self.H,X:X+self.W]
        return crop_img

    def trace_profil(self,dpi,width,height):
        """Trace le profil d'intensité sur les axes du barycentre de l'image"""
        t=time.time()
        print('Start plot Gauss x,y')
        img=self.crop_img # on récupère l'image
        #on pose les variables et on récupère les informations de l'image
        Lx,Ly=[],[]
        img_y, img_x =img.shape
        w=math.ceil(self.W/2)
        h=math.ceil(self.H/2)
 
        # on récupère la valeur des pixels selon les axes
        for iy in range(img_y):
            Ly=np.append(Ly,img[iy, w])
        for ix in range(img_x):
            Lx=np.append(Lx, img[h, ix])

        #on fait une liste de ces valeurs
        x=np.arange(img_x)
        y=np.arange(img_y)

        sigma_x = np.std(Lx)
        sigma_y = np.std(Ly)

        #on prépare la fonction de fit gaussien en précisant la méthode de fit
        fitter = modeling.fitting.LevMarLSQFitter()

        #courbe gaussien selon les axes x et y
        modelx = modeling.models.Gaussian1D(amplitude=np.max(Lx), mean=w, stddev=sigma_x)   # depending on the data you need to give some initial values
        modely = modeling.models.Gaussian1D(amplitude=np.max(Ly), mean=h, stddev=sigma_y)

        #fit des courbes et des données
        x_fitted_model = fitter(modelx, x, Lx)
        y_fitted_model = fitter(modely, y, Ly)

        #paramètres pour affichage correct
        fig_width_i = width / dpi
        fig_height_i = height / dpi

        #On affiche les courbes résultantes
        fig = Figure()
        fig.set_size_inches(fig_width_i,fig_height_i)
        fig.suptitle("Gaussienne x,y")
        ax = fig.add_subplot(1 ,2 ,1)
        ax.plot(x,Lx)
        ax.plot(x, x_fitted_model(x))
        ax2 = fig.add_subplot(1, 2, 2)
        ax2.plot(y,Ly)
        ax2.plot(y, y_fitted_model(y))
        ax.set_title('X profil')
        ax.set_xlabel ("Largeur de l'image en pixels")
        ax.set_ylabel ("Intensité sur 8bits")
        ax2.set_title ('Y profil')
        ax2.set_xlabel ("Hauteur de l'image en pixels")
        ax2.set_ylabel ("Intensité sur 8bits")

        temps=time.time()-t
        print("Temps plot Gauss x,y : ", temps)

        return fig, x_fitted_model, y_fitted_model

    def plot_2D(self,dpi,width,height):

        t=time.time()
        print("start plot Gauss 2D")
        img=self.crop_img # on récupère l'image
        fitter = modeling.fitting.LevMarLSQFitter()

        y0, x0 = np.unravel_index(np.argmax(img), img.shape)
        sigma = np.std(img)
        amp=np.max(img)

        w = modeling.models.Gaussian2D(amp, x0, y0, sigma, sigma)
        #print(w)

        yi, xi = np.indices(img.shape)

        g = fitter(w, xi, yi, img)

        model_data = g(xi, yi)

        #paramètres pour affichage correct
        fig_width_i = width / dpi
        fig_height_i = height / dpi

        #On affiche les résultats
        fig2, ax3 = plt.subplots()
        fig2.set_size_inches(fig_width_i,fig_height_i)
        eps = np.min(model_data[model_data > 0]) / 10.0
        # use logarithmic scale for sharp Gaussians
        #cs = ax3.imshow(np.log(eps + model_data), label='Gaussian')
        cs = ax3.imshow(eps + model_data, label='Gaussian')
        cbar = fig2.colorbar(cs)
        cbar.set_label('Intensité sur 8bits')
        ax3.set_title('Gaussienne 2D')
        ax3.set_xlabel ("Largeur de l'image en pixels")
        ax3.set_ylabel ("Hauteur de l'image en pixels")

        temps=time.time()-t
        print("Temps plot Gauss 2D : ", temps)

        return fig2, g   
    
    def points_ellipse(self):
        """
        Permet de récupérer les points extremes de l'image selon le grand et
        petit axe de l'ellipse pour par la suite fiter la gaussienne sur ces lignes
        """
        img=self.crop_img #On récupère l'image
        img_l=img.shape[0] #le nombre de ligne de l'image
        img_c=img.shape[1] #le nombre de colonne de l'image
        
        #le milieu de l'image en ligne et colonne
        cl_ell=img_l/2 
        cc_ell=img_c/2
        
        #On récupère l'angle de l'ellipse et on le met en radians
        ang_ell=self.ellipse[2]
        ang=np.radians(ang_ell)

        #On initialise les points de coordonnées
        GP1c, GP1l, GP2c, GP2l, PP1c, PP1l, PP2c, PP2l=0,0,0,0,0,0,0,0

        #Dans le cas où l'ellipse est orientée verticalement
        if 0<=ang_ell<45 or 135<= ang_ell <=180:
            #Les points de lignes sont aux extrémitées de l'image
            GP1l=0 #Grand axe
            GP2l=img_l

            PP1c=0 #Petit axe
            PP2c=img_c

            #Les points des colonnes sont dépendant de l'angle de l'ellipse
            l1_ang=np.floor(cl_ell*np.tan(ang))

            GP1c=cc_ell+l1_ang#Grand axe
            if GP1c > img_c: #Condition sur les longueurs dû aux arrondis dans les angles de l'image
                GP1c=img_c-1
            if GP1c < 0:
                GP1c=0

            GP2c=cc_ell-l1_ang
            if GP2c < 0:
                GP2c=0
            if GP2c > img_c:
                GP2c=img_c-1

            c1_ang=np.floor(cc_ell*np.tan(ang))

            PP1l=cl_ell-c1_ang#Petit axe
            if PP1l < 0:
                PP1l=0
            if PP1l > img_l:
                PP1l= img_l-1

            PP2l=cl_ell+c1_ang
            if PP2l > img_l:
                PP2l=img_l-1
            if PP2l < 0:
                PP2l=0

        #Dans le cas où l'ellipse est orientée horizontalement
        if 45<= ang_ell <135:
            #Les points de colonnes sont aux extrémitées de l'image
            GP1c=img_c#Grand axe
            GP2c=0

            PP1l=0#Petit axe
            PP2l=img_l

            #Les points des colonnes sont dépendant de l'angle de l'ellipse
            c2_ang=np.floor(cc_ell/np.tan(ang))

            GP1l=cl_ell-c2_ang#Grand axe
            if GP1l < 0:
                GP1l = 0
            if GP1l > img_l:
                GP1l = img_l-1

            GP2l=cl_ell+c2_ang
            if GP2l >img_l :
                GP2l = img_l-1
            if GP2l < 0 :
                GP2l = 0

            l2_ang=np.floor(cl_ell/np.tan(ang))

            PP1c=cc_ell-l2_ang#Petit axe
            if PP1c > img_c:
                PP1c = img_c-1
            if PP1c < 0:
                PP1c = 0

            PP2c=cc_ell+l2_ang
            if PP2c < 0:
                PP2c = 0
            if PP2c > img_c:
                PP2c = img_c-1

        #Création des tuples de points
        GP1, GP2=[np.int32(GP1l),np.int32(GP1c)], [np.int32(GP2l),np.int32(GP2c)]
        PP1, PP2=[np.int32(PP1l),np.int32(PP1c)], [np.int32(PP2l),np.int32(PP2c)]

        return GP1, GP2, PP1, PP2

    def trace_ellipse(self,dpi,width,height):
        """ Trace le fit gaussien selon les axes de l'ellipse"""
        t=time.time()
        print("Start plot Gauss ellipse axis")
        #on pose les variables et on récupère les informations de l'image
        img=self.crop_img
        Lg, Lp= [],[]
        i,y = 0,0
        width=self.ellipse[1][1]
        height=self.ellipse[1][0]
        ang_ell=self.ellipse[2]

        #on récupère les points des axes de la fonction précédente
        GP1, GP2, PP1, PP2=self.points_ellipse()

        #on récupère les valeurs des pixels selon la ligne qui relie les pixels trouvés précedemment
        Gr, Gc=line(GP1[0], GP1[1], GP2[0], GP2[1])
        Pr, Pc=line(PP1[0], PP1[1], PP2[0], PP2[1])

        #Création des listes d'intensités de l'image en fonction de l'orientation de l'ellipse
        if 45 <= ang_ell <135:
            for y in range (len(Pr)-1) :
                Lp=np.append(Lp, img[Pr[y], Pc[y]])
            for i in range (len(Gr)-1) :
                Lg=np.append(Lg, img[Gr[i], len(Gc)-2-i])
                
        else :
            for y in range (len(Pr)-1) :
                Lp=np.append(Lp, img[Pr[y], Pc[y]])
            for i in range (len(Gr)-1) :
                Lg=np.append(Lg, img[Gr[i], Gc[i]])

    
        #On créer la liste qui sert d'axe pour le fit
        G = np.arange(len(Lg))
        P = np.arange(len(Lp))

        #Calcul des sigmas sur les valeurs             
        sigma_g = np.std(Lg)
        sigma_p = np.std(Lp) 

        #model du fit
        fitter = modeling.fitting.LevMarLSQFitter()

        #fonction gaussienne
        modelG = modeling.models.Gaussian1D(amplitude=np.max(Lg), mean=width, stddev=sigma_g)   # depending on the data you need to give some initial values
        modelP = modeling.models.Gaussian1D(amplitude=np.max(Lp), mean=height, stddev=sigma_p)
        
        #Fit de la courbe et des données
        G_fitted_model = fitter(modelG, G, Lg)
        P_fitted_model = fitter(modelP, P, Lp)

        #paramètres pour affichage correct
        fig_width_i = width / dpi
        fig_height_i = height / dpi

        #affichage des résultats
        fig = Figure()
        fig.set_size_inches(fig_width_i,fig_height_i)
        fig.suptitle("Gaussienne ellipse")
        ax = fig.add_subplot(1 ,2 ,1)
        ax.plot(G,Lg)
        ax.plot(G, G_fitted_model(G))
        ax2 = fig.add_subplot(1, 2, 2)
        ax2.plot(P,Lp)
        ax2.plot(P, P_fitted_model(P))
        ax.set_title('Grand axe profil')
        ax.set_xlabel ('Grand axe en pixel')
        ax.set_ylabel ('Intensité sur 8bits')
        ax2.set_title ('Petit axe profil')
        ax2.set_xlabel ('Petit axe en pixel')
        ax2.set_ylabel ('Intensité sur 8bits')

        temps = time.time()-t
        print("Temps plot Gauss ellipse : ", temps)

        return fig, G_fitted_model, P_fitted_model

    