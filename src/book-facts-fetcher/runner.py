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
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from learning.ml_model.extract_links.extractLinksFn import getRelevantTitleIndices

search_words = [
    'trivia',
    'interesting trivia',
    'interesting things',
    'interesting facts',
    'shocking facts',
    "things you didn't know"
]

proxyServerUrl = 'http://localhost:3002/getlinks'
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
    url = f'{proxyServerUrl}?{query}'
    return url   

def saveLinks(bookRow):
    # dfLinks.append(bookRow)
    bookRow.to_csv(linksFile, mode='a', index=False, header=False)

class QueueObj(TypedDict):
    id: str
    query: str

async def searchWorker(name: str, searchQueue: Queue):
    while True:
        # Get a "work item" out of the queue.
        data: QueueObj = await searchQueue.get()
        query = data['query']
        url = queryToUrl(query)
        print(f'{name} got url: {url} to work on')
        start = time.time()
        async with aiohttp.ClientSession() as session:
            # nonlocal results
            results = await getSearchQueryResults(session, url)
        print(f'{name}\'s work for url {url} done; time taken {time.time() - start} seconds')
        if(len(results[0]['results']) > 0 and len(results[0]['results'][query]) > 0):
            print(f'query: \'{query}\' fetched with data')
            allResults = fromSearchData(results, query)
            searchQueue.task_done()
            onlyTitles = [item['title'] for item in allResults]
            relevantIndices = getRelevantTitleIndices(onlyTitles)
            relevantSearchData = [allResults[index] for index in relevantIndices]
            bookRow = booksDf[booksDf['id']==data['id']].copy()
            bookRow['searchLinks'] = [relevantSearchData]
            bookRow['query'] = query
            saveLinks(bookRow)
            # searchResults.append({
            #     query: results
            # })
        else:
            print(f'query: \'{query}\' unsuccessful, adding to queue again') 
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
    for i in range(maxWorkers):
        task = asyncio.create_task(searchWorker(f'worker{i}',searchQueue))
        searchWorkers.append(task)
        task.add_done_callback(_handle_task_result)

    for row in booksDf.itertuples():
        # check in output file, if already that book id exist then skip
        if('id' not in dfLinks or len(dfLinks[dfLinks['id']==row.id]) < len(search_words)):
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
    await searchQueue.join()
    # cancel the now-idle workers, which wait for a new message that will never arrive
    for w in searchWorkers:
        w.cancel()


asyncio.run(findAndSaveLinks(maxWorkers=10))
# find facts now


