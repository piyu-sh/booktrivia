from asyncio.queues import Queue
import time
from typing import List
import pandas as pd
import numpy as np
import os.path
import asyncio
import aiohttp
from urllib import parse

proxyServerUrl = 'http://localhost:3002/getlinks'
dir_path = os.path.dirname(os.path.realpath(__file__))

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

async def searchWorker(name: str, searchQueue: Queue, searchResults: List):
    while True:
        # Get a "work item" out of the queue.
        query = await searchQueue.get()
        url = queryToUrl(query)
        print(f'{name} got url: {url} to work on')
        start = time.time()
        async with aiohttp.ClientSession() as session:
            # nonlocal results
            results = await getSearchQueryResults(session, url)
        print(f'{name}\'s work for url {url} done; time taken {time.time() - start} seconds')
        if(len(results[0]['results']) > 0 and len(results[0]['results'][query]) > 0):
            searchResults.append({
                query: results
            })
            print(f'query: \'{query}\' fetched with data')
            searchQueue.task_done()
        else:
            await searchQueue.put(str(query).strip())
            print(f'query: \'{query}\' unsuccessful, adding to queue again')

def queryToUrl(title):
    query = parse.urlencode({
                'keyword': title
            })
    url = f'{proxyServerUrl}?{query}'
    return url    

async def saveFacts(maxWorkers = 5):
    factsFile = os.path.join(dir_path,'books-with-facts.csv')
    if os.path.isfile(factsFile):
        dfFacts = pd.read_csv(factsFile)
    else:
        dfFacts = pd.DataFrame()

    booksFile = os.path.join(dir_path,'goodreads-10k-dataset-integrated.csv')
    df = pd.read_csv(booksFile)

    searchQueue = asyncio.Queue(maxsize=maxWorkers)
    searchWorkers = []
    searchResults = []
    for i in range(maxWorkers):
        searchWorkers.append(asyncio.create_task(searchWorker(f'worker{i}',searchQueue, searchResults)))

    for row in df[:10].itertuples():
        # print(row)
        # title = row.title
        # check in output file, if already facts exist then skip
        if('id' not in dfFacts or dfFacts[dfFacts['id']==row.id].size == 0):
            # extract title
            title, work = getStringsAB(row.title)
            await searchQueue.put(str(title).strip())
    await searchQueue.join()
    # cancel the now-idle workers, which wait for a new message
    # that will never arrive
    for w in searchWorkers:
        w.cancel()
    # find facts
    # 


asyncio.run(saveFacts())


