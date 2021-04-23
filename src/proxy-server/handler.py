import json
from aiohttp import web
from proxies import fetch_proxies
import asyncio

proxiesObj = ""

async def getProxiesObject(numProxies):
    global proxiesObj
    proxiesObj = await fetch_proxies(numProxies)

def getOwnProxies(event, context):
    result = ''
    try:
        ifNumInParams = event['pathParameters'] is not None and event['pathParameters']['num'] is not None
        numProxies = int(event['pathParameters']['num']) if ifNumInParams is True else 1
        loop = asyncio.get_event_loop()
        loop.run_until_complete(getProxiesObject(numProxies))
        print('proxiesObj: ', proxiesObj)
        result =  {
            "statusCode": 200,
            "body": json.dumps(proxiesObj)
        }
        print('result: ', result)
    except Exception as e:
        print(e)
    return result