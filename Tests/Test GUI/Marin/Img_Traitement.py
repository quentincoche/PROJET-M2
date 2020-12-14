    # -*- coding: utf-8 -*-
"""
Created on Wen Oct 14 10:27:21 2020

@author: Optique
"""
   
import cv2 #Bibliothèque d'interfaçage de caméra et de traitement d'image
import numpy as np #Bibliothèque de traitement des vecteurs et matrice
import math
import matplotlib.pyplot as plt #Bibliothèque d'affichage mathématiques
from matplotlib.figure import Figure  
from matplotlib import rcParams
from astropy import modeling
from skimage.draw import line
from PIL import Image, ImageStat
import time #Bibliothèque permettant d'utiliser l'heure de l'ordinateur


rcParams.update({'figure.autolayout': True})

 
class Traitement():
    """Cette classe comprend tous les traitements et analyse de l'image qui permettent la création du ROI, des graphs
    et de toutes les données correspondantes"""

    def traitement(self, img, choix):
        """Fonction qui va faire l'appel des traitements majeurs de notre image"""
        t=time.time() #Monitoring du temps de traitement
        img_bin=self.binarisation(img, choix) # appel de la fonction binarisation
        self.img=img #Permet l'usage de l'image "brut" par les autres fonctions de la classe
        img100, ellipse, cX, cY=self.calcul_traitement(self.img, img_bin) #Calcul des paramètres de l'image
        choix_fig = 1
        temps=time.time()-t
        print("Temps de traitement de l'image : ", temps)
        return img100, ellipse, cX, cY, choix_fig

    def binarisation(self, img, choix):
        """ Filtrage de l'image et binarisation de celle-ci"""
        kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)) #Matrice permettant de définir la taille de travail des filtres
        thres=img #En cas de problème dans les choix de filtrage
        if choix==1: #Choix de filtre Otsu
            gauss = cv2.GaussianBlur(img,(5,5),0) #Met un flou gaussien
            ret3,thres = cv2.threshold(gauss,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) #Applique le filtre d'Otsu
        
        elif choix ==2 : #Choix du filtre adaptatif
            thres= cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 3, 3) 
        
        elif choix ==3 : #Choix du filtre I/e^2
            thres = cv2.GaussianBlur(img,(5,5),0) #Met un flou gaussien
            amp=np.max(thres)
            exponentielle = math.exp(1)
            I=amp/exponentielle**2
            thres_indice0=thres<I #Liste des pixels dont la valeur est inférieur au seuil
            thres_indice1=thres>I #Liste des pixels dont la valeur est supérieur au seuil
            thres[thres_indice0]=0 #Binarisation de l'image
            thres[thres_indice1]=255
        img_cls = cv2.morphologyEx(thres, cv2.MORPH_CLOSE, kernel) #Dilatation puis errosion : Enlève le bruit dans la binarisation
        img_opn = cv2.morphologyEx(img_cls, cv2.MORPH_OPEN, kernel) #errosion puis dilatation : Enlève le bruit hors de la binarisation
        return img_opn


    def calcul_traitement(self,frame, thres):
        """ Amélioration de l'image par binarisation d'Otsu """    
        # find contours in the binary image
        contours, hierarchy = cv2.findContours(thres,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key = cv2.contourArea, reverse = True)[:1]
        #print(contours)

        for c in contours:
            # permet de fit une ellipse sur toutes les formes identifiés sur l'image
            if len(c) < 5:
                break
            
            area = cv2.contourArea(c)
            if area <= 1000:  # skip ellipses smaller then 
                continue
            #cv2.drawContours(frame, [c], 0, (0,255,0), 3)
            # calculate moments for each contour
            M = cv2.moments(c)

        # calculate x,y coordinate of center
            if M["m00"] != 0:
                self.cX = int(M["m10"] / M["m00"])
                self.cY = int(M["m01"] / M["m00"])
            else:
                self.cX, self.cY = 0, 0

            #Fit une ellipse sur le(s) faisceau(x)
            self.ellipse = cv2.fitEllipse(c)
            #print('Ellipse : ', self.ellipse)
 
            #Fit un rectangle sur la zone d'intérêt pour la zoomer par la suite
            self.x,self.y,self.w,self.h = cv2.boundingRect(c)
            #rectangle = cv2.rectangle(frame,(self.x,self.y),(self.x+self.w,self.y+self.h),(0,175,175),1)
            #print('Rectangle : Position = ', self.x,',',self.y,'; Size = ',self.w,',',self.h)

        av_fond=self.fond(frame) #sort la moyenne du fond

        av_img=self.img-av_fond #retranche le fond de l'image
        img_indices = self.img-av_img < 0 #Vérifie que l'image sans fond n'a pas pixel inférieur à 0
        self.img[img_indices]=0 #remplace les pixels inférieur à 0 par 0

        av_frame=np.array(frame-av_fond).astype(np.uint8) #Retranche le fond de l'image et le mets en 8bits entier pour le transformer en couleur
        frame_indices = frame-av_frame < 0
        frame[frame_indices]=0

        #Remet l'image en RGB pour y dessiner toutes les formes par la suite et en couleur
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        #Dessine un cercle sur tous les blobs de l'image (formes blanches)
        cv2.circle(frame, (self.cX, self.cY), 2, (0, 0, 255), -1)

        #Dessiner l'ellipse
        thresh = cv2.ellipse(frame,self.ellipse,(0,255,0),1)

        #Dessine les formes sur l'image
        cv2.line(frame, (self.cX, 0), (self.cX, frame.shape[0]), (255, 0, 0), 1)#Dessine une croix sur le barycentre de l'image
        cv2.line(frame, (0, self.cY), (frame.shape[1], self.cY), (255, 0, 0), 1)

        #coupe l'image sur le ROI
        crop_img = self.crop(frame)
        self.crop_img = self.crop(self.img) 

        return crop_img, self.ellipse, self.cX, self.cY

  
    def fond (self, frame):
        """Fonction qui récupère une partie du fond puis le "patch" sur le faisceau pour moyenner le fond de l'image"""
        #lance un crop pour récuperer la taille du crop
        test=self.crop(frame)

        #Récupère une fraction du fond pour une première estimation hors du ROI
        if self.X < frame.shape[1]/4:
            x=self.X+self.W+100
        else:
            x=self.X-200
        if self.Y < frame.shape[0]/4:
            y=self.Y+self.H+100
        else:
            y=self.Y-200

        crop = frame[y:y+100,x:x+100] #sélection de la partie du fond hors du faisceau
        crop_img = Image.fromarray(crop) #Transforme le crop en image
        crop_fond = ImageStat.Stat(crop_img) #Récupère les stats de l'image
        crop_av=int(np.round(crop_fond.mean)) #Récupère la moyenne de l'intensité

        patch = Image.new("L", (self.W,self.H), crop_av) #Créer un patch de taille du faisceau et d'intensité de la moyenne précédente
        mask = Image.fromarray(frame) #Transforme l'"image" original en image
        mask.paste(patch, box=(self.X,self.Y)) #Copie le patch sur l'image
        fond = ImageStat.Stat(mask) #les stats de l'image
        av_fond=fond.mean #Sort le fond moyen de l'image plus du patch
        print("Moyenne du fond", av_fond)

        return av_fond


    def crop(self,frame):
        """ Fonction qui crop le centre d'intérêt à 2 fois la taille associé au rectangle fitté"""
        #on défini les tailles de crop, les conditions qui suivent sont là pour éviter les problèmes de bord
        self.X=self.x-math.ceil(self.w/2)
        self.Y=self.y-math.ceil(self.h/2)
        self.W=2*self.w
        self.H=2*self.h
        
        #Conditions de bord
        if self.X<0:
            self.X=0
            off_x=self.x-self.X
            self.W=self.w+2*off_x
        if self.Y<0:
            self.Y=0
            off_y=self.y-self.Y
            self.H=self.h+2*off_y
        if self.X+self.W>frame.shape[1]:
            off_x=self.X+self.W-frame.shape[1]
            self.W=self.W-2*off_x
            self.X=self.X+off_x
        if self.Y+self.H>frame.shape[0]:
            off_y=self.Y+self.H-frame.shape[0]
            self.H=self.H-2*off_y
            self.Y=self.Y+off_y

        crop_img = frame[self.Y:self.Y+self.H,self.X:self.X+self.W] #crop
        return crop_img


    def trace_profil(self,dpi,width,height, pixel_size):
        """Trace le profil d'intensité sur les axes du barycentre de l'image"""
        t=time.time()
        print('Start plot Gauss x,y')
        img=self.crop_img # on récupère l'image
        #on pose les variables et on récupère les informations de l'image
        Lx,Ly=[],[]
        img_y, img_x =img.shape
        w=math.ceil(self.W/2)
        h=math.ceil(self.H/2)
 
        # on récupère la valeur des pixels selon les axes
        for iy in range(img_y):
            Ly=np.append(Ly,img[iy, w])
        for ix in range(img_x):
            Lx=np.append(Lx, img[h, ix])

        #on fait une liste de ces valeurs
        x=np.arange(img_x)
        y=np.arange(img_y)

        x_pixel=x * pixel_size
        y_pixel=y * pixel_size

        sigma_x = np.std(Lx)
        sigma_y = np.std(Ly)

        #on prépare la fonction de fit gaussien en précisant la méthode de fit
        fitterx = modeling.fitting.LevMarLSQFitter()
        fittery = modeling.fitting.LevMarLSQFitter()

        #courbe gaussien selon les axes x et y
        modelx = modeling.models.Gaussian1D(amplitude=np.max(Lx), mean=w, stddev=sigma_x)   # depending on the data you need to give some initial values
        modely = modeling.models.Gaussian1D(amplitude=np.max(Ly), mean=h, stddev=sigma_y)

        #fit des courbes et des données
        x_fitted_model = fitterx(modelx, x, Lx)
        y_fitted_model = fittery(modely, y, Ly)

        #Création de la liste de données
        cov_diag_x = np.diag(fitterx.fit_info['param_cov'])
        cov_diag_y = np.diag(fittery.fit_info['param_cov'])
        data_x=(x_fitted_model.amplitude.value, x_fitted_model.mean.value, x_fitted_model.stddev.value, cov_diag_x)
        data_y=(y_fitted_model.amplitude.value, y_fitted_model.mean.value, y_fitted_model.stddev.value, cov_diag_y)
        
        #paramètres pour affichage correct
        fig_width_i = width / dpi
        fig_height_i = height / dpi

        #Ligne de hauteur I/e^2
        Ie_X = np.max(Lx)/math.exp(1)**2
        Ie_Y = np.max(Ly)/math.exp(1)**2

        line_X=np.linspace(Ie_X, Ie_X, len(Lx))
        line_Y=np.linspace(Ie_Y, Ie_Y, len(Ly))

        #On affiche les courbes résultantes
        fig = Figure()
        fig.set_size_inches(fig_width_i,fig_height_i)
        fig.suptitle("Gaussienne x,y")

        ax = fig.add_subplot(1 ,2 ,1)
        ax.plot(x_pixel, Lx, label="Données bruts")
        ax.plot(x_pixel, x_fitted_model(x), label="Modèle fitté")
        ax.plot(x_pixel , line_X, label="I/e^2")

        ax2 = fig.add_subplot(1, 2, 2)
        ax2.plot(y_pixel, Ly, label="Données bruts")
        ax2.plot(y_pixel, y_fitted_model(y), label="Modèle fitté")
        ax2.plot(y_pixel, line_Y, label="I/e^2")

        ax.set_title('X profil')
        ax.set_xlabel ("Largeur de l'image en µm")
        ax.set_ylabel ("Intensité sur 8bits")
        ax.legend(loc='upper right')

        ax2.set_title ('Y profil')
        ax2.set_xlabel ("Hauteur de l'image en µm")
        ax2.set_ylabel ("Intensité sur 8bits")
        ax2.legend(loc='upper right')

        temps=time.time()-t
        print("Temps plot Gauss x,y : ", temps)

        return fig, data_x, data_y

   
    def plot_2D(self,dpi,width,height):
        """Trace la gaussienne 2D associé à l'image"""
        t=time.time()
        print("start plot Gauss 2D")
        img=self.crop_img # on récupère l'image

        Lg, Lp= [],[]
        ang_ell=self.ellipse[2]

        #on récupère les points des axes de la fonction précédente
        GP1, GP2, PP1, PP2=self.points_ellipse()

        #on récupère les valeurs des pixels selon la ligne qui relie les pixels trouvés précedemment
        Gr, Gc=line(GP1[0], GP1[1], GP2[0], GP2[1])
        Pr, Pc=line(PP1[0], PP1[1], PP2[0], PP2[1])

        #Création des listes d'intensités de l'image en fonction de l'orientation de l'ellipse
        if 45 <= ang_ell <135:
            for y in range (len(Pr)-1) :
                Lp=np.append(Lp, img[Pr[y], Pc[y]])
            for i in range (len(Gr)-1) :
                Lg=np.append(Lg, img[Gr[i], len(Gc)-2-i])
                
        else :
            for y in range (len(Pr)-1) :
                Lp=np.append(Lp, img[Pr[y], Pc[y]])
            for i in range (len(Gr)-1) :
                Lg=np.append(Lg, img[Gr[i], Gc[i]])

        #Calcul des sigmas sur les valeurs             
        sigma_g = np.std(Lg)
        sigma_p = np.std(Lp) 

        #Choix de la méthode de fit
        fitter = modeling.fitting.LevMarLSQFitter()

        y0, x0 = np.unravel_index(np.argmax(img), img.shape) #Indices à parcourir pour la fonction
        
        amp=np.max(img)#Aùmplitude

        w = modeling.models.Gaussian2D(amp, x0, y0, sigma_g, sigma_p,math.pi/180*ang_ell-0.5*math.pi)
        #print(w)

        yi, xi = np.indices(img.shape) #Indices pour le plot

        g = fitter(w, xi, yi, img) #Fitting du modèle et des données

        model_data = g(xi, yi) #Création du modèle à afficher
        
        #Création de la liste de données
        cov_diag = np.diag(fitter.fit_info['param_cov']) 
        data_2D=(g.amplitude.value, g.x_mean.value, g.y_mean.value, g.x_stddev.value, g.y_stddev.value, g.theta.value, cov_diag)

        #paramètres pour affichage correct
        fig_width_i = width / dpi
        fig_height_i = height / dpi

        fig2, ax3 = plt.subplots()
        fig2.set_size_inches(fig_width_i,fig_height_i)
        eps = np.min(model_data[model_data > 0]) / 10.0

        cs = ax3.imshow(eps + model_data, label="Modèle Gaussien 2D")
        cbar = fig2.colorbar(cs)

        cbar.set_label('Intensité sur 8 bits')
        ax3.set_title('Gaussienne 2D')
        ax3.set_xlabel ("Largeur de l'image en pixels")
        ax3.set_ylabel ("Hauteur de l'image en pixels")
        
        temps=time.time()-t
        print("Temps plot Gauss 2D : ", temps)
        #print(g)

        return fig2, data_2D
        

    def points_ellipse(self):
        """
        Permet de récupérer les points extremes de l'image selon le grand et
        petit axe de l'ellipse pour par la suite fiter la gaussienne sur ces lignes
        """
        img=self.crop_img #On récupère l'image
        img_l=img.shape[0] #le nombre de ligne de l'image
        img_c=img.shape[1] #le nombre de colonne de l'image
        
        #le milieu de l'image en ligne et colonne
        cl_ell=img_l/2 
        cc_ell=img_c/2
        
        #On récupère l'angle de l'ellipse et on le met en radians
        ang_ell=self.ellipse[2]
        ang=np.radians(ang_ell)

        #On initialise les points de coordonnées
        GP1c, GP1l, GP2c, GP2l, PP1c, PP1l, PP2c, PP2l=0,0,0,0,0,0,0,0

        #Dans le cas où l'ellipse est orientée verticalement
        if 0<=ang_ell<45 or 135<= ang_ell <=180:
            #Les points de lignes sont aux extrémitées de l'image
            GP1l=0 #Grand axe
            GP2l=img_l

            PP1c=0 #Petit axe
            PP2c=img_c

            #Les points des colonnes sont dépendant de l'angle de l'ellipse
            l1_ang=np.floor(cl_ell*np.tan(ang))

            GP1c=cc_ell+l1_ang#Grand axe
            if GP1c > img_c: #Condition sur les longueurs dû aux arrondis dans les angles de l'image
                GP1c=img_c-1
            if GP1c < 0:
                GP1c=0

            GP2c=cc_ell-l1_ang
            if GP2c < 0:
                GP2c=0
            if GP2c > img_c:
                GP2c=img_c-1

            c1_ang=np.floor(cc_ell*np.tan(ang))

            PP1l=cl_ell-c1_ang#Petit axe
            if PP1l < 0:
                PP1l=0
            if PP1l > img_l:
                PP1l= img_l-1

            PP2l=cl_ell+c1_ang
            if PP2l > img_l:
                PP2l=img_l-1
            if PP2l < 0:
                PP2l=0

        #Dans le cas où l'ellipse est orientée horizontalement
        if 45<= ang_ell <135:
            #Les points de colonnes sont aux extrémitées de l'image
            GP1c=img_c#Grand axe
            GP2c=0

            PP1l=0#Petit axe
            PP2l=img_l

            #Les points des colonnes sont dépendant de l'angle de l'ellipse
            c2_ang=np.floor(cc_ell/np.tan(ang))

            GP1l=cl_ell-c2_ang#Grand axe
            if GP1l < 0:
                GP1l = 0
            if GP1l > img_l:
                GP1l = img_l-1

            GP2l=cl_ell+c2_ang
            if GP2l >img_l :
                GP2l = img_l-1
            if GP2l < 0 :
                GP2l = 0

            l2_ang=np.floor(cl_ell/np.tan(ang))

            PP1c=cc_ell-l2_ang#Petit axe
            if PP1c > img_c:
                PP1c = img_c-1
            if PP1c < 0:
                PP1c = 0

            PP2c=cc_ell+l2_ang
            if PP2c < 0:
                PP2c = 0
            if PP2c > img_c:
                PP2c = img_c-1

        #Création des tuples de points
        GP1, GP2=[np.int32(GP1l),np.int32(GP1c)], [np.int32(GP2l),np.int32(GP2c)]
        PP1, PP2=[np.int32(PP1l),np.int32(PP1c)], [np.int32(PP2l),np.int32(PP2c)]

        return GP1, GP2, PP1, PP2
   

    def trace_ellipse(self,dpi,cv_width,cv_height, pixel_size):
        """ Trace le fit gaussien selon les axes de l'ellipse"""
        t=time.time()
        print("Start plot Gauss ellipse axis")
        #on pose les variables et on récupère les informations de l'image
        img=self.crop_img
        Lg, Lp= [],[]
        i,y = 0,0
        w=math.ceil(self.W/2)
        h=math.ceil(self.H/2)
        ang_ell=self.ellipse[2]

        #on récupère les points des axes de la fonction précédente
        GP1, GP2, PP1, PP2=self.points_ellipse()

        #on récupère les valeurs des pixels selon la ligne qui relie les pixels trouvés précedemment
        Gr, Gc=line(GP1[0], GP1[1], GP2[0], GP2[1])
        Pr, Pc=line(PP1[0], PP1[1], PP2[0], PP2[1])

        #Création des listes d'intensités de l'image en fonction de l'orientation de l'ellipse
        if 45 <= ang_ell <135:
            for y in range (len(Pr)-1) :
                Lp=np.append(Lp, img[Pr[y], Pc[y]])
            for i in range (len(Gr)-1) :
                Lg=np.append(Lg, img[Gr[i], len(Gc)-2-i])
                
        else :
            for y in range (len(Pr)-1) :
                Lp=np.append(Lp, img[Pr[y], Pc[y]])
            for i in range (len(Gr)-1) :
                Lg=np.append(Lg, img[Gr[i], Gc[i]])

    
        #On créer la liste qui sert d'axe pour le fit
        G = np.arange(len(Lg))
        P = np.arange(len(Lp))

        G_pixel = G*pixel_size
        P_pixel = P*pixel_size

        #Calcul des sigmas sur les valeurs             
        sigma_g = np.std(Lg)
        sigma_p = np.std(Lp) 

        #model du fit
        fitterG = modeling.fitting.LevMarLSQFitter()
        fitterP = modeling.fitting.LevMarLSQFitter()


        #fonction gaussienne
        modelG = modeling.models.Gaussian1D(amplitude=np.max(Lg), mean=w, stddev=sigma_g)   # depending on the data you need to give some initial values
        modelP = modeling.models.Gaussian1D(amplitude=np.max(Lp), mean=h, stddev=sigma_p)
        
        #Fit de la courbe et des données
        G_fitted_model = fitterG(modelG, G, Lg)
        P_fitted_model = fitterP(modelP, P, Lp)

        #Créations des données à afficher
        cov_diag_g = np.diag(fitterG.fit_info['param_cov'])
        cov_diag_p = np.diag(fitterP.fit_info['param_cov'])
        data_g=(G_fitted_model.amplitude.value, G_fitted_model.mean.value, G_fitted_model.stddev.value, cov_diag_g)
        data_p=(P_fitted_model.amplitude.value, P_fitted_model.mean.value, P_fitted_model.stddev.value, cov_diag_p)

        #paramètres pour affichage correct
        fig_width_i = cv_width / dpi
        fig_height_i = cv_height / dpi

        #Ligne de hauteur I/e^2
        Ie_G = np.max(Lg)/math.exp(1)**2
        Ie_P = np.max(Lp)/math.exp(1)**2

        line_G=np.linspace(Ie_G, Ie_G, len(Lg))
        line_P=np.linspace(Ie_P, Ie_P, len(Lp))


        #affichage des résultats
        fig = plt.figure(figsize=plt.figaspect(0.5))
        fig.set_size_inches(fig_width_i,fig_height_i)
        fig.suptitle("Gaussienne ellipse")

        ax = fig.add_subplot(1 ,2 ,1)
        ax.plot(G_pixel, Lg, label="Données bruts")
        ax.plot(G_pixel, G_fitted_model(G), label="Modèle fitté")
        ax.plot(G_pixel, line_G, label="I/e^2")

        ax2 = fig.add_subplot(1, 2, 2)
        ax2.plot(P_pixel, Lp, label="Données bruts")
        ax2.plot(P_pixel, P_fitted_model(P), label="Modèle fitté")
        ax2.plot(P_pixel, line_P, label="I/e^2")

        ax.set_title('Grand axe profil')
        ax.set_xlabel ('Grand axe en µm')
        ax.set_ylabel ('Intensité sur 8bits')
        ax.legend(loc='upper right')

        ax2.set_title ('Petit axe profil')
        ax2.set_xlabel ('Petit axe en µm')
        ax2.set_ylabel ('Intensité sur 8bits')
        ax2.legend(loc='upper right')

        temps = time.time()-t
        print("Temps plot Gauss ellipse : ", temps)

        return fig, data_g, data_p


    # def divergence(self, lambda):
    #     """Calcul la divergence du faisceau"""
    #     theta=(4*lambda)/(math.pi*self.ellipse[1][1]) #Calcul de la divergence
    #     return theta


    # def M_square(self, lambda):
    #     """Permet de déterminer le M^2 du faisceau"""
    #     img=self.binarisation(self.img, 3)
    #     contours, hierarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #     contours = sorted(contours, key = cv2.contourArea, reverse = True)[:1]
    #     #print(contours)

    #     for c in contours:
    #         # permet de fit une ellipse sur toutes les formes identifiés sur l'image
    #         if len(c) < 5:
    #             break
            
    #         area = cv2.contourArea(c)
    #         if area <= 1000:  # skip ellipses smaller then 
    #             continue
    #         ellipse = cv2.fitEllipse(c)

    #     theta=self.divergence(lambda) #Récupère la divergence
    #     M=(theta*math.pi*ellipse[1][1])/(4*lambda) #calcul du M^2
    #     return M