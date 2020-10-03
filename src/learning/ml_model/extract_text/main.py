from sklearn.feature_extraction.text import TfidfVectorizer
from random import randint
import datetime, sys
import math
import nltk
import pandas as pd
from .htmlProcess import getDocs, tokenize_and_stem

import yaml
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(dir_path, "../../../config.yaml"), "r") as ymlfile:
    cfg = yaml.load(ymlfile)

articleUrl = 'https://www.goodreads.com/book/show/30257963-12-rules-for-life'
# print(getHtmlUsingProxies('https://www.goodreads.com/book/show/30257963-12-rules-for-life', cfg['proxyApi']))

urlDataframe = pd.DataFrame([articleUrl], columns=['1'])
docs_dict, sents_dict = getDocs(urlDataframe, '1')
        
tfidf = TfidfVectorizer(tokenizer=tokenize_and_stem, stop_words='english', decode_error='ignore', ngram_range=(1,3))
print('building term-document matrix... [process started: ' + str(datetime.datetime.now()) + ']')
sys.stdout.flush()

tdm = tfidf.fit_transform(docs_dict.values()) # this can take some time (about 60 seconds on my machine)
print('done! [process finished: ' + str(datetime.datetime.now()) + ']')


feature_names = tfidf.get_feature_names()
print('TDM contains ' + str(len(feature_names)) + ' terms and ' + str(tdm.shape[0]) + ' documents')

print('first term: ' + feature_names[0])
print('last term: ' + feature_names[len(feature_names) - 1])

for i in range(0, 4):
    print('random term: ' + feature_names[randint(1,len(feature_names) - 2)])


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



doc_complete = sents_dict[0]

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

