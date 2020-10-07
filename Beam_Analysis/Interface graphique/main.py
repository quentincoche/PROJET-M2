import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
import oneCameraCapture
import PIL.Image, PIL.ImageTk
import cv2
import time

    
class Page(tk.Frame):
    
    def __init__(self, parent, window):

        tk.Frame.__init__(self, parent)
        self.window = window
        self.window.title = "Title"

        #Open camera source
        self.vid = oneCameraCapture.cameraCapture()

        #Create a canvas that will fit the camera source
        self.canvas = tk.Canvas(window, width=1000,height=600)
        self.canvas.grid(row=0, column=0)

        menuFrame = ttk.Labelframe(window, text=("Menu"))
        menuFrame.grid(row=1, column=0, sticky="NSW",
            padx=5, pady=2)

        #Button that lets the user take a snapshot
        self.btnSaveImage = tk.Button(menuFrame, text="Save Image", command=self.saveImage)
        self.btnSaveImage.grid(row=0, column=2, sticky="W")

        self.delay=100
        self.update()
        #self.window.mainloop()


    def update(self):
        #Get a frame from cameraCapture
        frame = self.vid.getFrame() #This is an array
        #https://stackoverflow.com/questions/48121916/numpy-resize-rescale-image/48121996
        frame = cv2.resize(frame, dsize=(1000, 600), interpolation=cv2.INTER_CUBIC)

        #OpenCV bindings for Python store an image in a NumPy array
        #Tkinter stores and displays images using the PhotoImage class
        # Use PIL (Pillow) to convert the NumPy ndarray to a PhotoImage
        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
        self.canvas.create_image(500,300,image=self.photo)

        self.window.after(self.delay, self.update)

    def saveImage(self):
        # Get a frame from the video source
        frame = self.vid.getFrame()

        cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg",
                    cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))



if __name__ == "__main__":
    root = tk.Tk()
    testWidget = Page(root, root) 
    testWidget.grid(row=0, column=0, sticky="W")
    root.mainloop()