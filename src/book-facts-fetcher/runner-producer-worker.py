from asyncio.queues import Queue
import time
from typing import List
import pandas as pd
import numpy as np
import os.path
import asyncio
import aiohttp
from urllib import parse

from pandas.core.frame import DataFrame

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
        url = await searchQueue.get()
        print(f'{name} got url: {url} to work on')
        start = time.time()
        async with aiohttp.ClientSession() as session:
            # nonlocal results
            task = asyncio.ensure_future(getSearchQueryResults(session, url))
            results = await asyncio.gather(task)
        print(f'{name}\'s work for url {url} done; time taken {time.time() - start} seconds')
        searchQueue.task_done()
        searchResults.append({
            url: results
        })

async def searchProducer( searchQueue: Queue, dfFacts: DataFrame, df: DataFrame):
    i = 0
    while True:
        if(searchQueue.full()):
            await asyncio.sleep(1)
            continue
        else:
            row = df.iloc[i]
            i+=1
            if(i <10 and ('id' not in dfFacts or dfFacts[dfFacts['id']==row.id].size == 0)):
                # extract title
                title, work = getStringsAB(row.title)
                query = parse.urlencode({
                    'keyword': title
                })
                url = f'{proxyServerUrl}?{query}'
                await searchQueue.put(url)
                print(f'added one url: {url} to queue; queue length: {searchQueue.qsize()}')
        
async def saveFacts(maxWorkers = 5):
    factsFile = os.path.join(dir_path,'books-with-facts.csv')
    if os.path.isfile(factsFile):
        dfFacts = pd.read_csv(factsFile)
    else:
        dfFacts = pd.DataFrame()

    booksFile = os.path.join(dir_path,'goodreads-10k-dataset-integrated.csv')
    df = pd.read_csv(booksFile)

    searchQueue = asyncio.Queue(maxsize=maxWorkers)

    producers = [asyncio.create_task(searchProducer(searchQueue, dfFacts, df))]

    searchWorkers = []
    searchResults = []
    for i in range(maxWorkers):
        searchWorkers.append(asyncio.create_task(searchWorker(f'worker{i}',searchQueue, searchResults)))

    await asyncio.gather(*producers)

    await searchQueue.join()
    [producer.cancel() for producer in producers]
    # cancel the now-idle workers, which wait for a new message
    # that will never arrive
    for w in searchWorkers:
        w.cancel()
    
    # find facts
    # 


asyncio.run(saveFacts())


