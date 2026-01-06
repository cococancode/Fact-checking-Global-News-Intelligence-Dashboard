import streamlit as st
import requests
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN

st.set_page_config(page_title="Global News Intelligence Dashboard", layout="wide")

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Dashboard Controls")
translate_toggle = st.sidebar.checkbox("Enable translation (API)", False)
auto_refresh = st.sidebar.checkbox("Auto refresh", False)
refresh_interval = st.sidebar.slider("Refresh interval (sec)", 30, 300, 60)
min_cluster_size = st.sidebar.slider("Minimum cluster size", 1, 5, 1)
articles_per_outlet = st.sidebar.slider("Articles per outlet", 1, 5, 3)

# -----------------------------
# News outlets registry
# -----------------------------
outlets = [
    {"name": "AP", "rss": "https://apnews.com/rss", "bias":"center", "reliability":"high"},
    {"name": "Reuters", "rss": "http://feeds.reuters.com/reuters/topNews", "bias":"center", "reliability":"high"},
    {"name": "BBC News", "rss": "http://feeds.bbci.co.uk/news/rss.xml", "bias":"center", "reliability":"high"},
    {"name": "CNN", "rss": "http://rss.cnn.com/rss/edition.rss", "bias":"left", "reliability":"high"},
    {"name": "Al Jazeera", "rss": "https://www.aljazeera.com/xml/rss/all.xml", "bias":"center-left", "reliability":"high"},
    # Add more outlets as needed...
]

# -----------------------------
# Sidebar outlet selection
# -----------------------------
st.sidebar.header("Select News Outlets")
selected_outlets = st.sidebar.multiselect(
    "Choose outlets to load",
    [o["name"] for o in outlets]
)

# -----------------------------
# App header
# -----------------------------
st.title("🌍 Global News Intelligence Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# -----------------------------
# Search bar
# -----------------------------
search_query = st.text_input("🔍 Search all articles by topic or keyword:")

# -----------------------------
# Cached RSS fetch
# -----------------------------
@st.cache_data(ttl=300)
def fetch_rss(url):
    try:
        api_url = f"https://api.rss2json.com/v1/api.json?rss_url={url}"
        resp = requests.get(api_url, timeout=5)
        return resp.json().get("items", [])
    except:
        return []

# -----------------------------
# Fetch articles (only selected outlets)
# -----------------------------
articles = []
if selected_outlets:
    with st.spinner("Fetching articles from selected outlets..."):
        for outlet in outlets:
            if outlet["name"] not in selected_outlets:
                continue
            items = fetch_rss(outlet["rss"])
            for entry in items[:articles_per_outlet]:
                articles.append({
                    "title": entry.get("title",""),
                    "summary": entry.get("description",""),
                    "link": entry.get("link","#"),
                    "source": outlet["name"],
                    "bias": outlet.get("bias","N/A"),
                    "reliability": outlet.get("reliability","N/A")
                })

# -----------------------------
# Filter by search query
# -----------------------------
if search_query:
    filtered_articles = [
        a for a in articles
        if search_query.lower() in a["title"].lower() or search_query.lower() in a["summary"].lower()
    ]
    if not filtered_articles:
        st.warning(f"No articles found for '{search_query}'")
        st.stop()
else:
    filtered_articles = articles

# -----------------------------
# Translation placeholder
# -----------------------------
def translate(text):
    if translate_toggle:
        return f"[Translated] {text}"
    return text

# -----------------------------
# Cached clustering
# -----------------------------
@st.cache_data(ttl=300)
def cluster_articles(texts):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(texts)
    db = DBSCAN(metric='cosine', eps=0.3, min_samples=2)
    return db.fit_predict(tfidf_matrix)

article_texts = [a["title"] + " " + a["summary"] for a in filtered_articles]
if article_texts:
    labels = cluster_articles(article_texts)
else:
    labels = []

# -----------------------------
# Group articles by cluster
# -----------------------------
clusters = {}
for label, article in zip(labels, filtered_articles):
    clusters.setdefault(label, []).append(article)

# -----------------------------
# Display clusters
# -----------------------------
if not clusters:
    st.info("No clusters to display. Try selecting different outlets or keywords.")
else:
    for cluster_id, cluster_articles in clusters.items():
        if cluster_id == -1 or len(cluster_articles) < min_cluster_size:
            continue
        with st.expander(f"Cluster #{cluster_id} - {len(cluster_articles)} sources reporting"):
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
