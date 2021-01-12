import tkinter as tk
from PIL import Image, ImageTk
 
fenetre = tk.Tk()
 
## Ouverture du fichier
image = Image.open('Photos/foton.jpg')
image=image.resize((100,70), Image.ANTIALIAS)
## Remplace PhotoImage de Tkinter par celui de PIL
photo = ImageTk.PhotoImage(image)
 
label = tk.Label(fenetre, image=photo)
label.grid(row=0, column=0)
 
fenetre.mainloop()