# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 16:56:29 2020

@author: Optique
"""

import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
 
app = tk.Tk()
app.wm_title("Graphe Matplotlib dans Tkinter")
 
fig = Figure(figsize=(6, 4), dpi=96)
ax = fig.add_subplot(111)
ax.plot(range(10), [5, 4, 2, 6, 9, 8, 7, 1, 2, 3])
 
graph = FigureCanvasTkAgg(fig, master=app)
canvas = graph.get_tk_widget()
canvas.grid(row=0, column=0)
 
app.mainloop()