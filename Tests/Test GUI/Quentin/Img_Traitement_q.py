    # -*- coding: utf-8 -*-
"""
Created on Wen Oct 14 10:27:21 2020

@author: Optique
"""
    
import cv2 #Bibliothèque d'interfaçage de caméra et de traitement d'image
import numpy as np #Bibliothèque de traitement des vecteurs et matrice
from math import *
import matplotlib.pyplot as plt #Bibliothèque d'affichage mathématiques
from matplotlib.figure import Figure
from scipy.optimize import curve_fit
from astropy import modeling
from statistics import mean
import time #Bibliothèque permettant d'utiliser l'heure de l'ordinateur


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

        #Dessine les formes sur l'image
        cv2.line(frame, (self.cX, 0), (self.cX, frame.shape[0]), (255, 0, 0), 1)#Dessine une croix sur le barycentre de l'image
        cv2.line(frame, (0, self.cY), (frame.shape[1], self.cY), (255, 0, 0), 1)

        crop_img = self.crop(frame)
        self.crop_img = self.crop(self.img)

        return crop_img, self.ellipse, cX, cY


    def crop(self,frame):
        """ Fonction qui crop le centre d'intérêt à 2 fois sa taille"""

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
            W=frame.shape[1]-(X+self.w)
            X=X+self.w-W
        if Y+self.H>frame.shape[0]:
            self.H=frame.shape[0]-(Y+self.h)
            Y=Y+self.h-self.H

        crop_img = frame[Y:Y+self.H,X:X+self.W]
        return crop_img


    def trace_profil(self):
        """Trace le profil d'intensité sur les axes du barycentre de l'image"""
        print('Start plotting')
        img=self.crop_img
        Lx,Ly=[],[]
        img_y=img.shape[0]
        img_x=img.shape[1]
        w=ceil(self.W/2)
        h=ceil(self.H/2)
        #print(img_x,img_y)
        #print(w,h)
        for iy in range(img_y):
            Ly=np.append(Ly,img[iy, w])
        for ix in range(img_x):
            Lx=np.append(Lx, img[h, ix])
        x=np.arange(img_x)
        y=np.arange(img_y)

        fitter = modeling.fitting.LevMarLSQFitter()
        model = modeling.models.Gaussian1D()   # depending on the data you need to give some initial values
        x_fitted_model = fitter(model, x, Lx)
        y_fitted_model = fitter(model, y, Ly)
    
        fig = Figure(figsize=plt.figaspect(0.5))
        ax = fig.add_subplot(1 ,2 ,1)
        ax.plot(x,Lx)
        ax.plot(x, x_fitted_model(x))
        ax2 = fig.add_subplot(1, 2, 2)
        ax2.plot(y,Ly)
        ax2.plot(y, y_fitted_model(y))
        ax.set_title('X profil')
        ax.set_xlabel ('Axe x')
        ax.set_ylabel ('Axe y')
        ax2.set_title ('Y profil')
        ax2.set_xlabel ('Axe x')
        ax2.set_ylabel ('Axe y')
        print('End plotting')

        return fig

    def trace_ellipse(self):
        img=self.crop_img
        img_y=img.shape[0]
        img_x=img.shape[1]
        cx_ell=self.ellipse[1][1]-self.x-self.w
        cy_ell=self.ellipse[1][0]-self.y-self.h
        ang_ell=self.ellipse[2]
        GP1x, GP1y, GP2x, GP2y, pP1x, pP1y, pP2x, pP2y =0,0,0,0,0,0,0,0
        if 0<=ang_ell<45 or 135<ang_ell<=180:
            GP1x=img_y*tan(ang_ell)+cx_ell
            GP1y=img_y
        elif 45<=ang_ell<=135:
            GP1x=img_x
            GP1y=img_x/tan(ang_ell)+cy_ell
        
        print(GP1x, GP1y)