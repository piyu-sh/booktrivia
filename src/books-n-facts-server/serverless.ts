import type { AWS } from '@serverless/typescript';

import getBooksNFacts from '@functions/getBooksNFacts';

const serverlessConfiguration: AWS = {
  service: 'books-n-facts-server',
  app: 'booktrivia-own-proxy-app',
  org: 'piyushg',
  frameworkVersion: '2',
  custom: {
    webpack: {
      webpackConfig: './webpack.config.js',
      includeModules: true,
    },
    globalTables: {
      version: 'v2', // optional, default is 'v1' (2017.11.29), please use 'v2' for (2019.11.21) version creation
      regions: [
        'us-east-1',
        'ap-south-1'
      ],
      createStack: false
    }
  },
  plugins: [
    'serverless-webpack',
    'serverless-create-global-dynamodb-table'
  ],
  provider: {
    name: 'aws',
    runtime: 'nodejs14.x',
    apiGateway: {
      minimumCompressionSize: 1024,
      shouldStartNameWithService: true,
    },
    environment: {
      AWS_NODEJS_CONNECTION_REUSE_ENABLED: '1',
    },
    lambdaHashingVersion: '20201221',
  },
  // import the function via paths
  functions: { getBooksNFacts },
  resources: {
    "Resources": {
       "booksNFactsTable": {
          "Type": "AWS::DynamoDB::Table",
          // "DeletionPolicy": "Retain", // Keeps around the DynamoDB resource when we redeploy/destroy
          "Properties": {
             "TableName": "booksNFactsTable",
             "AttributeDefinitions": [
                {
                   "AttributeName": "id",
                   "AttributeType": "S"
                }
             ],
             "KeySchema": [
                {
                   "AttributeName": "id",
                   "KeyType": "HASH"
                },
                {
                  
                }
             ],
             "ProvisionedThroughput": {
                "ReadCapacityUnits": 4,
                "WriteCapacityUnits": 4
             }
          }
       }
    }
 }
};

module.exports = serverlessConfiguration;
