# used for flask web application
# define roots
# write functions to ... user actions
# handle requests
# render templates

# brings together the 


# import Flask to create web application
# import render_template to render HTML files
# import request to manage input
from flask import Flask, render_template, request
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

# importing the class Crawler from the other file
#from crawl import Crawler

app = Flask(__name__)
index = open_dir("indexdir")

#prefix = "https://vm009.rz.uos.de/crawl/"
# point where crawler starts: the index page
#start_url = prefix + "index.html"
#initialize the Crawler with the starting point
#crawler = Crawler(start_url)
# taking/fetching the web pages starting from the index page
#crawler.fetching_web_pages(start_url)

# setting the route from the starting point
@app.route('/')
def home():
    return render_template("start.html")

# defining which route to take
@app.route('/search', methods=['GET'])
def search():
    " Searching the web pages from the starting point"
    # getting the search query
    query = request.args.get('q', '')
    # find matching URLs 
    #results = crawler.search(query)
    results = []

    if query:
        with index.searcher() as searcher:
            parser = QueryParser("content", index.schema)
            parsed_query = parser.parse(query)
            search_results = searcher.search(parsed_query, limit=10)  # Limit to 10 results
            for result in search_results:
                results.append({
                    "url": result["url"],
                    "title": result["title"],
                    "snippet": result["snippet"]
                })


    # displaying the findings on the results page
    return render_template('results.html', query=query, results=results)

if __name__ == '__main__':
    app.run(debug=True)

