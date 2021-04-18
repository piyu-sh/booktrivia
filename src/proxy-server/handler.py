import json
from aiohttp import web
from proxies import fetch_proxies


async def hello(event, context):
    result = ''
    try:
        ifNumInParams = event['pathParameters'] is not None and event['pathParameters']['num'] is not None
        numProxies = int(event['pathParameters']['num']) if ifNumInParams is True else 1
        proxies = await fetch_proxies(numProxies)
        result = web.json_response(proxies)
    except Exception as e:
        print(e)
    return result

