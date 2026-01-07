import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Global News Intelligence Dashboard",
    layout="wide"
)

# -----------------------------
# DARK MODE (READABLE)
# -----------------------------
st.markdown("""
<style>
body, .stApp {
    background-color: #000;
    color: #fff;
}
a { color: #4da6ff !important; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.title("🌍 Global News Intelligence Dashboard")
st.caption(f"Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

# -----------------------------
# RSS NEWS REGISTRY (NO API)
# -----------------------------
NEWS_OUTLETS = {
    "Reuters": "https://www.reuters.com/rssFeed/worldNews",
    "Associated Press": "https://apnews.com/apf-topnews?utm_source=rss",
    "BBC News": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "CNN": "https://rss.cnn.com/rss/edition_world.rss",
    "The Guardian": "https://www.theguardian.com/world/rss",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "Bloomberg": "https://www.bloomberg.com/feed/podcast/etf-report.xml",
    "CNBC": "https://www.cnbc.com/id/100727362/device/rss/rss.html",
    "NPR": "https://feeds.npr.org/1004/rss.xml"
}

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("Controls")

selected_outlets = st.sidebar.multiselect(
    "Select news outlets",
    list(NEWS_OUTLETS.keys())
)

search_term = st.sidebar.text_input(
    "Search topic",
    placeholder="e.g. Ukraine, inflation, AI"
)

load_news = st.sidebar.button("Load articles")

# -----------------------------
# RSS PARSER (SAFE)
# -----------------------------
def fetch_rss(url):
    articles = []
    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)

        for item in root.iter("item"):
            title = item.findtext("title", "")
            description = item.findtext("description", "")
            link = item.findtext("link", "")

            articles.append({
                "title": title,
                "summary": description,
                "link": link
            })
    except Exception as e:
        st.warning(f"Failed to load feed: {url}")
    return articles

# -----------------------------
# MAIN LOGIC
# -----------------------------
if load_news:

    all_articles = []

    for outlet in selected_outlets:
        feed_url = NEWS_OUTLETS[outlet]
        feed_articles = fetch_rss(feed_url)

        for article in feed_articles:
            article["source"] = outlet
            all_articles.append(article)

    # SEARCH FILTER
    if search_term:
        all_articles = [
            a for a in all_articles
            if search_term.lower() in a["title"].lower()
            or search_term.lower() in a["summary"].lower()
        ]

    if not all_articles:
        st.warning("No articles found.")
    else:
        st.subheader(f"📰 {len(all_articles)} Articles")

        for article in all_articles:
            st.markdown(f"### [{article['title']}]({article['link']})")
            st.caption(article["source"])

            if article["summary"]:
                st.write(article["summary"])

            st.divider()

# -----------------------------
# FOOTER
# -----------------------------
st.caption("Key-free · RSS-based · Streamlit Cloud compatible")
