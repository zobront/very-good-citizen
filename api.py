import requests
from datetime import datetime

class ForumAPI:
    BASE_URL = "https://gov.optimism.io"

    @staticmethod
    def fetch_latest_topics():
        url = f"{ForumAPI.BASE_URL}/latest.json?per_page=100"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching posts: {e}")
            return None

    @staticmethod
    def fetch_topic_content(topic_id):
        url = f"{ForumAPI.BASE_URL}/t/{topic_id}.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching post content: {e}")
            return None

    @staticmethod
    def post_comment(topic_id, comment):
        print("Printing comment to simulate forum post...")
        print(f"Suggested comment: {comment}")
        print("-" * 50)
