import cv2 as cv2
import numpy as np
from matplotlib import pyplot as plt

def histo(self) :
    hist = cv2.calcHist([self.frame],[0],None,[256],[0,256])
    # Plot de hist.
    plt.plot(hist)
    plt.xlim([0,256])
    #Affichage.
    plt.show()
    return