import os
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from urllib.robotparser import RobotFileParser

class WhooshCrawler:
    def __init__(self, start_url, index_dir="indexdir", delay=2):
        self.start_url = start_url
        self.visited = set()
        self.delay = delay  # Delay in seconds between requests
        self.robots_parser = RobotFileParser()
        self.init_robots_parser()

        # Define schema for Whoosh index
        schema = Schema(
            url=ID(stored=True, unique=True),
            title=TEXT(stored=True),
            content=TEXT(stored=True)
        )
        os.makedirs(index_dir, exist_ok=True)
        self.index = create_in(index_dir, schema)
        self.writer = self.index.writer()

    def init_robots_parser(self):
        """Initialize the robots.txt parser."""
        robots_url = urljoin(self.start_url, "/robots.txt")
        try:
            self.robots_parser.set_url(robots_url)
            self.robots_parser.read()
        except Exception as e:
            print(f"Error reading robots.txt: {e}")
            self.robots_parser = None  # Fallback in case of errors

    def is_allowed_by_robots(self, url):
        """Check if the URL is allowed by robots.txt."""
        if self.robots_parser:
            return self.robots_parser.can_fetch("*", url)  # Assume "*" as the user agent
        return True  # Allow crawling if robots.txt is not accessible

    def crawl(self, url=None):
        if url is None:
            url = self.start_url

        if url in self.visited:
            return
        self.visited.add(url)

        if not self.is_allowed_by_robots(url):
            print(f"Skipping {url}: Disallowed by robots.txt")
            return

        print(f"Crawling: {url}")

        try:
            # Rate-limiting: Wait before making a new request
            time.sleep(self.delay)

            # Fetch the page
            response = requests.get(url, timeout=10)  # Add timeout
            if response.status_code != 200:
                print(f"Skipping {url}: Received status code {response.status_code}")
                return

            if 'text/html' not in response.headers.get('Content-Type', ''):
                print(f"Skipping {url}: Not an HTML page")
                return

            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract title and text content
            title = soup.title.string if soup.title else url
            content = soup.get_text(separator=" ", strip=True)

            # Add the document to the Whoosh index
            self.writer.add_document(url=url, title=title, content=content)

            # Find and follow internal links
            for link in soup.find_all('a', href=True):
                next_url = urljoin(url, link['href'])
                if self.is_same_domain(next_url):
                    self.crawl(next_url)

        except requests.exceptions.Timeout:
            print(f"Timeout occurred while crawling {url}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to crawl {url}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while crawling {url}: {e}")

    def is_same_domain(self, url):
        """Check if the URL is on the same domain as the start URL."""
        start_domain = urlparse(self.start_url).netloc
        next_domain = urlparse(url).netloc
        return start_domain == next_domain


    def finalize_index(self):
        self.writer.commit()

if __name__ == "__main__":
    # Define the start URL
    start_url = "https://vm009.rz.uos.de/crawl/index.html"

    # Create and run the crawler
    crawler = WhooshCrawler(start_url, delay=2)  # Set delay to 2 seconds
    crawler.crawl()
    crawler.finalize_index()
    print("Indexing complete.")

