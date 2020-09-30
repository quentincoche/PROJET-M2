from tkinter import*
 
class cadre(Frame):
    def __init__(self, bg=None, hauteur=None, largeur=None):
       Frame.__init__(self, bg=bg, width=largeur, height=hauteur)
 
class fenetre(Tk):
    def __init__(self, couleur='grey'):
        Tk.__init__(self)
        self.cadre=cadre(bg='blue', hauteur=200, largeur=300)
        self.cadre.grid(row=0, column=0, sticky='EWNS')
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
 
def main():
    ma_fenetre=fenetre()
    mainloop()
 
if __name__ == '__main__':
    main()