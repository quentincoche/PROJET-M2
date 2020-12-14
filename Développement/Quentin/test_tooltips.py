from tkinter import *
from tkinter import tix
root = Tk()
status = Label(root, height = 3, width=30, bd=1,bg='yellow',wraplength = 210, text = "All angles are in degrees")
status.grid(row = 0,column = 0,pady = 10)
bal = tix.Balloon(root,statusbar = status)
frame_1 = Frame(root,relief=RIDGE,bd = 2)
frame_1.grid(row=1,column = 0)
Angles = [StringVar(),StringVar()]

#Incomming
label_in = Label(frame_1,text = "TH_in")
label_in.grid(row = 0,column = 0)

entry_in = Entry(frame_1, width = 20, textvariable = Angles[0])
entry_in.grid(row = 0,column = 1)

#Outgoing
label_out = Label(frame_1,text = "TH_out")
label_out.grid(row = 1,column = 0)

entry_out = Entry(frame_1, width = 20, textvariable = Angles[1])
entry_out.grid(row=1,column=1)

#tool tip / status bar
bal.bind_widget(label_in,balloonmsg='Incidence Angle',statusmsg = 'Incidence angle of the incoming light with respect to the surface normal.')
bal.bind_widget(label_out,balloonmsg='Detector Angle',statusmsg = 'Angle between the surface normal and the detector')
root.mainloop()