"""V8.1 geometric measures of the mouth zone (complements, never replaces, the visual evaluation).
Zone = pocket columns of the pre-LCM grid (open to the outside, floor within 6 layers, ceiling within 5) in the component touching a mouth patch.
For each model grid: mean / min clear height of those columns (layers of 3.2 mm), number of exposed interior-colour cells (dark 0 / red 4) in the zone
(+-1 column) that touch the outside, and the number of zone columns whose clear height is under 3 layers."""
import json, sys, numpy as np
from scipy import ndimage
def load(f):
    d=np.load(f); G=d['grid'].astype(int); F=d['fine']; K=int(d['k']); NX,NY,NZ=G.shape
    return G,(G>=0)&(F.reshape(NX,K,NY,K,NZ,K).mean(axis=(1,3,5))>=0.5)
def outside_of(occ):
    lab,n=ndimage.label(~occ); b=np.unique(np.concatenate([lab[0].ravel(),lab[-1].ravel(),lab[:,0].ravel(),lab[:,-1].ravel(),lab[:,:,0].ravel(),lab[:,:,-1].ravel()]))
    return np.isin(lab,b[b>0])
G0,o0=load(sys.argv[1]); out0=outside_of(o0); NX,NY,NZ=o0.shape
pk={}
for x in range(NX):
    for z in range(NZ):
        for y in range(6,NY-6):
            if o0[x,y,z] or not out0[x,y,z]: continue
            u=next((k for k in range(1,6) if o0[x,y+k,z]),None); d=next((k for k in range(1,7) if o0[x,y-k,z]),None)
            if u is None or d is None: continue
            pk.setdefault((x,z),[]).append(y)
# keep the component touching the mouth (patch centres in mm -> cells)
D=json.load(open(sys.argv[2])); P=[p for p in D['details'] if p['classe']=='bouche']
cols=sorted(pk); S=set(cols); comp={}; cid=0
for c in cols:
    if c in comp: continue
    cid+=1; st=[c]; comp[c]=cid
    while st:
        x,z=st.pop()
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            q=(x+dx,z+dz)
            if q in S and q not in comp: comp[q]=cid; st.append(q)
keep=set()
for k in range(1,cid+1):
    mem=[c for c in cols if comp[c]==k]
    for p in P:
        cen=np.array(p['centre_mm']); 
        if min(np.linalg.norm(np.array([(x+.5)*8,(int(np.median(pk[(x,z)]))+.5)*3.2,-(z+.5)*8])-cen) for x,z in mem)<=p['longueur_mm']/2+8: keep.add(k)
zone=[c for c in cols if comp[c] in keep]; zs=set(zone)
zone1=set((x+dx,z+dz) for x,z in zone for dx in (-1,0,1) for dz in (-1,0,1))
res={}
for name,f in zip(sys.argv[3::2],sys.argv[4::2]):
    G,o=load(f); out=outside_of(o); heights=[]
    for x,z in zone:
        ys=[y for y in pk[(x,z)]]; lo=min(ys)-1; hi=max(ys)+1
        # clear height in this model: empty cells between the floor top and the first solid above, starting from the pocket's lowest cell
        y=min(ys); 
        while y>0 and not o[x,y-1,z]: y-=1
        top=y
        while top<NY and not o[x,top,z]: top+=1
        heights.append(min(top-y,9))
    exp={'dark':0,'red':0}
    for x,z in zone1:
        if not(0<=x<NX and 0<=z<NZ): continue
        for y in range(70,96):
            if not o[x,y,z]: continue
            nb=[(x+1,y,z),(x-1,y,z),(x,y+1,z),(x,y-1,z),(x,y,z+1),(x,y,z-1)]
            if any(0<=a<NX and 0<=b<NY and 0<=c<NZ and out[a,b,c] for a,b,c in nb):
                if G[x,y,z]==0: exp['dark']+=1
                elif G[x,y,z]==4: exp['red']+=1
    res[name]=dict(colonnes_zone=len(zone),hauteur_libre_moy_plaques=round(float(np.mean(heights)),2),hauteur_libre_min=int(min(heights)),colonnes_sous_3_plaques=int(sum(1 for h in heights if h<3)),
                   cellules_sombres_exposees=exp['dark'],cellules_rouges_exposees=exp['red'])
print(json.dumps(res,indent=1,ensure_ascii=False))
