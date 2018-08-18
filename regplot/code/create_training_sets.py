import pandas as pd
import numpy as np

from skimage.io import imread
from skimage import color
from skimage.transform import rescale

import pickle

def process_image(path):
    img = imread(path)
    img_gray = color.rgb2gray(img)
    img_scale = rescale(img_gray, .35, anti_aliasing=True)
    return img_scale
    
meta_data = pd.read_csv('data/control_file.csv')

y = pd.get_dummies(meta_data['type'])
X = np.stack(meta_data['filename'].apply(process_image))

pickle.dump(y, file="data/y.pkl")
pickle.dump(X, file="data/X.pkl")
