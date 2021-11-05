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

from learning.ml_model.extract_text.htmlProcess import getDocsAndSentsPerUrl

tqdm.pandas()

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from learning.ml_model.extract_text.gensim_main import getTrainedModel
from learning.ml_model.extract_text.gensimModel import getLdaModel, getSummary, getTfidfModel, getTfidfSummary, printSummary


proxyServerUrl = 'http://localhost:3002/getlinks'
dir_path = os.path.dirname(os.path.realpath(__file__))
linksFile = os.path.join(dir_path,'books-with-relevant-links.csv')
dedupedFile = os.path.join(dir_path,'books-with-relevant-links-deduped.csv')
factsFile = os.path.join(dir_path,'books-with-facts.csv')

if os.path.isfile(linksFile):
    dfLinks = pd.read_csv(linksFile, converters={'searchLinks': ast.literal_eval})
else:
    raise os.error(f'{linksFile}  file needed')

if os.path.isfile(factsFile):
    dfFacts = pd.read_csv(factsFile)
else:
    dfFacts = pd.DataFrame()


def agg_searchLinks(x):
    return list(x) if pd.Series(x).name == 'searchLinks' else x.iloc[0]
    
def deDupeAndSortLinks(searchLinks):
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
    linkSet.sort(key= lambda linkObj: linkObj['rank'])
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
        dfDedupedFull['searchLinks'] = dfUpdatedFull['searchLinks'].progress_apply(deDupeAndSortLinks)
        print(f"dropping query column...")
        dfDedupedFull = dfDedupedFull.drop('query', 1)
        print(f"saving dataframe to file: {dedupedFile}")
        dfDedupedFull.to_csv(dedupedFile, index=False)
    return dfDedupedFull

# dedupe links for a book id
dfDeduped = getDedupedSearchLinksDF()

# get trained model
(tfidf, dictionary, bow) = getTrainedModel(corpusDir='D:/linuxDownloads/iweb/')

# fetch webpages per link per book
# articleUrl = dfDeduped.iloc[0]['searchLinks'][0]['link']
# docs_dict, sents_dict = getDocsAndSentsPerUrl(articleUrl, 3)
# print(docs_dict, sents_dict)
# summary_sents = getTfidfSummary(tfidfModel=tfidf, dictionary=dictionary, docs_dict=docs_dict, sents_dict=sents_dict)
# printSummary(summary_sents)




def saveFacts(bookRow):
    bookRow.to_csv(factsFile, mode='a', index=False, header=False)

class QueueObj(TypedDict):
    id: str
    factsLink: str


async def searchWorker(name: str, searchQueue: Queue, queueProgress: tqdm):
    while True:
        # Get a "work item" out of the queue.
        data: QueueObj = await searchQueue.get()
        factsLink = data['factsLink']
        # url = queryToUrl(query)
        print(Fore.MAGENTA+f'{name} got url: {factsLink} to work on'+Fore.RESET)
        start = time.time()
        custom_timeout = aiohttp.ClientTimeout(total=60) # type: ignore
        # custom_timeout.total = 2*60
        async with aiohttp.ClientSession(timeout=custom_timeout) as session:
            # nonlocal results
            results=[]
            try:
                docs_dict, sents_dict = getDocsAndSentsPerUrl(factsLink, 5)
                summary_sents = getTfidfSummary(tfidfModel=tfidf, dictionary=dictionary, docs_dict=docs_dict, sents_dict=sents_dict)
            except asyncio.TimeoutError as e:
                logging.exception(Fore.RED+f'Exception raised by worker = {name}; error = {e}'+Fore.RESET )
            except Exception as e:  # pylint: disable=broad-except
                logging.exception(Fore.RED+f'Exception raised by worker = {name}; error = {e}'+Fore.RESET )
        print(Fore.YELLOW+f'{name}\'s work for url {factsLink} done; time taken {time.time() - start} seconds'+Fore.RESET)
        if(len(sents_dict[0]) > 2):
            print(f'factsLink: \'{factsLink}\' fetched with > 2 sentences'.encode(encoding='utf-8'))
            searchQueue.task_done()
            bookRow = dfDeduped[dfDeduped['id']==data['id']].copy()
            bookRow['factsLink'] = summary_sents[0]
            saveFacts(bookRow)
            queueProgress.update(1)
        else:
            print(f'factsLink: \'{factsLink}\' unsuccessful, returned < 2 sents, adding to queue again'.encode(encoding='utf-8')) 
            searchQueue.task_done()
            searchQueue.put_nowait(data)

def _handle_task_result(task: asyncio.Task) -> None:
    try:
        task.result()
    except asyncio.CancelledError:
        pass  # Task cancellation should not be logged as an error.
    except Exception:  # pylint: disable=broad-except
        logging.exception('Exception raised by task = %r', task)


async def fetchWebpagesAndSaveFacts(maxWorkers = 5):
    fetchQueue = asyncio.Queue()
    fetchWorkers = []
    # searchResults = []
    queueProgress = tqdm(desc="total queue progress")
    for i in range(maxWorkers):
        task = asyncio.create_task(searchWorker(f'worker{i}',fetchQueue, queueProgress))
        fetchWorkers.append(task)
        task.add_done_callback(_handle_task_result)

    with tqdm(total=len(dfDeduped), desc="books data reading progress") as pbar:
        for row in dfDeduped.itertuples():
            # check in output file, if already that book id exist then skip
            for searchLink in row.searchLinks:
                if('id' not in dfFacts or 'factsLink' not in dfFacts or len(dfFacts[(dfFacts['id'] == row.id) & (dfFacts['factsLink'] == searchLink.link)] < 1)):
                    fetchQueue.put_nowait({
                            'id': row.id,
                            'factsLink': searchLink.link
                        })
            pbar.update(1)

    queueProgress.total = fetchQueue.qsize()
    queueProgress.refresh()
    await fetchQueue.join()
    # cancel the now-idle workers, which wait for a new message that will never arrive
    for w in fetchWorkers:
        w.cancel()

asyncio.run(fetchWebpagesAndSaveFacts(maxWorkers=6))




# dfDeduped10 = dfDeduped.iloc[:10].copy()
# [[linkObj['rank'] for linkObj in row.searchLinks] for row in dfDeduped10.itertuples()]

# # create a mapping of searchLinks to scraped webpage accoring to position in original dataframe
# scrapedPageMap = []

# # create a mapping of searchLinks to summarised scraped webpage accoring to position in original dataframe
# summaryOfPageMap = []

# run model on webpages
# (tfidf, dictionary, bow) = getTrainedModel()

# save highlighted facts with navigation info(possible ?)
