# PROJET-M2
  
Ce projet a pour but de programmer un analyseur de faisceaux laser. Il permet l'analyse de celui-ci au moyen d'une caméra et de ce programme. Le projet portera essentiellement sur le développement d’un logiciel de traitements d’images en langage Python, permettant de calculer et de fournir à l’utilisateur les caractéristiques du faisceau mesurées. Il correspond aux fonctionnalités principales des programmes commerciaux équivalents. 
  
Le programme est en cours de **développement** et des bugs peuvent survenir et leurs signalements sont appéciés.  
  
La base de développement du système est une caméra Basler ([acA1920-40uc](https://www.baslerweb.com/en/products/cameras/area-scan-cameras/ace/aca1920-40uc/) et [acA5472-17um](https://www.baslerweb.com/en/products/cameras/area-scan-cameras/ace/aca5472-17um/)) mais un module ouvert [OpenCV](https://opencv.org/) en permet l'usage le plus courant avec tout type de caméra.  
  
  
## Fonctionnalités :  
  
Il accuse certaines fonctionnalités :    
  * Preview de la caméra  
  * Traitement de l'image :  
    * Détection du faisceau par 2 méthodes de seuillage  
    * Détection du faisceau principal  
    * Détection du Barycentre d'intensité de l'image  
    * Détection de l'ellipticité du faisceau principal  
    * Détection et crop du ROI de l'image  
  * Affichage des graphiques des gaussiennes associés :  
    * Selon x et y  
    * Selon le Grand axe et Petit axe de l'ellipse  
    * Gaussienne 2D sur l'ensemble du faisceau  
  * Alignement de faisceaux :  
    * Garde la position du premier faisceau  
    * Affiche en temps réel la position du nouveau faisceau et affiche les coordonnées  
  * Export des données :  
     * Export des images brutes, traitées, graphiques  
     * Export des données du faisceaux, des graphiques  
   
  
## Installation  
  
Pour l'installation avec une caméra Basler, veuillez suivre le Git : [pypylon](https://github.com/basler/pypylon) (à l'heure actuelle fonctionne sur les version Python jusqu'à la [3.8](https://www.python.org/downloads/release/python-386/)).  
Le développement a été effectué sous Python3.8 et les bibliothèques à jour à la date du 12/12/2020.  
  
Les dernières versions en cours de développement se trouvent à [Fork 1](https://github.com/quentincoche/PROJET-M2/tree/master/D%C3%A9veloppement/Marin) et [Fork 2](https://github.com/quentincoche/PROJET-M2/tree/master/D%C3%A9veloppement/Quentin).  
Pour le **Fork 1** executez ``New_GUI.py``
Pour le **Fork 2** executez ``QUI.py``
