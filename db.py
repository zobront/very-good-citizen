import os
import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime

class Database:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )
        self.collection = self.client.get_or_create_collection(
            name="optimism_posts",
            embedding_function=self.ef
        )

    def upsert_topic(self, processed_topic_data):
        self.collection.upsert(
            ids=[processed_topic_data['id']],
            documents=[processed_topic_data['content']],
            metadatas=[{
                'title': processed_topic_data['title'],
                'url': processed_topic_data['url'],
                'last_updated': processed_topic_data['last_updated'].isoformat() if processed_topic_data['last_updated'] else None
            }]
        )

    def inspect_db(self):
        results = self.collection.get()
        print(f"Total documents in DB: {len(results['ids'])}")
        print("\nStored Documents:")
        print("================")

        for id, metadata in zip(results['ids'], results['metadatas']):
            print(f"\nID: {id}")
            print(f"Title: {metadata['title']}")
            print(f"URL: {metadata['url']}")
            print(f"Last Updated: {metadata['last_updated']}")
            print("-" * 50)

    def get_document(self, doc_id):
        return self.collection.get(ids=[doc_id])
