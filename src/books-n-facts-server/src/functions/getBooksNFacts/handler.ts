import 'source-map-support/register';

// import { DynamoDB } from 'aws-sdk'

import type { ValidatedEventAPIGatewayProxyEvent } from '@libs/apiGateway';
import { formatJSONResponse } from '@libs/apiGateway';
import { middyfy } from '@libs/lambda';

import schema from './schema';

const hello: ValidatedEventAPIGatewayProxyEvent<typeof schema> = async (event) => {

  // get keyword from query
    // const { query, count } = event.body;
  
  // get books from flipkart
  // save books data in dynamodb if not present
  // return books data to ui
  return formatJSONResponse({
    message: `Hello , welcome to the exciting Serverless world! flipkartApiKey: ${process.env.flipkartApiKey} flipkartAffiliateId: ${process.env.flipkartAffiliateId}`,
    event,
  });
}

export const main = middyfy(hello);
