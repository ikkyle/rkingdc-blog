import os
from shutil import copy
from functools import partial
from multiprocessing import Pool

os.chdir(os.path.expanduser('~/personal/rkingdc-blog/regplot'))

with open('data/files_used_2.txt', 'r') as f:
    fls_full = f.readlines()
    
used_files = set([os.path.basename(f).replace('\n', '') for f in fls_full])
all_files = set(os.listdir('data/png'))

avail_files = list(all_files - used_files)

def getlst(files, pattern, n=1000):
    f = list(filter(lambda x: x.startswith(pattern), files))
    f[:n]

def cpyfile(x, dest=None, source_dir='data/png'):
    copy(os.path.join(source_dir, x), dest)
    
def doit(name, pool, outdir, imgs, n_train=8000, n_test=2000):
    
    files = list(filter(lambda x: x.startswith(f'{name}_'), imgs))
    train, test = indx12(files, n_train, n_test)
    
    pool.map(partial(cpyfile, dest=os.path.join(outdir, 'train2', name)), train)
    pool.map(partial(cpyfile, dest=os.path.join(outdir, 'test2', name)), test)
    

with Pool(4) as p:
    doit('none', p, outdir=out_dir, imgs=files, n_train=16000, n_test=4000)
   # doit('ceiling', p, outdir=out_dir, imgs=files)
   # doit('outlier', p, outdir=out_dir, imgs=files)
   # doit('biased', p, outdir=out_dir, imgs=files)