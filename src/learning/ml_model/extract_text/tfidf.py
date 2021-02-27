from typing import Iterable, List
from sklearn.feature_extraction.text import TfidfVectorizer
from .htmlProcess import tokenize_and_stem
import datetime, sys
from random import randint
import nltk
import math
from nltk.corpus import stopwords 
from nltk.stem.wordnet import WordNetLemmatizer
import string

def getTrainedTfidfModel(trainData):
    tfidf = TfidfVectorizer(tokenizer=tokenize_and_stem, stop_words='english', decode_error='ignore', ngram_range=(1,3))
    print('building term-document matrix... [process started: ' + str(datetime.datetime.now()) + ']')
    sys.stdout.flush()

    tdm = tfidf.fit_transform(trainData) # this can take some time (about 60 seconds on my machine)
    print('done! [process finished: ' + str(datetime.datetime.now()) + ']')
    return (tfidf, tdm)


def get_feature_names(tfidf: TfidfVectorizer):
    feature_names = tfidf.get_feature_names()
    # print('TDM contains ' + str(len(feature_names)) + ' terms and ' + str(tdm.shape[0]) + ' documents')

    print('first term: ' + feature_names[0])
    print('last term: ' + feature_names[len(feature_names) - 1])

    for i in range(0, 4):
        print('random term: ' + feature_names[randint(1,len(feature_names) - 2)])
    return feature_names

def getSummary(article_sents, article_id, tdm, tfidf, summary_len=None, article_text=None):
    sent_scores = []
    feature_names = get_feature_names(tfidf)
    for sentence in article_sents:
        score = 1
        sent_tokens = tokenize_and_stem(sentence)
        if len(sent_tokens)>0:
            for token in (t for t in sent_tokens if t in feature_names):
                score += tdm[article_id, feature_names.index(token)]
            sent_scores.append((score / len(sent_tokens), sentence))

    summary_length = summary_len if summary_len is not None else int(math.ceil(len(sent_scores) / 5))
    sent_scores.sort(key=lambda sent: sent[0], reverse=True)

    print('*** SUMMARY ***')
    for summary_sentence in sent_scores[:summary_length]:
        if(len(nltk.word_tokenize(summary_sentence[1])) > 3):
            print(summary_sentence[1])

    if article_text is not None:
        print('\n*** ORIGINAL ***')
        print(article_text)
    
    return sent_scores[:summary_length]

def getLemmatizedDoc(doc_complete:List[str]):
    stop = set(stopwords.words('english'))
    exclude = set(string.punctuation) 
    lemma = WordNetLemmatizer()
    def clean(doc):
        stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
        punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
        normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
        return normalized

    doc_clean = [clean(doc).split() for doc in doc_complete] 
    return doc_clean