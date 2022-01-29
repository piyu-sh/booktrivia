
# first create table in local dynamodb to test, command below
# aws dynamodb create-table --cli-input-json file://booksNFactsTableConfig.json --endpoint-url http://localhost:8000 --region=ap-south-1

# command to run local dynamodb
# java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb

import boto3

dynamodb = boto3.resource('dynamodb', region_name="ap-south-1", endpoint_url='http://localhost:8000')
table = dynamodb.Table('booksNFactsTable')
# read book facts grouped file 
# skip already written facts, maintain in other file, i think ID should be sufficient to save but lets think about it more

with table.batch_writer(overwrite_by_pkeys=['id']) as batch:
    batch.put_item(
        Item={
            'id': 'p1',
            'sort_key': 's1',
            'other': '111',
        }
    )
    batch.put_item(
        Item={
            'id': 'p1',
            'sort_key': 's1',
            'other': '222',
        }
    )
    batch.delete_item(
        Key={
            'id': 'p1',
            'sort_key': 's2'
        }
    )
    batch.put_item(
        Item={
            'id': 'p1',
            'sort_key': 's2',
            'other': '444',
        }
    )

# write new facts to dynamodb in batches
