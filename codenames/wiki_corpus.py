import os
import sys

os.environ['PYWIKIBOT_NO_USER_CONFIG'] = '1'

import pywikibot

from collections import namedtuple
from random import shuffle

with open('data/wordlist.txt', 'r') as wf:
    codewords = wf.read().splitlines()
    
codewords = [w for w in codewords if w != '']
shuffle(codewords)

site = pywikibot.Site("en", "wikipedia")

#page = pywikibot.Page(site, codewords[0])
#pls = page.linkedPages(content=True)

Pg = namedtuple('Pg', ['title', 'text'])


def format_wiki_term(term):
    return term.lower().replace(' ', '_')

def translate_wiki_term(term):
    if term == 'Scuba Diver':
        term = 'Scuba Diving'
    if term == 'Himalayas':
        term = 'Himalaya'
    
    return format_wiki_term(term)

def scrape_page(site, keyword, disambig_only=False):
    page = pywikibot.Page(site, translate_wiki_term(keyword))
    
    if not page.exists():
        return ([], [])
    
    if not disambig_only:
        page_content_, links = pull_page_content(page, 
                                                 get_links=True, 
                                                 get_backlinks=True)
        page_content = [page_content_]
            
    else: 
        page_content, links = [], []
        
    # work around if the main page itself is a disambiguation page (like the page for Crown)
    # but not listed as one by isDisambig 
    if (any([p.title().find('Disambiguation') >= 0 for p in page.categories()]) and
        not page.isDisambig() and
        not page.title().find('disambiguation') > -1):
        for db in links:
            edcontent, edlinks = pull_page_content(db, 
                                                   get_links=True,
                                                   get_backlinks=False)
            page_content.append(edcontent)
            links.extend(edlinks)
    
    # get all the disambiguation pages as well
    if not (page.isDisambig() or 
            page.title().find('disambiguation') > -1 or 
            any([p.title().find('Disambiguation') >= 0 for p in page.categories()])):
        
        disambig, dlinks = scrape_page(
            site = site, 
            keyword = f"{translate_wiki_term(keyword)}_(disambiguation)",
            disambig_only=False
        )
        
        
        for db in dlinks:
            dcontent, links = pull_page_content(db, 
                                                get_links=True,
                                                get_backlinks=False)
            
        
            page_content.append(dcontent)
            links.extend(links)
    
    return (page_content, links)
    
def pull_page_content(page, get_links=True, get_backlinks=True):
    title = page.title()
    text = page.expand_text()
    links, backlinks = [], []
    
    if get_links:
        links = [l for l in page.linkedPages()]
        
    if get_backlinks:
        backlinks = [l for l in page.backlinks()]
        links += backlinks
    
    pg = Pg(title, text)
    
    return (pg, links)


def write_page(Pg, word, weight, overwrite=False):
    valid_chars = '.-_() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    fname = f"{str(weight)}__{Pg.title}.txt"   
    fname = ''.join(c for c in fname if c in valid_chars)
    
    pname = f"data/text/{word}"
    
    if not os.path.exists(pname):
        os.mkdir(pname)
        
    if overwrite or not os.path.exists(fname):
        with open(os.path.join(pname, fname), "w") as f:
            f.write(Pg.text)


def page_to_pg(page):
    return Pg(title = page.title(), 
              text = page.expand_text())

if __name__ == '__main__':

    DISAMBIG_ONLY = sys.argv[1] == '0'
    
    for w in codewords:

        exists = os.path.exists(f'data/text/{w}')

        if not exists or DISAMBIG_ONLY:
            print(f"Scraping {w}")
            if DISAMBIG_ONLY:
                print("Disambiguation pages only.")
            page_data, links = scrape_page(site, w, disambig_only = DISAMBIG_ONLY)

            for p in page_data:
                write_page(Pg=p, word=w, weight=1, overwrite=False)

#             for ln in links:
#                 p = page_to_pg(ln)
                
#                 # colon indicates namespaced post
#                 if p.title.find(":") == -1 and \
#                    p.title.find("User") == -1 and \
#                    p.title.find("Wikipedia") == -1:
#                     write_page(Pg=p, word=w, weight=0, overwrite=False)


