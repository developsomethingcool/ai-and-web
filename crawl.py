# used to crawl the website
# starting URL and follow links


# import libraries

# fetching web pages
import requests
# parsing html
from bs4 import BeautifulSoup
# regular expressions library
import re
# operating system interaction
import os
# add base URL with relative URL
from urllib.parse import urljoin
# defining index schema, creating an index and adding pages
from whoosh.fields import Schema, TEXT, ID
from whoosh.writing import AsyncWriter
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser


# fetching the page by requests
# parsing bs
# storing links

# URL where crawler will start
prefix = 'https://vm009.rz.uos.de/crawl/'
start_url = prefix+"index.html"

# index directory
index_dir = "indexdir"

if not os.path.exists("indexdir"):
    os.mkdir("indexdir")
    schema = Schema(
        url = ID(stored = True, unique = True),
        title = TEXT(stored = True),
        content = TEXT,
        excerpt = TEXT(stored = True)
    )
    index = create_in("indexdir", schema)
else:
    index = open_dir("indexdir")

# without whoosh:
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

    
    def valid_url(self, url):
        "Check if url is valid"
        if url.startswith("http") or url.startswith("https"):
            return url
    

# fetching a web pages
    def fetching_web_pages(self, url, depth=0, max_depth=5):
        if depth > max_depth:
            print(f"Reached max depth for {url}")
            return

        # if the URL was already seen, don't add it
        if url in self.seen:
            return
        
        # add the URL to the seen list
        self.seen.add(url)
        print(f"Fetching: {url}")

        try:
            r = requests.get(url)
            if r.status_code == 200:
                print(f"Successfully fetched: {url}")

                soup = BeautifulSoup(r.content, "html.parser")

                # extract the title and content for indexing
                title = soup.title.string if soup.title else "Website has no title."
                content = soup.get_text()
                excerpt = content[:150]

                # index the page
                self.index_page(url, title, content, excerpt)

                # fetch and process links
                for anchor in soup.find_all("a", href=True):
                    url_complete = urljoin(url, anchor["href"])
                    if self.valid_url(url_complete):
                        self.fetching_web_pages(url_complete, depth + 1, max_depth)

        except requests.RequestException as e:
            print(f"There was an error fetching {url}: {e}")

                # extracting links
                #for anchor in soup.find_all('a', href = True):
                #    url_complete = urljoin(url, anchor["href"])
                #    if url_complete.startswith(prefix):
                #        self.fetching_web_pages(url_complete)




                # index of content of web pages
                #text = soup.get_text()
                #self.index_page(url, text)


                # take title and text of the web page
                
                # excerpt of the web page for first 150th characters saved
               

                # index the web page
               

                # fetch the links that are valid URLs from the web pages







    def index_page(self, url, title, content, excerpt):
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
                    excerpt=excerpt
                )
                print(f"Indexed: {url} - Title: {title}")
        except Exception as e:
            print(f"There was an error indexing {url}: {e}")

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

        results = []
        with index.searcher() as searcher:
            parser = QueryParser("content", index.schema)
            parsed_query = parser.parse(query.lower())
            search_results = searcher.search(parsed_query, limit = 10)
            for result in search_results:
                results.append({
                    "url": result["url"],
                    "title": result["title"],
                    "excerpt": result["excerpt"]
                })
        return results
    
# Main
if __name__ == "__main__":
    crawler = Crawler(start_url)
    print("Crawling and indexing started...")
    crawler.fetching_web_pages(start_url)
    print("Crawling and indexing completed.")

    # After the crawling process is finished, check the indexed documents
    print("\nChecking indexed documents:")
    with index.searcher() as searcher:
        num_docs = searcher.doc_count()
        print(f"Total indexed documents: {num_docs}")
        for doc_num in range(num_docs):
            stored_fields = searcher.stored_fields(doc_num)
            print(f"Document {doc_num}: URL: {stored_fields['url']}, Title: {stored_fields['title']}, Excerpt: {stored_fields['excerpt']}")

    # parsing html (bs)
    # extracting links
    # which fct first?

    # Example search query
    #query = "example search term"
    #search_results = crawler.search(query)
    #for result in search_results:
    #    print(f"URL: {result['url']}")
    #    print(f"Title: {result['title']}")
    #    print(f"Excerpt: {result['excerpt']}")
    #    print()



#ix = open_dir("indexdir")

#with ix.searcher() as searcher:
#    for doc in searcher.all_stored_fields():
#        print(f"URL: {doc['url']}, Title: {doc['title']}, Excerpt: {doc['excerpt']}")

    # Example search
    example_query = "the"
    print(f"\nSearching for: {example_query}")
    search_results = crawler.search(example_query)
    for result in search_results:
        print(f"URL: {result['url']}")
        print(f"Title: {result['title']}")
        print(f"Excerpt: {result['excerpt']}")
        print()

 