from typing import Text
from bs4 import BeautifulSoup
from pandas.core.arrays.string_ import StringDtype
from pandas.core.frame import DataFrame
from .html_util import getHtmlUsingProxies
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from goose3 import Goose
import numpy as np
import re
from nltk.stem.snowball import SnowballStemmer

stemmer = SnowballStemmer("english")

####
# Config block
import yaml
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(dir_path, "../../../config.yaml"), "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.Loader)
#
####

def tagDoc(url):
    soup = getSoupObj(url)
    sentences = getSentences(soup)
    tags = nltk.pos_tag(sentences)
    return tags

def getSentences(soup):
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.decompose()    # rip it out

#     # get text
#     text = soup.get_text('.\n',strip=True )

#     # break into lines and remove leading and trailing space on each
#     lines = (line.strip() for line in text.splitlines())
#     # break multi-headlines into a line each
#     chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
#     # drop blank lines
#     text = '\n'.join(chunk for chunk in chunks if chunk)

#     sentences = nltk.sent_tokenize(text)

    sentences = [chunk for chunk in soup.get_text().splitlines() if chunk.strip()]
    return sentences


def getSoupObj(url, retries: int):
#     req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
#     html = urlopen(req).read()
    html = getHtmlUsingProxies(url, cfg['proxyApi'], retries)
    soup = BeautifulSoup(html, 'lxml')
    return soup



def removeTitleLikeSents(title, sents, similarity=0.35):
    if(len(sents) < 3):
        return sents
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(sents)
    title_vector = tfidf_vectorizer.transform([title])
    sim_vector = cosine_similarity(title_vector, tfidf_matrix)
    npsents = np.array(sents)
    return list(npsents[sim_vector[0] < similarity])


# In[12]:


def getSents(text: str):
    sentences = [sent for sent in text.splitlines() if sent.strip()]
    return sentences

# example usage
# articleUrl = 'https://www.goodreads.com/book/show/30257963-12-rules-for-life'
# urlDataframe = pd.DataFrame([articleUrl], columns=['1'])
# docs_dict, sents_dict = getDocsAndSents(urlDataframe, '1', 5)
def getDocsAndSents(results: DataFrame, columnName: str, retries: int):
    text_dic = {}
    sents_dic = {}
    g = Goose()
    for index in range(len(results)):
        url = results.iloc[index][columnName]
        soup = getSoupObj(url, retries)
#         sents = getSentences(soup)
        article = g.extract(raw_html=str(soup if soup.get_text().strip() else '.'))
        sents = getSents(article.cleaned_text)
#         doc = '. '.join(chunk for chunk in sents if chunk)
#         doc = soup.get_text()
        sents = removeTitleLikeSents(article.title, sents, 0.34)
        text_dic[index] = article.cleaned_text
        sents_dic[index] = sents
#         if(len(results > 5) and index !=len(results)-1):
#             time.sleep(5)
    return text_dic, sents_dic

# copied from @getDocsAndSents just to run for one url
def getDocsAndSentsPerUrl(url: str, retries: int):
    text_dic = {}
    sents_dic = {}
    g = Goose()
    # for index in range(len(results)):
    # url = results.iloc[index][columnName]
    soup = getSoupObj(url, retries)
#         sents = getSentences(soup)
    article = g.extract(raw_html=str(soup if soup.get_text().strip() else '.'))
    sents = getSents(article.cleaned_text)
#         doc = '. '.join(chunk for chunk in sents if chunk)
#         doc = soup.get_text()
    sents = removeTitleLikeSents(article.title, sents, 0.34)
    text_dic[0] = article.cleaned_text
    sents_dic[0] = sents
#         if(len(results > 5) and index !=len(results)-1):
#             time.sleep(5)
    return text_dic, sents_dic



def tokenize_and_stem(text):
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing punctuation (e.g., raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z0-9]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems

