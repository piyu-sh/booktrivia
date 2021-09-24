from asyncio.queues import Queue
import time
from typing import List, TypedDict
import pandas as pd
import numpy as np
import os.path
import asyncio
import aiohttp
from urllib import parse
import os, sys
import logging
import ast
from tqdm import tqdm

tqdm.pandas()

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from learning.ml_model.extract_text.gensim_main import getTrainedModel


proxyServerUrl = 'http://localhost:3002/getlinks'
dir_path = os.path.dirname(os.path.realpath(__file__))
linksFile = os.path.join(dir_path,'books-with-relevant-links.csv')
dedupedFile = os.path.join(dir_path,'books-with-relevant-links-deduped.csv')

if os.path.isfile(linksFile):
    dfLinks = pd.read_csv(linksFile, converters={'searchLinks': ast.literal_eval})
else:
    raise os.error(f'{linksFile}  file needed')


def agg_searchLinks(x):
    return list(x) if pd.Series(x).name == 'searchLinks' else x.iloc[0]
    
def deDupeLinks(searchLinks):
    # print('new row')
    uniqueLinks = {}
    linkSet = []
    for multiLinks in searchLinks:
        # print(f"multilinks: {len(multiLinks)}")
        for links in multiLinks:
            if (links['link'] not in uniqueLinks):
                uniqueLinks[links['link']] = 1
                linkSet.append(links)
            # else:
                # print(f"duplicate: {links['link']}")
    return linkSet

def getDedupedSearchLinksDF():
    dfDedupedFull = {}
    if os.path.isfile(dedupedFile):
        dfDedupedFull = pd.read_csv(dedupedFile, converters={'searchLinks': ast.literal_eval})
    else:
        # raise os.error(f'{dedupedFile}  file needed')
        print(f"agregating searchlinks...")
        dfUpdatedFull =  dfLinks.groupby('book_id', sort=False).progress_aggregate(agg_searchLinks).reset_index()
        dfDedupedFull = dfUpdatedFull.copy()
        print(f"deduping searchlinks...")
        dfDedupedFull['searchLinks'] = dfUpdatedFull['searchLinks'].progress_apply(deDupeLinks)
        print(f"dropping query column...")
        dfDedupedFull = dfDedupedFull.drop('query', 1)
        print(f"saving dataframe to file: {dedupedFile}")
        dfDedupedFull.to_csv(dedupedFile, index=False)
    return dfDedupedFull

getDedupedSearchLinksDF()

# dedupe links for a book id

# fetch webpages per link per book

# run model on webpages
# (tfidf, dictionary, bow) = getTrainedModel()

# save highlighted facts with navigation info(possible ?)
