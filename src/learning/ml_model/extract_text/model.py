#!/usr/bin/env python
# coding: utf-8

# In[1]:


import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import nltk
import time
import asyncio
from proxybroker import Broker
from goose3 import Goose
from sklearn.metrics.pairwise import cosine_similarity
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords')
import nest_asyncio
nest_asyncio.apply()

# In[2]:


from pprint import pprint


# In[3]:


import requests
from lxml.html import fromstring
def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


# In[4]:


async def show(proxies):
    while True:
        proxy = await proxies.get()
        if proxy is None: break
        print('Found proxy: %s' % proxy)
        
proxiesStore = set()

async def storeProxies(proxies):
    while True:
        proxy = await proxies.get()
        if proxy is None: break
        print('Found proxy: %s' % proxy)
        proxiesStore.add(proxy)
        
proxies = asyncio.Queue()
broker = Broker(proxies)
tasks = asyncio.gather(
    broker.find(types=['HTTP','HTTPS'], limit=10),
    storeProxies(proxies))

loop = asyncio.get_event_loop()
loop.run_until_complete(tasks)


# In[5]:


def getHtmlUsingProxies(url):    
    proxies = get_proxies()
    timeout=1
#     for proxyObj in proxiesStore:
    proxiesList = list(proxiesStore)
    for x in range(0, len(proxiesList)-1):
        proxyObj = proxiesList[x]
        proxy = str(proxyObj.host)+':'+str(proxyObj.port)
        try:
            print('fetching '+url+ ' using proxy '+proxy)
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, headers=headers, proxies={"http": proxy}, timeout=timeout)
            if(response.status_code == requests.codes.ok):
                print('fetched')
                return response.text
            else:
                print('Skipping. status code '+ str(response.status_code))
        except requests.exceptions.Timeout:
            x -= 1;
            timeout += 1;
            print("timed out increasing timeout, timeout now is: "+ str(timeout) )
        except Exception as e:
            #Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work. 
            #We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url 
            print("Skipping. Connnection error " + str(e))
    print("can't fetch this doc")
    return ''


# In[6]:


# headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
# resp = requests.get('https://catholicexchange.com/facts-satan-fallen-angels',headers=headers, proxies ={'http': '95.211.228.218:3128'})
# resp.text


# In[7]:


searchResults= pd.read_csv('results.csv');


# In[8]:


success_label = 2
index = 0
succ_results = searchResults[searchResults['2']==success_label]


# In[9]:


example_res= succ_results.iloc[index]['1']
example_res


# In[10]:


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

import requests

def getSoupObj(url):
#     req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
#     html = urlopen(req).read()
    html = getHtmlUsingProxies(url)
    soup = BeautifulSoup(html, 'lxml')
    return soup


# In[11]:


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


def getSents(text):
    sentences = [sent for sent in text.splitlines() if sent.strip()]
    return sentences


# In[13]:


soup = getSoupObj(example_res)


# In[14]:


# getSentences(soup)
# soup.get_text()
# req = Request(example_res, headers={'User-Agent': 'Mozilla/5.0'})
# html = urlopen(req).read()


# In[15]:


sents = getSentences(soup)
# sents


# In[16]:


def getDocs(results):
    text_dic = {}
    sents_dic = {}
    g = Goose()
    for index in range(len(results)):
        url = results.iloc[index]['1']
        soup = getSoupObj(url)
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


# In[17]:


from nltk.stem.snowball import SnowballStemmer

stemmer = SnowballStemmer("english")
# stemmed_tokens = [stemmer.stem(t) for t in tokens]

# for token in sorted(set(stemmed_tokens)):
#     print(token + ' [' + str(stemmed_tokens.count(token)) + ']')


# In[18]:


# lemmatizer = nltk.WordNetLemmatizer()
# temp_sent = "Several women told me I have lying eyes."

# print([stemmer.stem(t) for t in nltk.word_tokenize(temp_sent)])
# print([lemmatizer.lemmatize(t) for t in nltk.word_tokenize(temp_sent)])


# In[19]:


succ_results[:2]


# In[20]:


import datetime, re, sys
from sklearn.feature_extraction.text import TfidfVectorizer

def tokenize_and_stem(text):
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing punctuation (e.g., raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z0-9]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems


# In[21]:


docs_dict, sents_dict = getDocs(succ_results[10:20])


# In[22]:


# for article in reuters.fileids():
#     docs_dict[article] = reuters.raw(article)
        
tfidf = TfidfVectorizer(tokenizer=tokenize_and_stem, stop_words='english', decode_error='ignore', ngram_range=(1,3))
print('building term-document matrix... [process started: ' + str(datetime.datetime.now()) + ']')
sys.stdout.flush()

tdm = tfidf.fit_transform(docs_dict.values()) # this can take some time (about 60 seconds on my machine)
print('done! [process finished: ' + str(datetime.datetime.now()) + ']')


# In[23]:


# print(docs_dict[0])


# In[24]:


from random import randint

feature_names = tfidf.get_feature_names()
print('TDM contains ' + str(len(feature_names)) + ' terms and ' + str(tdm.shape[0]) + ' documents')

print('first term: ' + feature_names[0])
print('last term: ' + feature_names[len(feature_names) - 1])

for i in range(0, 4):
    print('random term: ' + feature_names[randint(1,len(feature_names) - 2)])


# In[25]:


import math
from __future__ import division

# article_id = randint(0, tdm.shape[0] - 1)
article_id = 0
article_text = docs_dict[article_id]
article_sents = sents_dict[article_id]

sent_scores = []
for sentence in article_sents:
    score = 1
    sent_tokens = tokenize_and_stem(sentence)
    if len(sent_tokens)>0:
        for token in (t for t in sent_tokens if t in feature_names):
            score += tdm[article_id, feature_names.index(token)]
        sent_scores.append((score / len(sent_tokens), sentence))

summary_length = int(math.ceil(len(sent_scores) / 5))
sent_scores.sort(key=lambda sent: sent[0], reverse=True)

print('*** SUMMARY ***')
for summary_sentence in sent_scores[:summary_length]:
    if(len(nltk.word_tokenize(summary_sentence[1])) > 3):
        print(summary_sentence[1])

print('\n*** ORIGINAL ***')
print(article_text)


# In[26]:


# sent_scores


# In[27]:


doc_complete = sents_dict[0]


# In[28]:


from nltk.corpus import stopwords 
from nltk.stem.wordnet import WordNetLemmatizer
import string
stop = set(stopwords.words('english'))
exclude = set(string.punctuation) 
lemma = WordNetLemmatizer()
def clean(doc):
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized

doc_clean = [clean(doc).split() for doc in doc_complete]   


# In[29]:


import gensim
from gensim import corpora

# Creating the term dictionary of our courpus, where every unique term is assigned an index. 
dictionary = corpora.Dictionary(doc_clean)

# Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]


# In[30]:


# Creating the object for LDA model using gensim library
Lda = gensim.models.ldamodel.LdaModel

# Running and Trainign LDA model on the document term matrix.
ldamodel = Lda(doc_term_matrix, num_topics=1, id2word = dictionary, passes=50)


# In[31]:


print(ldamodel.print_topics())


# In[32]:


topic_scores = ldamodel.show_topics(0,formatted=False)[0][1]
topic_scores


# In[33]:


sentence_scores=[]
for index in range(0,len(sents_dict[0])-1):
    words = [word for word in nltk.word_tokenize(sents_dict[0][index])]
    
    # score/len(words) -  normalize score based on length of sentence
    sentence_scores.append((sum([score/len(words) for word in words 
                                 for (topic, score) in topic_scores 
                                 if word.lower() == topic.lower()]),
                            sents_dict[0][index]))


# In[34]:


sorted_scores = sorted(sentence_scores,key= lambda x: x[0], reverse=True)


# In[ ]:





# In[35]:


from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

summary_dict= {}
for doc_index in sents_dict:
    doc_complete = sents_dict[doc_index]
    doc_clean = [clean(doc).split() for doc in doc_complete]
    
    if(len(doc_clean) < 5):
        summary_dict[doc_index] = None
        continue
        
    # Creating the term dictionary of our courpus, where every unique term is assigned an index. 
    dictionary = corpora.Dictionary(doc_clean)

    # Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]
    # Creating the object for LDA model using gensim library
    Lda = gensim.models.ldamodel.LdaModel

    # Running and Trainign LDA model on the document term matrix.
    ldamodel = Lda(doc_term_matrix, num_topics=1, id2word = dictionary, passes=50)
    
    topic_scores = ldamodel.show_topics(0,formatted=False)[0][1]
    
    sentence_scores=[]
    for index in range(0,len(sents_dict[doc_index])-1):
        sents_in_sent = [sent for sent in nltk.sent_tokenize(sents_dict[doc_index][index])]
        sent_scores = []
        max_index = 0
        for s_index in range(0, len(sents_in_sent)-1):
            words = [word for word in nltk.word_tokenize(sents_in_sent[s_index])]
            sum_score = sum([score/len(words) for word in words 
                                     for (topic, score) in topic_scores 
                                     if word.lower() == topic.lower()])
            sent_scores.append(sum_score)
            max_index = s_index if sent_scores[s_index] > sent_scores[max_index] else max_index
        
#         words = [word for word in nltk.word_tokenize(sents_dict[doc_index][index])]
#         score/len(words) -  normalize score based on length of sentence
        sentsToAdd = sents_in_sent[:max_index+2]
#         sentence_scores.append((max(sent_scores) if sent_scores else 0, sents_dict[doc_index][index]))
        sentence_scores.append((max(sent_scores) if sent_scores else 0, sentsToAdd))
    
    
    sorted_scores = sorted(sentence_scores,key= lambda x: x[0], reverse=True)
    summary_dict[doc_index] = sorted_scores


# In[36]:


for summary_index in range(0,len(summary_dict)-1):
    summary= summary_dict[summary_index]
    summary_len = 0 if summary is None else int(len(summary)/10)
    print('\n\n\ndocument '+ str(summary_index)+'')
    print('') if summary is None else [print(' '.join(text)) for (score, text) in summary[:5]]


# In[57]:


for doc_index in range(0, len(docs_dict)):
    sents = nltk.sent_tokenize(docs_dict[doc_index])
    words = len([word for sent in sents for word in nltk.word_tokenize(sent)])
    average = words / len(sents) if len(sents)>0 else 0
    print('doc '+ str(doc_index) + ' average sentence len '+str(average))


# In[ ]:





# In[206]:

g = Goose()
soup = getSoupObj(succ_results.iloc[8]['1'])
article = g.extract(raw_html=str(soup))


# In[213]:


removeTitleLikeSents(article.title,getSents(article.cleaned_text), 0.34)


# In[209]:


article.title


# In[216]:


summary_dict[8]


# In[217]:


import matplotlib.pyplot as plt


# In[257]:


x, y = zip(*summary_dict[dict_index])


# In[258]:


plt.bar(x= range(0, len(x)),height=x, )


# In[259]:


plt.bar(x= range(0, summ_len),height=x[:summ_len], )


# In[233]:


summary_dict[4]


# In[255]:


dict_index = 8
score_sum=0
for (score, text) in summary_dict[dict_index]:
    score_sum+=score
summ_len=0
sum_till_now=0
for index in range(0, len(summary_dict[dict_index])-1):
    score, text = summary_dict[dict_index][index] 
    sum_till_now += score
    if(sum_till_now > (score_sum/2)):
        summ_len = index
        break


# In[256]:


len(summary_dict[dict_index])


# In[286]:





# In[ ]:



