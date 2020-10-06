import numpy as np
from PIL import Image as Img
from PIL import ImageTk
import cv2
import matplotlib.pyplot as plt

# Capture video from file
cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    if ret == True:

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(gray,(5,5),0) #Mets un flou gaussien
        ret3,otsu = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) #Applique le filtre d'Otsu

        cv2.imshow('frame', otsu)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    else:
        break

cap.release()
cv2.destroyAllWindows()