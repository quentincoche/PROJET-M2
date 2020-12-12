# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 11:24:25 2020

@author: OPTIQUE
"""

#import numpy as np
import cv2

"""def rescale_frame(frame, percent=25):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv3.resize(frame, dim, interpolation =cv3.INTER_AREA)
"""

def objet_camera():
    cap = cv2.VideoCapture(0)
    while(True):
        # Capture image par imaghe
        cap.set(3, 5472)
        cap.set(4, 3648)
        ret, img = cap.read()
        #qprint (img.dtype)
        #cap.set(cv2.CAP_PROP_FORMAT, CV_16UC1)
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE,0.25)
        cap.set(cv2.CAP_PROP_EXPOSURE, -6)
        #img25=rescale_frame(img, 10)
        # Préparation de l'affichage de l'
        #Oimg=cv2.flip(img25,0)
        #cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('frame',img)
        #cv2.imwrite('image.png',img)
        # Lecture fps 
        #print("FPS=",cap.get(cv2.CAP_PROP_FPS))
        #print("EXP=",cap.get(cv2.CAP_PROP_EXPOSURE))
        print("format=",cap.get(cv2.CAP_PROP_FORMAT))
        #print("size : ",cap.get(3)," x ",cap.get(4))
        #print("size= ",cap.get(cv2.CAP_PROP_FRAME_WIDTH)," x ",cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # affichage et saisie d'un code clavier
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   
    # Ne pas oublier de fermer le flux et la fenetre
    cap.release()
    cv2.destroyAllWindows()
    return

objet_camera()