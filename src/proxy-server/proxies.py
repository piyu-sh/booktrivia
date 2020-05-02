
import asyncio
from proxybroker import Broker


async def show(proxies, result):
    while True:
        proxy = await proxies.get()
        if proxy is None or proxy.is_working is False: break
        proto = 'http'
        proxyStr = proto+"://"+str(proxy.host)+":"+str(proxy.port)
        result.append(proxyStr)

async def fetch_proxies(numProxies):
    result = []
    result.clear()
    proxies = asyncio.Queue()
    broker = Broker(queue=proxies, verify_ssl=True)
    await asyncio.gather(broker.find(types=[('HTTP', 'High')], limit=numProxies, strict=True), show(proxies, result)) 
    return result
