from typing import Any, Dict, List
import gensim
from gensim import corpora
from gensim.models import tfidfmodel
from gensim.models.ldamodel import LdaModel
from goose3 import Goose
import nltk
from nltk.corpus import stopwords
from nltk.corpus import stopwords 
from nltk.stem.wordnet import WordNetLemmatizer
import string
import datetime
from gensim.utils import simple_preprocess
from gensim.models import TfidfModel
from gensim.corpora import Dictionary
import math
from .htmlProcess import tokenize_and_stem
from gensim.models.phrases import Phrases 
from tqdm import tqdm

stop = set(stopwords.words('english'))
exclude = set(string.punctuation) 
lemma = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
g = Goose()

def clean(docOrTokenList, returnTokens=False):
    tokenList = None
    if( isinstance(docOrTokenList, str) ):
        tokenList = simple_preprocess(docOrTokenList)
    elif( isinstance(docOrTokenList, List) ):
        tokenList = docOrTokenList
    else:
        raise TypeError("docOrTokenList must be a str or List of str")

    tokens = [lemma.lemmatize(token) for token in tokenList if token not in stop and token not in exclude]
    if(returnTokens):
        return tokens
    else:
        cleanedDoc = " ".join(tokens)
        return cleanedDoc

def getLdaModel(docs_dict_values):
    print('training lda model at: ' + str(datetime.datetime.now()))
    clean_docs_dict = [clean(docOrTokenList=doc, returnTokens=True) for doc in docs_dict_values]
    dictionary = corpora.Dictionary(clean_docs_dict)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in clean_docs_dict]
    Lda = gensim.models.ldamodel.LdaModel
    ldamodel = Lda(doc_term_matrix, id2word = dictionary, passes=50)
    print('lda model trained at: ' + str(datetime.datetime.now()))
    return ldamodel

def getSummary(ldamodel: LdaModel, sents_dict: Dict[Any, list]):
    topic_scores = ldamodel.show_topics(0,formatted=False)[0][1]
    summary_dict= {}
    for doc_index in sents_dict:
        doc_complete = sents_dict[doc_index]
        doc_clean = [clean(doc).split() for doc in doc_complete]
        
        if(len(doc_clean) < 5):
            summary_dict[doc_index] = None
            continue
        
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
    return summary_dict

def printSummary(summary_dict):
    for summary_index in range(0,len(summary_dict)-1):
        summary= summary_dict[summary_index]
        summary_len = 0 if summary is None else int(len(summary)/10)
        print('\n\n\ndocument '+ str(summary_index)+'')
        print('') if summary is None else [print(' '.join(text)) for (score, text) in summary[:5]]

def printAvgSentLeng(docs_dict):
    for doc_index in range(0, len(docs_dict)):
        sents = nltk.sent_tokenize(docs_dict[doc_index])
        words = len([word for sent in sents for word in nltk.word_tokenize(sent)])
        average = words / len(sents) if len(sents)>0 else 0
        print('doc '+ str(doc_index) + ' average sentence len '+str(average))


def getTfidfModel(docs_dict_values):
    print('training tfidf model at: ' + str(datetime.datetime.now()))

    # sents_list = [sent for sent in getTokenizedSents(docs_dict_values)]

    #TODO: 16-2-21: Let's skip bigram/tigrams fow now and focus on getting tfidf correct 


    # Bigram using Phraser Model               
    # bigram_model = Phrases(sentences = sents_list, threshold = 3)
    
    # Trigram using Phraser Model 
    # trigram_model = Phrases(bigram_model[sents_list], threshold = 3) 
  
    clean_docs_dict = [clean(docOrTokenList=docs, returnTokens=True) for docs in tqdm(docs_dict_values, "cleaning docs")]
    dictionary = corpora.Dictionary(clean_docs_dict)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in tqdm(clean_docs_dict, "doc_term_matrix")]
    tfidfModel = TfidfModel(corpus=doc_term_matrix, smartirs ='ntc')
    print('tfidf model trained at: ' + str(datetime.datetime.now()))
    # return (tfidfModel, dictionary, doc_term_matrix, trigram_model)
    return (tfidfModel, dictionary, doc_term_matrix)

def getTokenizedSents(docs_dict_values, isHtml = True):
    for doc in docs_dict_values:
        doc_text = (g.extract(raw_html=doc)).cleaned_text if isHtml else doc
        sents = [sent for sent in nltk.sent_tokenize(doc_text)]
        for sent in sents:
            yield nltk.word_tokenize(sent)

def getTfidfSummary(tfidfModel:TfidfModel, dictionary:Dictionary, docs_dict, sents_dict, summary_num_sents:Dict[int, int]={}, summary_ratio=0.2):

    # sents_list = [sent for sent in getTokenizedSents(docs_dict.values(), isHtml=False)]
    #TODO: 16-2-21: Let's skip bigram/tigrams fow now and focus on getting tfidf correct 


    # # Bigram using Phraser Model               
    # bigram_model = Phrases(sentences = sents_list, threshold = 3)
    
    # # Trigram using Phraser Model 
    # trigram_model = Phrases(bigram_model[sents_list], threshold = 3) 

    clean_docs_dict = [clean(docOrTokenList=doc, returnTokens=True) for doc in docs_dict.values()]

    doc_term_matrix = [dictionary.doc2bow(doc) for doc in clean_docs_dict]
    transformedData = tfidfModel[doc_term_matrix]
    weight_tfidf = {}
    summary_sents = {}
    sent_scores = {}

    for index, doc in enumerate(transformedData): 
        weight_tfidf[index] = {}
        sent_scores[index] = []
        for id, freq in doc: 
            # weight_tfidf.append([dictionary[id], freq]) 
            weight_tfidf[index][id] = freq
        for sentence in sents_dict[index]:
            score = 1
            # sent_tokens = tokenize_and_stem(sentence)
            sent_tokens = clean(sentence, returnTokens=True)
            if len(sent_tokens)>0:
                tokens_that_exist = [t for t in sent_tokens if t in dictionary.token2id and dictionary.token2id[t] in weight_tfidf[index]]
                for token in tokens_that_exist:
                    score += weight_tfidf[index][dictionary.token2id[token]]
                sent_scores[index].append((score / len(sent_tokens), sentence))
        
        summary_length = summary_num_sents[index] if index in summary_num_sents else int(math.ceil(len(sent_scores[index]) * summary_ratio))
        sent_scores[index].sort(key=lambda sent: sent[0], reverse=True)
        summary_sents[index] = sent_scores[index][:summary_length]

    return summary_sents

def getTfidfSummary2(tfidfModel:TfidfModel, dictionary:Dictionary, trigrams: Phrases, docs_dict, sents_dict, summary_num_sents:Dict[int, int]={}, summary_ratio=0.2):

    for index, doc in enumerate(docs_dict):
        clean_docs_dict = [clean(docOrTokenList=tokenList, returnTokens=True) for tokenList in trigrams[sents_dict[index]]]
        


def printSummary(summary_sents):
    for doc_index in summary_sents:
        print('*** SUMMARY for ',doc_index, ' doc ***' )
        for summary_sentence in summary_sents[doc_index]:
            if(len(nltk.word_tokenize(summary_sentence[1])) > 3):
                print(summary_sentence[1])
