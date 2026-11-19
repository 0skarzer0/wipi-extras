import subprocess,os,shutil,collections
base=os.environ.get('LIBRETRO_DIR','./libretro-thumbnails')
dirs={'Sega_-_Naomi':'Sega_-_Naomi','Sega_-_Naomi_2':'Sega_-_Naomi_2','Atomiswave':'Atomiswave','MAME':'MAME','N64':'N64','Dreamcast':'sega_-_dreamcast'}
rows=[l.rstrip('\n').split('\t') for l in open(os.environ.get('MAPA','mapa-previews.tsv'))]
by=collections.defaultdict(list)
for r in rows: by[r[2]].append(r)
os.makedirs('final',exist_ok=True)
miss=[]
for repo,rs in by.items():
    d=f'{base}/{dirs[repo]}'
    paths=sorted({f'Named_Snaps/{r[3]}.png' for r in rs})
    open('/tmp/p.txt','w').write('\n'.join(paths)+'\n')
    env=dict(os.environ,GIT_LFS_SKIP_SMUDGE='1')
    subprocess.run(['git','-C',d,'checkout','HEAD','--pathspec-from-file=/tmp/p.txt'],env=env,capture_output=True)
    for p in paths:   # resolve symlinks
        fp=f'{d}/{p}'
        if os.path.islink(fp):
            t=os.path.normpath(os.path.join(os.path.dirname(p),os.readlink(fp)))
            open('/tmp/p2.txt','w').write(t+'\n')
            subprocess.run(['git','-C',d,'checkout','HEAD','--pathspec-from-file=/tmp/p2.txt'],env=env,capture_output=True)
    for r in rs:
        fp=f'{d}/Named_Snaps/{r[3]}.png'
        if os.path.isfile(fp) and os.path.getsize(fp)>500: shutil.copy(os.path.realpath(fp),f'final/{r[1]}')
        else: miss.append(r)
print(len(os.listdir('final')),'png; faltan',len(miss),miss[:5])
