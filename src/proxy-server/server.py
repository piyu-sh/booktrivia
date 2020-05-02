from aiohttp import web
from proxies import fetch_proxies
import json

async def handle(request):
    result = ''
    try:
        numProxies = int(request.match_info.get('numProxies', '1'))
        proxies = await fetch_proxies(numProxies)
        result = web.json_response(proxies)
    except Exception as e:
        print(e)
    return result

app = web.Application()
app.add_routes([web.get('/proxy', handle),
                web.get('/proxy/{numProxies}', handle)])

if __name__ == '__main__':
    web.run_app(app, port=3001)