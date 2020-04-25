from aiohttp import web
from main import fetch_proxies
import json

async def handle(request):
    numProxies = int(request.match_info.get('numProxies', '1'))
    proxies = await fetch_proxies(numProxies)
    return web.json_response(proxies)

app = web.Application()
app.add_routes([web.get('/', handle),
                web.get('/{numProxies}', handle)])

if __name__ == '__main__':
    web.run_app(app, port=3001)