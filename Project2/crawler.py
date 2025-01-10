import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import os
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser
from whoosh.writing import AsyncWriter
import time


class WebCrawler:
    def __init__(self, base_url, index_dir="indexdir"):
        self.base_url = base_url
        self.visited = set()
        self.index_dir = index_dir

        # Create or open the Whoosh index
        if not os.path.exists(self.index_dir):
            os.mkdir(self.index_dir)
            schema = Schema(
                url=ID(stored=True, unique=True),  # Unique identifier for each document
                title=TEXT(stored=True),
                teaser=TEXT(stored=True),
                content=TEXT  # Full-text searchable content
            )
            self.ix = create_in(self.index_dir, schema)
        else:
            self.ix = open_dir(self.index_dir)

    def crawl(self, url):
        """Crawl the url and follow links on the same server"""
        if url in self.visited:
            return 
        
        self.visited.add(url)

        try:
            response = requests.get(url)

            time.sleep(1)

            # Skip non-HTML responses
            if 'text/html' not in response.headers.get("Content-Type", ''):
                return
            
            soup = BeautifulSoup(response.text, "html.parser")
            self.index_page(url, soup.text)

            # Find and normalize links
            for link in soup.find_all("a", href=True):
                full_url = urljoin(url, link['href'])
                if self.is_same_server(full_url):
                    self.crawl(full_url)

        except requests.RequestException as e:
            print(f"Error crawling {url}: {e}")

    def is_same_server(self, url):
        """Check if the URL belongs to the same server."""
        return urlparse(url).netloc == urlparse(self.base_url).netloc
    
    def index_page(self, url, text):
        """Index a page using Whoosh."""
        soup = BeautifulSoup(text, "html.parser")
        title = soup.title.string if soup.title else "No Title"
        #print("title:", title)
        body_text = soup.get_text(separator=' ', strip=True)
        #print("body text:", body_text)
        teaser = text[:200]
        #print("teaser:", teaser)

        writer = AsyncWriter(self.ix)
        writer.update_document(url=url, title=title, teaser=teaser, content=body_text)
        writer.commit()


    def search(self, words):
        """Search the Whoosh index."""
        with self.ix.searcher() as searcher:
            query_parser = QueryParser("content", schema=self.ix.schema)
            query = query_parser.parse(" ".join(words))
            results = searcher.search(query)
            return [hit["url"] for hit in results]
        
    def finalize_index(self):
        """Finalize the Whoosh index, committing all changes."""
        try:
            self.ix.writer().commit()
            print("Index finalized and commited successfully")
        except Exception as e:
            print(f"Error finalizing index: {e}")

        
if __name__ == "__main__":
    base_url = "https://vm009.rz.uos.de/crawl/index.html"
    crawler = WebCrawler(base_url)
    crawler.crawl(base_url)

    print("Search for 'example':", crawler.search(['platypus']))