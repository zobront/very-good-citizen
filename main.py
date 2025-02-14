import os
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

from db import Database
from api import ForumAPI
from utils import (
    load_last_read_time,
    save_last_read_time,
    process_topic_content,
    datetime_from_iso,
    STARTING_TIMESTAMP
)

load_dotenv()

def main():
    db = Database()
    last_read = STARTING_TIMESTAMP

    data = ForumAPI.fetch_latest_topics()
    if not data:
        return

    current_time = datetime.now(timezone.utc)
    new_or_updated_posts = 0

    for topic in data['topic_list']['topics']:
        last_posted_at = datetime_from_iso(topic['last_posted_at'])

        if last_posted_at > last_read:
            topic_content = ForumAPI.fetch_topic_content(topic['id'])
            if topic_content:
                processed_content = process_topic_content(topic_content)
                if processed_content:
                    db.upsert_topic(processed_content)
                    new_or_updated_posts += 1

            time.sleep(1)

    save_last_read_time(current_time)
    print(f"Processed {new_or_updated_posts} new or updated posts")
    db.inspect_db()

if __name__ == "__main__":
    main()
