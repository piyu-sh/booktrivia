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

from pandas.core.frame import DataFrame
from colorama import init, Fore, Back, Style
from tqdm import tqdm

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

init(autoreset=True)

from learning.ml_model.extract_links.extractLinksFn import getRelevantTitleIndices



search_words = [
    # 'trivia',
    'interesting trivia',
    # 'interesting things',
    'interesting facts',
    # 'shocking facts',
    "things you didn't know"
]

webSearcherUrl = 'http://localhost:3002/getlinks'
webSearcherJhaoUrl = 'http://localhost:3002/getLinksJhao'

dir_path = os.path.dirname(os.path.realpath(__file__))
linksFile = os.path.join(dir_path,'books-with-relevant-links.csv')
if os.path.isfile(linksFile):
    dfLinks = pd.read_csv(linksFile)
else:
    dfLinks = pd.DataFrame()

booksFile = os.path.join(dir_path,'goodreads-10k-dataset-integrated.csv')
booksDf = pd.read_csv(booksFile)

def getStringsAB(title):
    strA=title
    strB=''
    if(title.find('(') > -1):
        strA = title[:title.find('(')]
        strB = title[title.find('(')+1 : title.find(',')]
    return [strA, strB]

async def getSearchQueryResults(session, url):
    async with session.get(url) as resp:
        facts = await resp.json()
        return facts

def fromSearchData(data, keyword):
    results = data[0]['results'][keyword]['1']['results']
    return results

def queryToUrl(title):
    query = parse.urlencode({
                'keyword': title
            })
    url = f'{webSearcherUrl}?{query}'
    return url   

def saveLinks(bookRow):
    # dfLinks.append(bookRow)
    bookRow.to_csv(linksFile, mode='a', index=False, header=False)

class QueueObj(TypedDict):
    id: str
    query: str

async def searchWorker(name: str, searchQueue: Queue, queueProgress: tqdm):
    while True:
        # Get a "work item" out of the queue.
        data: QueueObj = await searchQueue.get()
        query = data['query']
        url = queryToUrl(query)
        print(Fore.MAGENTA+f'{name} got url: {url} to work on'+Fore.RESET)
        start = time.time()
        custom_timeout = aiohttp.ClientTimeout(total=60) # type: ignore
        # custom_timeout.total = 2*60
        async with aiohttp.ClientSession(timeout=custom_timeout) as session:
            # nonlocal results
            results=[]
            try:
                results = await getSearchQueryResults(session, url)
            except asyncio.TimeoutError as e:
                logging.exception(Fore.RED+f'Exception raised by worker = {name}; error = {e}'+Fore.RESET )
            except Exception as e:  # pylint: disable=broad-except
                logging.exception(Fore.RED+f'Exception raised by worker = {name}; error = {e}'+Fore.RESET )
        print(Fore.YELLOW+f'{name}\'s work for url {url} done; time taken {time.time() - start} seconds'+Fore.RESET)
        if(len(results) > 0 and len(results[0]['results']) > 0 and len(results[0]['results'][query]) > 0):
            print(f'query: \'{query}\' fetched with data'.encode(encoding='utf-8'))
            allResults = fromSearchData(results, query)
            searchQueue.task_done()
            onlyTitles = [item['title'] for item in allResults]
            relevantIndices = getRelevantTitleIndices(onlyTitles)
            relevantSearchData = [allResults[index] for index in relevantIndices]
            bookRow = booksDf[booksDf['id']==data['id']].copy()
            bookRow['searchLinks'] = [relevantSearchData]
            bookRow['query'] = query
            saveLinks(bookRow)
            queueProgress.update(1)
            # searchResults.append({
            #     query: results
            # })
        else:
            print(f'query: \'{query}\' unsuccessful, adding to queue again'.encode(encoding='utf-8')) 
            searchQueue.task_done()
            searchQueue.put_nowait(data)

def _handle_task_result(task: asyncio.Task) -> None:
    try:
        task.result()
    except asyncio.CancelledError:
        pass  # Task cancellation should not be logged as an error.
    except Exception:  # pylint: disable=broad-except
        logging.exception('Exception raised by task = %r', task)

async def findAndSaveLinks(maxWorkers = 5):
    searchQueue = asyncio.Queue()
    searchWorkers = []
    # searchResults = []
    queueProgress = tqdm(total=len(booksDf)*len(search_words), desc="total queue progress")
    for i in range(maxWorkers):
        task = asyncio.create_task(searchWorker(f'worker{i}',searchQueue, queueProgress))
        searchWorkers.append(task)
        task.add_done_callback(_handle_task_result)

    with tqdm(total=len(booksDf), desc="books data reading progress") as pbar:
        for row in booksDf.itertuples():
            # check in output file, if already that book id exist then skip
            # len(search_words)+3 because we started with 6 search terms, but it would have taken weeks of continous scraping to fetch 60000 records, so skipping 3 terms
            # also we already had done scraping for some for 6 terms so this check has to be run with len+3 which is 6 right now
            if('id' not in dfLinks or len(dfLinks[dfLinks['id']==row.id]) < len(search_words)+3): 
                # extract title
                title, work = getStringsAB(row.title)
                for term in search_words:
                    query = f'{str(title).strip()} {term}'
                    # check if that particular query for that book exists
                    if('query' not in dfLinks or dfLinks[dfLinks['query']==query].size == 0 ):
                        searchQueue.put_nowait({
                                'id': row.id,
                                'query': query
                            })
            pbar.update(1)
            
    queueProgress.total = searchQueue.qsize()
    queueProgress.refresh()
    await searchQueue.join()
    # cancel the now-idle workers, which wait for a new message that will never arrive
    for w in searchWorkers:
        w.cancel()

asyncio.run(findAndSaveLinks(maxWorkers=6))
# find facts now


