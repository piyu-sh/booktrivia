import os, sys

# currentdir = os.path.dirname(os.path.realpath(__file__))
# parentdir = os.path.dirname(currentdir)
# sys.path.append(parentdir)
# sys.path.append(currentdir)


from random import randint
import nltk
import pandas as pd
from yaml import dump, load
from .htmlProcess import getDocsAndSents
from .tfidf import getLemmatizedDoc, getSummary, getTrainedTfidfModel
import yaml
from ..train_data.train_data import getCorpusData
import joblib
from hashlib import blake2b
import datetime

def getHash(data: dict):
    hashObj = blake2b()
    for item in data:
        hashObj.update(item.encode('utf-8'))
    return hashObj.hexdigest()

def writeHash(hashValue, hashFilePath):
    hashSame = True
    prevHashValue = ''

    if(os.path.isfile(hashFilePath)):
        hashFile = open(hashFilePath, 'r')
        prevHashValue = hashFile.read()
        hashFile.close()
    
    if(hashValue != prevHashValue):
        hashFile = open(hashFilePath, 'w')
        hashFile.write(hashValue)
        hashSame = False
        hashFile.close()

    return hashSame

dir_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(dir_path, "../../../config.yaml"), "r") as ymlfile:
    cfg = yaml.load(ymlfile)


corpusData = getCorpusData(corpusdir='/home/piyush/Downloads/text0/')
# corpusData = getCorpusData(corpusdir='/home/piyush/Downloads/iweb/')


hashValue = getHash(corpusData)
hashSame = writeHash(hashValue, os.path.join(dir_path,'corpusHash.txt'))
# hashSame = writeHash(hashValue, os.path.join(dir_path,'corpusHashIweb.txt'))

trainedModel = ()
if(hashSame and os.path.isfile(os.path.join(dir_path,'trainedTFVector.joblib'))):
# if(hashSame and os.path.isfile(os.path.join(dir_path,'trainedTFVectorIweb.joblib'))):
    print('loading model at: ' + str(datetime.datetime.now()))
    trainedModel = joblib.load(os.path.join(dir_path,'trainedTFVector.joblib'))
    # trainedModel = joblib.load(os.path.join(dir_path,'trainedTFVectorIweb.joblib'))
    print('done! model loaded' + str(datetime.datetime.now()))
else:
    # TODO - use corpus data for training, docs_dict is test data 
    trainedModel = getTrainedTfidfModel(trainData=corpusData.values())
    joblib.dump(trainedModel, os.path.join(dir_path,'trainedTFVector.joblib'))
    # joblib.dump(trainedModel, os.path.join(dir_path,'trainedTFVectorIweb.joblib'))
(tfidf, tdm) = trainedModel

# articleUrl = 'https://www.goodreads.com/book/show/30257963-12-rules-for-life'
# articleUrl = 'https://michael-bonnell.com/12-rules-for-life-an-antidote-to-chaos/';
articleUrl = 'https://bookfail.com/nonfiction/658-12-rules-for-life-an-antidote-to-chaos.html';

# print(getHtmlUsingProxies('https://www.goodreads.com/book/show/30257963-12-rules-for-life', cfg['proxyApi']))

urlDataframe = pd.DataFrame([articleUrl], columns=['1'])
docs_dict, sents_dict = getDocsAndSents(urlDataframe, '1', 5)




# article_id = randint(0, tdm.shape[0] - 1)
article_id = 0
article_text = docs_dict[article_id]
article_sents = sents_dict[article_id]

# TODO: tfidf is a trained model, now use test data, instead of just train data 
summary_sents = getSummary( article_sents, article_id, tdm, tfidf)



doc_complete = sents_dict[0]

doc_clean = getLemmatizedDoc(doc_complete)  

