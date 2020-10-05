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

        gray=cv2.blur(gray,(5,5))
        """
        img = Img.fromarray(gray) # Convertit l'image pour PIL
        data=np.asarray(img)
        a=np.reshape(data,np.size(data,0)*np.size(data,1))
        h, bins, patches = plt.hist(a, bins = 25)
        ind = np.argmax(h)
        norm_ref=h[ind]
        """
        hist = cv2.calcHist(gray,[0],None,[256],[0,256])


        #cv2.imshow('frame',gray)
        plt.plot(hist)
        plt.xlim([0,256])
        plt.show

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    else:
        break

cap.release()
cv2.destroyAllWindows()