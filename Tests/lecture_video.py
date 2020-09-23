# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 11:24:25 2020

@author: OPTIQUE
"""

#import numpy as np
import cv2 as cv
cap = cv.VideoCapture(0)

def rescale_frame(frame, percent=25):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv.resize(frame, dim, interpolation =cv.INTER_AREA)


while(True):
    # Capture image par imaghe
    cap.set(3, 5472)
    cap.set(4, 3648)
    ret, img = cap.read()
    cap.set(cv.CAP_PROP_AUTO_EXPOSURE,0.25)
    cap.set(cv.CAP_PROP_EXPOSURE, -6)
    img25=rescale_frame(img, percent=25)
    # Préparation de l'affichage de l'
    Oimg=cv.flip(img25,0)
    cv.imshow('frame',Oimg)
    #cv.imwrite('image.png',img)
    # Lecture fps 
    #print("FPS=",cap.get(cv.CAP_PROP_FPS))
    print("EXP=",cap.get(cv.CAP_PROP_EXPOSURE))
    #print("size : ",cap.get(3)," x ",cap.get(4))
    #print("size= ",cap.get(cv.CAP_PROP_FRAME_WIDTH)," x ",cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    # affichage et saisie d'un code clavier
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
# Ne pas oublier de fermer le flux et la fenetre
cap.release()
cv.destroyAllWindows()