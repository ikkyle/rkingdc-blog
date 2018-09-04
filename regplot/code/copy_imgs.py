import os
import random
from shutil import copy
from functools import partial
from multiprocessing import Pool

os.chdir(os.path.expanduser('~/share/rkingdc-blog/regplot'))

n_train = 8000
n_test = 2000

source_dir = 'data/png'
train_dir = 'data/imgs/train'
test_dir = 'data/imgs/test'

files = os.listdir(source_dir)

none = list(filter(lambda x: x.startswith('none_'), files))
any_error = list(filter(lambda x: not x.startswith('none_'), files))

def indx12(samp, n1, n2):
    idx0 = random.sample(list(range(len(samp))), n1+n2)
    idx1 = idx0[:n1]
    del idx0[:n1]
    samp1 = [s for i,s in enumerate(samp) if i in idx1]
    samp2 = [s for i,s in enumerate(samp) if i in idx0]
    return samp1, samp2

def cpyfile(x, dest=None, source_dir='data/png'):
    copy(os.path.join(source_dir, x), dest)
    

train_none, test_none = indx12(none, n_train, n_test)
train_any, test_any = indx12(any_error, n_train, n_test)

with Pool(3) as p:
    print("Copying Training controls...")
    p.map(partial(cpyfile,dest=os.path.join(train_dir, 'none')), train_none)
    p.map(partial(cpyfile,dest=os.path.join(train_dir, 'any_error')), train_any)  
    
    print("Copying test set...")
    p.map(partial(cpyfile,dest=os.path.join(test_dir, 'none')), test_none)
    p.map(partial(cpyfile,dest=os.path.join(test_dir, 'any_error')), test_any)     