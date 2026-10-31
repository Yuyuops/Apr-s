# Free Hunyuan3D generation through the official Hugging Face Space (gradio client).
# usage: hf_gen.py <space> <dog> <outdir> [steps] [octree]
import sys, json, shutil, time, os
from gradio_client import Client, handle_file
space, dog, out = sys.argv[1:4]
steps = int(sys.argv[4]) if len(sys.argv) > 4 else 30
octree = int(sys.argv[5]) if len(sys.argv) > 5 else 256
D = os.environ.get('INDIR','/home/user/Apr-s/benchmark-results/01_inputs_prepared/')
v = {k: handle_file(D + f'{dog}_{n}_'+os.environ.get('SUF','rgba')+'.png') for k, n in
     [('front', 'face'), ('back', 'dos'), ('left', 'profil_gauche'), ('right', 'profil_droit')]}
os.makedirs(out, exist_ok=True)
c = Client(space, verbose=False)
kw = dict(mv_image_front=v['front'], mv_image_back=v['back'], mv_image_left=v['left'], mv_image_right=v['right'],
          steps=steps, guidance_scale=5.0, seed=1234, octree_resolution=octree, check_box_rembg=True,
          num_chunks=8000, randomize_seed=False, api_name=os.environ.get('EP','/generation_all'))
if '2mv' in space: kw['caption'] = None
t = time.time()
r = c.predict(**kw)
meta = {'space': space, 'params': {k: (val if not isinstance(val, dict) else 'image') for k, val in kw.items()},
        'seconds': round(time.time() - t, 1)}
files = []
for i, x in enumerate(r):
    p = x.get('value') if isinstance(x, dict) and 'value' in x else x
    if isinstance(p, str) and os.path.exists(p):
        dst = os.path.join(out, f'{dog}_out{i}{os.path.splitext(p)[1]}'); shutil.copy(p, dst); files.append(dst)
    else:
        meta[f'out{i}'] = p if not isinstance(p, str) or len(p) < 3000 else p[:3000]
meta['files'] = files
json.dump(meta, open(os.path.join(out, f'{dog}_meta.json'), 'w'), indent=1, default=str)
print(json.dumps(meta, indent=1, default=str)[:2500])
