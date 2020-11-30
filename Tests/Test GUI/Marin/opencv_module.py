import sys
import os
import time
import numpy as np
import cv2
import tkinter as tk


class openCamera():

    def __init__(self):
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            print("Cannot open camera")
            exit()


    def capture(self):
        # Capture frame-by-frame
        ret, self.frame = self.cap.read()
        print(self.cap.get(cv2.CAP_PROP_FPS))
        print(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

        # Our operations on the frame come here
        self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        
        return self.gray


if __name__=="__main__":        
    # Display the resulting frame
    while True:
        Cam=openCamera()
        gray=Cam.capture()
        cv2.imshow('frame',gray)
    
        if cv2.waitKey(1) == 27:
            break

openCamera.cap.release()
cv2.destroyAllWindows()
    

