# Images de la notice, tirees du rendu reel : couverture (pedale detouree + reflet + halo), vue d'ensemble numerotee, logo blanc.
# Usage : python3 tools/notice_assets.py   (lit tools/manual_assets/pedale_rendu.png = rendu 1316 x 1800 avec canal alpha)
import os, re, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = os.path.join(R, "tools", "manual_assets")
ped = Image.open(os.path.join(A, "pedale_rendu.png")).convert("RGBA"); W, H = ped.size
# ---- couverture : halo bleu tres doux + pedale + reflet sur sol noir
pad = 300; refl_h = int(H * 0.30)
cw, ch = W + 2 * pad, pad + H + refl_h + 40
cv = np.zeros((ch, cw, 4), np.float32)
a = np.zeros((ch, cw), np.float32); a[pad:pad + H, pad:pad + W] = np.asarray(ped)[..., 3] / 255
halo = cv2.GaussianBlur(a, (0, 0), 90)
yy, xx = np.mgrid[0:ch, 0:cw]; edge = np.minimum.reduce([xx, cw - 1 - xx, yy, ch - 1 - yy]).astype(np.float32)
halo = halo * np.clip(edge / 120, 0, 1) ** 2 * 0.55                       # retombe a zero avant les bords de l'image
cv[..., 0], cv[..., 1], cv[..., 2], cv[..., 3] = 80, 190, 245, halo * 255
im = Image.fromarray(cv.astype(np.uint8), "RGBA")
refl = ped.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, W, refl_h)); ra = np.asarray(refl).copy().astype(np.float32)
ra[..., 3] *= np.linspace(0.30, 0, refl_h)[:, None]; refl = Image.fromarray(ra.astype(np.uint8), "RGBA")
im.alpha_composite(refl, (pad, pad + H + 6)); im.alpha_composite(ped, (pad, pad))
im.save(os.path.join(A, "cover_pedale.png"))
# ---- vue d'ensemble numerotee
bg = Image.new("RGBA", ped.size, (22, 24, 28, 255)); bg.alpha_composite(ped); d = ImageDraw.Draw(bg)
f = ImageFont.truetype(os.path.join(R, "assets", "fonts", "Poppins-Bold.ttf"), 34)
CL, CC, CR = .215, .5, .785; bodyW, PROT = 1228, 44
def P(fx, fy): return (PROT + fx * bodyW, fy * H)
pts = [P(CL, .108), P(CR, .108), P(CL, .282), P(CC, .282), P(CR, .282), P(CL, .469), P(CR, .469)]
badges = [(x - 100, y - 100) for x, y in pts]
mx, my = P(.5008, .0614); fx_, fy_ = P(.5008, .5205); sx, sy = P(.5007, .905)
badges += [(mx + 70, my - 20), (fx_ + 70, fy_ - 30), (sx + 130, sy - 60), (300, .654 * H - 52)]
for n, (x, y) in enumerate(badges, 1):
    d.ellipse([x - 24, y - 24, x + 24, y + 24], fill=(255, 196, 40, 255), outline=(20, 20, 20, 255), width=3)
    d.text((x, y + 1), str(n), font=f, fill=(15, 15, 15, 255), anchor="mm")
bg.convert("RGB").save(os.path.join(A, "overview_annotated.png"))
print("ok")
