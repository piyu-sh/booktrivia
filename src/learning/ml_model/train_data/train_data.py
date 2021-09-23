import os
from tqdm import tqdm

def getCorpusData(corpusdir):
    content = {}
    for filename in tqdm(os.listdir(corpusdir), "file reading progress"):
        with open(os.path.join(corpusdir, filename), 'r') as f: # open in readonly mode
            # do your stuff
            content[filename] = f.read()
            f.close()
    return content
