import os
import time

from datetime import datetime, timezone
import requests
import json

from openai import OpenAI
from pydantic import BaseModel
import chromadb
from chromadb.utils import embedding_functions

from dotenv import load_dotenv
load_dotenv()

STARTING_TIMESTAMP = datetime.fromisoformat("2025-02-14T03:58:32.000+00:00")

# Initialize the OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORGANIZATION_ID"),
    project=os.getenv("OPENAI_PROJECT_ID")
)

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)
collection = chroma_client.get_or_create_collection(
    name="optimism_posts",
    embedding_function=openai_ef
)

def fetch_latest_topic():
    url = "https://gov.optimism.io/latest.json?per_page=40"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching posts: {e}")
        return None

def fetch_topic_content(topic_id):
    url = f"https://gov.optimism.io/t/{topic_id}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching post content: {e}")
        return None

def datetime_from_iso(iso_str):
    return datetime.fromisoformat(iso_str.replace('Z', '+00:00'))

def load_last_read_time():
    try:
        with open('last_read.json', 'r') as f:
            data = json.load(f)
            return datetime.fromisoformat(data['last_read'])
    except FileNotFoundError:
        # If no file exists, return a very old date
        return STARTING_TIMESTAMP

def save_last_read_time(timestamp):
    with open('last_read.json', 'w') as f:
        json.dump({'last_read': timestamp.isoformat()}, f)


def process_topic_content(topic_data):
    if not topic_data or 'post_stream' not in topic_data:
        return None

    # Combine title with all post contents
    title = topic_data.get('title', '')
    posts = topic_data['post_stream']['posts']

    full_content = f"Title: {title}\n\n"
    for post in posts:
        full_content += f"Post by {post.get('username', 'unknown')}:\n{post.get('cooked', '')}\n\n"

    return {
        'id': str(topic_data['id']),
        'title': title,
        'content': full_content,
        'url': f"https://gov.optimism.io/t/{topic_data['id']}",
        'last_updated': datetime_from_iso(topic_data['last_posted_at']) if topic_data.get('last_posted_at') else None
    }

def update_vector_db(processed_topic_data):
    # Update or insert the post in ChromaDB
    collection.upsert(
        ids=[processed_topic_data['id']],
        documents=[processed_topic_data['content']],
        metadatas=[{
            'title': processed_topic_data['title'],
            'url': processed_topic_data['url'],
            'last_updated': processed_topic_data['last_updated'].isoformat() if processed_topic_data['last_updated'] else None
        }]
    )

def inspect_db():
    # Get all entries
    results = collection.get()
    print(f"Total documents in DB: {len(results['ids'])}")


def main():
    last_read = load_last_read_time()

    data = fetch_latest_topic()
    if not data:
        return

    current_time = datetime.now(timezone.utc)
    new_or_updated_posts = 0

    for topic in data['topic_list']['topics']:
        last_posted_at = datetime_from_iso(topic['last_posted_at'])

        # Check if this post is new or has been updated since our last read
        if last_posted_at > last_read:
            # Fetch full post content
            topic_content = fetch_topic_content(topic['id'])
            if topic_content:
                processed_content = process_topic_content(topic_content)
                if processed_content:
                    update_vector_db(processed_content)
                    new_or_updated_posts += 1

            # Add a small delay to be nice to the server
            time.sleep(1)

    # Update the last read time
    save_last_read_time(current_time)
    print(f"Processed {new_or_updated_posts} new or updated posts")

if __name__ == "__main__":
    main()
