from flask import Flask, request, g
from crawler import WebCrawler  # Import your Crawler class
from whoosh.qparser import QueryParser

app = Flask(__name__)

#base_url = "https://vm009.rz.uos.de/crawl/index.html"
base_url = "https://realpython.com/"
index_dir = "indexdir"


def get_crawler():
    if 'crawler' not in g:
        g.crawler = WebCrawler(base_url, index_dir )
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
    
    if not search_term.strip():
        return """
            <h1>No search term provided.</h1>
            <a href='/'>Search again</a>
        """

    # Perform the search using Whoosh
    with crawler.ix.searcher() as searcher:
        query_parser = QueryParser("content", schema=crawler.ix.schema)
        query = query_parser.parse(search_term)
        results = searcher.search(query)
        
        if not results:
            return f"""
                <h1>No results found for '{search_term}'</h1>
                <a href='/'>Search again</a>
            """

        # Format results as clickable links
        results_html = "".join(
        f"<li>"
        f"<a href='{hit['url']}'>{hit['title']}</a><br>"
        f"<small>{hit['teaser']}</small>"
        f"</li>"
        for hit in results
        )

        return f"""
            <h1>Search results for '{search_term}':</h1>
            <ul>{results_html}</ul>
            <a href='/'>Search again</a>
        """


