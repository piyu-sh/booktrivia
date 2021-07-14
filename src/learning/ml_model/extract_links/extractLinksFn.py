import pickle
import requests
import os 
import numpy as np
import re
import joblib


dir_path = os.path.dirname(os.path.realpath(__file__))

model_filename = 'saved_model_v1.pickle'
fileUri = os.path.join(dir_path, model_filename)

pipeline_filename = 'saved_pipeline_1.pickle'
pipelineFileUri = os.path.join(dir_path, pipeline_filename)

lookup_tbl_file = 'saved_lookup_table.pickle'
lookupFileUri = os.path.join(dir_path, lookup_tbl_file)

loaded_model = pickle.load(open(fileUri, 'rb'))
loaded_pipeline = pickle.load(open(pipelineFileUri, 'rb'))
loaded_lookup_tbl = pickle.load(open(lookupFileUri, 'rb'))


def getRelevantTitleIndices(titles, indexOfRelevantTitles = 2):
    cleanedData= np.array(list(map(lambda v: re.sub(r'\b[0-9]{1,4}\b', 'NUMBERSPECIALTOKEN', v) ,titles)))
    transformedData = loaded_pipeline.transform(cleanedData).todense()

    result = loaded_model.predict(transformedData)

    sorted_result = loaded_lookup_tbl[result]

    # print('result: ',result )
    # print('sorted_result: ',sorted_result )
    relevantIndices = [ index for index, item in enumerate(titles) if sorted_result[index] == indexOfRelevantTitles ]
    return relevantIndices

# titles = ['The Great Gatsby Tri...ut the ...',
# '15 Fantastical Facts...- 15 Facts',
# 'Five Fascinating Fac...Gatsby ...',
# '24 Great Gatsby Fact...ntal Floss',
# "10 Things You Didn...eat Gatsby",
# 'The Great Gatsby: Ke...SparkNotes',
# 'Did You Know These F...?',
# 'The Great Gatsby- In...en Mahoney',
# "25 Things You Didn...Gatsby ...",
# 'The Great Gatsby...uffPost UK']
# getRelevantTitleIndices(titles)