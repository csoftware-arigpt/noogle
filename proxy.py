import aiohttp
import asyncio
import requests

e = requests.get("https://sunny9577.github.io/proxy-scraper/proxies.json")
proxy_l = e.json()

def filter_proxies(proxies):
    filtered_proxies = []
    for proxy in proxies:
        if proxy["type"] == 'HTTP/HTTPS' and proxy["anonymity"] != 'Transparent':
            filtered_proxies.append(proxy)
    return filtered_proxies

filtered_proxies = filter_proxies(proxy_l)

async def validate_proxy(session, proxy, timeout=4):
    proxy_url = f'http://{proxy["ip"]}:{proxy["port"]}'
    try:
        async with session.get("http://ip-api.com/json", proxy=proxy_url, timeout=timeout) as response:
            if response.status == 200:
                return (proxy["ip"], proxy["port"])
    except:
        pass
    return None

async def get_proxy_list():
    async with aiohttp.ClientSession() as session:
        tasks = [validate_proxy(session, proxy) for proxy in filtered_proxies]
        validated_proxies = await asyncio.gather(*tasks)
        validated_proxies = list(filter(None, validated_proxies))
        return validated_proxies


