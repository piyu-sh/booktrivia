import type { AWS } from '@serverless/typescript';

export const booksNFactsTable: AWS['resources']['Resources'][keyof AWS['resources']['Resources']] = {
    "Type": "AWS::DynamoDB::Table",
    "DeletionPolicy": "Retain", // Keeps around the DynamoDB resource when we redeploy/destroy
    "Properties": {
        "TableName": "booksNFactsTable",
        "AttributeDefinitions": [
            {
                "AttributeName": "id",
                "AttributeType": "S"
            },
            {
                "AttributeName": "title",
                "AttributeType": "S"
            },
            {
                "AttributeName": "info",
                "AttributeType": "S"
            },
            {
                "AttributeName": "facts",
                "AttributeType": "S"
            }
        ],
        "KeySchema": [
            {
                "AttributeName": "id",
                "KeyType": "HASH"
            }
        ],
        "ProvisionedThroughput": {
            "ReadCapacityUnits": 4,
            "WriteCapacityUnits": 4
        }
    }
}