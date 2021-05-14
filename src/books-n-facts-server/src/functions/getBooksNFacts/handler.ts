import 'source-map-support/register';
import fetch from 'node-fetch';
import { stringify} from 'querystring';
// import { DynamoDB } from 'aws-sdk'

import type { ValidatedEventAPIGatewayProxyEvent } from '@libs/apiGateway';
import { formatJSONResponse } from '@libs/apiGateway';
import { middyfy } from '@libs/lambda';
import schema from './schema';
import config from '@config/index'
const hello: ValidatedEventAPIGatewayProxyEvent<typeof schema> = async (event) => {

  const { flipkartAPI: {keywordAPI}} = config;
  const { flipkartApiKey, flipkartAffiliateId } = process.env;
  // get keyword from query
  const { query, count } = event.body;

  // get books from flipkart

  const queryParams = {
    query: query,
    resultCount: count
  }
  const queryUrl = `${keywordAPI}?${stringify(queryParams)}`;
  console.log("🚀 ~ file: handler.ts ~ line 25 ~ consthello:ValidatedEventAPIGatewayProxyEvent<typeofschema>= ~ queryUrl", queryUrl)
  
  const response = await fetch(queryUrl, {
    headers: {
      'Fk-Affiliate-Id': flipkartAffiliateId,
      'Fk-Affiliate-Token': flipkartApiKey
    }
  });
  const flipkartBooks = await response.json();
  console.log("🚀 ~ file: handler.ts ~ line 34 ~ consthello:ValidatedEventAPIGatewayProxyEvent<typeofschema>= ~ flipkartBooks", flipkartBooks)
  // save books data in dynamodb if not present
  // return books data to ui
  return formatJSONResponse({
    message: `Hello , welcome to the exciting Serverless world!`,
    event,
  });
}

export const main = middyfy(hello);
