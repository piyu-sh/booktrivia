# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd
import numpy as np
from pandasgui import show
from strsimpy.levenshtein import Levenshtein
from strsimpy.normalized_levenshtein import NormalizedLevenshtein
from strsimpy.weighted_levenshtein import WeightedLevenshtein
from strsimpy.damerau import Damerau
from strsimpy.optimal_string_alignment import OptimalStringAlignment
from strsimpy.jaro_winkler import JaroWinkler
from strsimpy.longest_common_subsequence import LongestCommonSubsequence
from strsimpy.metric_lcs import MetricLCS
from strsimpy.ngram import NGram
from strsimpy.qgram import QGram
from strsimpy.cosine import Cosine
from fuzzywuzzy import fuzz
import regex as re

# %%
df = pd.read_csv('goodreads-10k-dataset-integrated.csv')


# %%
show(df)


# %%
df

#%%
# regexp = re.compile(r'(.*)\((.*),.*')
# re_match = regexp.match('The Lightning Thief (Percy Jackson and the Olympians, #1)')



#%%
def getStringsAB(title):
    strA=title
    strB=''
    if(title.find('(') > -1):
        strA = title[:title.find('(')]
        strB = title[title.find('(')+1 : title.find(',')]
    return [strA, strB]


# stringsAB = [[[a, b] for a, b in getStringsAB(str(title))] for title in df['original_title'].to_list()]
stringsAB = [getStringsAB(str(title)) for title in df['title'].to_list()]
npStringsAB = np.array(stringsAB)

# %%
levenshtein = Levenshtein()
normalized_levenshtein = NormalizedLevenshtein()
damerau = Damerau()
optimal_string_alignment = OptimalStringAlignment()
jarowinkler = JaroWinkler()
lcs = LongestCommonSubsequence()
metric_lcs = MetricLCS()
twogram = NGram(2)
qgram = QGram(2)
cosine = Cosine(2)

strAs = npStringsAB[:, 0].tolist()
strBs = npStringsAB[:, 1].tolist()
results = {
    'str A': strAs,
    'str B': strBs,
    # 'Levenshtein': [
    #     levenshtein.distance(str1a, str1b),
    #     levenshtein.distance(str2a, str2b),
    #     levenshtein.distance(str3a, str3b)
    # ],
    # 'NormalizedLevenshtein': [
    #     normalized_levenshtein.distance(str1a, str1b),
    #     normalized_levenshtein.distance(str2a, str2b),
    #     normalized_levenshtein.distance(str3a, str3b)
    # ],
    # 'Damerau': [
    #     damerau.distance(str1a, str1b),
    #     damerau.distance(str2a, str2b),
    #     damerau.distance(str3a, str3b)
    # ],
    # 'OptimalStringAlignment': [
    #     optimal_string_alignment.distance(str1a, str1b),
    #     optimal_string_alignment.distance(str2a, str2b),
    #     optimal_string_alignment.distance(str3a, str3b)
    # ],
    'JaroWinkler': [
        jarowinkler.similarity(strA, strB) for strA, strB in stringsAB
    ],
    # 'LongestCommonSubsequence': [
    #     lcs.distance(str1a, str1b),
    #     lcs.distance(str2a, str2b),
    #     lcs.distance(str3a, str3b)
    # ],
    # 'MetricLCS': [
    #     metric_lcs .distance(str1a, str1b),
    #     metric_lcs .distance(str2a, str2b),
    #     metric_lcs .distance(str3a, str3b)
    # ],
    'NGram(2)': [
        twogram.distance(strA, strB) for strA, strB in stringsAB
    ],
    # 'QGram(2)': [
    #     qgram.distance(str1a, str1b),
    #     qgram.distance(str2a, str2b),
    #     qgram.distance(str3a, str3b)
    # ],
    # 'Cosine(2)': [
    #     cosine.similarity_profiles(cosine.get_profile(str(strA)), cosine.get_profile(str(strB))) for strA, strB in stringsAB
    # ],
    'fuzz(Simple Ratio)': [
        fuzz.ratio(strA, strB) for strA, strB in stringsAB
    ],
    'fuzz(Partial Ratio)': [
        fuzz.partial_ratio(strA, strB) for strA, strB in stringsAB
    ],
    'fuzz(Token Sort Ratio)': [
        fuzz.token_sort_ratio(strA, strB) for strA, strB in stringsAB
    ],
    'fuzz(Token Set Ratio)': [
        fuzz.token_set_ratio(strA, strB) for strA, strB in stringsAB
    ]

}


#%%
resultsDF = pd.DataFrame(results)

show(resultsDF)

# %%
