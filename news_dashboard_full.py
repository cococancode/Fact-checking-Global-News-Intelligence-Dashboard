import streamlit as st
import feedparser
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
import numpy as np

st.set_page_config(page_title="Global News Intelligence Dashboard", layout="wide")

# -----------------------------
# Session state for safe refresh
# -----------------------------
if "refresh_trigger" not in st.session_state:
    st.session_state.refresh_trigger = 0

if st.sidebar.button("Manual refresh"):
    st.session_state.refresh_trigger += 1  # Increment triggers a soft refresh

# -----------------------------
# Define all news outlets
# -----------------------------
outlets = [
    # Global agencies
    {"name": "Associated Press (AP)", "rss": "https://apnews.com/rss", "bias": "center", "reliability": "high"},
    {"name": "Reuters", "rss": "http://feeds.reuters.com/reuters/topNews", "bias": "center", "reliability": "high"},
    {"name": "AFP", "rss": "https://www.afp.com/en/feeds", "bias": "center", "reliability": "high"},

    # Top broadcasters
    {"name": "BBC News", "rss": "http://feeds.bbci.co.uk/news/rss.xml", "bias": "center", "reliability": "high"},
    {"name": "CNN", "rss": "http://rss.cnn.com/rss/edition.rss", "bias": "left", "reliability": "high"},
    {"name": "Al Jazeera", "rss": "https://www.aljazeera.com/xml/rss/all.xml", "bias": "center-left", "reliability": "high"},
    {"name": "Sky News", "rss": "https://feeds.skynews.com/feeds/rss/home.xml", "bias": "center", "reliability": "high"},
    {"name": "CNA (Channel NewsAsia)", "rss": "https://www.channelnewsasia.com/rssfeeds/8395986", "bias": "center", "reliability": "high"},
    {"name": "NHK World-Japan", "rss": "https://www3.nhk.or.jp/nhkworld/en/news/rss.xml", "bias": "center", "reliability": "high"},
    {"name": "Yahoo! News", "rss": "https://www.yahoo.com/news/rss", "bias": "center", "reliability": "medium"},

    # Influential newspapers
    {"name": "The New York Times", "rss": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", "bias": "left", "reliability": "high"},
    {"name": "The Wall Street Journal", "rss": "https://www.wsj.com/xml/rss/3_7014.xml", "bias": "right", "reliability": "high"},
    {"name": "The Washington Post", "rss": "http://feeds.washingtonpost.com/rss/politics", "bias": "left", "reliability": "high"},
    {"name": "The Guardian", "rss": "https://www.theguardian.com/world/rss", "bias": "left", "reliability": "high"},
    {"name": "The Times", "rss": "https://www.thetimes.co.uk/rss", "bias": "center-right", "reliability": "high"},
    {"name": "Le Monde", "rss": "https://www.lemonde.fr/rss/une.xml", "bias": "center-left", "reliability": "high"},
    {"name": "Asahi Shimbun", "rss": "https://www.asahi.com/rss/asahi/newsheadlines.rdf", "bias": "center", "reliability": "high"},
    {"name": "Bloomberg News", "rss": "https://www.bloomberg.com/feed/podcast/etf-report.xml", "bias": "center", "reliability": "high"},
    {"name": "Forbes", "rss": "https://www.forbes.com/business/feed2/", "bias": "center-right", "reliability": "high"},
    {"name": "NPR", "rss": "https://www.npr.org/rss/rss.php?id=1001", "bias": "center-left", "reliability": "high"},

    # Other sources
    {"name": "Fox News", "rss": "http://feeds.foxnews.com/foxnews/latest", "bias": "right", "reliability": "medium"},
    {"name": "CNBC", "rss": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "bias": "center-right", "reliability": "high"},
    {"name": "ABC News", "rss": "https://abcnews.go.com/abcnews/topstories", "bias": "center", "reliability": "high"},
    {"name": "CBS News", "rss": "https://www.cbsnews.com/latest/rss/main", "bias": "center", "reliability": "high"},
    {"name": "NBC News", "rss": "https://feeds.nbcnews.com/nbcnews/public/news", "bias": "center", "reliability": "high"},
    {"name": "NDTV 24x7", "rss": "https://feeds.feedburner.com/ndtvnews-latest", "bias": "center", "reliability": "high"},
]

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Controls")
selected_outlets = st.sidebar.multiselect(
    "Select news outlets",
    [o["name"] for o in outlets],
    default=[o["name"] for o in outlets]  # default = all outlets
)

translate_toggle = st.sidebar.checkbox("Enable translation (API)", False)
auto_refresh = st.sidebar.checkbox("Auto refresh", False)
refresh_interval = st.sidebar.slider("Refresh interval (sec)", 30, 300, 60)
min_cluster_size = st.sidebar.slider("Minimum cluster size", 1, 5, 1)

# -----------------------------
# App header
# -----------------------------
st.title("🌍 Global News Intelligence Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# -----------------------------
# Collect all articles
# -----------------------------
articles = []
for outlet in outlets:
    if outlet["name"] not in selected_outlets:
        continue
    feed = feedparser.parse(outlet["rss"])
    for entry in feed.entries[:3]:
        articles.append({
            "title": entry.title,
            "summary": entry.get("summary", ""),
            "link": entry.link,
            "source": outlet["name"],
            "bias": outlet.get("bias", "N/A"),
            "reliability": outlet.get("reliability", "N/A")
        })

if not articles:
    st.warning("No articles found for selected outlets.")
    st.stop()

# -----------------------------
# Translation placeholder
# -----------------------------
def translate(text):
    if translate_toggle:
        return f"[Translated] {text}"  # placeholder for API call
    return text

# -----------------------------
# TF-IDF + DBSCAN Clustering
# -----------------------------
article_texts = [a["title"] + " " + a["summary"] for a in articles]

vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(article_texts)

db = DBSCAN(metric='cosine', eps=0.3, min_samples=2)
labels = db.fit_predict(tfidf_matrix)

clusters = {}
for label, article in zip(labels, articles):
    clusters.setdefault(label, []).append(article)

# -----------------------------
# Display clusters
# -----------------------------
for cluster_id, cluster_articles in clusters.items():
    if cluster_id == -1 or len(cluster_articles) < min_cluster_size:
        continue
    st.subheader(f"Cluster #{cluster_id} - {len(cluster_articles)} sources reporting")
    for article in cluster_articles:
        title = translate(article["title"])
        st.markdown(f"[{title}]({article['link']}) - {article['source']}")
        st.caption(f"Bias: {article['bias']} | Reliability: {article['reliability']} | Score: 0.8")
        with st.expander("Summary / Fact Check / Cross-Source Info"):
            summary_text = translate(article["summary"])
            st.write(summary_text)
            st.write("Fact check: AI analysis pending")
            st.write("Cross-source cluster info: placeholder")

# -----------------------------
# Monetization placeholders
# -----------------------------
st.sidebar.header("Subscription Tiers (Placeholder)")
st.sidebar.write("Free: Limited headlines")
st.sidebar.write("Pro: Full access + translation + clustering")
st.sidebar.write("Enterprise: Custom feeds + API access")

# -----------------------------
# Auto refresh logic (optional)
# -----------------------------
if auto_refresh:
    st.experimental_set_query_params(refresh=st.session_state.refresh_trigger)
    st.experimental_rerun()
