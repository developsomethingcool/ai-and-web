import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

class WebCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.index = {}

    def crawl(self, url):
        """Crawl the url and follow links on the same server"""
        if url in self.visited:
            return 
        
        self.visited.add(url)

        try:
            response = requests.get(url)
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
        words = re.findall(r'\w+', text.lower())
        for word in words:
            if word not in self.index:
                self.index[word] = []
            if url not in self.index[word]:
                self.index[word].append(url)


    def search(self, words):
        words = [word.lower() for word in words]  # Normalize to lowercase
        results = [set(self.index.get(word, [])) for word in words]
        return list(set.intersection(*results)) if results else []
    
if __name__ == "__main__":
    base_url = "https://vm009.rz.uos.de/crawl/index.html"
    crawler = WebCrawler(base_url)
    crawler.crawl(base_url)

    print("Search for 'example':", crawler.search(['platypus']))