from flask import Flask, request, g, render_template
from crawler import WebCrawler  # Import your Crawler class
from whoosh.qparser import QueryParser

app = Flask(__name__)

base_url = "https://vm009.rz.uos.de/crawl/index.html"
#base_url = "https://realpython.com/"
index_dir = "indexdir"


def get_crawler():
    """Initialize and cache the WebCrawler instance in Flask's application context."""
    if 'crawler' not in g:
        g.crawler = WebCrawler(base_url, index_dir )
        g.crawler.crawl(base_url) # Perform crawling
    return g.crawler

@app.route("/")
def start():
    """Render the search form."""
    return render_template("search_form.html")

@app.route("/word_search")
def word_search():
    """Perform the search and render the results."""
    crawler = get_crawler()

    # Get the search term from the query string
    search_term = request.args.get('q', '').strip()  # Get and clean the search term    
    
    if not search_term:
        # Render the search form with an error message
        return render_template("search_form.html", error="Please enter a search term.")

    results = []

    try:
        with crawler.ix.searcher() as searcher:
            query_parser = QueryParser("content", schema=crawler.ix.schema)
            query = query_parser.parse(search_term)
            hits = searcher.search(query, limit=10)
            results = [
                {
                    "url": hit["url"],
                    "title": hit["title"],
                    "content": hit.get("teaser", "No description available"),
                }
                for hit in hits
            ]
    except Exception as e:
        # Log the error (optional)
        print(f"Error during search: {e}")
        # Render the search form with a generic error message
        return render_template("search_form.html", error="An error occurred during the search.")

    # If no results are found, show a message in the results page
    if not results:
        return render_template("search_results.html", query=search_term, results=[])

    # Render the search results page
    return render_template("search_results.html", query=search_term, results=results)

@app.teardown_appcontext
def teardown_crawler(exxception):
    """Clean up the WebCrawler instance when the application context ends."""
    crawler = g.pop("crawler", None)
    if crawler is not None:
        crawler.finalize_index()

if __name__ == "__main__":
    app.run(debug=True)