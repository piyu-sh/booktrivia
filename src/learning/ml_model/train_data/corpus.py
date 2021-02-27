from nltk.corpus.reader.plaintext import PlaintextCorpusReader
# import os, sys
# currentdir = os.path.dirname(os.path.realpath(__file__))
# parentdir = os.path.dirname(currentdir)
# sys.path.append(parentdir)

# from extract_text.htmlProcess import tokenize_and_stem

corpusdir = '/home/piyush/Downloads/text0/' # Directory of corpus.

newcorpus = PlaintextCorpusReader(corpusdir, '.*')