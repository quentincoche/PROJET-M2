    # -*- coding: utf-8 -*-
"""
Created on Wen Oct 14 10:27:21 2020

@author: Optique
"""
    
import cv2 #Bibliothèque d'interfaçage de caméra et de traitement d'image
import numpy as np #Bibliothèque de traitement des vecteurs et matrice
from math import *
from statistics import mean
import time #Bibliothèque permettant d'utiliser l'heure de l'ordinateur
    
    
class Traitement():
    
    def traitement(self, img):
        #img_gris=self.frame
        gray=cv2.normalize(img, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1)
        img_trait, img_bin=self.binarisation(gray)
        img100, ellipse, cX, cY=self.calcul_traitement(img_trait, img_bin)
        #cv2.imshow('100%', img100)
        return img100, ellipse, cX, cY


    def binarisation(self,img):
        """ Filtrage de l'image et binarisation de celle-ci"""
        i,j=0,0
        l=[]
        kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10,10))

        otsu = cv2.GaussianBlur(img,(5,5),0) #Mets un flou gaussien
        ret3,otsu = cv2.threshold(otsu,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) #Applique le filtre d'Otsu
        img_opn = cv2.morphologyEx(otsu, cv2.MORPH_OPEN, kernel)
        #frame= cv2.fastNlMeansDenoising( img , None , 10 , 7 , 21)

        return img, img_opn



    def calcul_traitement(self,frame, otsu):
        """ Amélioration de l'image par binarisation d'Otsu """

        #Remet l'image en RGB pour y dessiner toutes les formes par la suite et en couleur
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            
        # find contours in the binary image
        contours, hierarchy = cv2.findContours(otsu,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key = cv2.contourArea, reverse = True)[:5]
        #print(contours)
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
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0

            #Dessine un cercle sur tous les blobs de l'image (formes blanches)
            cv2.circle(frame, (cX, cY), 2, (0, 0, 255), -1)

            #Fit une ellipse sur le(s) faisceau(x)
            ellipse = cv2.fitEllipse(c)
            thresh = cv2.ellipse(frame,ellipse,(0,255,0),1)
            print('Ellipse : ', ellipse)

            
            #Fit un rectangle sur la zone d'intérêt pour la zoomer par la suite
            x,y,w,h = cv2.boundingRect(c)
            rectangle = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,175,175),1)
            print('Rectangle : Position = ', x,',',y,'; Size = ',w,',',h)


            # dessine les contours des formes qu'il a identifiés
            #cv2.drawContours (self.frame, contours, -1, (255,215,0), 1)

        M=cv2.moments(otsu)
        # calculate x,y coordinate of center
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        print('barycentre : ', cX, ',', cY)

        #Dessine une croix sur le barycentre de l'image
        cv2.line(frame, (cX, 0), (cX, frame.shape[0]), (255, 0, 0), 1)
        cv2.line(frame, (0, cY), (frame.shape[1], cY), (255, 0, 0), 1)

        crop_img = self.crop(frame)
        self.crop_img = self.crop(self.img)
        
        #img=cv2.resize(self.frame, dsize=(1200, 800), interpolation=cv2.INTER_CUBIC)
        #otsu=cv2.resize(self.otsu, dsize=(1200, 800), interpolation=cv2.INTER_CUBIC)
        #cv2.imshow('Otsu', otsu)

        return crop_img


    def crop(self,frame):
        """ Fonction qui crop le centre d'intérêt à 2 fois sa taille"""

        X=self.x-ceil(self.w/2)
        Y=self.y-ceil(self.h/2)
        W=2*self.w
        H=2*self.h
        
        if X<0:
            X=0
            off_x=self.x-X
            W=self.w+2*off_x
        if Y<0:
            Y=0
            off_y=self.y-Y
            H=self.h+2*off_y
        if X+2*self.w>frame.shape[0]:
            W=frame.shape[0]-(X+self.w)
            X=X+self.w-W
        if Y+2*self.h>frame.shape[1]:
            H=frame.shape[1]-(Y+self.h)
            Y=Y+self.h-H

        crop_img = frame[Y:Y+H,X:X+W]
        return crop_img


    def trace_profil(self):
        """Trace le profil d'intensité sur les axes du barycentre de l'image"""
        img=self.crop_img
        Lx,Ly=[],[]
        img_y=img.shape[0]
        img_x=img.shape[1]
        print(img_x,img_y)
        print(self.w, self.h)
        for iy in range(img_y):
            Ly.append(img[iy, self.w])
        for ix in range(img_x):
            Lx.append(img[self.h, ix])
        x=np.arange( img_x)
        y=np.arange(img_y)

        fig = plt.figure(figsize=plt.figaspect(0.5))
        ax = fig.add_subplot(1 ,2 ,1)
        ax.plot(x,Lx)
        ax2 = fig.add_subplot(1, 2, 2)
        ax2.plot(y,Ly)
        ax.set_title('X profil')
        ax.set_xlabel ('Axe x')
        ax.set_ylabel ('Axe y')
        ax2.set_title ('Y profil')
        ax2.set_xlabel ('Axe x')
        ax2.set_ylabel ('Axe y')

        plt.show()
