# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 11:24:25 2020

@author: OPTIQUE
"""

import numpy as np
import cv2 as cv
cap = cv.VideoCapture(0)
while(True):
    # Capture image par imaghe
    ret, img = cap.read()
    # Préparation de l'affichage de l'
    cv.imshow('frame',img)
    # affichage et saisie d'un code clavier
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
# Ne pas oublier de fermer le flux et la fenetre
cap.release()
cv.destroyAllWindows()