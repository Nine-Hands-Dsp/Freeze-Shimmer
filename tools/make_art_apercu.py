import sys, math, os, io, json
sys.path.insert(0,'.')
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import photo_controls as PC
AS=2                       # px par unite
OUT_H=1800
SHELL=sys.argv[1] if len(sys.argv)>1 else 'shell.png'; OUTP=sys.argv[2] if len(sys.argv)>2 else 'preview_full.png'
shell=Image.open(SHELL).convert('RGBA'); sw,sh=shell.size
k=OUT_H/sh
bodyW=int(round(sw*k))
jack,jw,jh=PC.jack_sprite(104,AS,1); PROT=int(round(jw*AS))
Wf=bodyW+2*PROT; Hf=OUT_H
print('image',Wf,Hf,'corps',bodyW)
def P(fx,fy): return (PROT+fx*bodyW, fy*Hf)
def U(v): return v*AS
bg=Image.new('RGBA',(Wf,Hf),(0,0,0,0))
# ---- jacks (derriere le boitier)
jy=0.585*Hf
for side,(sx) in ((-1,0),(1,Wf-PROT)):
    spr,w,h=PC.jack_sprite(104,AS,side)
    im=Image.fromarray(np.clip(spr,0,255).astype(np.uint8),'RGBA')
    bg.alpha_composite(im,(sx if side<0 else sx, int(round(jy-im.height/2))))
# ---- boitier
body=shell.resize((bodyW,Hf),Image.LANCZOS)
from PIL import ImageFilter
body=body.filter(ImageFilter.UnsharpMask(radius=1.0,percent=25,threshold=2))
bg.alpha_composite(body,(PROT,0))
# ---- repères (fractions du boitier)
CL,CC,CR=.215,.5,.785
pos={ 'dry':(CL,.108),'effect':(CR,.108),'blend':(CL,.282),'time':(CC,.282),'speed':(CR,.282),'voice':(CL,.469),'tone':(CR,.469)}
led_mode=(.5008,.0614); led_frz=(.5008,.5205); fsP=(.5007,.905)
# ---- occlusion ambiante sur la coque (potards, LED, footswitch) : cuite dans le fond, sous les pieces
def ao_layer(items):
    A=np.zeros((Hf,Wf),np.float32)
    yy,xx=np.mgrid[0:Hf,0:Wf].astype(np.float32)
    for cx,cy,R,wide,amp in items:
        for dx,dy,k,s,w in ((0,0,1.0,0.16,0.55),(0.045*R,0.06*R,1.0,0.07,0.55),(0.05*R,0.07*R,1.0,wide,0.30)):
            d=np.hypot(xx-cx-dx,yy-cy-dy)
            A=np.maximum(A,amp*w*np.exp(-(np.maximum(d-R,0)/(s*R*2.2))**1.35)*(d>R*0.0))
    return A
KR=212/2*1.02; _a,_b,_c,btnR=PC.footswitch_sprite(104,AS)
items=[(*P(fx_,fy_),KR,0.62,0.95) for fx_,fy_ in pos.values()]
items+=[(*P(*led_mode),15*AS/2*1.9,1.9,0.9),(*P(*led_frz),15*AS/2*1.9,1.9,0.9)]
items+=[(*P(*fsP),btnR*AS*1.0,0.55,1.0)]
Aao=ao_layer(items)*(np.asarray(body.split()[3]).astype(np.float32)[:, :].copy() if False else 1)
bodyA=np.zeros((Hf,Wf),np.float32); bodyA[:,PROT:PROT+bodyW]=np.asarray(body.split()[3]).astype(np.float32)/255
Aao=np.clip(Aao*bodyA,0,1)*0.78
lay_ao=np.zeros((Hf,Wf,4),np.uint8); lay_ao[...,:3]=(3,9,22); lay_ao[...,3]=(Aao*255).astype(np.uint8)
bg.alpha_composite(Image.fromarray(lay_ao,'RGBA'))
# ---- footswitch photo (statique)
fl,refl,FS_S,btnR=PC.footswitch_sprite(104,AS)
fx,fy=P(*fsP)
fim=Image.fromarray(np.clip(fl,0,255).astype(np.uint8),'RGBA')
bg.alpha_composite(fim,(int(round(fx-fim.width/2)),int(round(fy-fim.height/2))))
# ---- LED eteintes
off,on,S_=PC.led_sprites(17,AS,colour='blue')
offi=Image.fromarray(np.clip(off,0,255).astype(np.uint8),'RGBA'); oni=Image.fromarray(np.clip(on,0,255).astype(np.uint8),'RGBA')
for lp in (led_mode,led_frz):
    x,y=P(*lp); bg.alpha_composite(offi,(int(round(x-offi.width/2)),int(round(y-offi.height/2))))
bg.save('background.png')
# =============== apercu : ajoute ce que dessine l'editeur ===============
pv=bg.copy()
def font(n,u): return ImageFont.truetype(f'fonts/Poppins-{n}.ttf',int(round(u*AS)))
def spaced(img,x,y,txt,f,track_u,fill,anchor='m',rot=0,shadow=True):
    tr=track_u*AS; ws=[f.getlength(c) for c in txt]; tot=sum(ws)+tr*(len(txt)-1)
    pad=int(f.size*2); lay=Image.new('RGBA',(int(tot+2*pad),int(f.size*3)),(0,0,0,0)); d=ImageDraw.Draw(lay); cx=pad
    for c,w in zip(txt,ws): d.text((cx,lay.height/2),c,font=f,fill=fill,anchor='lm'); cx+=w+tr
    if shadow:
        a=np.asarray(lay)[...,3].astype(float)/255; sh=np.clip(cv2.GaussianBlur(np.roll(np.roll(a,2,0),2,1),(0,0),4.0)*2.0+cv2.GaussianBlur(np.roll(np.roll(a,1,0),1,1),(0,0),1.3)*1.0,0,1)*0.92
        sl=np.zeros(a.shape+(4,),np.uint8); sl[...,:3]=(6,28,60); sl[...,3]=(sh*255).astype(np.uint8)
        base=Image.fromarray(sl,'RGBA'); base.alpha_composite(lay); lay=base
    if rot: lay=lay.rotate(-rot,expand=True,resample=Image.BICUBIC)
    img.alpha_composite(lay,(int(round(x-lay.width/2)),int(round(y-lay.height/2))))
    return tot
WHITE=(232,238,245,255); BLUE=(150,222,255,255)
# knobs
lay={n:Image.open(f'knob_{n}.png') for n in ['shadow','crown','cap','marker','highlight']}
CROWN_D=212; comp=int(round(CROWN_D/0.742))
def knob(img,cx,cy,v):
    a=-135+270*v
    def r(n): return lay[n].resize((comp,comp),Image.LANCZOS).rotate(-a,resample=Image.BICUBIC)
    sh=r('shadow'); img.alpha_composite(sh,(int(cx-comp/2+0.025*comp),int(cy-comp/2+0.025*comp)))
    for n in ['crown','cap','marker']: img.alpha_composite(r(n),(int(cx-comp/2),int(cy-comp/2)))
    img.alpha_composite(lay['highlight'].resize((comp,comp),Image.LANCZOS),(int(cx-comp/2),int(cy-comp/2)))
vals=dict(dry=.5,effect=.72,blend=.28,time=.5,speed=.62,voice=.38,tone=.8)
for n,(fx_,fy_) in pos.items():
    x,y=P(fx_,fy_); knob(pv,x,y,vals[n])
# labels
LAB={'dry':('DRY',[]),'effect':('EFFECT',[]),'blend':('BLEND',['RVB MIX']),'time':('TIME',['DELAY']),'speed':('SPEED',['LAYER']),'voice':('VOICE',['DEPTH']),'tone':('TONE',['RATE','GLISS'])}
fm=font('Medium',22); fs2=font('Medium',20)
for n,(fx_,fy_) in pos.items():
    x,y=P(fx_,fy_); m,sec=LAB[n]; yy=y+U(70)
    spaced(pv,x,yy,m,fm,3.5,WHITE)
    for i,s in enumerate(sec): spaced(pv,x,yy+U(22)*(i+1),s,fs2,2.5,BLUE)
x,y=P(*led_mode); spaced(pv,x,y+U(38),'MODE',fm,3.5,WHITE)
# titre givre (apercu : degrade + grain de la glace de la coque)
def title(img,cx,cy):
    f=font('Bold',42); w1=f.getlength('FREEZE '); w2=f.getlength('SHIMMER'); tr=2.8*AS
    n1,n2=len('FREEZE '),len('SHIMMER'); tot=w1+w2+tr*(n1+n2-1)
    pad=80; L=Image.new('L',(int(tot+2*pad),int(f.size*2.4)),0); d=ImageDraw.Draw(L); xx=pad
    for c in 'FREEZE SHIMMER': d.text((xx,L.height/2),c,font=f,fill=255,anchor='lm'); xx+=f.getlength(c)+tr
    Lm=np.asarray(L).astype(float)/255
    h,w=Lm.shape; xs=np.linspace(0,1,w)[None,:]; ys=np.linspace(0,1,h)[:,None]
    split=(pad+w1+tr*n1)/w
    col=np.zeros((h,w,3)); a1=np.array([236,242,248.]); a2=np.array([96,190,240.])
    mix=np.clip((xs-split)/0.01+0.5,0,1)[...,None]
    col=a1*(1-mix)+a2*mix
    col=col*(0.86+0.14*(1-ys))[...,None]
    # grain givre : bruit multi-echelle
    rng=np.random.default_rng(7); g=np.zeros((h,w))
    for s,wt in ((1.2,.5),(3,.35),(8,.25)):
        g+=cv2.GaussianBlur(rng.normal(0,1,(h,w)),(0,0),s)*wt*s**0.5
    g=g/ g.std()*0.06
    col=col*(1+g[...,None])
    # relief : arete haut-gauche eclairee, bas-droit sombre
    bl=cv2.GaussianBlur(Lm,(0,0),2.2); gy,gx=np.gradient(bl); lit=np.clip(-(gx+gy)*14,0,1)*0.6
    col=np.clip(col*(1+0.22*lit[...,None]),0,255)
    # ombre portee douce
    k=int(round(2.2*AS)); M=np.float32([[1,0,k],[0,1,k]])
    sh=cv2.warpAffine(cv2.GaussianBlur(Lm.astype(np.float32),(0,0),2.0*AS),M,(w,h))
    sh=np.clip(sh*0.85+cv2.GaussianBlur(cv2.warpAffine(Lm.astype(np.float32),M,(w,h)),(0,0),0.8*AS)*0.35,0,1)
    out=np.zeros((h,w,4)); out[...,:3]=(6,18,40); out[...,3]=sh*255
    base=Image.fromarray(out.astype(np.uint8),'RGBA')
    top=Image.fromarray(np.dstack([col,Lm*255]).astype(np.uint8),'RGBA')
    base.alpha_composite(top)
    img.alpha_composite(base,(int(cx-w/2),int(cy-h/2)))
x,y=P(.5,.724); title(pv,x,y)
# logo NINE HANDS | DSP (SVG blanc officiel, nettoye)
import subprocess
svg=open('logo_white_raw.svg').read()
LOGO_W=190*AS
from playwright.sync_api import sync_playwright
def render_logo():
    import re
    paths=re.findall(r'<path class="st2" d="([^"]+)"',svg)
    d=' '.join(paths)
    html=f'<html><body style="margin:0;background:transparent"><svg xmlns="http://www.w3.org/2000/svg" viewBox="195 378 2602 244" width="{LOGO_W*3}"><g fill="#fff"><path d="{d}"/></g></svg></body></html>'
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(viewport={'width':LOGO_W*3,'height':int(LOGO_W*3*244/2602)+4}); pg.set_content(html)
        pg.screenshot(path='logo_white.png',omit_background=True); b.close()
render_logo()
lg=Image.open('logo_white.png').convert('RGBA'); bb=lg.getbbox(); lg=lg.crop(bb); lg=lg.resize((LOGO_W,int(LOGO_W*lg.height/lg.width)),Image.LANCZOS)
x,y=P(.5,.7625); pv.alpha_composite(lg,(int(x-lg.width/2),int(y-lg.height/2)))
# IN / OUT
fio=font('Medium',17)
spaced(pv,U(60),jy,'OUT',fio,2,WHITE,rot=90); spaced(pv,Wf-U(60),jy,'IN',fio,2,WHITE,rot=90)
# pastille presets (400 x 38 unites)
x,y=P(.5,.654); pw,ph=U(400),U(38)
pil=Image.new('RGBA',(int(pw)+4,int(ph)+4),(0,0,0,0)); d=ImageDraw.Draw(pil)
d.rounded_rectangle([2,2,2+pw,2+ph],radius=ph/2,fill=(5,8,13,255),outline=(150,170,190,255),width=2)
pv.alpha_composite(pil,(int(x-pil.width/2),int(y-pil.height/2)))
spaced(pv,x,y,'Clean Plate',font('Medium',23),0,(238,242,247,255))
d=ImageDraw.Draw(pv)
for sx,sg in ((x-pw/2+U(17),-1),(x+pw/2-U(17),1)):
    t=U(5.5); d.polygon([(sx+sg*t*0.6,y),(sx-sg*t*0.6,y-t),(sx-sg*t*0.6,y+t)],fill=(150,160,172,255))
# LED freeze allumee + halo facade
def glowlayer(cx,cy,col,sig,amp):
    yy,xx=np.mgrid[0:Hf,0:Wf].astype(np.float32); d2=((xx-cx)**2+(yy-cy)**2)
    I=amp/(1+d2/(sig**2))**1.5
    lay=np.zeros((Hf,Wf,4),np.float32); lay[...,:3]=col; lay[...,3]=np.clip(I,0,1)*255
    return Image.fromarray(lay.astype(np.uint8),'RGBA')
x,y=P(*led_frz); pv.alpha_composite(glowlayer(x,y,(60,170,255),U(34),0.55)); pv.alpha_composite(oni,(int(round(x-oni.width/2)),int(round(y-oni.height/2))))
# anneau du footswitch (halo d'Octopus), freeze actif
fx,fy=P(*fsP); footR=btnR*AS
ringR=footR*1.0775; ringW=footR*0.0674; col=(88,200,255)
SS=3; ring=Image.new('RGBA',(int(footR*5)*SS,)*2,(0,0,0,0)); rd=ImageDraw.Draw(ring); c=ring.width/2
k_=ringR/ (33.2*AS)
t=20
while t>=3:
    a=int(255*0.075*1.0); w=t*AS*k_*SS/AS*1.0
    rd.ellipse([c-ringR*SS-w/2*0,c-ringR*SS,c+ringR*SS,c+ringR*SS],outline=col+(a,),width=int(max(1,w))); t-=1.5
rd.ellipse([c-ringR*SS,c-ringR*SS,c+ringR*SS,c+ringR*SS],outline=col+(217,),width=int(ringW*SS))
rd.ellipse([c-ringR*SS,c-ringR*SS,c+ringR*SS,c+ringR*SS],outline=(215,240,255,230),width=int(ringW*0.42*SS))
ring=ring.resize((ring.width//SS,ring.height//SS),Image.LANCZOS)
pv.alpha_composite(ring,(int(fx-ring.width/2),int(fy-ring.height/2)))
pv.save(OUTP); print(pv.size)
