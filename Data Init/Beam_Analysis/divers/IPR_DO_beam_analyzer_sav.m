%% ---------------------------
% IPR_DO_beam_analyzer

%-----------------------------
% Analyse de faisceaux laser 
%-----------------------------
% Auteurs: Josselin Martin, Julien Fade, Goulc'hen Loas. + Marc V 
% pour la sauvegarde
% Version: 15 fev. 2014
% Bug corrections: 
% - plantage si axes verticaux/horizontaux exactement: corrigé
% - traduction anglaise des params et fenetres
%-----------------------------
% Département Optique - Institut de Physique de Rennes - Campus Beaulieu
% 35 042 Rennes - France
% ---------------------------

function varargout = IPR_DO_beam_analyzer_sav(varargin);
warning off
disp({ '======================================================================';
       '=                      IPR_DO_beam_analyzer                          =';
       '======================================================================';
       '= Usage:  type ''IPR_DO_beam_analyzer'' on Matlab prompt              =';
       '======================================================================';
       '= Martin J., Fade J., Loas G.                                        =';
       '= Institut de Physique de Rennes -UMR CNRS 6251                      =';
       '= 01/10/2012                                                         =';
       '======================================================================';
       '= Dependences:                                                       =';
       '= MATLAB - MATLAB ACQUISITION TOOLBOX                                =';
       '= EllipseFit.m      img_bin.m        nansum.m                        =';
       '======================================================================';
       '= Use with CAMERA: CONTOUR IR USB CAMERA                             =';
       '======================================================================'});
   
%% Suppression de toutes les fenêtres de type figure
close all

%% Définition des variables globales
global ma_vid img src obj
global fig1 fig_fit  fig_visu fig_img fig_seuil S fig_profile_X fig_profile_Y fig_param 
global choix_seuil choix_bin text text2
global size_pix N M
global pos_fig1 pos_visu pos_img pos_seuil pos_profile_X pos_profile_Y pos_fit pos_param
global numfichier
%% Params physiques camera
size_pix=5.2;
M=1024;
N=1280;
numfichier=1; % initialisation du numéro de sauvegarde
%% Définition de la figure contenant le GUI
fig1=figure('name','Control and acquisition','numbertitle','off','units','normalized','position',[0.24 0.36 0.503 0.584]);

%Definition autre fenetres
fig_img = figure('name','Beam Image','numbertitle','off','units','normalized','position',[0.24 0.04 0.25 0.23]);
fig_seuil = figure('name','Thresholded ellipse','numbertitle','off','units','normalized','position',[0.748 0.04 0.25 0.23]);
fig_profile_X = figure('name','Great axis profile','numbertitle','off','units','normalized','position',[0.748 0.683 0.25 0.23]);
fig_profile_Y = figure('name','Small axis profile ','numbertitle','off','units','normalized','position',[0.748 0.362 0.25 0.23]);
fig_fit = figure('name','Fitted Ellipse and axes','numbertitle','off','units','normalized','position',[0.494 0.04 0.25 0.23]);
fig_param = figure('name','Estimated parameters','numbertitle','off','units','normalized','Position',[0.002 0.04 0.233 0.553]);
fig_visu=figure('name','Beam previewing','numbertitle','off','units','normalized','position',[0.002 0.683 0.233 0.23]);


%Sélection de la position de chaque fenêtre

pos_img=get(fig_img,'position');
pos_seuil=get(fig_seuil,'position');
pos_profile_X=get(fig_profile_X,'position');
pos_profile_Y=get(fig_profile_Y,'position');
pos_fit=get(fig_fit,'position');
pos_param=get(fig_param,'position');
pos_visu=get(fig_visu,'position');



%% Définition des boutons de commande, de la liste de choix et de la fenêtre de texte

%Création de la visualisation en temps réel
uicontrol(fig1,'style','pushbutton',...
    'units','normalized',...
    'position',[0.1 0.95 0.15 0.04],...
    'string','Video Acquisition',...
    'callback',@preview_video);

%Fermeture de la visualisation en temps réel
uicontrol(fig1,'style','pushbutton',...
    'units','normalized',...
    'position',[0.25 0.95 0.15 0.04],...
    'string','Stop preview',...
    'callback',@close_preview_video);

%Création de l'objet Fermer toutes les fenêtres
uicontrol(fig1,'style','pushbutton',...
    'units','normalized',...
    'position',[0.55 0.95 0.15 0.04],...
    'string','Close windows',...
    'callback',@close_all_windows);

%Création de l'objet Fermer tout
uicontrol(fig1,'style','pushbutton',...
    'units','normalized',...
    'position',[0.9 0.15 0.1 0.04],...
    'string','QUIT',...
    'callback',@end_beam_analyzer);

%Création de l'objet Aide
uicontrol(fig1,'style','pushbutton',...
    'units','normalized',...
    'position',[0.9 0.2 0.1 0.04],...
    'string','HELP',...
    'callback',@disp_help);

% Création de l'objet Fitter gaussienne 2D
uicontrol(fig1,'style','pushbutton',...
    'units','normalized',...
    'position',[0.9 0.5525 0.1 0.04],...
    'string','Gauss2D Fit',...
    'callback',@fit_gauss_2D);

% Création de l'objet Fitter l'Ellipse
uicontrol(fig1,'style','pushbutton',...
    'units','normalized',...
    'position',[0.9 0.6025 0.1 0.04],...
    'string','Ellipse Fit',...
    'callback',@fitter_ellipse);

% Création de l'objet Fit XY
uicontrol(fig1,'style','pushbutton',...
    'units','normalized',...
    'position',[0.9 0.6525 0.1 0.04],...
    'string','XY Cuts',...
    'callback',@coupe_hor_vert);

% Sauvegarde img courante
uicontrol(fig1,'style','pushbutton',...
    'units','normalized',...
    'position',[0.9 0.7525 0.1 0.04],...
    'string','Save img',...
    'callback',@save_img_cur);

% Création de l'objet Temps Expo
uicontrol(fig1,'style','pushbutton',...
    'units','normalized',...
    'position',[0.9 0.8825 0.1 0.04],...
    'string','Auto Exposure',...
    'callback',@temps_exp);

%Création de la fenêtre de texte 'Seuil'
uicontrol(fig1,'style','text',...
    'units','normalized',...
    'BackgroundColor',[0.8 0.8 0.8],...
    'position',[0.74 0.93 0.1 0.04],...
    'fontsize',8,...
    'string','Threshold :');

%Création de la liste déroulante de valeurs de seuil
choix_seuil=uicontrol(fig1,'style','popup',...
    'units','normalized',...
    'position',[0.85 0.93 0.15 0.05],...
    'string','16.5%(1/e^2)|60%|80%');
%S=get(choix_seuil,'value');


%Création de la fenêtre de texte 'Bin. param'
uicontrol(fig1,'style','text',...
    'units','normalized',...
    'BackgroundColor',[0.8 0.8 0.8],...
    'position',[0.9 0.50 0.1 0.04],...
    'fontsize',8,...
    'string','Bin. param.');

%Création de la liste déroulante de valeurs de binning
choix_bin=uicontrol(fig1,'style','popup',...
    'units','normalized',...
    'position',[0.95 0.46 0.05 0.05],...
    'string','16|NO|2|4|8|16');

%Création de la zone de texte pour affichage alarmes tps pause
text=uicontrol(fig1,'style','text',...
        'units','normalized',...
        'position',[.0 0.0 0.2 0.05],...
        'BackgroundColor',[0 0 0],'ForegroundColor',[1 0 0],...
        'fontsize',8,'enable','off');
   
%Création de la zone de texte pour affichage alarmes
text2=uicontrol(fig1,'style','text',...
        'units','normalized',...
        'position',[.2 0.0 0.2 0.05],...
        'BackgroundColor',[0 0 0],'ForegroundColor',[1 0 0],...
        'fontsize',8,'enable','off');

%% ########################################################################
%% FONCTIONS 
%% ########################################################################

function disp_help(hObject,data)
% affichage de l'aide


%set(hhelp,'position',[100 100 600 600]);
hhelp=helpdlg({'================================================';
    '||       IPR_DO_BEAM_ANALYZER   -- HELP MESSAGE       ||';
    '================================================';
    '';
    ' Use with CONTOUR IR USB Camera';
    '';	
    '';    
    'Commands and controls:';
    '-------------------------------------'
    '- Video acquisition : start video preview';
    '- Stop preview : stop video preview';
    '- Close windows : close all satellite windows';
    '';
    '- Auto Exposure : set exposure time automatically';
    '';
    '- Threshold : select threshold value S (in % w.r.t. to maximum intensity in the image) [default: 1/e²]';
    '';
    '- Save img : save an image as a .mat file in Matlab workspace (incremental index)';
    '';
    '- XY cuts : compute horizontal/vertical cuts at the maximum intensity of the beam (center of mass of image after threshold)';
    '- Ellipse fit : compute best ellipse fit on the beam after threshold';
    '- Gauss2D fit : compute best 2D gaussian fit on the beam';
    '- Bin. param. : binning parameter (use > 1 to speed up Gauss2D fit) [default: 16]';
    '';
    '- HELP : display this help message';
    '';
    '- QUIT : quit programm and close windows';
    '';
    '';
    'Error Messages:';
    '--------------------------';
    '- Exp time uncal -/+ : uncalibrated exposure time';
    '- EXP TIME TOO LOW : min. exposure time reached. Reduce beam power';
    '- EXP TIME TOO HIGH : max. exposure time reached. Increase beam power';
    '- PB ESTI BCKG : background estimation impossible. Use another threshold, or increase beam power.';
    '- SATU : saturation of the analyzed image';
    '';
    '';
    '----------------------------------------------------------';
    'Authors: Martin J., Fade J., Loas G.                      ';
    'Institut de Physique de Rennes - Univ. Rennes 1 - CNRS - UMR 6251';
    'Creation: 01 oct. 2012'},'Help - IPR_DO_beam_analyzer');


%% ########################################################################

function save_img_cur(hObject,data)

global ma_vid img src obj numfichier

%Sauvegarde l'image courante de fig1 dans un fichier nommé
%img_cur'numfichier)
nomfichier=['img_cur' num2str(numfichier) '.mat'];

save(nomfichier,'img');
numfichier=numfichier+1;
%% ########################################################################

function close_all_windows(hObject,data)

%Ferme toutes les figures sauf l'image de preview camera courante.
%

%% Sélection de toutes les figures

figs=get(0,'children');


%% Sélection de la figure active comme vide

figs(figs==gcf)=[];


%% Fermeture de toutes les figures sauf la figure active (Module d'Acquisition)

close(figs)
%% ########################################################################


function close_preview_video(hObject,data)

% Ferme la fenetre de preview video
%% Définition de la variable

global fig_visu


%% Fermeture de la fenêtre contenant la visualisation en temps réel

close(fig_visu)
%% ########################################################################

function preview_video(hObject,data)


%% Définition des variables
%% Définition des variables globales
global ma_vid img src obj
global fig1 fig_fit  fig_visu fig_img fig_seuil S fig_profile_X fig_profile_Y fig_param 
global choix_seuil choix_bin text text2
global size_pix N M
global pos_fig1 pos_visu pos_img pos_seuil pos_profile_X pos_profile_Y pos_fit pos_param



figure(fig_visu);
%% Sélection du flux vidéo sur camera USB

ma_vid=videoinput('winvideo', 1, 'RGB24_1280x1024');

src = getselectedsource(ma_vid);
set(src,'Gamma',1);

 
%% Sélection des paramètres pour la lecture de la vidéo
vidRes = get(ma_vid, 'VideoResolution'); 
nBands = get(ma_vid, 'NumberOfBands'); 
hImage = image( zeros(vidRes(2), vidRes(1), nBands) ); 

%% Affichage video temps réel

preview(ma_vid, hImage); 
set(fig_visu,'numbertitle','off','name','Beam Visualization - Real Time','units','normalized','position',pos_visu);
%% ########################################################################

function end_beam_analyzer(hObject,data)

% Fin du programme beam_analyzer
% Ferme toutes les figures, y compris la preview video

%% Sélection de toutes les figures

figs=get(0,'children');


%% Fermeture de toutes les figures

close(figs)
%% ########################################################################

function temps_exp(hObject,data) 

global ma_vid img src obj
global fig1 fig_fit  fig_visu fig_img fig_seuil S fig_profile_X fig_profile_Y fig_param 
global choix_seuil choix_bin  text text2
global size_pix N M
global norm_ref estimax


%% Boucle de réglage du temps d'exposition automatique + controles et alarmes


%% Réglage du temps d'exposition
exp_time_ok=0; % variable de test 

% Réinit. message erreur
set(text2,'BackgroundColor',[0 0 0],'ForegroundColor',[1 0 0],'enable','off'); 
pause(0.01);
% Réinit. message erreur
set(text,'BackgroundColor',[1 0 0],'ForegroundColor',[1 1 0],'string','Wait...','enable','on'); 
pause(0.01);

while (exp_time_ok==0) % boucle tant que expo time non ok
    
    obj=getsnapshot(ma_vid);    % capture flux video
    img = double(rgb2gray(obj));
    
     if (max(max(img)) >= 254)   % Si saturation, reduction tps exp
        src.Exposure = floor(src.Exposure /2);
        strg=strcat('Exp time uncal+ \',num2str(src.Exposure));
                set(text,'BackgroundColor',[1 0 0],'ForegroundColor',[1 1 1],'string',strg,'enable','on');
        pause(0.01);
        
     elseif (max(max(img)) <= 160) % Si low level, augmentation tps exp
        src.Exposure = ceil(src.Exposure * 1.5);
        strg=strcat('Exp time uncal- \',num2str(src.Exposure));
        set(text,'BackgroundColor',[1 0 0],'ForegroundColor',[1 1 1],'string',strg,'enable','on');
        pause(0.01);
    else
        exp_time_ok=1;
        strg=strcat('Exp time OK \',num2str(src.Exposure));
        set(text,'BackgroundColor',[0 1 0],'ForegroundColor',[1 1 1],'string',strg,'enable','on'); %Message d'erreur masqué quand il n'y a aucun problème
     end
     
    if  src.exposure >= 2000  % test sur tps d'expo trop long
            src.exposure=2045;
            exp_time_ok=1;
            strg=strcat('EXP TIME TOO BIG !\',num2str(src.Exposure));
            set(text,'BackgroundColor',[1 0 0],'ForegroundColor',[1 1 1],'string',strg,'enable','on')
     end
     
     if  src.exposure <= 1
            src.exposure=1;
            exp_time_ok=1;
            strg=strcat('EXP TIME TOO LOW !\',num2str(src.Exposure));
            set(text,'BackgroundColor',[1 0 0],'ForegroundColor',[1 1 1],'string',strg,'enable','on')
     end
end

%% Correction fond
filtre=fspecial('average',5); % lissage spatial image
imgf=imfilter(img,filtre);
[h,bins]=hist(reshape(imgf,1,size(imgf,1)*size(imgf,2 )),25); % Calcul histogramme

%estimation fond continu
[maxh,ind]=max(h);
norm_ref=bins(ind);

if (norm_ref >= max(max(img-norm_ref))/2) % Verif en cas d'image non contrastée : erreur
set(text2,'BackgroundColor',[1 0 0],'ForegroundColor',[1 1 1],'string','PB ESTI BCKG!','enable','on');   
end

% Estimation max à partir de la premiere rupture de pente des effectifs
% d'histogramme
h=h(end:-1:1);bins=bins(end:-1:1);
h=h.*(h>100);
vec_pente=h(2:length(h))-h(1:length(h)-1);
pos_max=find(vec_pente(1:end-1) - vec_pente(2:end)>0);
estimax=round(bins(pos_max(1))) - norm_ref;

% estimax=round(max(max(img))-norm_ref); % Estimation max a/p max image


%% Affichage image
figure(fig1);
imagesc(img - norm_ref);colormap('gray');daspect([1 1 1]);
set(fig1,'name','Acquisition & Control')
%% ########################################################################

function [c_contour,X0,Y0,init_waist_x,init_waist_y,x,y,xp,yp,prof1,prof2,Pfga,Pfpa]=coupe_et_fit(maxim,ref) 

% Effectue une detection du max de l'image apres seuillage, puis détection des coupes et fits gaussiens des coupes. 
% Utilisé par fonction Gauss 2D et coupe_simple_hor_vert
%

global ma_vid img src obj
global fig1 fig_fit  fig_visu fig_img fig_seuil S fig_profile_X fig_profile_Y fig_param 
global choix_seuil choix_bin  text text2
global size_pix N M
global norm_ref estimax
global pos_fig1 pos_visu pos_img pos_seuil pos_profile_X pos_profile_Y pos_fit pos_param

%% Seuillage de l'image capturée
img_norm=img-ref; % image normalisée
c_contour=(img_norm> (S*maxim)); % seuillage
[row_ell,col_ell] = find(c_contour);

%% Calcul barycentre image seuillée 
Y0 = round(mean(row_ell));
X0 = round(mean(col_ell));

init_waist_x=(max(col_ell)-min(col_ell))/2/sqrt(2); % estim tailles waist
init_waist_y=(max(row_ell)-min(row_ell))/2/sqrt(2);

I=img;
    
%% Tracé axe H + profil
    X=1:N;
    Y= Y0*ones(1,N);
    [x,y,prof1]=improfile(I,X,Y);
    
%% Tracé axe V + profil
    Yp=1:M;
    Xp= X0*ones(1,M);
    [xp,yp,prof2]=improfile(I,Xp,Yp);
 
   
%% Fit Gaussien axe H:
    f1D= @(p,X) (p(1)+p(2)*exp(-(X-p(3)).^2/2/p(4)^2));
    crit1D= @(p,X,Y)  sum((f1D(p,X)-Y).^2);
    [maxx,pos_max_x]=max(prof1);
    Pfga=fminsearch(@(p) crit1D(p,[1:length(x)]',prof1), [ref maxx-ref pos_max_x init_waist_x]);
    
    
%% Fit Gaussien axe V:
    f1D= @(p,X) (p(1)+p(2)*exp(-(X-p(3)).^2/2/p(4)^2));
    crit1D= @(p,X,Y)  sum((f1D(p,X)-Y).^2);
    [maxy,pos_max_y]=max(prof2);
    Pfpa=fminsearch(@(p) crit1D(p,[1:length(yp)]',prof2), [ref maxy-ref pos_max_y init_waist_y]);
%% ########################################################################

function coupe_hor_vert(hObject,Data)

% Calcul de fit simple Hor/Vert sur max image

global ma_vid img src obj
global fig1 fig_fit  fig_visu fig_img fig_seuil S fig_profile_X fig_profile_Y fig_param 
global choix_seuil choix_bin  text text2
global size_pix N M
global norm_ref estimax
global pos_fig1 pos_visu pos_img pos_seuil pos_profile_X pos_profile_Y pos_fit pos_param

clear('X','x','Xp','Y','y','Yp','xp','yp');

%% Reinit affichage erreur
set(text,'BackgroundColor',[0 0 0],'ForegroundColor',[1 0 0],'enable','off')
% Réinit. message erreur
set(text2,'BackgroundColor',[0 0 0],'ForegroundColor',[1 0 0],'enable','off'); 

%% Lecture seuil selectionné
if get(choix_seuil,'value')==1;
    
        S=1/exp(1)^2;
    
    elseif get(choix_seuil,'value')==2;
    
        S=0.6;
    
    elseif get(choix_seuil,'value')==3;
        
        S=0.8;
end

%% Verif satu image
ref=norm_ref;
maxim=max(max(img)); % Esti max sur max image
    
if (maxim>=254)
   set(text,'BackgroundColor',[1 0 0],'ForegroundColor',[1 1 1],'string','SATU','enable','on')
end

% Appel à fonction coupe_et_fit pour effectuer coupes XY et fit Gaussien des
% coupes
[c_contour,X0,Y0,init_waist_x,init_waist_y,x,y,xp,yp,prof1,prof2,Pfga,Pfpa]=coupe_et_fit(maxim,ref);
    
    
%%%%%% AFFICHAGES 
%% Affichage de l'image capturée
figure(fig_img);
imagesc(img);
daspect([1 1 1]);
set(fig_img,'numbertitle','off','name','Beam Image','units','normalized','position',pos_img);

%% Affichage points seuil 
figure(fig_seuil);
imagesc(c_contour);
daspect([1 1 1]);
set(fig_seuil,'numbertitle','off','name','Beam Thresholded','units','normalized','position',pos_seuil);

%% Affichage ellipse fittée desactivé
    figure(fig_fit);
    clf;
    set(fig_fit,'numbertitle','off','name','---','units','normalized','position',pos_fit);
    
%% Affichage profil X
f1D= @(p,X) (p(1)+p(2)*exp(-(X-p(3)).^2/2/p(4)^2));
    figure(fig_profile_X);
    cla;    xlabel('µm');
    set(fig_profile_X,'numbertitle','off','name','Hor. Axis Profile','units','normalized','position',pos_profile_X);
    [maxx,pos_max_x]=max(prof1);
    plot([1:length(x)]*size_pix,prof1,'-r',[1:length(x)]*size_pix,ref*ones(length(x),1),'--k',[1:length(x)]*size_pix,maxim*ones(length(x),1),'--k',...,
        [1:length(x)]*size_pix,(maxim-ref)/exp(1)^2*ones(length(x),1),'--r');
    %hold on; plot([1:length(x)]*size_pix,f1D([ref (maxx-ref) pos_max_x init_waist_x],[1:length(x)]),'--m');
    hold on; plot([1:length(x)]*size_pix,f1D(Pfga,[1:length(x)]),'--b');
    
%% Affichage profil Y
f1D= @(p,X) (p(1)+p(2)*exp(-(X-p(3)).^2/2/p(4)^2));
    figure(fig_profile_Y);
    cla;
    set(fig_profile_Y,'numbertitle','off','name','Vert. Axis Profile','units','normalized','position',pos_profile_Y);
    xlabel('µm')
    [maxy,pos_max_y]=max(prof2);
    plot([1:length(xp)]*size_pix,prof2,'-r',[1:length(xp)]*size_pix,ref*ones(length(xp),1),'--k',[1:length(xp)]*size_pix,maxim*ones(length(xp),1),'--k',...,
        [1:length(xp)]*size_pix,(maxim-ref)/exp(1)^2*ones(length(xp),1),'--r');
    %hold on; plot([1:length(xp)]*size_pix,f1D([ref (maxx-ref) pos_max_y init_waist_y],[1:length(xp)]),'--m');
    hold on; plot([1:length(xp)]*size_pix,f1D(Pfpa,[1:length(xp)]),'--b');

    %% Affichage paramètres final
figure(fig_param);clf;
set(fig_param,'numbertitle','off','name','Estimated Parameters','units','normalized','position',pos_param);

cnames1 = {'Thr. value','Center X0','Center Y0'};
mesdonnees1 = {S,X0,Y0};
uitable('units','normalized','ColumnName',cnames1,'Data',mesdonnees1,'Position',[0.03 0.78 0.85 0.1]);

cnames4 = {'Hor. radius (µm)','Vert. radius (µm)'};
mesdonnees4 = {2*Pfga(4)*size_pix,2*Pfpa(4)*size_pix};
uitable('units','normalized','ColumnName',cnames4,'Data',mesdonnees4,'Position',[0.03 0.58 0.85 0.1]);

cnames3 = {'Ratio radii (H/V)'};
mesdonnees3 = {Pfga(4)/Pfpa(4)};
uitable('units','normalized','ColumnName',cnames3,'Data',mesdonnees3,'Position',[0.03 0.38 0.85 0.1]);

%% Affichage image + fit sur fenêtre principale
figure(fig1);
imagesc(img);daspect([1 1 1]);
X=1:N;
Y= Y0*ones(1,N);
line(X,Y);
Yp=1:M;
Xp= X0*ones(1,M);
line(Xp,Yp);
set(fig1,'name','Acquisition & Controls - X-Y Cuts')

%% ########################################################################

function fitter_ellipse(hObject,Data)

% Routine de fit ellipse sur image faisceau seuillé

global ma_vid img src obj
global fig1 fig_fit  fig_visu fig_img fig_seuil S fig_profile_X fig_profile_Y fig_param 
global choix_seuil choix_bin text
global size_pix N M
global norm_ref estimax
global pos_fig1 pos_visu pos_img pos_seuil pos_profile_X pos_profile_Y pos_fit pos_param

clear('X','x','Xp','Y','y','Yp','xp','yp','c_contour_ell','c_contour_ell_c');
inv=0;
%% Lecture seuil selectionné
if get(choix_seuil,'value')==1;
    
        S=1/exp(1)^2;
    
    elseif get(choix_seuil,'value')==2;
    
        S=0.6;
    
    elseif get(choix_seuil,'value')==3;
        
        S=0.8;
        
end

%% Verif satu image
ref=norm_ref;
maxim=max(max(img)); % Esti max sur max image
    
if (maxim>=254)
   set(text,'BackgroundColor',[1 0 0],'ForegroundColor',[1 1 1],'string','SATU','enable','on')
end


%% Estimation ellipse fittée avec boucle en 2 temps
cnt=0;
maxim=estimax;
ref=norm_ref;

while (cnt<=1);
    inv=0;
    %% Seuillage de l'image capturée


    %Seuillage ellipse
    img_norm=img-ref;
    delta=4; 
    c_contour=(img_norm< (S*maxim+ delta) ) .* ( img_norm>(S*maxim-delta ) );
    [row_ell,col_ell] = find(c_contour);

    %% Fit de l'ellipse
    R = [row_ell,col_ell]; % R :ensemble des points de l'ellipse
    A=EllipseFit(R)';   % Appel a fonction EllipseFit qui calcule le fit optimal
 

    %% Calcul paramètres de l'ellipse (équation cartésienne)
    a=A(1,1);
    b=A(1,2);
    c=A(1,3);
    d=A(1,4);
    e=A(1,5);
    f=A(1,6);

    % Calcul centre ellipse
    Y0=(c*d/2-b/2*e/2)/((b/2)^2-a*c);
    X0=(a*e/2-b/2*d/2)/((b/2)^2-a*c);

 %% Définition de g et test de g pour savoir si le calcul des coefficients de l'ellipse est possible

    g=b^2-4*a*c;
    if  (g<=0)
    
        % Message d'erreur masqué quand la condition est respectée
        set(text2,'string','CALC ELL IMP !','enable','off');
        
        % Calcul des demi-axesà l'aide des coefficients de l'équation
        % cartésienne obtenue avec Ellipsefit.m
        demi_gd_axe=sqrt((2*(c*(d/2)^2+a*(e/2)^2+f*(b/2)^2-2*(b/2)*(d/2)*(e/2)-a*c*f))/(((b/2)^2-a*c)*(sqrt((a-c)^2+b^2)-(a+c))));
        demi_ptt_axe=sqrt((2*(c*(d/2)^2+a*(e/2)^2+f*(b/2)^2-2*(b/2)*(d/2)*(e/2)-a*c*f))/(((b/2)^2-a*c)*((-sqrt((a-c)^2+b^2))-(a+c))));
    
        if (b==0) % cas cercle
            theta=0;
        else
            if (a >= c)
                toto=0;
                theta=0.5*acotd(-(a-c)/(b));
            else
                toto=1;
                theta=90-0.5*acotd((a-c)/(b));
            end
        end
    
        if demi_gd_axe <= demi_ptt_axe
            inv=1;
            demi_ptt_axe=sqrt((2*(c*(d/2)^2+a*(e/2)^2+f*(b/2)^2-2*(b/2)*(d/2)*(e/2)-a*c*f))/(((b/2)^2-a*c)*(sqrt((c-a)^2+b^2)-(a+c))));
            demi_gd_axe=sqrt((2*(c*(d/2)^2+a*(e/2)^2+f*(b/2)^2-2*(b/2)*(d/2)*(e/2)-a*c*f))/(((b/2)^2-a*c)*((-sqrt((c-a)^2+b^2))-(a+c))));
        end
    
        %% Création du contour de l'ellipse fittée
        x=1:N;
        y=1:M;
        imtest=a*(y.*y)'*ones(1,N)+b*y'*x+c*ones(M,1)*(x.*x)+d*y'*ones(1,N)+e*ones(M,1)*x+f*ones(M,N);
        eps=0.0005;
        c_contour_ell=(imtest<=eps).*(imtest>=-eps);

        %% Création d'une image vierge pour y superposer l'image, le contour du seuillage et le contour de l'ellipse fittée 
        c_contour_ell_c=zeros(size(img,1),size(img,2),3);
        c_contour_ell_c(:,:,1)=(double(img)/255).*(1-c_contour_ell) + c_contour_ell;
        c_contour_ell_c(:,:,2)=(double(img)/255).*(1-c_contour.*(1-c_contour_ell)) + c_contour.*(1-c_contour_ell);
        c_contour_ell_c(:,:,3)=(double(img)/255).*(1-c_contour_ell.*c_contour);
    
        coeff=tand(theta);
%         %% Tracé du grand axe
%         Y=1:M;
%         X=X0+(Y-Y0)*(-1/tand(theta));
%         sel=(0<X).*(X<N);
%         if sum(sel==1)==0
%          X=[0 round(X0) N];%round(X0)*ones(1,M);
%          Y=round([Y0-1 Y0 Y0+1]); %round(Y0)*ones(1,M);
%         else
%             Y=Y(sel==1); X=round(X(sel==1));
%         end
%         
%         %% Tracé du petit axe
%         M
%         Yp=1:M
%         Xp=X0+(Yp-Y0)*(tand(theta));
%         sel=(0<Xp).*(Xp<N);
%         if sum(sel==1)==0
%             Xp=[0 round(X0) N];
%             Yp=round([Y0-1 Y0 Y0+1]);
%         else
%         Yp=Yp(sel==1);Xp=round(Xp(sel==1));
%          end
       %% Tracé du grand axe
        X=1:N;
        Y=Y0+(X-X0)*(tand(theta));
        X=X((0<Y<M));YY=round(Y((0<Y<M)));
        
        %% Tracé du petit axe
        Xp=1:N;
        Yp=Y0+(Xp-X0)*(-1/tand(theta));
        XXp=Xp((0<Yp<M));YYp=round(Yp((0<Yp<M)));
        
        %% Tracé du profil selon le grand axe et définition des caractéristiques associées à sa fenêtre de visualisation
        I=img;
        X1=X(1);
        X2=X(end);
        Y1=Y(1);
        Y2=Y(end);
        x=[X1 X2];
        y=[Y1 Y2];
        [X,Y,prof1]=improfile(I,x,y);
   
        %% Fit Gaussien du grand axe:
        f1D= @(p,X) (p(1)+p(2)*exp(-(X-p(3)).^2/2/p(4)^2));
        fga= @(p,X,Y)  sum((f1D(p,X)-Y).^2);
        Pfga=fminsearch(@(p) fga(p,[1:length(X)]',prof1), [ref maxim-ref find(X>=X0,1) 2*S*demi_gd_axe]);
    
        %% Tracé du profil selon le petit axe et définition des caractéristiques associées à sa fenêtre de visualisation
        X1p=Xp(1);
        X2p=Xp(end);
        Y1p=Yp(1);
        Y2p=Yp(end);
        xp=[X1p X2p];
        yp=[Y1p Y2p];
        [Xp,Yp,prof2]=improfile(I,xp,yp);
        
        %% Fit Gaussien du petit axe:
        f1D= @(p,X) (p(1)+p(2)*exp(-(X-p(3)).^2/2/p(4)^2));
        fga= @(p,X,Y)  sum((f1D(p,X)-Y).^2);
        Pfpa=fminsearch(@(p) fga(p,[1:length(Xp)]',prof2), [ref maxim-ref find(Xp>=X0,1) 2*S*demi_ptt_axe]);
        
        %Actualisation params pour fit  
        ref = mean([Pfpa(1) Pfga(1)]);
        maxim = norm_ref+mean([Pfga(2) Pfpa(2)]);
        cnt=cnt+1; % incrém.
        
    else
        % Affichage d'un message d'erreur si g est positif (calcul de fit
        % impossible)
        set(text2,'string','CALC ELL IMP !','enable','on');
        cnt=2;
    end

end %% Fin de boucle



%% %%%% AFFICHAGES 

%% Affichage de l'image capturée
    figure(fig_img);
    imagesc(img);
    daspect([1 1 1]);
    set(fig_img,'numbertitle','off','name','Beam Image','units','normalized','position',pos_img);

%% Affichage points seuil 
    figure(fig_seuil);
    imagesc(c_contour);
    daspect([1 1 1]);
    set(fig_seuil,'numbertitle','off','name','Image Ellipse Threshold','units','normalized','position',pos_seuil);

%% Affichage ellipse fittée
    figure(fig_fit);
    imagesc(c_contour_ell_c);daspect([1 1 1]);
    set(fig_fit,'numbertitle','off','name','Image - Best Fit Ellipse','units','normalized','position',pos_fit);

%% Affichage profils
inv;
if (inv==0)
    % Affichage profil X
    figure(fig_profile_X);
    cla;xlabel('µm');
    f1D= @(p,X) (p(1)+p(2)*exp(-(X-p(3)).^2/2/p(4)^2));
    set(fig_profile_X,'numbertitle','off','name','Great Axis Profile','units','normalized','position',pos_profile_X);
    plot(size_pix*[1:length(X)],prof1,'-r',size_pix*[1:length(X)],ref*ones(length(X),1),'--k',size_pix*[1:length(X)],maxim*ones(length(X),1),'--k',size_pix*[1:length(X)],(maxim-ref)/exp(1)^2*ones(length(X),1),'--r');
    hold on; plot(size_pix*[1:length(X)],f1D(Pfga,[1:length(X)]),'--b');
    

    
    % Affichage profil Y
    figure(fig_profile_Y);
    cla;xlabel('µm');
    f1D= @(p,X) (p(1)+p(2)*exp(-(X-p(3)).^2/2/p(4)^2));
    set(fig_profile_Y,'numbertitle','off','name','Small Axis Profile','units','normalized','position',pos_profile_Y);
    plot(size_pix*[1:length(Xp)],prof2,'-r',size_pix*[1:length(Xp)],ref*ones(length(Xp),1),'--k',size_pix*[1:length(Xp)],maxim*ones(length(Xp),1),'--k',size_pix*[1:length(Xp)],(maxim-ref)/exp(1)^2*ones(length(Xp),1),'--r');
    hold on; plot(size_pix*[1:length(Xp)],f1D(Pfpa,[1:length(Xp)]),'--b');
    
    demi_gd_axe_fit=2*Pfga(4);
    demi_ptt_axe_fit=2*Pfpa(4);    
else
    theta=theta-90; 
    % Affichage profil X
    figure(fig_profile_Y);
    cla;xlabel('µm');
    f1D= @(p,X) (p(1)+p(2)*exp(-(X-p(3)).^2/2/p(4)^2));
    set(fig_profile_Y,'numbertitle','off','name','Small Axis Profile','units','normalized','position',pos_profile_Y);
    plot(size_pix*[1:length(X)],prof1,'-r',size_pix*[1:length(X)],ref*ones(length(X),1),'--k',size_pix*[1:length(X)],maxim*ones(length(X),1),'--k',size_pix*[1:length(X)],(maxim-ref)/exp(1)^2*ones(length(X),1),'--r');
    hold on; plot(size_pix*[1:length(X)],f1D(Pfga,[1:length(X)]),'--b');
    
    % Affichage profil Y
    figure(fig_profile_X);
    cla;xlabel('µm');
    f1D= @(p,X) (p(1)+p(2)*exp(-(X-p(3)).^2/2/p(4)^2));
    set(fig_profile_X,'numbertitle','off','name','Great Axis Profile','units','normalized','position',pos_profile_X);
    plot(size_pix*[1:length(Xp)],prof2,'-r',size_pix*[1:length(Xp)],ref*ones(length(Xp),1),'--k',size_pix*[1:length(Xp)],maxim*ones(length(Xp),1),'--k',size_pix*[1:length(Xp)],(maxim-ref)/exp(1)^2*ones(length(Xp),1),'--r');
    hold on; plot(size_pix*[1:length(Xp)],f1D(Pfpa,[1:length(Xp)]),'--b');
    
    demi_gd_axe_fit=2*Pfpa(4);
    demi_ptt_axe_fit=2*Pfga(4);    
end
    
%% Affichage paramètres final
    figure(fig_param);clf;
    set(fig_param,'numbertitle','off','name','Estimated Parameters','units','normalized','position',pos_param);

    cnames1 = {'Thr. Value','Center X0','Center Y0'};
    mesdonnees1 = {S,X0,Y0};
    uitable('units','normalized','ColumnName',cnames1,'Data',mesdonnees1,'Position',[0.03 0.78 0.85 0.1]);

    cnames2 = {'Theta Value(°)'};
    if ( theta< -90) 
        theta=theta+180;
    elseif (theta > 90);
        theta=theta-180;
    end
    mesdonnees2 = {-theta};
    uitable('units','normalized','ColumnName',cnames2,'Data',mesdonnees2,'Position',[0.03 0.53 0.85 0.1]);

    cnames3 = {'HW G.A. Ellipse (µm)','HW. S. A. Ellipse (fit)(µm)'};
    mesdonnees3 = {demi_gd_axe*size_pix,demi_ptt_axe*size_pix};
    uitable('units','normalized','ColumnName',cnames3,'Data',mesdonnees3,'Position',[0.03 0.28 0.85 0.1]);

    cnames4 = {'Radius G.A. (µm)','Radius S.A. (µm)','Ratio radii'};
    mesdonnees4 = {demi_gd_axe_fit*size_pix,demi_ptt_axe_fit*size_pix,demi_gd_axe_fit/demi_ptt_axe_fit};
    uitable('units','normalized','ColumnName',cnames4,'Data',mesdonnees4,'Position',[0.03 0.08 0.85 0.1]);

  
%% Affichage image + fit sur fenêtre principale
    figure(fig1);
    imagesc(c_contour_ell_c);daspect([1 1 1]);
    line(X,Y);
    line(Xp,Yp);
    set(fig1,'name','Acquisition & Control - Ellipse Fitting')
%% ########################################################################

function fit_gauss_2D(hObject,Data)

% Calcul de fit gaussien 2D (utilise coupe XY pour estimation préliminaire)


global ma_vid img src obj
global fig1 fig_fit  fig_visu fig_img fig_seuil S fig_profile_X fig_profile_Y fig_param 
global choix_seuil choix_bin text
global size_pix N M
global norm_ref estimax
global pos_fig1 pos_visu pos_img pos_seuil pos_profile_X pos_profile_Y pos_fit pos_param

clear('X','x','Xp','Y','y','Yp','xp','yp','c_contour_ell','c_contour_ell_c');

%% Reinit affichage erreur
set(text,'BackgroundColor',[0 0 0],'ForegroundColor',[1 0 0],'enable','off')
% Réinit. message erreur
set(text2,'BackgroundColor',[0 0 0],'ForegroundColor',[1 0 0],'enable','off'); 
inv=0;

%% Lecture seuil selectionné
if get(choix_seuil,'value')==1;
    
        S=1/exp(1)^2;
    
    elseif get(choix_seuil,'value')==2;
    
        S=0.6;
    
    elseif get(choix_seuil,'value')==3;
        
        S=0.8;
end

switch get(choix_bin,'value')
    case 1 
        binpar=16;
    case 2 
        binpar=1;
    case 3 
        binpar=2;
    case 4 
        binpar=4;
    case 5 
        binpar=8;
    case 6 
        binpar=16;
end

%pimg=[12 120 240 145 0.25 255 520]
%pstart=[10 (130-15) 250 150 0.3 250 550];

%% Calcul params initiaux

% Appel à fonction coupe_et_fit pour effectuer coupes XY et fit Gaussien des coupes
maxim=max(max(img));
[c_contour,X0,Y0,init_waist_x,init_waist_y,x,y,xp,yp,prof1,prof2,Pfga,Pfpa]=coupe_et_fit(maxim,norm_ref);
pstart=[mean([Pfga(1) Pfpa(1)]) mean([Pfga(2) Pfpa(2)]) Pfga(4) Pfpa(4) 0 Pfga(3) Pfpa(3)]; % vecteur d'estimés initial

x=1:N;
xx=ones(1,M)'*x;
y=1:M;
yy=y'*ones(1,N);


%% Binning de l'image

Nb=N/binpar;    
Mb=M/binpar;

xt=1:Nb;
yt=1:Mb;
xxt=ones(1,Mb)'*xt;
yyt=yt'*ones(1,Nb);

imgbin=img_bin(img,binpar);
pstart=pstart.*[1 1 1/binpar 1/binpar 1 1/binpar 1/binpar];

%% Calcul du Fit 2D
critere=@(p,x,y,M,N,img) sum(sum( (f2Dp(p,x,y,M,N) - img ).^2));

pres=fminsearch(@(p) critere(p,xxt,yyt,Mb,Nb,imgbin),pstart);
pres=pres./[1 1 1/binpar 1/binpar 1 1/binpar 1/binpar];



%% Calcul des paramètres du faisceau fitté

%xdata=zeros(M,N,2); % Calcul rotation
%xdata(:,:,1)=xx;
%xdata(:,:,2)=yy;
%xdatarot(:,:,1)= xdata(:,:,1)*cos(pres(5)) - xdata(:,:,2)*sin(pres(5));
%xdatarot(:,:,2)= xdata(:,:,1)*sin(pres(5)) + xdata(:,:,2)*cos(pres(5));

X0 = pres(6);
Y0 = pres(7);

%% Création d'une image vierge pour y superposer l'image, le contour du seuillage et le contour de l'ellipse fittée 
% Creation image fittée
imfit = f2Dp(pres,xx,yy,M,N);
delta=0.5;
imgnorm=imfit-pres(1)*ones(M,N);
c_contour_ell = (imgnorm < (pres(2)/exp(1)^2+ delta) ) .* ( imgnorm >(pres(2)/exp(1)^2-delta ) ); 
      
        c_contour_ell_c=zeros(size(imfit,1),size(imfit,2),3);
        c_contour_ell_c(:,:,1)=(double(img)/255).*(1-c_contour_ell) + c_contour_ell;
        c_contour_ell_c(:,:,2)=(double(img)/255);
        c_contour_ell_c(:,:,3)=(double(img)/255);

        
theta=90-pres(5)*180/pi;

        

%% Tracé du grand axe
        Y=1:M;
        X=X0+(Y-Y0)*(tand(theta));
        sel=(0<X).*(X<N);
        if (sum(sel==1)<=1) 
         X=[0 round(X0) N];%round(X0)*ones(1,M);
         Y=round([Y0-1 Y0 Y0+1]); %round(Y0)*ones(1,M);
        else
            Y=Y(sel==1); X=round(X(sel==1));
        end
        
        %% Tracé du petit axe
        
        Yp=1:M;
        Xp=X0+(Yp-Y0)*(-1/tand(theta));
        sel=(0<Xp).*(Xp<N);
        if (sum(sel==1)<=1)
            Xp=[0 round(X0) N];
            Yp=round([Y0-1 Y0 Y0+1]);
        else
        Yp=Yp(sel==1);Xp=round(Xp(sel==1));
        end
  
        %% Tracé du profil selon le grand axe et définition des caractéristiques associées à sa fenêtre de visualisation
        I=img;
        X1=X(1);
        X2=X(end);
        Y1=Y(1);
        Y2=Y(end);
        x=[X1 X2];
        y=[Y1 Y2];
        [X,Y,prof1]=improfile(I,x,y);       
   
        %% Tracé du profil selon le petit axe et définition des caractéristiques associées à sa fenêtre de visualisation
        X1p=Xp(1);
        X2p=Xp(end);
        Y1p=Yp(1);
        Y2p=Yp(end);
        xp=[X1p X2p];
        yp=[Y1p Y2p];
        [Xp,Yp,prof2]=improfile(I,xp,yp);
     
        % VERIFS
%imstart = f2Dp(pstart,xx,yy,M,N);
%figure(fig_seuil);
%imagesc(imstart);

%%imtest=f2Dp(pres,xx,yy,M,N);
%figure(fig_img);
%imagesc(imtest);


%% %%%% AFFICHAGES 

%% Affichage de l'image capturée
    figure(fig_img);
    imagesc(img);
    daspect([1 1 1]);
    set(fig_img,'numbertitle','off','name','Beam Image','units','normalized','position',pos_img);

%% Affichage points seuil 
    figure(fig_seuil);
    imagesc(c_contour);
    daspect([1 1 1]);
    set(fig_seuil,'numbertitle','off','name','Image Threshold Contour','units','normalized','position',pos_seuil);

%% Affichage ellipse fittée
    figure(fig_fit);
    imagesc(imfit);daspect([1 1 1]);
    set(fig_fit,'numbertitle','off','name','Fitted 2D Gaussian','units','normalized','position',pos_fit);

%% Affichage profils

if (pres(3)>=pres(4))
         inv=0;
          theta_res=pres(5)*180/pi;
else
         inv=1;
         theta_res=pres(5)*180/pi+90;
          
end
inv;

if (inv==0)
     % Affichage profil X
     figure(fig_profile_X);
     cla;xlabel('µm');
     f1D= @(p,X) (p(1)+p(2)*exp(-(X-p(3)).^2/2/p(4)^2));
     set(fig_profile_X,'numbertitle','off','name','Profil Grand Axe','units','normalized','position',pos_profile_X);
     plot(size_pix*[1:length(X)],prof1,'-r',size_pix*[1:length(X)],pres(1)*ones(length(X),1),'--k',size_pix*[1:length(X)],(pres(2)+pres(1))*ones(length(X),1),'--k',size_pix*[1:length(X)],(pres(1)+pres(2)/exp(1)^2)*ones(length(X),1),'--r');
     hold on; plot(size_pix*[1:length(X)],f1D([pres(1) pres(2) find(abs(X-pres(6))<=1,1) pres(3)],[1:length(X)]),'--b');
     
 
     
     % Affichage profil Y
     figure(fig_profile_Y);
     cla;xlabel('µm');
     f1D= @(p,X) (p(1)+p(2)*exp(-(X-p(3)).^2/2/p(4)^2));
     set(fig_profile_Y,'numbertitle','off','name','Profil Petit Axe','units','normalized','position',pos_profile_Y);
     plot(size_pix*[1:length(Xp)],prof2,'-r',size_pix*[1:length(Xp)],pres(1)*ones(length(Xp),1),'--k',size_pix*[1:length(Xp)],(pres(2)+pres(1))*ones(length(Xp),1),'--k',size_pix*[1:length(Xp)],(pres(1)+pres(2)/exp(1)^2)*ones(length(Xp),1),'--r');
     hold on; plot(size_pix*[1:length(Xp)],f1D([pres(1) pres(2) find(abs(Yp-pres(7))<=1,1) pres(4)],[1:length(Xp)]),'--b');
     
     demi_gd_axe_fit=2*pres(3);
     demi_ptt_axe_fit=2*pres(4);    

else
    % Affichage profil X
     figure(fig_profile_Y);
     cla;xlabel('µm');
     f1D= @(p,X) (p(1)+p(2)*exp(-(X-p(3)).^2/2/p(4)^2));
     set(fig_profile_Y,'numbertitle','off','name','Profil Petit Axe','units','normalized','position',pos_profile_Y);
     plot(size_pix*[1:length(X)],prof1,'-r',size_pix*[1:length(X)],pres(1)*ones(length(X),1),'--k',size_pix*[1:length(X)],(pres(2)+pres(1))*ones(length(X),1),'--k',size_pix*[1:length(X)],(pres(1)+pres(2)/exp(1)^2)*ones(length(X),1),'--r');
     hold on; plot(size_pix*[1:length(X)],f1D([pres(1) pres(2) find(abs(X-pres(6))<=1,1) pres(3)],[1:length(X)]),'--b');
     
     % Affichage profil Y
     figure(fig_profile_X);
     cla;xlabel('µm');
     f1D= @(p,X) (p(1)+p(2)*exp(-(X-p(3)).^2/2/p(4)^2));
     set(fig_profile_X,'numbertitle','off','name','Profil Grand Axe','units','normalized','position',pos_profile_X);
     plot(size_pix*[1:length(Xp)],prof2,'-r',size_pix*[1:length(Xp)],pres(1)*ones(length(Xp),1),'--k',size_pix*[1:length(Xp)],(pres(2)+pres(1))*ones(length(Xp),1),'--k',size_pix*[1:length(Xp)],(pres(1)+pres(2)/exp(1)^2)*ones(length(Xp),1),'--r');
     hold on; plot(size_pix*[1:length(Xp)],f1D([pres(1) pres(2) find(abs(Yp-pres(7))<=1,1) pres(4)],[1:length(Xp)]),'--b');
     
     demi_gd_axe_fit=2*pres(4);
     demi_ptt_axe_fit=2*pres(3);    
 end
    
%% Affichage paramètres final
    figure(fig_param);clf;
    set(fig_param,'numbertitle','off','name','Estimated Parameters','units','normalized','position',pos_param);

    cnames1 = {'Thr. Value','Centre X0','Centre Y0'};
    mesdonnees1 = {S,X0,Y0};
    uitable('units','normalized','ColumnName',cnames1,'Data',mesdonnees1,'Position',[0.03 0.78 0.85 0.1]);

    if ( theta_res< -90) 
        theta_res=theta_res+180;
    elseif (theta_res > 90);
        theta_res=theta_res-180;
    end
    cnames2 = {'Theta Value(°)'};
    mesdonnees2 = {theta_res};
    uitable('units','normalized','ColumnName',cnames2,'Data',mesdonnees2,'Position',[0.03 0.53 0.85 0.1]);

    cnames4 = {'Rad. G.A. (µm)','Rad. S.A. (µm)','Ratio radii'};
    mesdonnees4 = {demi_gd_axe_fit*size_pix,demi_ptt_axe_fit*size_pix,demi_gd_axe_fit/demi_ptt_axe_fit};
    uitable('units','normalized','ColumnName',cnames4,'Data',mesdonnees4,'Position',[0.03 0.08 0.85 0.1]);


%% Affichage image + fit sur fenêtre principale
    figure(fig1);
    imagesc(c_contour_ell_c);daspect([1 1 1]);
    line(X,Y);
    line(Xp,Yp);
    set(fig1,'name','Acquisition & Control - 2D Gaussian Fit')
    %str1=sprintf('Ctr:X %d Y %d / Seuil: %.2f / Theta: %.2f  Demi gd axe: %.2f / Demi ptt axe: %.2f Rapp. waists: %.2f ' ,...
    %   round(X0),round(Y0),S,theta,demi_gd_axe,demi_ptt_axe,demi_gd_axe/demi_ptt_axe);
 %% ###################################################################   
    
    function F = f2Dp(p,x,y,M,N)

xdata=zeros(M,N,2);
xdata(:,:,1)=x;
xdata(:,:,2)=y;
xdatarot(:,:,1)= xdata(:,:,1)*cos(p(5)) - xdata(:,:,2)*sin(p(5));
xdatarot(:,:,2)= xdata(:,:,1)*sin(p(5)) + xdata(:,:,2)*cos(p(5));
x0rot = p(6)*cos(p(5)) - p(7)*sin(p(5));
y0rot = p(6)*sin(p(5)) + p(7)*cos(p(5));


F = p(1)*ones(M,N) + p(2)*exp(-((xdatarot(:,:,1)-x0rot).^2/(2*p(3)^2) + ((xdatarot(:,:,2)-y0rot).^2)/(2*p(4)^2)));     