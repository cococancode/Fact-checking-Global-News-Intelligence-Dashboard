import streamlit as st
import feedparser
import json
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
import numpy as np

st.set_page_config(page_title="Global News Intelligence Dashboard", layout="wide")

# -----------------------------
# Load news registry
# -----------------------------
with open("news_registry.json", "r", encoding="utf-8") as f:
    outlets = json.load(f)

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Controls")
selected_outlets = st.sidebar.multiselect(
    "Select news outlets",
    [o["name"] for o in outlets],
    default=[o["name"] for o in outlets[:5]]
)

translate_toggle = st.sidebar.checkbox("Enable translation (API)", False)
auto_refresh = st.sidebar.checkbox("Auto refresh", False)
refresh_interval = st.sidebar.slider("Refresh interval (sec)", 30, 300, 60)
min_cluster_size = st.sidebar.slider("Minimum cluster size", 1, 5, 1)

# -----------------------------
# Safe manual refresh
# -----------------------------
if st.sidebar.button("Manual refresh"):
    st.experimental_rerun()  # call directly, not via another function

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
