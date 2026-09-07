def clean_interests(interests):
    """Clean interests and remove duplicates."""
    cleaned = []

    for interest in interests:
        value = interest.strip().lower()

        if value and value not in cleaned:
            cleaned.append(value)

    return cleaned


def matched_interests(story, interests):
    """Return interests that appear in the story title."""
    title = story.title.lower()
    interests = clean_interests(interests)

    matches = []

    for interest in interests:
        if interest in title:
            matches.append(interest)

    return matches


def relevance_score(story, interests):
    """Calculate keyword relevance from 0 to 100."""
    interests = clean_interests(interests)

    if not interests:
        return 0

    matches = matched_interests(story, interests)

    score = len(matches) / len(interests)
    score = score * 100

    return round(score)


def trending_score(story):
    """Calculate a simple time-aware trending score."""
    score = story.score / (story.hours_old + 2)
    score = round(score)

    if score > 100:
        score = 100

    return score


def combined_score(story, interests):
    """Combine relevance and trending scores."""
    relevance = relevance_score(story, interests)
    trending = trending_score(story)

    final_score = (relevance * 0.70) + (trending * 0.30)

    return round(final_score)


def rank_stories(stories, interests, category="All"):
    """Filter by category and rank highest score first."""
    filtered_stories = []

    for story in stories:
        if category == "All":
            filtered_stories.append(story)
        elif story.category() == category:
            filtered_stories.append(story)

    ranked_stories = sorted(
        filtered_stories,
        key=lambda story: combined_score(story, interests),
        reverse=True,
    )

    return ranked_stories
