from flask import Flask, render_template, request
import proxy
import requests
import cloudscraper
import asyncio
import random
from bs4 import BeautifulSoup
import googlesearch
import json
import lxml

app = Flask(__name__)

def search_r(query):
    answers = [{"google":[], "ecosia": [], "duckduckgo": []}]

    headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    }

    scraper = cloudscraper.create_scraper()

    ecosia_page_request = scraper.get("https://www.ecosia.org/search?method=index", headers=headers, params={"q": query})
    ecosia_page_content = ecosia_page_request.text
    

    page = requests.get(f'https://duckduckgo.com/html/?q={query}', headers=headers).text
    soup = BeautifulSoup(page, 'html.parser').find_all("a", class_="result__url", href=True)
    for link in soup:
        get_link = link['href']
        response = requests.get(get_link, headers=headers)
        soup = BeautifulSoup(response.text)
        metas = soup.find_all('meta')
        website_meta_description = []
        for m in metas:
            if m.get ('name') == 'description':
                desc = m.get('content')
                website_meta_description.append(desc)
        answers[0]['duckduckgo'].append({'link': get_link, 'description': website_meta_description})


    soup_ecosia = BeautifulSoup(ecosia_page_content, "html.parser")
    try:
        google_search = googlesearch.search(query,advanced=True, lang="EN", num_results=5)
        google_search = list(google_search)
        json_google = json.loads(json.dumps([{'description': result.description, 'url': result.url, 'title': result.title} for result in google_search]))
        answers[0]["google"].append(json_google)
    except:
        pass
    
    
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
    return search_r(query)

if __name__ == '__main__':
    app.run(host="0.0.0.0")

