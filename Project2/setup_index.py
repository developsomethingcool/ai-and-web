from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in
import os

def setup_index(index_dir="indexdir"):
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
        schema = Schema(
            url=ID(stored=True, unique=True),
            content=TEXT
        )

        create_in(index_dir, schema)
        print(f"Index created in directory: {index_dir}")
    else:
        print(f"Index already exists in directory: {index_dir}")