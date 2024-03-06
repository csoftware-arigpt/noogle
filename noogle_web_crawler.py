import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urlparse, urljoin
import threading
import queue
import logging
from xata.client import XataClient

xata = XataClient(db_url="", api_key="")

page_info = list()
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"
}

logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

def process_link(link_queue):
    while not link_queue.empty():
        link = link_queue.get()
        try:
            r = requests.get(link, headers=headers)
            r.raise_for_status()  # raise exception for 4xx status codes
        except requests.exceptions.HTTPError as errh:
            logger.error("HTTP Error:", errh)
            title = "No Text"
            text = "No Info"
        except requests.exceptions.ConnectionError as errc:
            logger.error("Error Connecting:", errc)
            return
        except requests.exceptions.Timeout as errt:
            logger.error("Timeout Error:", errt)
            return
        except requests.exceptions.RequestException as err:
            logger.error("Something Else:", err)
            return
        else:
            data = r.text
            soup = BeautifulSoup(data, "html.parser")
            try:
                title = soup.title.string
            except:
                title = "Title not detected"
            text = ' '.join(soup.stripped_strings)
            text = ' '.join(text.split()[:100])
            links_page = [a['href'] for a in soup.find_all('a', href=True) if not a['href'].startswith("#")]
            links_page = [urljoin(link, l) for l in links_page]

        page_info.append({"url": link, "title": title, "desc": text})
        data = xata.records().insert("search", {
                "url": link,
                "name": title,
                "description": text
                })
        if 'links_page' in locals():
                for link in links_page:
                    link_queue.put(link)

initial_links = ["https://www.aixploria.com/en/ultimate-list-ai/",
                 "https://stackoverflow.com",
                 "https://en.wikipedia.org/",
                 "https://ru.wikipedia.org/",
                 "https://github.com/",
                 "https://en.wikipedia.org/wiki/Linux",
                 "https://en.wikipedia.org/wiki/List_of_Google_products",
                 "https://www.britannica.com/",
                 "https://ru.wikipedia.org/wiki/%D0%9F%D0%BE%D1%80%D1%82%D0%B0%D0%BB:%D0%9A%D1%83%D0%BB%D0%B8%D0%BD%D0%B0%D1%80%D0%B8%D1%8F",
                 "https://en.wikipedia.org/wiki/Category:Cooking_websites",
                 "https://github.com/trending"]

threads = []

for initial_link in initial_links:
    link_queue = queue.Queue()
    link_queue.put(initial_link)
    thread = threading.Thread(target=process_link, args=(link_queue,))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()
