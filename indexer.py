from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in
import os

# Define the schema
schema = Schema(
    url=ID(stored=True, unique=True),  # Store URL as a unique field
    title=TEXT(stored=True),           # Store and index the title
    content=TEXT,                      # Index the full content
    snippet=TEXT(stored=True)          # Store a snippet of the content
)

# Create an index directory if it doesn't exist
if not os.path.exists("indexdir"):
    os.mkdir("indexdir")

# Create the Whoosh index
index = create_in("indexdir", schema)
