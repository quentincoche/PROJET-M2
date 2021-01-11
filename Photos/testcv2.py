import tkinter as tk
from PIL import Image, ImageTk
 
fenetre = tk.Tk()
 
## Ouverture du fichier
image = Image.open('Photos/foton.png')
## Remplace PhotoImage de Tkinter par celui de PIL
photo = ImageTk.PhotoImage(image)
 
label = tk.Label(fenetre, image=photo)
label.pack()
 
fenetre.mainloop()