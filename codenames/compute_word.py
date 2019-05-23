import os 
import joblib
import pickle
import hunspell

import numpy as np

import codenames as cdn

from scipy import sparse
from google.cloud import storage

from dtm_to_tfidf import read_blob_pickle, read_blob_joblib

hobj = hunspell.HunSpell('/usr/share/hunspell/en_US.dic', '/usr/share/hunspell/en_US.aff')

class Board(object):
    def __init__(self, tfidf, word_map, categories, 
                 board=None, red=None, blue=None, black=None):
        if not board or not red or not blue or not black:
            board, red, blue, black = cdn.create_game(cdn.codewords)

        word_map_en = {k: word_map[k] if hobj.spell(k.encode('utf-8')) \
                       else None for k in word_map.keys()}
        self.word_map = word_map_en
        self.categories= categories
        self.board = [x.lower() for x in board]
        self.red = [x.lower() for x in red]
        self.blue = [x.lower() for x in blue]
        self.black = [x.lower() for x in black]
        self.tfidf = tfidf

    def subset_tfidf(self, target_categories):
        tc = [x.lower() for x in target_categories]
        col_idx = [i for i,x in enumerate(self.categories) if x.lower() in tc]
        row_idx = [i for i in self.word_map.values() if i]
        sub_tfidf = self.tfidf[..., col_idx]
        sub_tfidf = sub_tfidf[row_idx, ...]
        return sub_tfidf
    
    def compute_candidates(self, red_tfidf, blue_tfidf, black_tfidf=None):
        # red score - element wise geometric mean 
        red_score = np.expm1(red_tfidf.log1p().mean(axis=1))
        blue_score = blue_tfidf.mean(axis=1)
        #black_score = black_tfidf.mean(axis=1)
        
        #total_score = red_score - (blue_score + black_score)
        total_score = red_score - blue_score
        word_idx = np.argmax(total_score)
        word = [w for w,i in self.word_map.items() if i == word_idx]
        return word
        
    def word_for_red_cluster(self, red_words):
        red_tfidf = self.subset_tfidf(red_words)
        blue_tfidf = self.subset_tfidf(self.blue + self.black)
        #black_tfidf = self.subset_tfidf(self.black)
        
        word = self.compute_candidates(
            red_tfidf = red_tfidf, 
            blue_tfidf = blue_tfidf,
            black_tfidf = None)
        return word
        


if __name__ == '__main__':
    
    blob_date = '2019-05-18'
    blob_root = os.path.join('data', 'processed', blob_date)
    
    client = storage.Client()
    bucket = client.get_bucket('rkdc-codenames-west1b')
    
    tfidf = read_blob_joblib(bucket.get_blob(os.path.join(blob_root, 'tfidf_matrix.jblb')))
    word_map = read_blob_pickle(bucket.get_blob(os.path.join(blob_root, 'word_map.pkl')))
    file_list = read_blob_pickle(bucket.get_blob(os.path.join(blob_root, 'files.pkl')))
    categories = read_blob_pickle(bucket.get_blob(os.path.join(blob_root, 'categories.pkl')))

    #board, red, blue, black = cdn.create_game(cdn.codewords)
    red = ['Post','Chocolate', 'Chest', 'Night', 'Microscope', 'Chair','Iron','England']
    blue = ['Charge', 'India', 'Aztec', 'Bed', 'Oil', 'Ice', 'Boot']
    black = ['Mug']
    board = ['England','India','Egypt','Chest','Dice',\
 'Heart','Soul','Charge','Microscope','Post','Bed','Night','Oil','Iron','Hand',\
 'Boot','Chair','Mug','Chocolate','Ice','Aztec','Wall','Pheonix','Ground','Press']
    
    words_to_cluster = ['Iron', 'Chair', 'England']
    
    B = Board(
        tfidf = tfidf,
        word_map = word_map,
        categories = categories,
        board = board, 
        red = red, 
        blue = blue,
        black = black)
    
    B.word_for_red_cluster(['Microscope', 'Iron'])
    
