
import pandas as pd
import numpy as np
import itertools

class SearchQuery:
    def __init__(self, titleList, searchWords):
        self.titleList = titleList
        self.searchWords= searchWords

    def setTitleList(self, title)
    def getSearchQueries():


booklist= pd.read_csv('../data/Top UK book sales of all time - Top 100 199801-201231.csv')


# In[3]:


booklist.drop(booklist.index[[100]], inplace=True)


# In[4]:


booklist['Title_1'] = booklist['Title'].apply(lambda x: ' '.join(x.split(',')[::-1]))
booklist['Author_1'] = booklist['Author'].apply(lambda x: ' '.join(x.split(',')[::-1]))


# In[5]:


booklist['title_author']= booklist['Title_1']+' '+booklist['Author_1']


# In[6]:


booklist


# In[18]:


np.savetxt('../data/top100Titles.txt', booklist['Title_1'].values, '%s')


# In[10]:


search_words = pd.read_csv('../data/searchwords.csv')


# In[11]:


search_words


# In[31]:


search_query = pd.DataFrame([(x+' '+y) for (x,y) in itertools.product(booklist['Title_1'], search_words['strings'])], columns=['query'])


# In[41]:


np.savetxt('../data/searchQuery.txt', search_query['query'].values, '%s')

