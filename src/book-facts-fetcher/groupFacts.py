from asyncio.queues import Queue
import time
from typing import List, TypedDict
import pandas as pd
import os.path
import asyncio
import aiohttp
import os, sys
import logging
import ast
from tqdm import tqdm
from colorama import init, Fore, Back, Style
from urllib.parse import urlparse
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

tqdm.pandas()

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

# from learning.ml_model.extract_text.htmlProcess import getDocsAndSentsPerUrl
# from learning.ml_model.extract_text.gensim_main import getTrainedModel
# from learning.ml_model.extract_text.gensimModel import getLdaModel, getSummary, getTfidfModel, getTfidfSummary, printSummary


# proxyServerUrl = 'http://localhost:3002/getlinks'
dir_path = os.path.dirname(os.path.realpath(__file__))
# linksFile = os.path.join(dir_path,'books-with-relevant-links.csv')
factsGroupedFile = os.path.join(dir_path,'books-with-facts-grouped.csv')
factsFile = os.path.join(dir_path,'books-with-facts.csv')

# if os.path.isfile(linksFile):
#     dfLinks = pd.read_csv(linksFile, converters={'searchLinks': ast.literal_eval})
# else:
#     raise os.error(f'{linksFile}  file needed')

if os.path.isfile(factsFile):
    dfFacts = pd.read_csv(factsFile)
else:
    dfFacts = pd.DataFrame()


def aggFactsInfo(x):
    return list(x) if pd.Series(x).name == 'factsInfo' else x.iloc[0]

def getFactsGrouped():
    dfFactsGrouped = {}
    if os.path.isfile(factsGroupedFile):
        dfFactsGrouped = pd.read_csv(factsGroupedFile, converters={'factsInfo': ast.literal_eval})
    else:
        dfFactsGrouped = dfFacts.copy()
        print(f"combining (factsLink, facts) -> factsInfo ...")
        dfFactsGrouped['factsInfo'] =dfFactsGrouped[['factsLink','facts']].agg(lambda x : ( x.factsLink, x.facts), axis=1)
        print(f"agregating factsInfo...")
        dfFactsGrouped =  dfFactsGrouped.groupby('book_id', sort=False).progress_aggregate(aggFactsInfo).reset_index()
        # print(f"deduping searchlinks...")
        # dfDedupedFull['searchLinks'] = dfUpdatedFull['searchLinks'].progress_apply(deDupeAndSortLinks)
        print(f"dropping facts, factsLink columns...")
        dfFactsGrouped = dfFactsGrouped.drop(columns=['facts', 'factsLink'])
        print(f"saving dataframe to file: {factsGroupedFile}")
        dfFactsGrouped.to_csv(factsGroupedFile, index=False)
    return dfFactsGrouped
        
        
dfFactsGrouped = getFactsGrouped()
