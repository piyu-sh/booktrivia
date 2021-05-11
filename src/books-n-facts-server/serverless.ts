import type { AWS } from '@serverless/typescript';

import getBooksNFacts from '@functions/getBooksNFacts';
import { booksNFactsTable } from '@resources/booksNFactsTable';
const serverlessConfiguration: AWS = {
  service: 'books-n-facts-server',
  app: 'books-n-facts-server',
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
        'ap-south-1'
      ],
      createStack: false
    },
    capacities: [
      {
         "table": "booksNFactsTable",
         "read": {
            "minimum": 2,
            "maximum": 10,
            "usage": 0.75
         },
         "write": {
            "minimum": 2,
            "maximum": 10,
            "usage": 0.75
         }
      }
   ]
  },
  plugins: [
    'serverless-webpack',
    'serverless-create-global-dynamodb-table',
    'serverless-dynamodb-autoscaling'
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
      booksNFactsTable
    }
 }
};

module.exports = serverlessConfiguration;
