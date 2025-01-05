from flask import Flask, request, g
from crawler import WebCrawler  # Import your Crawler class

app = Flask(__name__)

base_url = "https://vm009.rz.uos.de/crawl/index.html"
def get_crawler():
    if 'crawler' not in g:
        g.crawler = WebCrawler(base_url)
        g.crawler.crawl(base_url)
    return g.crawler

@app.route("/")
def start():
    # Form to enter search terms and optional base URL
    return """
        <form action='word_search' method='get'>
            <input name='rev' placeholder='Enter search term'></input>
            <button type='submit'>Search</button>
        </form>
    """

# @app.route("/")
# def start():
#     return "<form action='word_search' method='get'><input name='rev'></input></form>"

@app.route("/word_search")
def word_search():
    crawler = get_crawler()

    # Get the search term from the query string
    search_term = request.args.get('rev', '')  # Default to empty string if 'rev' is not provided
    
    # Perform the search
    search_results = crawler.search([search_term])

    # Format results as clickable links
    if not search_results:
        return f"<h1>No results found for '{search_term}'</h1>"

    results_html = "".join(f"<li><a href='{url}'>{url}</a></li>" for url in search_results)
    return f"<h1>Search results for '{search_term}':</h1><ul>{results_html}</ul>"


# @app.route("/word_search")
# def word_search():
#     base_url = "https://vm009.rz.uos.de/crawl/index.html"
#     crawler = WebCrawler(base_url)
#     crawler.crawl(base_url)

#     # Get the search term from the query string
#     search_term = request.args.get('rev', '')  # Default to empty string if 'rev' is not provided
    
#     # Perform the search
#     search_results = crawler.search([search_term])

#     results_html = "".join(f"<li><a href='{url}'>{url}</a></li>" for url in search_results)
#     return f"<h1>Search results for '{search_term}':</h1><ul>{results_html}</ul>"


    # Return the results as an HTML response
    #return f"<h1>Search results for '{search_term}':</h1><p>{search_results}</p>"
