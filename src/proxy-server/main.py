
import asyncio
from proxybroker import Broker

result = []

async def show(proxies):
    while True:
        proxy = await proxies.get()
        if proxy is None or proxy.is_working is False: break
        proto = 'http'
        proxyStr = proto+"://"+str(proxy.host)+":"+str(proxy.port)
        result.append(proxyStr)

async def fetch_proxies(numProxies):
    result.clear()
    proxies = asyncio.Queue()
    broker = Broker(queue=proxies, verify_ssl=True)
    await asyncio.gather(broker.find(types=[('HTTP', 'High')], limit=numProxies, strict=True), show(proxies)) 
    return result
