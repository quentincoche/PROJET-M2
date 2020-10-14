    # -*- coding: utf-8 -*-
"""
Created on Wen Oct 14 10:27:21 2020

@author: Optique
"""
    
import cv2 #Bibliothèque d'interfaçage de caméra et de traitement d'image
import numpy as np #Bibliothèque de traitement des vecteurs et matrice
from statistics import mean
import time #Bibliothèque permettant d'utiliser l'heure de l'ordinateur
    
    
class Traitement():

    
    def traitement(self, img):
        #img_gris=self.frame
        gray=cv2.normalize(img, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8UC1)
        width = int(gray.shape[1]*0.2) #Redimensionne l'image pour plus de rapidité (flux réel)
        height = int(gray.shape[0]*0.2)
        dim = (width, height)
        gris = cv2.resize(gray,dim, interpolation = cv2.INTER_AREA) #Redimensionne l'image pour plus de rapidité (flux réel)
        img020=self.calcul_traitement(gris)
        cv2.imshow('20%', img020)
        img100=self.calcul_traitement(gray)
        cv2.imshow('100%', img100)
        return img100


    def calcul_traitement(self,img):
        """ Test d'amélioration de l'image par binarisation d'Otsu """
        i,j=0,0
        l=[]

        """
        ROI = cv2.selectROI(img)
        if ROI!=(0,0,0,0):
            imgCrop = img[int(ROI[1]):int(ROI[1]+ROI[3]), int(ROI[0]):int(ROI[0]+ROI[2])]
        """

        otsu = cv2.GaussianBlur(img,(5,5),0) #Mets un flou gaussien
        ret3,otsu = cv2.threshold(otsu,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) #Applique le filtre d'Otsu
        data1 = np.asarray(img) #Récupère la matrice de l'image initiale
        data2 = np.asarray(otsu) #Récupère la matrice de l'image filtrée
        for i in range (data2.shape[0]): #Interverti les pixels blancs de la deuxième matrice par ceux nuancés de la première
            for j in range (data2.shape[1]):
                if data2[i,j]==0 :
                    l.append(data1[i,j])
        moy_fond=mean(l)
        for i in range (data1.shape[0]): #Interverti les pixels blancs de la deuxième matrice par ceux nuancés de la première
            for j in range (data1.shape[1]):
                data1[i,j]=data1[i,j]-moy_fond
        frame=data1 #Nouvelle image dont le fond est filtré en fonction de l'intensité du reste de l'image

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
            if area <= 1000:  # skip ellipses smaller then 10x10
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
        cv2.line(frame, (cX, 0), (cX, img.shape[0]), (255, 0, 0), 1)
        cv2.line(frame, (0, cY), (img.shape[1], cY), (255, 0, 0), 1)

        crop_img = frame[y:y+h, x:x+w]

        #img=cv2.resize(self.frame, dsize=(1200, 800), interpolation=cv2.INTER_CUBIC)
        #otsu=cv2.resize(self.otsu, dsize=(1200, 800), interpolation=cv2.INTER_CUBIC)
        #cv2.imshow('Otsu', otsu)

        return crop_img