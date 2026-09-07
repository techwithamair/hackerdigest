import json
import urllib.error
import urllib.request

from models import Story


class HackerNewsAPI:
    """Handles requests to the Hacker News Firebase API."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self, timeout=10):
        self.timeout = timeout

    def _get_json(self, url):
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "HackerDigest/1.0"},
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                data = response.read().decode("utf-8")
                return json.loads(data)

        except (
            urllib.error.URLError,
            TimeoutError,
            json.JSONDecodeError,
        ) as error:
            print(f"Hacker News API request failed: {error}")
            return None

    def fetch_top_ids(self):
        url = f"{self.BASE_URL}/topstories.json"
        result = self._get_json(url)

        if isinstance(result, list):
            return result

        return []

    def fetch_story(self, story_id):
        url = f"{self.BASE_URL}/item/{story_id}.json"
        result = self._get_json(url)

        if isinstance(result, dict):
            return result

        return None

    def fetch_top_stories(self, limit=50):
        story_ids = self.fetch_top_ids()
        story_ids = story_ids[:limit]

        stories = []

        for story_id in story_ids:
            raw_story = self.fetch_story(story_id)

            if not raw_story:
                continue

            if raw_story.get("type") != "story":
                continue

            if not raw_story.get("title"):
                continue

            story = Story(raw_story)
            stories.append(story)

        return stories
