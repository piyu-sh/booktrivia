// import schema from './schema';
import { handlerPath } from '@libs/handlerResolver';
import type { AWS } from '@serverless/typescript';
import schema from './schema';

export default {
  handler: `${handlerPath(__dirname)}/handler.main`,
  events: [
    {
      http: {
        method: 'post',
        path: 'getBooksNFacts',
        request: {
          schema: {
            'application/json': schema
          },
        },
        cors: true 
      }
    }
  ],
  environment: {
    flipkartApiKey: "${ssm:/flipkartApiKey}",
    flipkartAffiliateId: "${ssm:/flipkartAffiliateId}"
  }
} as AWS['functions'][keyof AWS['functions']]
