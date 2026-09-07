import time


class Story:
    """Represents one Hacker News story."""

    def __init__(self, raw_data):
        self.id = raw_data["id"]
        self.title = raw_data["title"]
        self.score = raw_data.get("score", 0)
        self.comments = raw_data.get("descendants", 0)
        self.author = raw_data.get("by", "unknown")
        self.posted_time = raw_data.get("time", 0)

        self.hours_old = self._calculate_hours_old()

        if raw_data.get("url"):
            self.url = raw_data["url"]
        else:
            self.url = self._hn_discussion_url()

    def _calculate_hours_old(self):
        if self.posted_time == 0:
            return 0

        age_in_seconds = time.time() - self.posted_time

        if age_in_seconds < 0:
            age_in_seconds = 0

        return age_in_seconds / 3600

    def _hn_discussion_url(self):
        return f"https://news.ycombinator.com/item?id={self.id}"

    def is_show_hn(self):
        return self.title.lower().startswith("show hn:")

    def is_ask_hn(self):
        return self.title.lower().startswith("ask hn:")

    def is_job(self):
        title = self.title.lower()
        job_words = ["who is hiring", "hiring", "job", "jobs"]

        for word in job_words:
            if word in title:
                return True

        return False

    def category(self):
        if self.is_show_hn():
            return "Show HN"

        if self.is_ask_hn():
            return "Ask HN"

        if self.is_job():
            return "Jobs"

        return "Story"

    def discussion_url(self):
        return self._hn_discussion_url()

    def __repr__(self):
        return f"Story(title={self.title!r}, score={self.score})"
