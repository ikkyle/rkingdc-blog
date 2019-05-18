import os
import textacy
import pickle
import itertools
import gensim
import joblib

from tqdm import tqdm

from datetime import datetime

from gensim.models import TfidfModel
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/roz/share/rkingdc-blog/erudite-flag-214115-6984f327da68.json'

class BlobDoc(object):
    
    def __init__(self, 
                 bucket_name='rkdc-codenames-west1b', 
                 doc_prefix='data/interim/docs',
                 max_results=None):
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(bucket_name)
        self.doc_prefix = doc_prefix
        self.categories = []
        self.files = []
        self.word_map = {}
        self.map_counter = -1 # so the first value is zero
        self.max_results = max_results
        self.iter_int = True
        #import textacy # so unpickle works
        
    def __iter__(self):
        if not self.iter_int:
            print("Returning string-based BOW!")
        for blob in tqdm(self.bucket.list_blobs(prefix=self.doc_prefix, max_results=self.max_results)):
            for doc in self.read_blob(blob):
                bow = self.doc2bow(doc)
                if self.iter_int:
                    bow = self.update_word_map(bow)
                yield bow.items()

            
    def read_blob(self, blob):
        pkl = blob.download_as_string()
        docs = pickle.loads(pkl)
        name = blob.name
        categ = os.path.basename(name).split('__')[0]
        self.categories.extend([categ for d in docs])
        self.files.extend([name for d in docs])
        return docs

    def doc2bow(self, doc):
        bow = doc._.to_bag_of_terms(
          ngrams=1,
            filter_stops=True,
            filter_punct=True,
            normalize='lemma',
          weighting='count',
          as_strings=True)
        return bow
    
    def update_word_map(self, bow):
        new_bow = {}
        for bow_word, bow_value in bow.items():
            if bow_word not in self.word_map.keys():
                self.map_counter += 1
                self.word_map[bow_word] = self.map_counter
                
            new_bow[self.word_map[bow_word]] = bow_value
        
        return new_bow

           
def write_numpy_blob(obj, path, bucket):
    joblib.dump(obj, filename = path, compress=9)
    dest = bucket.blob(path)
    dest.upload_from_filename(path)
    
def write_blob(obj, path, bucket):
    pickle.dump(obj, file = path, protocol=3)
    dest = bucket.blob(path)
    dest.upload_from_filename(pkl)

def exists_blob(path, bucket):
    return bucket.blob(path).exists()


if __name__ == '__main__':
    
    outdir = os.path.join('data', 'processed', str(datetime.now().date()))
    os.makedirs(outdir, exist_ok=True)
    
    bd = BlobDoc(max_results=None)
    
    doc_term_matrix = gensim.matutils.corpus2csc(corpus = iter(bd))
    
    write_numpy_blob(obj=doc_term_matrix, 
               path = os.path.join(outdir, 'doc_term_matrix.jblb'), 
               bucket = bd.bucket)
    write_blob(bd.word_map, 
               path = os.path.join(outdir, 'word_map.pkl'),
               bucket = bd.bucket)
    write_blob(bd.files, 
               path = os.path.join(outdir, 'files.pkl'),
               bucket = bd.bucket)
    write_blob(bd.categories, 
               path = os.path.join(outdir, 'categories.pkl'),
               bucket = bd.bucket)
    
