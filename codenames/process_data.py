import os
import textacy
import spacy
import pickle


from textacy import make_spacy_doc

from multiprocessing import Pool

import mwparserfromhell as mwp

from google.cloud import storage


nlp = spacy.load('en')

datadir = os.path.join('data', 'text')
outdir = os.path.join('data', 'interim')


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/roz/share/rkingdc-blog/erudite-flag-214115-6984f327da68.json'

client = storage.Client()
bucket = client.get_bucket('rkdc-codenames-west1b')


# tokenize all 1_* documents in each Workld folder
# find tf-idf for each value

def exists_blob(path, bucket):
    return bucket.blob(path).exists()

def write_blob(obj, path, bucket):
    bin = pickle.dumps(obj)
    dest = bucket.blob(path)
    dest.upload_from_string(bin)
    
def read_blob(path, bucket):
    src = bucket.get_blob(path)
    pkl = src.download_as_string()
    return pickle.loads(pkl)

def write_line(file, val):
    with open(file, 'a') as f:
        f.write(val + '\n')

def read_file(file):
    with open(file, 'r') as f:
        txt = f.read()
    return txt

def preprocess(text):
    
    text = text.replace('|', ' ')
    
    return textacy.preprocess.preprocess_text(text, 
                                       lowercase=True,
                                       no_punct=True)


def clean(txt):
    parsed = mwp.parse(txt)
    cleaned = parsed.strip_code()    
    return preprocess(cleaned) 


def mkdoc(file):
    txt = read_file(file)
    txt = clean(txt)
    basepath, filename = os.path.split(file)
    title = (filename.replace('1__', '')
             .replace('0__', '')
             .replace('.txt', ''))
    metadata = {'title': title, 
                'category': os.path.basename(basepath),
                'file': file,
                'primary_link': os.path.basename(file).startswith('1__')}

    
    
    # docs can't be > 1 million chars
    doc = [textacy.doc.make_spacy_doc(txt[:1_000_000-1])]
    if len(doc) > 1e6:
        doc += [textacy.doc.make_spacy_doc(txt[1_000_000:2_000_000-1], disable = ['tagger', 'parser', 'ner', 'textcat'])]
    if len(doc) > 2e6:
        doc += [textacy.doc.make_spacy_doc(txt[2_000_000:3_000_000-1], disable = ['tagger', 'parser', 'ner', 'textcat'])]

    return doc


def _runner(dir_, overwrite=False):
    path, file = os.path.split(dir_)
    outfile = os.path.basename(file).replace('.txt', '.pkl')
    category = os.path.basename(path)
    outfile = os.path.join(outdir, 'docs', category + '__' + outfile)
    if not overwrite and exists_blob(outfile, bucket): 
        return
    doc = mkdoc(dir_)
    write_blob(obj = doc, path=outfile, bucket=bucket)

if __name__ == '__main__':

    dirs = []
    for dir_ in os.listdir(datadir):
        for file in os.listdir(os.path.join(datadir, dir_)):
            if file.startswith('0__'): continue
            if file.startswith('1__User'): continue
            if file.startswith('1__Wiki'): continue
            dirs.append(os.path.join(datadir, dir_, file))
    
    
    with Pool(8) as pool:
        pool.map(_runner, dirs)

