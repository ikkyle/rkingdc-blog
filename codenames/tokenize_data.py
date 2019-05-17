import os
import textacy
import pickle
import itertools

from gensim.models import TfidfModel
from google.cloud import storage

outdir = os.path.join('data', 'interim')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/roz/share/rkingdc-blog/erudite-flag-214115-6984f327da68.json'

class BlobDoc(object):
    def __init__(self, 
                 bucket_name='rkdc-codenames-west1b', 
                 doc_prefix='data/interim/docs'):
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(bucket_name)
        self.doc_prefix = doc_prefix
        self.categories = []
        self.files = []
        self.word_map = {}
        self.map_counter = 0
        import textacy # so unpickle works
        
    def __iter__(self):
        for blob in self.bucket.list_blobs(prefix=self.doc_prefix):
            # this code should iterate through each blob
            # updating the interal categories, files, and word_map as it goes
            for doc in self.read_blob(blob):
                str_bow = self.doc2bow(doc)
                int_bow = self.update_word_map(str_bow)
                yield int_bow.items()

            
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

           
def write_blob(obj, path, bucket):
    bin = pickle.dumps(obj)
    dest = bucket.blob(path)
    dest.upload_from_string(bin)

def exists_blob(path, bucket):
    return bucket.blob(path).exists()



if __name__ == '__main__':
    
    bd = BlobDoc()
    tf_idf = TfidfModel(corpus = iter(bd))
    
