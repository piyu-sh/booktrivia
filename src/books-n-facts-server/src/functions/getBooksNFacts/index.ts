// import schema from './schema';
import { handlerPath } from '@libs/handlerResolver';
import type { AWS } from '@serverless/typescript';

export default {
  handler: `${handlerPath(__dirname)}/handler.main`,
  events: [
    {
      http: {
        method: 'get',
        path: 'getBooksNFacts',
        // request: {
        //   schema: {
        //     'application/json': schema
        //   },
        // }
      }
    }
  ],
  environment: {
    flipkartApiKey: "${ssm:/flipkartApiKey}",
    flipkartAffiliateId: "${ssm:/flipkartApiKey}"
  }
} as AWS['functions'][keyof AWS['functions']]
