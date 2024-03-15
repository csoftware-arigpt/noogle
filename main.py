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

    headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    }

    scraper = cloudscraper.create_scraper()

    ecosia_page_request = scraper.get("https://www.ecosia.org/search?method=index", headers=headers, params={"q": query})
    ecosia_page_content = ecosia_page_request.text
    
    duckduckgo_page_request = requests.get("https://api.duckduckgo.com/", headers=headers, params={"q": query, "format": "json"})
    duckduckgo_page_content = duckduckgo_page_request.text
    duckduckgo_page_content = json.loads(duckduckgo_page_content)

    soup_ecosia = BeautifulSoup(ecosia_page_content, "html.parser")
    try:
        google_search = googlesearch.search(query,advanced=True, lang="EN", num_results=5)
        google_search = list(google_search)
        json_google = json.loads(json.dumps([{'description': result.description, 'url': result.url, 'title': result.title} for result in google_search]))
        answers[0]["google"].append(json_google)
    except:
        pass
    for topic in duckduckgo_page_content["RelatedTopics"]:
        if "FirstURL" in topic and "Result" in topic and "Text" in topic:
            answers[0]['duckduckgo'].append({
                "title": topic["Result"].split(">")[1].split("<")[0],
                "url": topic["FirstURL"],
                "description": topic["Text"]
                })
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

