import os

def getCorpusData(corpusdir):
    content = {}
    for filename in os.listdir(corpusdir):
        with open(os.path.join(corpusdir, filename), 'r') as f: # open in readonly mode
            # do your stuff
            content[filename] = f.read()
            f.close()
    return content
