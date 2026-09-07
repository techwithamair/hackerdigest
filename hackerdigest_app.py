import html
import time
from urllib.parse import urlparse

import streamlit as st

from hn_api import HackerNewsAPI
from scorer import (
    combined_score,
    matched_interests,
    rank_stories,
    relevance_score,
    trending_score,
)


# --------------------------------------------------
# Page setup
# --------------------------------------------------

st.set_page_config(
    page_title="HackerDigest",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# Presets and options
# --------------------------------------------------

PRESETS = {
    "AI & Machine Learning": (
        "AI, machine learning, LLM, agents, model, inference, "
        "python, pytorch, GPU, neural"
    ),
    "Web & Full-Stack": (
        "typescript, javascript, react, web, frontend, backend, "
        "API, node, browser, database"
    ),
    "Cloud & DevOps": (
        "cloud, docker, kubernetes, linux, devops, infrastructure, "
        "AWS, deployment, container, observability"
    ),
    "Data & Databases": (
        "data, database, SQL, postgres, analytics, pipeline, "
        "distributed systems, warehouse, python, storage"
    ),
    "Developer Tools & Open Source": (
        "open source, github, developer tools, programming, compiler, "
        "editor, terminal, CLI, git, framework"
    ),
}

CATEGORY_OPTIONS = [
    "All",
    "Story",
    "Ask HN",
    "Show HN",
    "Jobs",
]

RESULT_OPTIONS = [10, 20, 30]


# --------------------------------------------------
# CSS
# --------------------------------------------------

st.markdown(
    """
    <style>
        :root {
            --orange: #ff6600;
            --navy: #0d1728;
            --navy-light: #111f34;
            --text: #182230;
            --muted: #667085;
            --border: #e5e7eb;
            --background: #f7f8fa;
        }

        .stApp {
            background: var(--background);
        }

        .block-container {
            max-width: 1280px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        [data-testid="stSidebar"] {
            background: var(--navy);
            border-right: 1px solid #243044;
            min-width: 330px;
            max-width: 330px;
        }

        [data-testid="stSidebar"] * {
            color: white;
        }

        [data-testid="stSidebar"] label {
            color: #cbd5e1 !important;
        }

        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea {
            color: #111827 !important;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 4px;
        }

        .brand-icon {
            width: 36px;
            height: 36px;
            border-radius: 8px;
            background: var(--orange);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
        }

        .brand-name {
            font-size: 22px;
            font-weight: 800;
        }

        .brand-name span {
            color: var(--orange);
        }

        .brand-subtitle {
            color: #9ca9ba !important;
            font-size: 13px;
            margin-bottom: 22px;
        }

        .side-heading {
            color: #d8e0ea !important;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-top: 18px;
            margin-bottom: 7px;
        }

        .side-note {
            color: #94a3b8 !important;
            font-size: 12px;
            line-height: 1.4;
            margin-top: 5px;
        }

        .hero {
            background: white;
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 24px 26px;
            margin-bottom: 18px;
            box-shadow: 0 2px 9px rgba(16, 24, 40, 0.04);
        }

        .hero-title {
            color: var(--text);
            font-size: 32px;
            font-weight: 800;
            margin: 0;
        }

        .hero-title span {
            color: var(--orange);
        }

        .hero-subtitle {
            color: var(--muted);
            font-size: 15px;
            margin-top: 7px;
            max-width: 800px;
        }

        .orange-line {
            width: 68px;
            height: 3px;
            background: var(--orange);
            border-radius: 999px;
            margin-top: 15px;
        }

        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 14px 16px;
        }

        .feed-title {
            color: var(--text);
            font-size: 19px;
            font-weight: 800;
            margin-top: 28px;
        }

        .feed-subtitle {
            color: var(--muted);
            font-size: 13px;
            margin-top: 3px;
            margin-bottom: 12px;
        }

        .story-card {
            display: grid;
            grid-template-columns: 46px 1fr auto;
            gap: 14px;
            align-items: start;
            background: white;
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 17px 18px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(16, 24, 40, 0.03);
        }

        .rank-number {
            width: 34px;
            height: 34px;
            border-radius: 9px;
            background: #fff0e6;
            color: var(--orange);
            font-weight: 800;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .story-title a {
            color: var(--text) !important;
            text-decoration: none !important;
            font-size: 16px;
            font-weight: 750;
            line-height: 1.4;
        }

        .story-title a:hover {
            color: var(--orange) !important;
        }

        .story-meta {
            color: var(--muted);
            font-size: 12px;
            margin-top: 6px;
            margin-bottom: 9px;
        }

        .tag-row {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }

        .tag {
            background: #f2f4f7;
            color: #475467;
            border: 1px solid #e4e7ec;
            border-radius: 999px;
            padding: 3px 8px;
            font-size: 11px;
        }

        .score-column {
            min-width: 205px;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 6px;
        }

        .score-box {
            background: #fafafa;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 8px;
            text-align: center;
        }

        .score-label {
            color: var(--muted);
            font-size: 10px;
        }

        .score-value {
            color: var(--text);
            font-size: 14px;
            font-weight: 800;
            margin-top: 2px;
        }

        .score-box.final {
            background: #fff4ec;
            border-color: #ffd4b8;
        }

        .score-box.final .score-value {
            color: #c94f00;
        }

        .footer-note {
            background: white;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 12px 15px;
            color: var(--muted);
            font-size: 12px;
            margin-top: 18px;
        }

        @media (max-width: 900px) {
            .story-card {
                grid-template-columns: 40px 1fr;
            }

            .score-column {
                grid-column: 2;
                min-width: 0;
                margin-top: 8px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Small helper functions
# --------------------------------------------------

def parse_interests(text):
    interests = []

    for item in text.split(","):
        item = item.strip()

        if item:
            interests.append(item)

    return interests


def domain_from_url(url):
    domain = urlparse(url).netloc
    domain = domain.replace("www.", "")

    if domain:
        return domain

    return "news.ycombinator.com"


def last_updated_text(fetched_at):
    seconds_ago = time.time() - fetched_at
    minutes_ago = int(seconds_ago / 60)

    if minutes_ago < 1:
        return "Just now"

    if minutes_ago == 1:
        return "1 min ago"

    return f"{minutes_ago} min ago"


@st.cache_data(ttl=600, show_spinner=False)
def fetch_feed():
    api = HackerNewsAPI()
    stories = api.fetch_top_stories(50)
    fetched_at = time.time()

    return stories, fetched_at


def update_keywords_from_preset():
    selected_preset = st.session_state.preset
    st.session_state.keywords = PRESETS[selected_preset]


def show_story_card(story, interests, rank):
    relevance = relevance_score(story, interests)
    trending = trending_score(story)
    final_score = combined_score(story, interests)

    matches = matched_interests(story, interests)

    safe_title = html.escape(story.title)
    safe_url = html.escape(story.url, quote=True)
    safe_author = html.escape(story.author)
    safe_domain = html.escape(domain_from_url(story.url))
    safe_discussion_url = html.escape(
        story.discussion_url(),
        quote=True,
    )

    tags_html = ""

    if matches:
        for match in matches[:5]:
            safe_match = html.escape(match)
            tags_html += f'<span class="tag">{safe_match}</span>'
    else:
        tags_html = '<span class="tag">trending</span>'

    st.markdown(
        f"""
        <div class="story-card">
            <div class="rank-number">
                {rank}
            </div>

            <div>
                <div class="story-title">
                    <a href="{safe_url}" target="_blank">
                        {safe_title}
                    </a>
                </div>

                <div class="story-meta">
                    by {safe_author}
                    · {round(story.hours_old)}h ago
                    · {safe_domain}
                    · {story.score} points
                    · {story.comments} comments
                    · <a href="{safe_discussion_url}" target="_blank">
                        HN discussion ↗
                      </a>
                </div>

                <div class="tag-row">
                    {tags_html}
                </div>
            </div>

            <div class="score-column">
                <div class="score-box">
                    <div class="score-label">RELEVANCE</div>
                    <div class="score-value">{relevance}/100</div>
                </div>

                <div class="score-box">
                    <div class="score-label">TRENDING</div>
                    <div class="score-value">{trending}/100</div>
                </div>

                <div class="score-box final">
                    <div class="score-label">MATCH</div>
                    <div class="score-value">{final_score}/100</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "preset" not in st.session_state:
    st.session_state.preset = "AI & Machine Learning"

if "keywords" not in st.session_state:
    st.session_state.keywords = PRESETS[st.session_state.preset]


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">H</div>
            <div class="brand-name">
                Hacker<span>Digest</span>
            </div>
        </div>

        <div class="brand-subtitle">
            Personalised Hacker News Feed
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="side-heading">1. Choose a Topic Preset</div>',
        unsafe_allow_html=True,
    )

    st.selectbox(
        "Topic preset",
        options=list(PRESETS.keys()),
        key="preset",
        label_visibility="collapsed",
        on_change=update_keywords_from_preset,
    )

    st.markdown(
        '<div class="side-heading">2. Custom Search (Optional)</div>',
        unsafe_allow_html=True,
    )

    custom_search = st.text_input(
        "Custom search",
        placeholder="e.g. rust, CUDA, AI agents",
        label_visibility="collapsed",
    )

    st.markdown(
        """
        <div class="side-note">
            If entered, custom search terms override the preset
            keywords for ranking.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="side-heading">3. Your Keywords</div>',
        unsafe_allow_html=True,
    )

    st.text_area(
        "Keywords",
        key="keywords",
        height=120,
        label_visibility="collapsed",
    )

    st.markdown(
        """
        <div class="side-note">
            Add or edit interests as comma-separated keywords.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="side-heading">4. Filter by Category</div>',
        unsafe_allow_html=True,
    )

    category = st.selectbox(
        "Category",
        CATEGORY_OPTIONS,
        label_visibility="collapsed",
    )

    st.markdown(
        '<div class="side-heading">5. Results to Show</div>',
        unsafe_allow_html=True,
    )

    results_to_show = st.selectbox(
        "Results",
        RESULT_OPTIONS,
        index=1,
        format_func=lambda value: f"Top {value}",
        label_visibility="collapsed",
    )

    refresh_clicked = st.button(
        "↻ REFRESH FEED",
        use_container_width=True,
        type="primary",
    )

    if refresh_clicked:
        fetch_feed.clear()

    st.markdown(
        """
        <div class="side-note" style="margin-top: 16px;">
            Data from Hacker News Firebase API<br>
            Built with Python + Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# Main content
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">
            📰 Hacker<span>Digest</span>
        </div>

        <div class="hero-subtitle">
            Your personalised Hacker News feed. Stories are ranked
            by relevance to your interests and a simple time-aware
            trending score.
        </div>

        <div class="orange-line"></div>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.spinner("Loading Hacker News stories..."):
    stories, fetched_at = fetch_feed()


if not stories:
    st.error(
        "HackerDigest could not load stories from Hacker News. "
        "Please try refreshing the feed."
    )
    st.stop()


# --------------------------------------------------
# Choose the active interests
# --------------------------------------------------

if custom_search.strip():
    interests = parse_interests(custom_search)
    active_source = f'Custom search: "{custom_search.strip()}"'
else:
    interests = parse_interests(st.session_state.keywords)
    active_source = st.session_state.preset


if not interests:
    st.warning(
        "Add at least one interest keyword so HackerDigest "
        "can personalise the ranking."
    )
    st.stop()


# --------------------------------------------------
# Rank and limit stories
# --------------------------------------------------

ranked_stories = rank_stories(
    stories,
    interests,
    category,
)

visible_stories = ranked_stories[:results_to_show]


# --------------------------------------------------
# Dashboard metrics
# --------------------------------------------------

total_relevance = 0

for story in stories:
    total_relevance += relevance_score(
        story,
        interests,
    )

average_relevance = round(
    total_relevance / len(stories)
)

total_comments = 0

for story in stories:
    total_comments += story.comments


metric1, metric2, metric3, metric4 = st.columns(4)

metric1.metric(
    "Stories Found",
    len(stories),
)

metric2.metric(
    "Avg Relevance",
    f"{average_relevance}/100",
)

metric3.metric(
    "Total Comments",
    f"{total_comments:,}",
)

metric4.metric(
    "Last Updated",
    last_updated_text(fetched_at),
)


# --------------------------------------------------
# Ranked feed
# --------------------------------------------------

safe_active_source = html.escape(active_source)
safe_category = html.escape(category)

st.markdown(
    f"""
    <div class="feed-title">
        Ranked Stories
    </div>

    <div class="feed-subtitle">
        Using {safe_active_source}
        · Category: {safe_category}
    </div>
    """,
    unsafe_allow_html=True,
)


if not visible_stories:
    st.info(
        "No stories matched this category "
        "in the current top Hacker News feed."
    )
else:
    rank = 1

    for story in visible_stories:
        show_story_card(
            story,
            interests,
            rank,
        )

        rank += 1


st.markdown(
    """
    <div class="footer-note">
        Scores combine relevance to your interests (70%)
        and trending score (30%). Relevance uses literal
        keyword matches in story titles. This is a transparent
        ranking heuristic, not machine learning.
    </div>
    """,
    unsafe_allow_html=True,
)
