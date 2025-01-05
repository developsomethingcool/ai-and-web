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
        <h1>Welcome to the Search App</h1>
        <p>Enter a term below to search the web index:</p>
        <form action='word_search' method='get'>
            <input name='q' placeholder='Enter search term'></input>
            <button type='submit'>Search</button>
        </form>
    """

@app.route("/word_search")
def word_search():
    crawler = get_crawler()

    # Get the search term from the query string
    search_term = request.args.get('q', '') 
    
    # Perform the search
    search_results = crawler.search([search_term])

    if not search_results:
        return f"""
            <h1>No results found for '{search_term}'</h1>
            <a href='/'>Search again</a>
        """

    results_html = "".join(f"<li><a href='{url}'>{url}</a></li>" for url in search_results)
    return f"""
        <h1>Search results for '{search_term}':</h1>
        <ul>{results_html}</ul>
        <a href='/'>Search again</a>
    """


