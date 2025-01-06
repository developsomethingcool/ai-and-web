# used to crawl the website
# starting URL and follow links
# import libraries
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from whoosh.writing import AsyncWriter
import os

# fetching the pagey by requests
# parsing bs
# storing links

prefix = 'https://vm009.rz.uos.de/crawl/'
start_url = prefix+"index.html"

if not os.path.exists("indexdir"):
    os.mkdir("indexdir")
    schema = Schema(
        url=ID(stored=True, unique=True),
        title=TEXT(stored=True),
        content=TEXT,
        snippet=TEXT(stored=True)
    )
    index = create_in("indexdir", schema)
else:
    index = open_dir("indexdir")

#agenda = [start_url]
#seen = set()
#index = {}

# functions

class Crawler:
    def __init__(self, start_url):
        # starting url
        self.start_url = start_url
        # initiating list of seen URLs
        self.seen = set()
        # initiating index
        #self.index = {}

    @staticmethod
    def valid_url(url):
        "Check if url is valid"
        if url.startswith("http") or url.startswith("https"):
            return url
    

# fetching a web pages
    def fetching_web_pages (self, url):

        "Fetching web pages, parsing html, extracting links"

        if url in self.seen:
            return
        else:
            self.seen.add(url)

        try: 
            r = requests.get(url)
            # check if status is OK
            if r.status_code == 200:
                print(r.headers)
                soup = BeautifulSoup(r.content, 'html.parser')

                # extracting links
                #for anchor in soup.find_all('a', href = True):
                #    url_complete = urljoin(url, anchor["href"])
                #    if url_complete.startswith(prefix):
                #        self.fetching_web_pages(url_complete)




                # index of content of web pages
                #text = soup.get_text()
                #self.index_page(url, text)


                # Extracting title and content
                title = soup.title.string if soup.title else "No Title"
                content = soup.get_text()
                snippet = content[:150]

                # Index the page
                self.index_page(url, title, content, snippet)

                # Extract and follow links
                for anchor in soup.find_all('a', href=True):
                    url_complete = urljoin(url, anchor["href"])
                    if url_complete.startswith(prefix):
                        self.fetching_web_pages(url_complete)

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")



    def index_page(self, url, title, content, snippet):
        "Make index of content of web pages"
        #text = text.lower()
        #pattern = r'\b\w+\b'
        # all words of the query should be lowercase and without special characters
        #words = re.findall(pattern, text)
        #for word in words:
        #    if word not in self.index:
        #        self.index[word] = []
        #    if url not in self.index[word]:
        #        self.index[word].append(url)

        try:
            with AsyncWriter(index) as writer:
                writer.add_document(
                    url=url,
                    title=title,
                    content=content.lower(),
                    snippet=snippet
                )
            print(f"Indexed: {url}")
        except Exception as e:
            print(f"Error indexing {url}: {e}")

    def search(self, query):
        "Searching through index with web pages for query"
        #query = query.lower()
        #splitted_query = query.split()
        #results = None
        #for words in splitted_query:
        #    if words in self.index:
        #        urls = set(self.index[words])
        #        if results is None:
        #            results = urls
        #        else:
        #            results = results.intersection(urls)
        
        #    else:
        #        return set()

        #if results:
        #    return results

        #else:
        #    return set()

        from whoosh.qparser import QueryParser

        results = []
        with index.searcher() as searcher:
            parser = QueryParser("content", index.schema)
            parsed_query = parser.parse(query)
            search_results = searcher.search(parsed_query, limit=10)
            for result in search_results:
                results.append({
                    "url": result["url"],
                    "title": result["title"],
                    "snippet": result["snippet"]
                })
        return results
    
# Main
if __name__ == "__main__":
    crawler = Crawler(start_url)
    crawler.fetching_web_pages(start_url)
    print("Crawling and indexing completed.")

    # Example search query
    query = "example search term"
    search_results = crawler.search(query)
    for result in search_results:
        print(f"URL: {result['url']}")
        print(f"Title: {result['title']}")
        print(f"Snippet: {result['snippet']}")
        print()

    # parsing html (bs)
    # extracting links
    # which fct first?


 