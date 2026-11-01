"""Sagittal sections of the GLB snout (mesh polylines, black) and of the V8 voxel grid (grey cells), in (snout axis, height) coordinates."""
import numpy as np, trimesh, json, sys
from PIL import Image, ImageDraw
R=json.load(open('proto/v8/details.json'))['repere']; ax=np.array(R['axe_museau']); lat=np.array(R['normale_plan_sagittal']); off=R['plan_offset_mm']
m=trimesh.load('proto/v7/ref_full_frame.glb',force='mesh',process=False)
d=np.load('proto/v8/run/corps_V8.npz'); G=d['grid']
U0,U1,V0,V1=215,360,215,330; S=6   # px per mm
W,H=int((U1-U0)*S),int((V1-V0)*S)
cols={-1:None,0:(40,40,40),14:(235,215,90),4:(200,30,30),15:(255,255,255)}
offs=[-30,-20,-10,0,10,20,30]; tiles=[]
cen=np.array([[ (i+.5)*8,(j+.5)*3.2,-(k+.5)*8 ] for i in range(G.shape[0]) for j in range(G.shape[1]) for k in range(G.shape[2])]).reshape(G.shape+(3,))
for o in offs:
    img=Image.new('RGB',(W,H),(255,255,255)); dr=ImageDraw.Draw(img)
    # voxel cells whose centre is within 4 mm laterally of the plane
    lp=cen@lat-(off+o); sel=(np.abs(lp)<=4)&(G>=0)
    for c in cen[sel]:
        pass
    idx=np.argwhere(sel)
    for i,j,k in idx:
        c=cen[i,j,k]; u=c@ax; v=c[1]; col=cols.get(int(G[i,j,k]),(150,150,150))
        x0=(u-U0-4)*S; x1=(u-U0+4)*S; y0=H-(v-V0+1.6)*S; y1=H-(v-V0-1.6)*S
        dr.rectangle([x0,y0,x1,y1],fill=col,outline=(120,120,120))
    sec=m.section(plane_origin=lat*(off+o),plane_normal=lat)
    if sec is not None:
        for e in sec.entities:
            p=sec.vertices[e.points]; pts=[((q@ax-U0)*S,H-(q[1]-V0)*S) for q in p]
            dr.line(pts,fill=(0,0,255),width=2)
    dr.text((8,8),f"lateral {o:+d} mm",fill=(0,0,0))
    tiles.append(img)
out=Image.new('RGB',(W,H*len(tiles)),(255,255,255))
for n,t in enumerate(tiles): out.paste(t,(0,n*H))
out.save('proto/v8/sections.png'); print(out.size)
