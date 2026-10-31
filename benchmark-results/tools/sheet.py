import sys
from PIL import Image
d,out=sys.argv[1],sys.argv[2]
ims=[Image.open(f'{d}/{n}.png').convert('RGB') for n in ['a_face','b_profil_gauche','c_trois_quarts','d_dos']]
h=360;ims=[i.resize((int(i.width*h/i.height),h)) for i in ims]
W=Image.new('RGB',(sum(i.width for i in ims),h),'white');x=0
for i in ims: W.paste(i,(x,0));x+=i.width
W.save(out)
