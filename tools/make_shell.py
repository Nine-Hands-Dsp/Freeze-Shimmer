import numpy as np, cv2
from PIL import Image
old=np.asarray(Image.open('shell_old.png').convert('RGBA')).astype(np.float32)
H,W=old.shape[:2]; A=old[...,3]/255
import sys
FS=float(sys.argv[1]) if len(sys.argv)>1 else 0.5
fr0=Image.open('tex_frost2.png').convert('RGB'); n_=int(4096*FS)
fr=np.tile(np.asarray(fr0.resize((n_,n_),Image.LANCZOS)).astype(np.float32),(3,3,1))
me=np.asarray(Image.open('tex_metal.png').convert('RGB').resize((2662,2662),Image.LANCZOS)).astype(np.float32)
frost=fr[200:200+H,400:400+W].copy(); metal=me[300:300+H,500:500+W].copy()
def usm(a,r,amt):
    b=cv2.GaussianBlur(a,(0,0),r); return np.clip(a+(a-b)*amt,0,255)
frost=usm(frost,0.8,0.12)
# 2e calque : meme texture, plus grande (gros cristaux), pose par touches
FS2=float(sys.argv[2]) if len(sys.argv)>2 else 1.25
n2=int(4096*FS2)
big=np.asarray(fr0.resize((n2,n2),Image.LANCZOS)).astype(np.float32)
big=np.tile(big,(2,2,1))[900:900+H,1100:1100+W]
big=usm(big,1.0,0.10)
rg=np.random.default_rng(21)
def blob(sig,seed):
    m=cv2.GaussianBlur(np.random.default_rng(seed).normal(0,1,(H,W)).astype(np.float32),(0,0),sig); m=(m-m.mean())/m.std(); return m
m=blob(110,5)*0.8+blob(45,6)*0.45          # taches de taille variable
T=np.clip((m-0.55)*2.4,0,1); T=T*T*(3-2*T)  # ~25 % de la surface
# on ne garde que les cristaux clairs du grand calque (evite un voile), fondu doux
bl_l=big.mean(2); bl_l=cv2.GaussianBlur(bl_l,(0,0),1.0)
loc=np.clip((bl_l-np.percentile(bl_l,35))/(np.percentile(bl_l,92)-np.percentile(bl_l,35)),0,1)
Tm=np.clip(T*(0.55+0.45*loc),0,1)[...,None]
frost=frost*(1-Tm)+big*Tm
frost=np.clip(frost,0,255)
# gros cristaux isoles : decoupes dans la texture, agrandis, poses par-ci par-la
NST=int(sys.argv[3]) if len(sys.argv)>3 else 11
SCL=float(sys.argv[4]) if len(sys.argv)>4 else 3.0
T4=np.asarray(fr0).astype(np.float32); L4=T4.mean(2)
hp=L4-cv2.GaussianBlur(L4,(0,0),28)
en=cv2.GaussianBlur(np.clip(hp,0,None),(0,0),60)           # densite de details clairs
CS=300
en[:CS//2+2]=0; en[-CS//2-2:]=0; en[:,:CS//2+2]=0; en[:,-CS//2-2:]=0
cands=[]; e2=en.copy()
for _ in range(NST*2):
    y,x=np.unravel_index(np.argmax(e2),e2.shape); cands.append((x,y)); cv2.circle(e2,(int(x),int(y)),CS,0,-1)
rs=np.random.default_rng(33)
# positions sur la coque : surtout cote glace, quelques-unes vers la transition
pts=[(.10,.06),(.40,.13),(.07,.24),(.30,.35),(.13,.46),(.42,.50),(.09,.62),(.33,.70),(.12,.80),(.38,.88),(.22,.97),(.27,.20),(.05,.40),(.45,.30)]
yy_,xx_=np.mgrid[-CS//2:CS//2,-CS//2:CS//2].astype(np.float32)
win=np.clip(1-np.hypot(xx_,yy_)/(CS/2),0,1); win=win*win*(3-2*win)
frost_f=frost.copy()
for k in range(NST):
    cx,cy=cands[k]; cx=int(cx); cy=int(cy)
    p=T4[cy-CS//2:cy+CS//2,cx-CS//2:cx+CS//2]
    h_=hp[cy-CS//2:cy+CS//2,cx-CS//2:cx+CS//2]
    a=np.clip((h_-2)/22,0,1)*win                          # seuls les brins clairs, fondus vers les bords
    a=cv2.GaussianBlur(a,(0,0),1.5)
    sc=SCL*(0.85+0.4*rs.random()); ang=rs.uniform(0,360)
    sz=int(CS*sc*1.45)
    Mx=cv2.getRotationMatrix2D((CS/2,CS/2),ang,sc); Mx[:,2]+=[sz/2-CS/2,sz/2-CS/2]
    P=cv2.warpAffine(np.dstack([p*1.06,a*255]).astype(np.float32),Mx,(sz,sz),flags=cv2.INTER_CUBIC,borderValue=0)
    P[...,:3]=usm(np.clip(P[...,:3],0,255),1.4,0.35)
    fx,fy=pts[k]; ox=int(fx*W-sz/2); oy=int(fy*H-sz/2)
    x0,y0=max(ox,0),max(oy,0); x1,y1=min(ox+sz,W),min(oy+sz,H)
    if x1<=x0 or y1<=y0: continue
    q=P[y0-oy:y1-oy,x0-ox:x1-ox]; al=(q[...,3:4]/255)*0.9
    frost_f[y0:y1,x0:x1]=frost_f[y0:y1,x0:x1]*(1-al)+np.clip(q[...,:3],0,255)*al
frost=np.clip(frost_f,0,255)                 # nettete : micro-details puis contraste local
rng0=np.random.default_rng(11)
g=rng0.normal(0,1,(H,W)).astype(np.float32)
fine=cv2.GaussianBlur(g,(0,0),0.7)*2.4+cv2.GaussianBlur(rng0.normal(0,1,(H,W)).astype(np.float32),(0,0),(0.6,5.0) and 0.6)*0
brush=cv2.GaussianBlur(rng0.normal(0,1,(H,W)).astype(np.float32),(0,0),sigmaX=22,sigmaY=0.8)*7.0
metal=np.clip(metal+(fine*0.6+brush*0.6)[...,None],0,255)
# transition glace -> metal, d'apres la forme de la coque d'origine (R eleve = glace)
Rsrc=old[...,0].copy()
_d=cv2.distanceTransform(np.pad((old[...,3]>128).astype(np.uint8),1),cv2.DIST_L2,5)[1:-1,1:-1]
Rsrc[(_d<70)&(np.arange(W)[None,:]>W*0.5)]=0
R=cv2.GaussianBlur(Rsrc,(0,0),70)
M=np.clip((R-8)/(70-8),0,1); M=M*M*(3-2*M)
# un peu de relief : la glace garde sa texture jusque dans la transition (bruit de seuil)
n=cv2.GaussianBlur(np.random.default_rng(2).normal(0,1,(H,W)).astype(np.float32),(0,0),6); n=n/n.std()*0.10
fl=cv2.GaussianBlur(frost.mean(2),(0,0),1.5); fl=(fl-np.percentile(fl,5))/(np.percentile(fl,97)-np.percentile(fl,5)); fl=np.clip(fl,0,1)
M0=np.clip(M+n*M*(1-M)*3,0,1)
M=np.clip((M0*1.45+fl*0.55-0.50)/0.60,0,1); M=np.where(M0>0.97,1.0,M); M=cv2.GaussianBlur(M,(0,0),1.2)*np.clip((0.74*W-np.arange(W)[None,:])/(0.12*W),0,1)
# harmonisation : le givre un peu plus lumineux/blanc vers le bord gauche (comme l'original)
xs=np.linspace(0,1,W)[None,:,None]
fr2=frost*(1.0+0.10*(1-xs))
base=metal*(1-M[...,None])+fr2*M[...,None]
# bague exterieure (rebord) et traits conserves de la coque d'origine
dist=cv2.distanceTransform(np.pad((A>0.5).astype(np.uint8),1),cv2.DIST_L2,5)[1:-1,1:-1]
rim=np.clip((52-dist)/22,0,1)
out=base*(1-rim[...,None])+old[...,:3]*rim[...,None]
# bord droit : on lisse le rebord le long de sa hauteur (plus d'eclats de givre ni de rayures) avec un fondu doux en haut et en bas
bl=cv2.GaussianBlur(old[...,:3],(0,0),sigmaX=1.0,sigmaY=48)
yy=np.arange(H)[:,None].astype(np.float32)
def sm(t): t=np.clip(t,0,1); return t*t*(3-2*t)
wy=sm((yy-110)/150)*sm((H-110-yy)/150)
xx=np.arange(W)[None,:].astype(np.float32)
band=np.clip((70-dist)/16,0,1)*(xx>W*0.70)
wR=(wy*band)[...,None]
out=out*(1-wR)+(blur_rim:=bl)*wR
# traits fins (cadre, arc, etoile, points) : conserves de la coque d'origine cote sombre (top-hat), puis symetrie sur l'axe vertical
lum=old[...,:3].mean(2)
th=lum-cv2.GaussianBlur(lum,(0,0),9)
alpha=np.clip((th-16)/50,0,1)
alpha[dist<50]=0
bw=(alpha>0.3).astype(np.uint8)
nlab,lab,st,_=cv2.connectedComponentsWithStats(bw,connectivity=8)
keep=np.zeros(nlab,bool); keep[1:]=st[1:,4]>900
alpha=alpha*keep[lab]
SX,SY=W/2.0,1840
alpha[1790:1895,int(SX)-70:int(SX)+70]=0            # etoile retracee a part
cxi=int(W//2)
mir=alpha[:,::-1]
Lmask=np.where((np.arange(W)[None,:]<cxi),mir,alpha)
colimg=np.maximum(old[...,:3],0); colmir=colimg[:,::-1]
colL=np.where((np.arange(W)[None,:]<cxi)[...,None],colmir,colimg)
colL=np.clip(colL*1.0+25,0,255)
halo=cv2.GaussianBlur(Lmask,(0,0),3.0)
out=out*(1-halo[...,None]*0.38)
out=out*(1-Lmask[...,None])+colL*Lmask[...,None]
Lmask=Lmask
from PIL import ImageDraw
SS=4; sz=160; st_im=Image.new('L',(sz*SS,sz*SS),0); dd=ImageDraw.Draw(st_im); c=sz*SS/2
def ray(ang,L_,w):
    import math
    ca,sa=math.cos(ang),math.sin(ang); px,py=-sa,ca
    dd.polygon([(c+px*w*SS,c+py*w*SS),(c+ca*L_*SS,c+sa*L_*SS),(c-px*w*SS,c-py*w*SS),(c-ca*8*SS,c-sa*8*SS)],fill=255)
import math
for k in range(4): ray(k*math.pi/2,40,3.2)
for k in range(4): ray(math.pi/4+k*math.pi/2,22,2.2)
dd.ellipse([c-5*SS,c-5*SS,c+5*SS,c+5*SS],fill=255)
star=np.asarray(st_im.resize((sz,sz),Image.LANCZOS)).astype(np.float32)/255
y0=int(SY-sz/2); x0=int(round(SX-sz/2))
sm=np.zeros((H,W),np.float32); sm[y0:y0+sz,x0:x0+sz]=star
out=out*(1-sm[...,None])+np.array([120,196,236.])*sm[...,None]
Image.fromarray(np.dstack([np.clip(out,0,255),A*255]).astype(np.uint8),'RGBA').save('shell.png')
Image.fromarray((Lmask*255).astype(np.uint8)).resize((W//3,H//3)).save('lines_mask_prev.png')
