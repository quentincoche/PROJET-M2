function imgo=img_bin(img,p)

% Fonction de binning d'une image avec gestion nb col/lignes binnées non entiers.
% Créée L. Pouget & J. Fade 06/2011
% In: img: image d'origine
%	p : parametre de binning (moyenne sur pxp pixels)
% Out: imgo : image binnée
% ---------
% Dépendance: nansum.m (gestion de somme avec NaN values)

%% bin de l'image img
if (p==0 || p==1)
    imgo=img;
else
    
[h,w]=size(img);
a=mod(h,p);
b=mod(w,p);
img=img(1:h-a,1:w-b);
[h,w]=size(img);
imgb=[];


[img,idx]=nansum(reshape(img,p,[]));
img=reshape(img,floor(h./p),[]);
idx=reshape(idx,floor(h./p),[]);
[img,imgo]=nansum(reshape(img',p,[]));
[imgo,idx]=nansum(reshape(idx',p,[]));

imgo=reshape(img./imgo,floor(w./p),[])';


end
