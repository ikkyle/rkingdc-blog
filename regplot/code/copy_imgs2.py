import os
import random
from shutil import copy
from functools import partial
from multiprocessing import Pool

os.chdir(os.path.expanduser('~/share/rkingdc-blog/regplot'))

n_train = 8000
n_test = 2000

source_dir = 'data/png'
out_dir = 'data/imgs'

files = os.listdir(source_dir)

def indx12(samp, n1, n2):
    idx0 = random.sample(list(range(len(samp))), n1+n2)
    idx1 = idx0[:n1]
    del idx0[:n1]
    samp1 = [s for i,s in enumerate(samp) if i in idx1]
    samp2 = [s for i,s in enumerate(samp) if i in idx0]
    return samp1, samp2

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