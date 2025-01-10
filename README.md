# ai-and-web
# Easy Search - A Flask-based Web Crawler and Search Engine

This repository contains a simple Flask web application that crawls a given URL, indexes the pages using [Whoosh](https://pypi.org/project/Whoosh/), and provides a search interface to query the indexed content.

## Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Requirements](#requirements)  
4. [Installation](#installation)  
5. [Usage](#usage)  
6. [Project Structure](#project-structure)  
7. [Configuration](#configuration)  
8. [Customization](#customization)  
9. [Troubleshooting](#troubleshooting)  
10. [License](#license)

---

## Overview

**Easy Search** is a minimal search solution that crawls a specified URL (and related pages on the same domain) to build an index of page content. Once the crawl and indexing are complete, the application exposes a web interface (powered by Flask) for searching the indexed content.

### How It Works

1. **Crawling**: The web crawler starts at `base_url` and follows links on the same domain, extracting textual content from each page.  
2. **Indexing**: The crawler uses [Whoosh](https://pypi.org/project/Whoosh/) to create or update a search index stored in the `indexdir` directory.  
3. **Searching**: A Flask route (`/word_search`) allows users to enter a query, which is searched against the Whoosh index. Results are displayed with titles, snippets, and links.

---

## Features

- **Automated Crawling**: Recursively visits internal links starting from the given `base_url`.
- **Whoosh-based Indexing**: Stores page content for fast full-text search.
- **Simple Web Interface**: Users can input search queries and view results in an intuitive interface.
- **Teaser Extraction**: Shows a small excerpt (teaser) in the search results.
- **Beautiful UI**: Animated backgrounds, dynamic particles, cursor glow, and other styling enhancements using HTML, CSS, and JavaScript.

---

## Requirements

Make sure you have the following installed:

- **Python 3.7+**  
- **pip** (Python package manager)

Required Python libraries (install via `pip`):

- **requests**  
- **beautifulsoup4**  
- **whoosh**  
- **flask**

---

## Installation

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/developsomethingcool/ai-and-web/easy-search-flask.git
   cd easy-search-flask
