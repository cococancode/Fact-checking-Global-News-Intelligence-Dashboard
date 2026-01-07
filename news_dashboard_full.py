import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --------------------------------
# Page config
# --------------------------------
st.set_page_config(
    page_title="Global News Intelligence Dashboard",
    layout="wide"
)

# --------------------------------
# Styling (Black background, white text)
# --------------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #000000 !important;
    color: #FFFFFF !important;
}
a {
    color: #4da6ff !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------
# API key (SECURE)
# --------------------------------
API_KEY = st.secrets.get("NEWS_API_KEY")
if not API_KEY:
    st.error("NEWS_API_KEY not found in Streamlit secrets.")
    st.stop()

# --------------------------------
# News outlets registry (JSON)
# --------------------------------
OUTLETS = {
    "BBC News": "bbc-news",
    "The Guardian": "the-guardian-uk",
    "Reuters": "reuters",
    "Al Jazeera": "al-jazeera-english",
    "CNN": "cnn",
    "The New York Times": "the-new-york-times",
    "Bloomberg": "bloomberg",
    "Financial Times": "financial-times",
    "The Washington Post": "the-washington-post"
}

# --------------------------------
# UI Header
# --------------------------------
st.title("🌍 Global News Intelligence Dashboard")
st.caption(f"Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

# --------------------------------
# Sidebar Controls
# --------------------------------
st.sidebar.header("Controls")

selected_outlets = st.sidebar.multiselect(
    "Select news outlets",
    list(OUTLETS.keys()),
    default=["BBC News", "The Guardian", "Reuters"]
)

search_query = st.sidebar.text_input(
    "Search topic (optional)",
    placeholder="e.g. China, AI, Climate"
)

load_button = st.sidebar.button("Load Articles")

# --------------------------------
# Fetch function (JSON only)
# --------------------------------
def fetch_articles(sources, query):
    url = "https://newsapi.org/v2/everything"

    params = {
        "apiKey": API_KEY,
        "sources": ",".join(sources),
        "q": query if query else None,
        "language": "en",
        "pageSize": 50,
        "sortBy": "publishedAt",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

# --------------------------------
# Load articles
# --------------------------------
if load_button:
    if not selected_outlets:
        st.warning("Please select at least one outlet.")
        st.stop()

    with st.spinner("Fetching articles..."):
        try:
            source_ids = [OUTLETS[o] for o in selected_outlets]
            data = fetch_articles(source_ids, search_query)

        except Exception as e:
            st.error(f"Failed to fetch articles: {e}")
            st.stop()

    articles = data.get("articles", [])

    if not articles:
        st.info("No articles found for your selection.")
        st.stop()

    st.subheader(f"📰 {len(articles)} Articles")

    for article in articles:
        st.markdown(f"### [{article['title']}]({article['url']})")
        st.caption(f"{article['source']['name']} — {article.get('publishedAt','')}")
        if article.get("description"):
            st.write(article["description"])
        st.markdown("---")

else:
    st.info("Select outlets and click **Load Articles**.")
