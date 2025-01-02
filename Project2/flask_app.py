from flask import Flask, request
from crawler import WebCrawler  # Import your Crawler class

app = Flask(__name__)

@app.route("/")
def start():
    return "<form action='reversed' method='get'><input name='rev'></input></form>"

@app.route("/reversed")
def reversed():
    base_url = "https://vm009.rz.uos.de/crawl/index.html"
    crawler = WebCrawler(base_url)
    crawler.crawl(base_url)

    # Get the search term from the query string
    search_term = request.args.get('rev', '')  # Default to empty string if 'rev' is not provided
    
    # Perform the search
    search_results = crawler.search([search_term])


    # Return the results as an HTML response
    return f"<h1>Search results for '{search_term}':</h1><p>{search_results}</p>"
