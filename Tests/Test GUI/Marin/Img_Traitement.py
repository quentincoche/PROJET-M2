    # -*- coding: utf-8 -*-
"""
Created on Wen Oct 14 10:27:21 2020

@author: Optique
"""
    
import cv2 #Bibliothèque d'interfaçage de caméra et de traitement d'image
import numpy as np #Bibliothèque de traitement des vecteurs et matrice
from math import *
import matplotlib.pyplot as plt #Bibliothèque d'affichage mathématiques
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from scipy.optimize import curve_fit
from astropy import modeling
from skimage.draw import line
import statistics
from statistics import mean
import time #Bibliothèque permettant d'utiliser l'heure de l'ordinateur
import cProfile
import pstats


class Traitement():

    profiler=cProfile.Profile()
    profiler.enable()
    
    def traitement(self, img):
        gray=cv2.normalize(img, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1)
        img_trait, img_bin=self.binarisation(gray)
        self.img=img_trait
        img100, ellipse, cX, cY=self.calcul_traitement(img_trait, img_bin)
        return img100, ellipse, cX, cY


    def binarisation(self,img):
        """ Filtrage de l'image et binarisation de celle-ci"""
        i,j=0,0
        l=[]
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

            # dessine les contours des formes qu'il a identifiés
            #cv2.drawContours (self.frame, contours, -1, (255,215,0), 1)


        #Dessine les formes sur l'image
        cv2.line(frame, (self.cX, 0), (self.cX, frame.shape[0]), (255, 0, 0), 1)#Dessine une croix sur le barycentre de l'image
        cv2.line(frame, (0, self.cY), (frame.shape[1], self.cY), (255, 0, 0), 1)


        crop_img = self.crop(frame)
        self.crop_img = self.crop(self.img)
        
        #img=cv2.resize(self.frame, dsize=(1200, 800), interpolation=cv2.INTER_CUBIC)
        #otsu=cv2.resize(self.otsu, dsize=(1200, 800), interpolation=cv2.INTER_CUBIC)
        #cv2.imshow('Otsu', otsu)

        return crop_img, self.ellipse, cX, cY


    def crop(self,frame):
        """ Fonction qui crop le centre d'intérêt à 2 fois sa taille"""
        #on défini les tailles de crop, les conditions qui suivent sont là pour éviter les problèmes de bord
        X=self.x-ceil(self.w/2)
        Y=self.y-ceil(self.h/2)
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
            self.W=frame.shape[1]-(X+self.w)
            X=X+self.w-self.W
        if Y+self.H>frame.shape[0]:
            self.H=frame.shape[0]-(Y+self.h)
            Y=Y+self.h-self.H

        crop_img = frame[Y:Y+self.H,X:X+self.W]
        return crop_img


    def trace_profil(self):
        """Trace le profil d'intensité sur les axes du barycentre de l'image"""
        img=self.crop_img # on récupère l'image
        #on pose les variables et on récupère les informations de l'image
        self.Lx,self.Ly=[],[]
        img_y=img.shape[0]
        img_x=img.shape[1]
        self.w_trace=ceil(self.W/2)
        self.h_trace=ceil(self.H/2)
        #print(img_x,img_y)
        #print(w,h)
        # on récupère la valeur des pixels selon les axes
        for iy in range(img_y):
            self.Ly=np.append(self.Ly,img[iy, self.w_trace])
        for ix in range(img_x):
            self.Lx=np.append(self.Lx, img[self.h_trace, ix])
        #on fait une liste de ces valeurs
        x=np.arange(img_x)
        y=np.arange(img_y)

        #on prépare la fonction de fit gaussien en précisant la méthode de fit
        fitter = modeling.fitting.LevMarLSQFitter()
        #courbe gaussien selon les axes x et y
        modelx = modeling.models.Gaussian1D(amplitude=250, mean=self.w_trace, stddev=self.w_trace/2)   # depending on the data you need to give some initial values
        modely = modeling.models.Gaussian1D(amplitude=250, mean=self.h_trace, stddev=self.h_trace/2)
        #fit des courbes et des données
        x_fitted_model = fitter(modelx, x, self.Lx)
        y_fitted_model = fitter(modely, y, self.Ly)

        #On affiche les courbes résultantes
        fig = plt.figure(figsize=plt.figaspect(0.5))
        ax = fig.add_subplot(2 ,2 ,1)
        ax.plot(x,self.Lx)
        ax.plot(x, x_fitted_model(x))
        ax2 = fig.add_subplot(2, 2, 2)
        ax2.plot(y,self.Ly)
        ax2.plot(y, y_fitted_model(y))

        if img_x<img_y :
            x=np.arange(img_x)
            y=np.arange(img_x)
        else :
            x=np.arange(img_y)
            y=np.arange(img_y)

        z=self.plot_2D()

        #ax3 = fig.add_subplot(2,1,1,projection='3d')
        #ax3.plot_surface(x, y, img, rstride=1, cstride=1, cmap='gray')
        ax4 = fig.add_subplot(2,1,2,projection='3d')
        ax4.plot_surface(x, y, z, rstride=3, cstride=3, linewidth=1, antialiased=True, cmap='viridis')
        ax.set_title('X profil')
        ax.set_xlabel ('Axe x')
        ax.set_ylabel ('Axe y')
        ax2.set_title ('Y profil')
        ax2.set_xlabel ('Axe x')
        ax2.set_ylabel ('Axe y')
        

    
    def plot_2D(self):
        """Affiche le fit à la gausienne en 2D"""
        img = self.crop_img  # on récupère l'image

        if img.shape[1]<img.shape[0] :
            x=np.arange(img.shape[1])
            y=np.arange(img.shape[1])
        else :
            x=np.arange(img.shape[0])
            y=np.arange(img.shape[0])

        x,y = np.meshgrid(x,y)

        # Mean vector and covariance matrix
        sigma_x = self.w_trace/2
        sigma_y = self.h_trace/2

        z = (1/(2*np.pi*sigma_x*sigma_y) * np.exp(-((x-self.w_trace)**2/(2*sigma_x**2)+ (y-self.h_trace)**2/(2*sigma_y**2))))

        return z
        """
        #on prépare la fonction de fit gaussien en précisant la méthode de fit
        fitter = modeling.fitting.LevMarLSQFitter()

        model_2D = modeling.models.Gaussian2D(
        amplitude=250, x_mean=self.w_trace, y_mean=self.h_trace, x_stddev=self.w_trace/2, y_stddev=self.h_trace/2)

        fitted_model = fitter(model_2D, x, y, Lz)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(x, y, fitted_model, cmap=cm.coolwarm, linewidth=0, antialiased=False)
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        """
    
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
        ang=radians(ang_ell)

        #On initialise les points de coordonnées
        GP1c, GP1l, GP2c, GP2l, PP1c, PP1l, PP2c, PP2l=0,0,0,0,0,0,0,0

        #Dans le cas où l'ellipse est orientée verticalement
        if 0<=ang_ell<45 or 135<= ang_ell <=180:
            #Les points de lignes sont aux extrémitées de l'image
            GP1l=0 #Grand axe
            GP2l=img_l

            PP1c=img_c #Petit axe
            PP2c=0

            #Les points des colonnes sont dépendant de l'angle de l'ellipse
            GP1c=cc_ell+floor(cl_ell*tan(ang))#Grand axe
            GP2c=cc_ell-floor(cl_ell*tan(ang))

            PP1l=cl_ell+floor(cc_ell*tan(ang))#Petit axe
            PP2l=cl_ell-floor(cc_ell*tan(ang))

        #Dans le cas où l'ellipse est orientée horizontalement
        if 45<= ang_ell <135:
            #Les points de colonnes sont aux extrémitées de l'image
            GP1c=img_c#Grand axe
            GP2c=0

            PP1l=0#Petit axe
            PP2l=img_l

            #Les points des colonnes sont dépendant de l'angle de l'ellipse
            GP1l=cl_ell-floor(cc_ell/tan(ang))#Grand axe
            GP2l=cl_ell+floor(cc_ell/tan(ang))

            PP1c=cc_ell+floor(cl_ell/tan(ang))#Petit axe
            PP2c=cc_ell-floor(cl_ell/tan(ang))

        #Création des tuples de points
        GP1, GP2=[int(GP1l),int(GP1c)], [int(GP2l),int(GP2c)]
        PP1, PP2=[int(PP1l),int(PP1c)], [int(PP2l),int(PP2c)]

        return GP1, GP2, PP1, PP2



    def trace_ellipse(self):
        """ Trace le fit gaussien selon les axes de l'ellipse"""
        #on pose les variables et on récupère les informations de l'image
        img=self.crop_img
        Lg, Lp= [],[]
        width=self.ellipse[1][1]
        height=self.ellipse[1][0]
        #on récupère les points des axes de la fonction précédente
        GP1, GP2, PP1, PP2=self.points_ellipse()
        #on récupère les valeurs des pixels selon la ligne qui relie les pixels trouvés précedemment
        Gl, Gc = line(GP1[0], GP1[1], GP2[0], GP2[1])
        Pl, Pc = line(PP1[0], PP1[1], PP2[0], PP2[1])
        for x1 in range (Gl):
            for y1 in range (Gc):
                Lg=np.append(Lg, img[x1,y1])
        for x2 in range (Pl):
            for y2 in range (Pc):
                Lp=np.append(Lp, img[x2,y2])

        G=len(Lg)
        P=len(Lp)      

        #model du fit
        fitter = modeling.fitting.LevMarLSQFitter()
        #fonction gaussienne
        modelG = modeling.models.Gaussian1D(amplitude=250, mean=width, stddev=width/2)   # depending on the data you need to give some initial values
        modelP = modeling.models.Gaussian1D(amplitude=250, mean=height, stddev=height/2)
        #Fit de la courbe et des données
        G_fitted_model = fitter(modelG, G, Lg)
        P_fitted_model = fitter(modelP, P, Lp)

        #affichage des résultats
        fig = plt.figure(figsize=plt.figaspect(0.5))
        ax = fig.add_subplot(1 ,2 ,1)
        ax.plot(G,Lg)
        ax.plot(G, G_fitted_model(G))
        ax2 = fig.add_subplot(1, 2, 2)
        ax2.plot(P,Lp)
        ax2.plot(P, P_fitted_model(P))
        ax.set_title('Grand axe profil')
        ax.set_xlabel ('Axe x')
        ax.set_ylabel ('Axe y')
        ax2.set_title ('Petit axe profil')
        ax2.set_xlabel ('Axe x')
        ax2.set_ylabel ('Axe y')



    profiler.disable()
    profile_stats=pstats.Stats(profiler)
    profile_stats.strip_dirs()
    profile_stats.sort_stats('time')
    profile_stats.print_stats()   
