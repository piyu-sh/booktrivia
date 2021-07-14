import pickle
import requests
import os 
import numpy as np
import re
import joblib


dir_path = os.path.dirname(os.path.realpath(__file__))

model_filename = 'saved_model_v1.pickle'
fileUri = os.path.join(dir_path, model_filename)
# print("fileUri", fileUri)

pipeline_filename = 'saved_pipeline_1.pickle'
pipelineFileUri = os.path.join(dir_path, pipeline_filename)
# print("pipelineFileUri", pipelineFileUri)

lookup_tbl_file = 'saved_lookup_table.pickle'
lookupFileUri = os.path.join(dir_path, lookup_tbl_file)

webSearcher_url = 'http://localhost:3002/getlinks'

loaded_model = pickle.load(open(fileUri, 'rb'))
loaded_pipeline = pickle.load(open(pipelineFileUri, 'rb'))
# loaded_pipeline = joblib.load(pipelineFileUri)
loaded_lookup_tbl = pickle.load(open(lookupFileUri, 'rb'))

keyword = 'lolita interesting facts'
params = {
    'keyword': keyword
}
scrape_result = requests.get(webSearcher_url, params=params).json()
# print("scrape_result", scrape_result)

results = scrape_result[0]['results'][keyword]['1']['results']

url_titles = [item['title'] for item in results]

# print('url_titles', url_titles)

testD= np.array(list(map(lambda v: re.sub(r'\b[0-9]{1,4}\b', 'NUMBERSPECIALTOKEN', v) ,url_titles)))
# testD = ['Are you an Outlier? 6 Unexpected Keys to Success from Malcolm ...',
#                    'Fun facts found in Outliers by Gladwell - Marketing Action, Inc.',
#                     'Outliers Chapter 2: The 10,000-Hour Rule Summary & Analysis from ...',
#                    'Malcolm Gladwell"s 5 Best Life Lessons for Entrepreneurs | Inc.com']
# testD = np.array(['Are you an Outlier? 6 Unexpected Keys to Success from Malcolm ...',
#                    'Fun facts found in Outliers by Gladwell - Marketing Action, Inc.',
#                     'Outliers Chapter 2: The 10,000-Hour Rule Summary & Analysis from ...',
#                    'Malcolm Gladwell"s 5 Best Life Lessons for Entrepreneurs | Inc.com']
#                    )                   
testX = loaded_pipeline.transform(testD).todense()

result = loaded_model.predict(testX)

sorted_result = loaded_lookup_tbl[result]

print('result: ',result )
print('sorted_result: ',sorted_result )
final = [(sorted_result[index], title) for index, title in enumerate(url_titles)]