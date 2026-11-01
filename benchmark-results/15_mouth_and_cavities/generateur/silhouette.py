"""Lateral silhouettes (projection along the sagittal normal) of the head snout: GLB fine occupancy (blue) vs LEGO grid (orange)."""
import numpy as np, json, sys
from PIL import Image, ImageDraw
R=json.load(open('proto/v8/details.json'))['repere']; ax=np.array(R['axe_museau']); lat=np.array(R['normale_plan_sagittal'])
npz=sys.argv[1]; out=sys.argv[2]
d=np.load(npz); G=d['grid']; F=d['fine']; K=int(d['k']); NX,NY,NZ=G.shape
fr=F.reshape(NX,K,NY,K,NZ,K).mean(axis=(1,3,5)); occ=(G>=0)&(fr>=0.5)
U0,U1,V0,V1=215,365,225,335; S=8; W,H=int((U1-U0)*S),int((V1-V0)*S)
def proj(pts_mm):
    return pts_mm@ax, pts_mm[:,1]
img=Image.new('RGB',(W,H),(255,255,255)); px=np.array(img)
# GLB fine voxels
fi=np.argwhere(F)  # (x,y,z) fine indices, size 20/K x 8/K x 20/K LDU
cen=(fi+0.5)*np.array([20.0/K,8.0/K,20.0/K]); mm=np.c_[cen[:,0]*.4,cen[:,1]*.4,-cen[:,2]*.4]
u,v=proj(mm); sel=(u>U0)&(u<U1)&(v>V0)&(v<V1)&(mm[:,2]<-90)
a=np.zeros((H,W),bool); xi=((u[sel]-U0)*S).astype(int); yi=(H-1-((v[sel]-V0)*S)).astype(int); a[yi,xi]=True
from scipy import ndimage; a=ndimage.binary_closing(a,iterations=3)
px[a]=(150,170,255)
# grid cells outline
idx=np.argwhere(occ); c=(idx+0.5)*np.array([8.0,3.2,8.0]); c=np.c_[c[:,0],c[:,1],-c[:,2]]
uu,vv=proj(c); img=Image.fromarray(px); dr=ImageDraw.Draw(img)
for (x,y,z),u_,v_ in zip(idx,uu,vv):
    if not(U0<u_<U1 and V0<v_<V1) or c[0][2]>0: continue
    cc=(x*8+4,y*3.2+1.6,-(z*8+4))
    if cc[2]>-90: continue
    X=(u_-U0)*S; Y=H-(v_-V0)*S
    dr.rectangle([X-4*S*0.9,Y-1.6*S,X+4*S*0.9,Y+1.6*S],outline=(255,140,0))
for t in range(0,int(U1-U0),10): dr.line([(t*S,0),(t*S,12)],fill=(0,0,0)); dr.text((t*S+2,12),str(int(U0+t)),fill=(0,0,0))
img.save(out); print(img.size)
