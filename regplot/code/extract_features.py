#import functools

#import matplotlib.pyplot as plt

import pandas as pd
#import numpy as np

import pickle

import swifter

import os

from skimage.io import imread

os.chdir(os.path.expanduser('~/share/rkingdc-blog/regplot'))

meta_data = pd.read_csv('data/control_file.csv')

dummies = pd.get_dummies(meta_data['type'], prefix='d')
meta_data = pd.concat([meta_data, dummies], axis=1)

def img_reader(file):
    path, name = os.path.split(file)
    newpath = os.path.join(path, '../png_redux', name)
    img = imread(newpath)
    return img
    
meta_data['img_series'] = meta_data['filename'].swifter.apply(img_reader)

with open("data/feature_df.pkl", 'wb') as pkl:
    pickle.dump(meta_data, file=pkl)