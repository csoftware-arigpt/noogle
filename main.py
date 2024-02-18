from flask import Flask, render_template, request
import proxy
import requests
import cloudscraper
import asyncio
import random
from bs4 import BeautifulSoup
import googlesearch
import json

app = Flask(__name__)

def search_r(query):
    answers = [{"google":[], "ecosia": [], "duckduckgo": []}]

    proxy_list_parsing = asyncio.run(proxy.get_proxy_list())
    proxy_random = random.randint(0, len(proxy_list_parsing))
    proxy_list = {"http": f'http://{proxy_list_parsing[proxy_random][0]}:{proxy_list_parsing[proxy_random][1]}', "https": f'http://{proxy_list_parsing[proxy_random][0]}:{proxy_list_parsing[proxy_random][1]}'}
    headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    }

    scraper = cloudscraper.create_scraper()

    ecosia_page_request = scraper.get("https://www.ecosia.org/search?method=index", headers=headers, params={"q": query})
    ecosia_page_content = ecosia_page_request.text
    
    duckduckgo_page_request = requests.get("https://html.duckduckgo.com/html", headers=headers, data={"q": query})
    duckduckgo_page_content = duckduckgo_page_request.text
    
    
    soup_ddg = BeautifulSoup(duckduckgo_page_content, "html.parser")
    soup_ecosia = BeautifulSoup(ecosia_page_content, "html.parser")

    google_search = googlesearch.search(query,advanced=True, lang="EN")
    google_search = list(google_search)
    json_google = json.loads(json.dumps([{'description': result.description, 'url': result.url, 'title': result.title} for result in google_search]))
    answers[0]["google"].append(json_google)
    for el in soup_ddg.select(".result"):
        answers[0]["duckduckgo"].append(
                {"title": el.select_one(".result__a").text,
                "url": el.select_one(".result__snippet")['href'],
                "description": el.select_one(".result__snippet").text}
                )
    for el in soup_ecosia.select(".result__body"):
        answers[0]["ecosia"].append({
                "title": el.select_one('.result-title__heading').text,
                "url": el.select_one(".result__link")["href"],
                "description": el.select_one(".web-result__description").text}
                )
    return answers


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search_e():
    query = request.args.get('query')
    return search_r(query_
if __name__ == '__main__':
    app.run(host="0.0.0.0")

