import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib
import math

def updateGraph():
       """Example function triggered by Tkinter GUI to change matplotlib graphs."""
       global currentGraph
       # Clear all graphs drawn in figure
       plt.clf()
       y = []
       if currentGraph == "sin":
           for i in x:
               y.append(math.cos(i))
           currentGraph = "cos"
       else:
           for i in x:
               y.append(math.sin(i))
           currentGraph = "sin"
       plt.plot(x,y)
       fig.canvas.draw()

# This defines the Python GUI backend to use for matplotlib
matplotlib.use('TkAgg')

# Initialize an instance of Tk
root = tk.Tk()

# Initialize matplotlib figure for graphing purposes
fig = plt.figure(1)

# Special type of "canvas" to allow for matplotlib graphing
canvas = FigureCanvasTkAgg(fig, master=root)
plot_widget = canvas.get_tk_widget()

# Example data (note: default calculations for angles are in radians)
x = []
for i in range(0, 500):
       x.append(i/10)
y = []
for i in x:
       y.append(math.sin(i))
plt.plot(x, y)

currentGraph = "sin"

# Add the plot to the tkinter widget
plot_widget.grid(row=0, column=0)
# Create a tkinter button at the bottom of the window and link it with the updateGraph function
tk.Button(root,text="Update",command=updateGraph).grid(row=1, column=0)

root.mainloop()