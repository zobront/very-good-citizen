import json
from datetime import datetime, timezone

STARTING_TIMESTAMP = datetime.fromisoformat("2025-02-14T03:58:32.000+00:00")

def datetime_from_iso(iso_str):
    return datetime.fromisoformat(iso_str.replace('Z', '+00:00'))

def load_last_read_time():
    try:
        with open('last_read.json', 'r') as f:
            data = json.load(f)
            return datetime.fromisoformat(data['last_read'])
    except FileNotFoundError:
        return STARTING_TIMESTAMP

def save_last_read_time(timestamp):
    with open('last_read.json', 'w') as f:
        json.dump({'last_read': timestamp.isoformat()}, f)

def process_topic_content(topic_data):
    if not topic_data or 'post_stream' not in topic_data:
        return None

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
