import sys

try:
import Tkinter as tk
except ImportError:
import tkinter as tk

try:
import ttk
py3 = False
except ImportError:
import tkinter.ttk as ttk
py3 = True

import snapshot_support

##################tutorial################
import cv2
import PIL.Image, PIL.ImageTk
import time

def vp_start_gui():
'''Starting point when module is the main routine.'''
global val, w, root
root = tk.Tk()
top = scannerApp (root)
snapshot_support.init(root, top)
root.mainloop()

w = None
def create_scannerApp(rt, *args, **kwargs):
'''Starting point when module is imported by another module.
Correct form of call: 'create_scannerApp(root, *args, **kwargs)' .'''
global w, w_win, root
#rt = root
root = rt
w = tk.Toplevel (root)
top = scannerApp (w)
snapshot_support.init(w, top, *args, **kwargs)
return (w, top)

def destroy_scannerApp():
global w
w.destroy()
w = None

class scannerApp:
def init(self, top=None, video_source=0):
'''This class configures and populates the toplevel window.
top is the toplevel containing window.'''
_bgcolor = '#d9d9d9' # X11 color: 'gray85'
_fgcolor = '#000000' # X11 color: 'black'
_compcolor = '#d9d9d9' # X11 color: 'gray85'
_ana1color = '#d9d9d9' # X11 color: 'gray85'
_ana2color = '#ececec' # Closest X11 color: 'gray92'

    top.geometry("600x450+420+128")
    top.minsize(120, 1)
    top.maxsize(1370, 749)
    top.resizable(1, 1)
    top.title("scaner")
    top.configure(background="#d9d9d9")
    
    self.video_source = video_source

    # open video source (by default this will try to open the computer webcam)
    self.vid = MyVideoCapture(self.video_source)

    # Create a canvas that can fit the above video source size

    self.Canvas1 = tk.Canvas(top) 
     
    self.Canvas1.place(relx=0.05, rely=0.244, relheight=0.651
            , relwidth=0.355)
    self.Canvas1.configure(background="#d9d9d9")
    self.Canvas1.configure(borderwidth="2")
    self.Canvas1.configure(insertbackground="black")
    self.Canvas1.configure(relief="ridge")
    self.Canvas1.configure(selectbackground="blue")
    self.Canvas1.configure(selectforeground="white")
  

    self.startFeedButton = tk.Button(top)
    self.startFeedButton.place(relx=0.05, rely=0.022, height=34, width=207)
    self.startFeedButton.configure(activebackground="#ececec")
    self.startFeedButton.configure(activeforeground="#000000")
    self.startFeedButton.configure(background="#d9d9d9")
    self.startFeedButton.configure(disabledforeground="#a3a3a3")
    self.startFeedButton.configure(foreground="#000000")
    self.startFeedButton.configure(highlightbackground="#d9d9d9")
    self.startFeedButton.configure(highlightcolor="black")
    self.startFeedButton.configure(pady="0")
    self.startFeedButton.configure(text='''start''')

    self.snapshotButton = tk.Button(top)
    self.snapshotButton.place(relx=0.05, rely=0.133, height=34, width=207)
    self.snapshotButton.configure(activebackground="#ececec")
    self.snapshotButton.configure(activeforeground="#000000")
    self.snapshotButton.configure(background="#d9d9d9")
    self.snapshotButton.configure(disabledforeground="#a3a3a3")
    self.snapshotButton.configure(foreground="#000000")
    self.snapshotButton.configure(highlightbackground="#d9d9d9")
    self.snapshotButton.configure(highlightcolor="black")
    self.snapshotButton.configure(pady="0")
    self.snapshotButton.configure(text='''snapshot''', command=self.snapshot)

    # After it is called once, the update method will be automatically called every delay milliseconds
    self.delay = 15
    self.update()

    self.Canvas1.mainloop()

def snapshot(self):
     # Get a frame from the video source
      ret, frame = self.vid.get_frame()

      if ret:
        cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

def update(self):
     # Get a frame from the video source
      ret, frame = self.vid.get_frame()

      if ret:
         self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
         self.Canvas1.create_image(0, 0, image = self.photo, anchor = tk.NW)

      self.Canvas1.after(self.delay, self.update)

class MyVideoCapture:
def init(self, video_source=0):
# Open the video source
self.vid = cv2.VideoCapture(video_source)
if not self.vid.isOpened():
raise ValueError("Unable to open video source", video_source)

     # Get video source width and height
      self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
      self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

  def get_frame(self):
      if self.vid.isOpened():
         ret, frame = self.vid.read()
         if ret:
             # Return a boolean success flag and the current frame converted to BGR
              return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
         else:
              return (ret, None)
      else:
         return (ret, None)

 # Release the video source when the object is destroyed
  def __del__(self):
      if self.vid.isOpened():
         self.vid.release()

if name == 'main':
vp_start_gui()