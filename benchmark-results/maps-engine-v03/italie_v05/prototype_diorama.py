#!/usr/bin/env python3
"""V0.5 genuine LEGO-component proof: Alpine volume and miniature Colosseum.

Not a raster illustration, not a finished Italian map, not physically verified.
No modifications to the existing V0.3 map generation or engine 1.
"""
import argparse,csv,json,math,hashlib
from pathlib import Path
from collections import Counter
W,H=48,32
BLUE,GRAY,DGRAY,TAN,DTAN,BROWN,GREEN,WHITE=272,71,72,19,28,70,2,15
PL={(8,8):'41539',(8,4):'3035',(4,8):'3035',(4,4):'3031',
    (2,4):'3020',(4,2):'3020',(2,2):'3022',
    (2,1):'3023',(1,2):'3023',(1,1):'3024',
    (1,4):'3710',(4,1):'3710',(1,6):'3666',(6,1):'3666'}
BK={(2,2):'3003',(1,1):'3005',(1,2):'3004',(2,1):'3004'}
class Scene:
    def __init__(self):self.parts=[]
    def add(self,x,z,w,d,y,h,part,col,region,kind='plate',angle=0):
        assert 0<=x and 0<=z and x+w<=W and z+d<=H,(x,z,w,d)
        assert y>=0 and h in (1,3)
        p=dict(id=len(self.parts)+1,x=x,z=z,w=w,d=d,zbot=y,h=h,
               part=part,colour=col,region=region,kind=kind,angle=angle)
        self.parts.append(p);return p
    def plate(self,x,z,w,d,y,col,region):
        return self.add(x,z,w,d,y,1,PL[(w,d)],col,region)
    def brick(self,x,z,w,d,y,col,region,part=None):
        return self.add(x,z,w,d,y,3,part or BK[(w,d)],col,region,'brick')
def backing(s):
    for x in range(0,W,8):
        for z in range(0,H,8):s.plate(x,z,8,8,0,DGRAY,'backing')
    def seg(n):return [4]+[8]*((n-8)//8)+[4]
    x=0
    for w in seg(W):
        z=0
        for d in seg(H):
            s.plate(x,z,w,d,1,DGRAY,'backing');z+=d
        x+=w
    for x in range(0,W,2):
        for z in range(0,H,4):s.plate(x,z,2,4,2,BLUE,'sea')
def tiers(x,z):
    def hill(cx,cz,rx,rz,pow):
        return max(0,1-((x-cx)/rx)**2-((z-cz)/rz)**2)**pow
    a=5.9*hill(12.8,12.4,11.7,12.0,1.4)
    b=4.4*hill(19.4,20.5,7.8,7.9,1.25)
    valley=1.3*hill(16.7,17.0,5.8,5.0,1.7)
    return max(0,int(round(max(a,b)-valley)))
def mountain(s):
    h={(x,z):tiers(x+1,z+1) for x in range(2,28,2) for z in range(2,30,2)}
    h={k:v for k,v in h.items() if v>0}
    for (x,z),height in sorted(h.items()):
        for j in range(height):
            y=3+j*3
            if j<height-1:
                s.brick(x,z,2,2,y,DGRAY if j>=2 else BROWN if j else GREEN,'mountain_core')
            else:
                col=WHITE if height>=6 else GRAY if height>=5 else BROWN if height>=3 else GREEN
                neighbours=[h.get((x+2,z),0),h.get((x,z+2),0),h.get((x-2,z),0),h.get((x,z-2),0)]
                if min(neighbours)<height:
                    q=s.brick(x,z,2,2,y,col,'mountain_surface',part='3039')
                    q['angle']=[0,90,180,270][neighbours.index(min(neighbours))]
                else:s.brick(x,z,2,2,y,col,'mountain_surface')
    return h
def stadium(s):
    for x in range(30,46,2):
        for z in range(8,24,2):s.plate(x,z,2,2,3,TAN,'amphitheatre_base')
    cx,cz=38,16
    points=set()
    for z in (cz-5,cz+5):
        for x in (cx-4,cx-1,cx+2,cx+5):points.add((x,z))
    for x in (cx-7,cx+7):
        for z in (cz-3,cz,cz+3):points.add((x,z))
    for x in (cx-6,cx+6):
        for z in (cz-4,cz+4):points.add((x,z))
    unmatched=set(points);pairs=[]
    for x,z in sorted(points):
        if (x,z) not in unmatched:continue
        possible=sorted((abs(xx-x)+abs(zz-z),(xx,zz)) for xx,zz in unmatched
                        if (xx,zz)!=(x,z) and (xx==x or zz==z)
                        and 2<=abs(xx-x)+abs(zz-z)<=5)
        if possible:
            q=possible[0][1];pairs.append(((x,z),q))
            unmatched.remove((x,z));unmatched.remove(q)
    for x,z in sorted(points):
        s.brick(x,z,1,1,4,TAN,'lower_arcade',part='3062b')
        s.brick(x,z,1,1,8,TAN,'upper_arcade',part='3062b')
    for a,b in pairs:
        (x,z),(xx,zz)=a,b
        if x==xx:
            start=min(z,zz);length=4 if abs(z-zz)<=3 else 6
            if start+length>H:start=H-length
            for y in (7,11):s.plate(x,start,1,length,y,DTAN,'arcade_lintel')
        else:
            start=min(x,xx);length=4 if abs(x-xx)<=3 else 6
            if start+length>W:start=W-length
            for y in (7,11):s.plate(start,z,length,1,y,DTAN,'arcade_lintel')
    for x,z in sorted(unmatched):
        for y in (7,11):s.plate(x,z,1,1,y,DTAN,'arcade_lintel')
    for x in range(33,44,2):
        for z in range(11,22,2):
            r=((x+.5-cx)/5.3)**2+((z+.5-cz)/4.5)**2
            if .42<r<1:s.plate(x,z,2,2,4,DTAN,'amphitheatre_seating')
    return dict(pillars=len(points),arcade_pairs=len(pairs))
def ldline(p):
    xx=(p['z']+p['d']/2)*20
    zz=-(p['x']+p['w']/2)*20
    yy=-(p['zbot']+p['h'])*8
    rot=p['angle']
    if not rot and p['w']>p['d'] and p['part'] in ('3035','3020','3023','3710','3666'):rot=90
    matrix={0:'1 0 0 0 1 0 0 0 1',90:'0 0 1 0 1 0 -1 0 0',
            180:'-1 0 0 0 1 0 0 0 -1',270:'0 0 -1 0 1 0 1 0 0'}[rot%360]
    return '1 %s %g %g %g %s %s.dat'%(p['colour'],xx,yy,zz,matrix,p['part'])
def output(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    s=Scene();backing(s);h=mountain(s);monument=stadium(s)
    occupancy={}
    for p in s.parts:
        for x in range(p['x'],p['x']+p['w']):
            for z in range(p['z'],p['z']+p['d']):
                for y in range(p['zbot'],p['zbot']+p['h']):
                    cell=(x,z,y)
                    if cell in occupancy:
                        raise ValueError('Bounding collision %d %d at %s'%(occupancy[cell],p['id'],cell))
                    occupancy[cell]=p['id']
    top={}
    for p in s.parts:
        for x in range(p['x'],p['x']+p['w']):
            for z in range(p['z'],p['z']+p['d']):
                top[(x,z,p['zbot']+p['h'])]=p['id']
    unsupported=[]
    for p in s.parts:
        if p['zbot']==0:continue
        if not any((x,z,p['zbot']) in top for x in range(p['x'],p['x']+p['w'])
                   for z in range(p['z'],p['z']+p['d'])):unsupported.append(p['id'])
    if unsupported:raise ValueError('Unsupported parts '+str(unsupported))
    with (folder/'parts_list.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['part_num','color_id','quantity','stock_verified','unit_price'])
        for (part,col),quantity in sorted(Counter((p['part'],p['colour']) for p in s.parts).items()):
            w.writerow([part,col,quantity,'false',''])
    (folder/'parts.json').write_text(json.dumps(s.parts,indent=2)+'\n')
    line=['0 LEGO Maps V0.5 sculpted Alpine mountain and micro Colosseum',
          '0 Name: diorama.ldr','0 Author: Procedural design','0 !LICENSE Original generated test']
    for region in dict.fromkeys(p['region'] for p in s.parts):
        line += [ldline(p) for p in s.parts if p['region']==region]
        line.append('0 STEP')
    (folder/'diorama.ldr').write_text('\n'.join(line)+'\n')
    stats=dict(pieces=len(s.parts),references=len(set((p['part'],p['colour']) for p in s.parts)),
               mountain_columns=len(h),mountain_height_mm=3*max(h.values())*3.2,
               physical_size_mm=[W*8,H*8],max_total_height_mm=max((p['zbot']+p['h'])*3.2 for p in s.parts),
               bounding_collisions=0,bounding_unsupported=0,**monument,
               quality_target_studs=[128,128],quality_target_mm=[1024,1024],
               envelope_pieces=[10000,25000],physical_test=False,stock_verified=False,
               independent_ldraw_validation='PENDING')
    stats['ldraw_sha256']=hashlib.sha256((folder/'diorama.ldr').read_bytes()).hexdigest()
    (folder/'metrics.json').write_text(json.dumps(stats,indent=2)+'\n')
    print(json.dumps(stats,indent=2))
    return stats
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='results/diorama')
    a=ap.parse_args();output(a.out)
