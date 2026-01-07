import streamlit as st
import feedparser
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Global News Intelligence Dashboard", layout="wide")

# -----------------------------
# Session state init (CRITICAL)
# -----------------------------
if "articles" not in st.session_state:
    st.session_state.articles = []

# -----------------------------
# Dark mode CSS
# -----------------------------
st.markdown("""
<style>
body, .stApp { background-color:#000; color:#fff; }
a { color:#1E90FF; text-decoration:none; font-size:1.05rem; }
a:hover { text-decoration:underline; }
[data-testid="stSidebar"] { background-color:#111; color:#fff; }
.caption { color:#AAA; font-size:0.85rem; }
.stTextInput input { background:#222; color:#fff; }
.stButton button { background:#1E90FF; color:#fff; border:none; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# News outlets
# -----------------------------
OUTLETS = [
    {"name": "AP", "rss": "https://apnews.com/apf-topnews.rss", "bias":"center"},
    {"name": "Reuters", "rss": "https://feeds.reuters.com/reuters/topNews", "bias":"center"},
    {"name": "BBC News", "rss": "http://feeds.bbci.co.uk/news/rss.xml", "bias":"center"},
    {"name": "CNN", "rss": "http://rss.cnn.com/rss/edition.rss", "bias":"left"},
    {"name": "Al Jazeera", "rss": "https://www.aljazeera.com/xml/rss/all.xml", "bias":"center-left"},
]

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Controls")

selected_outlets = st.sidebar.multiselect(
    "Select outlets",
    [o["name"] for o in OUTLETS]
)

articles_per_outlet = st.sidebar.slider("Articles per outlet", 1, 5, 3)
min_cluster_size = st.sidebar.slider("Min cluster size", 1, 5, 1)

# -----------------------------
# Header
# -----------------------------
st.title("🌍 Global News Intelligence Dashboard")
st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

search = st.text_input("🔍 Search topics across all outlets")

# -----------------------------
# RSS fetch
# -----------------------------
def fetch_rss(url):
    feed = feedparser.parse(url)
    return feed.entries

# -----------------------------
# Load Articles BUTTON (FIXED)
# -----------------------------
if st.sidebar.button("Load Articles"):
    st.session_state.articles = []  # RESET ONLY ON CLICK

    with st.spinner("Fetching news…"):
        for outlet in OUTLETS:
            if outlet["name"] not in selected_outlets:
                continue

            entries = fetch_rss(outlet["rss"])
            for e in entries[:articles_per_outlet]:
                st.session_state.articles.append({
                    "title": e.get("title",""),
                    "summary": e.get("summary",""),
                    "link": e.get("link","#"),
                    "source": outlet["name"],
                    "bias": outlet["bias"],
                })

# -----------------------------
# EMPTY STATE (IMPORTANT)
# -----------------------------
if not st.session_state.articles:
    st.info("⬅️ Select news outlets and click **Load Articles**")
    st.stop()

articles = st.session_state.articles

# -----------------------------
# Search filter
# -----------------------------
if search:
    articles = [
        a for a in articles
        if search.lower() in a["title"].lower()
        or search.lower() in a["summary"].lower()
    ]

    if not articles:
        st.warning("No articles found for your search.")
        st.stop()

# -----------------------------
# Clustering
# -----------------------------
texts = [a["title"] + " " + a["summary"] for a in articles]

vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(texts)

db = DBSCAN(metric="cosine", eps=0.3, min_samples=2)
labels = db.fit_predict(X)

clusters = {}
for label, article in zip(labels, articles):
    clusters.setdefault(label, []).append(article)

# -----------------------------
# Display clusters
# -----------------------------
for cid, group in clusters.items():
    if cid == -1 or len(group) < min_cluster_size:
        continue

    st.subheader(f"🧠 Cluster ({len(group)} sources)")
    for art in group:
        st.markdown(f"**[{art['title']}]({art['link']})**")
        st.markdown(
            f"<div class='caption'>{art['source']} | Bias: {art['bias']}</div>",
            unsafe_allow_html=True,
        )

        with st.expander("Summary / Fact Check"):
            st.write(art["summary"])
            st.write("Bias explanation: placeholder")
            st.write("Fact-check status: pending")

# -----------------------------
# Monetization placeholder
# -----------------------------
st.sidebar.header("Plans")
st.sidebar.write("Free – limited")
st.sidebar.write("Pro – clustering & search")
st.sidebar.write("Enterprise – API + monitoring")
