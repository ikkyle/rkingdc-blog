import os 
import joblib
import pickle

import tempfile 
import numpy as np

from scipy import sparse
from operator import itemgetter
from google.cloud import storage

from corpus_to_dtm import write_numpy_blob

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/roz/share/rkingdc-blog/erudite-flag-214115-6984f327da68.json'

def read_blob_pickle(blob):
    assert blob is not None, "Blob not found"
    pkl = blob.download_as_string()
    return pickle.loads(pkl)

def read_blob_joblib(blob):
    assert blob is not None, "Blob not found"
    _, fl = tempfile.mkstemp(suffix='.jblb')
    blob.download_to_filename(fl)
    return joblib.load(fl)
    

def compute_tfidf(mat):
    inv_term_count = sparse.bsr_matrix(1/mat.sum(axis=1))
    term_freq = mat.multiply(term_count)
    
    n_documents = mat.shape[1]
    n_documents_with_term = mat.getnnz(axis=1)
    
    inv_doc_freq = np.log10(n_documents / 1+n_documents_with_term)
    tf_idf = (term_freq.transpose() * sparse.diags(inv_doc_freq)).transpose()
    
    return tf_idf


if __name__ == '__main__':
    
    blob_date = '2019-05-18'
    blob_root = os.path.join('data', 'processed', blob_date)
    
    client = storage.Client()
    bucket = client.get_bucket('rkdc-codenames-west1b')
    
    # document-term-matrix 
    dtm = read_blob_joblib(bucket.get_blob(os.path.join(blob_root, 'doc_term_matrix.jblb')))
    word_map = read_blob_pickle(bucket.get_blob(os.path.join(blob_root, 'word_map.pkl')))
    file_list = read_blob_pickle(bucket.get_blob(os.path.join(blob_root, 'files.pkl')))
    categories = read_blob_pickle(bucket.get_blob(os.path.join(blob_root, 'categories.pkl')))
    
    if False:
        # in DTM, columns are documents, rows are words
        i=word_map['python']

        # get row for index
        row = dtm.getrow(i)

        # number of docs with this word
        row.nnz

        # get word for index
        [w for w,ii in word_map.items() if ii == i] 

        # get files with non zero value
        itemgetter(*row.indices.tolist())(file_list)

        # get categories 
        itemgetter(*row.indices.tolist())(categories)
    
    # convert DTM to TF-IDF matrix
    tfidf = compute_tfidf(mat = dtm)
    
    write_numpy_blob(
        obj=tfidf,
        path=os.path.join(blob_root, 'tfidf_matrix.jblb'),
        bucket=bucket
    )
    