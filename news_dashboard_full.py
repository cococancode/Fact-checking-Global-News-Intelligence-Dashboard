import streamlit as st
import requests
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
import time

st.set_page_config(page_title="Global News Intelligence Dashboard", layout="wide")

# -----------------------------
# Session state for safe refresh
# -----------------------------
if "refresh_trigger" not in st.session_state:
    st.session_state.refresh_trigger = 0
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Controls")
auto_refresh = st.sidebar.checkbox("Auto refresh", False)
refresh_interval = st.sidebar.slider("Refresh interval (sec)", 30, 300, 60)
min_cluster_size = st.sidebar.slider("Minimum cluster size", 1, 5, 1)
translate_toggle = st.sidebar.checkbox("Enable translation (API)", False)

if st.sidebar.button("Manual refresh"):
    st.session_state.refresh_trigger += 1
    st.session_state.last_refresh = time.time()

# -----------------------------
# Safe auto-refresh
# -----------------------------
if auto_refresh:
    if time.time() - st.session_state.last_refresh > refresh_interval:
        st.session_state.refresh_trigger += 1
        st.session_state.last_refresh = time.time()
        st.experimental_set_query_params(refresh=st.session_state.refresh_trigger)
        st.experimental_rerun()

# -----------------------------
# Inject FT + Guardian hybrid CSS
# -----------------------------
st.markdown("""
<style>
/* Fonts */
body, .stApp {
    font-family: 'Arial', 'Helvetica', sans-serif;
    background-color: #FAF6F0;
    color: #1A1A1A;
}

/* Headline links */
a {
    color: #052962;  /* Guardian blue */
    text-decoration: none;
    font-family: 'Georgia', 'Times New Roman', serif; /* FT headlines */
    font-size: 1.05rem;
}
a:hover {
    text-decoration: underline;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #FFF9F0;
    padding-top: 2rem;
}

/* Cluster cards */
.cluster-card {
    background-color: #FFFFFF;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    border-left: 4px solid #F3C04D; /* FT accent */
    border-radius: 4px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}

/* Metadata captions */
.caption {
    font-size: 0.85rem;
    color: #555555;
    margin-top: 0.2rem;
}

/* Expander styling */
div[role="button"] {
    font-weight: 600;
    color: #052962;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Define all news outlets
# -----------------------------
outlets = [
    {"name": "Associated Press (AP)", "rss": "https://apnews.com/rss", "bias": "center", "reliability": "high"},
    {"name": "Reuters", "rss": "http://feeds.reuters.com/reuters/topNews", "bias": "center", "reliability": "high"},
    {"name": "AFP", "rss": "https://www.afp.com/en/feeds", "bias": "center", "reliability": "high"},
    {"name": "BBC News", "rss": "http://feeds.bbci.co.uk/news/rss.xml", "bias": "center", "reliability": "high"},
    {"name": "CNN", "rss": "http://rss.cnn.com/rss/edition.rss", "bias": "left", "reliability": "high"},
    {"name": "Al Jazeera", "rss": "https://www.aljazeera.com/xml/rss/all.xml", "bias": "center-left", "reliability": "high"},
    {"name": "Sky News", "rss": "https://feeds.skynews.com/feeds/rss/home.xml", "bias": "center", "reliability": "high"},
    {"name": "CNA (Channel NewsAsia)", "rss": "https://www.channelnewsasia.com/rssfeeds/8395986", "bias": "center", "reliability": "high"},
    {"name": "NHK World-Japan", "rss": "https://www3.nhk.or.jp/nhkworld/en/news/rss.xml", "bias": "center", "reliability": "high"},
    {"name": "Yahoo! News", "rss": "https://www.yahoo.com/news/rss", "bias": "center", "reliability": "medium"},
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
    {"name": "Fox News", "rss": "http://feeds.foxnews.com/foxnews/latest", "bias": "right", "reliability": "medium"},
    {"name": "CNBC", "rss": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "bias": "center-right", "reliability": "high"},
    {"name": "ABC News", "rss": "https://abcnews.go.com/abcnews/topstories", "bias": "center", "reliability": "high"},
    {"name": "CBS News", "rss": "https://www.cbsnews.com/latest/rss/main", "bias": "center", "reliability": "high"},
    {"name": "NBC News", "rss": "https://feeds.nbcnews.com/nbcnews/public/news", "bias": "center", "reliability": "high"},
    {"name": "NDTV 24x7", "rss": "https://feeds.feedburner.com/ndtvnews-latest", "bias": "center", "reliability": "high"},
]

# -----------------------------
# Sidebar outlet selection
# -----------------------------
st.sidebar.header("Select news outlets")
selected_outlets = st.sidebar.multiselect(
    "News outlets",
    [o["name"] for o in outlets],
    default=[o["name"] for o in outlets]
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
# RSS-to-JSON fetch function
# -----------------------------
def fetch_rss_json(url):
    try:
        api_url = f"https://api.rss2json.com/v1/api.json?rss_url={url}"
        resp = requests.get(api_url, timeout=5)
        data = resp.json()
        return data.get("items", [])
    except:
        return []

# -----------------------------
# Fetch articles safely
# -----------------------------
articles = []
with st.spinner("Fetching latest articles..."):
    for outlet in outlets:
        if outlet["name"] not in selected_outlets:
            continue
        items = fetch_rss_json(outlet["rss"])
        for entry in items[:3]:
            articles.append({
                "title": entry.get("title", ""),
                "summary": entry.get("description", ""),
                "link": entry.get("link", "#"),
                "source": outlet["name"],
                "bias": outlet.get("bias", "N/A"),
                "reliability": outlet.get("reliability", "N/A")
            })

if not articles:
    st.warning("No articles found for selected outlets.")
    st.stop()

# -----------------------------
# Apply search filter
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
# TF-IDF + DBSCAN clustering
# -----------------------------
article_texts = [a["title"] + " " + a["summary"] for a in filtered_articles]

vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(article_texts)

db = DBSCAN(metric='cosine', eps=0.3, min_samples=2)
labels = db.fit_predict(tfidf_matrix)

clusters = {}
for label, article in zip(labels, filtered_articles):
    clusters.setdefault(label, []).append(article)

# -----------------------------
# Display clusters
# -----------------------------
for cluster_id, cluster_articles in clusters.items():
    if cluster_id == -1 or len(cluster_articles) < min_cluster_size:
        continue
    st.markdown(f"<div class='cluster-card'><h3>Cluster #{cluster_id} - {len(cluster_articles)} sources reporting</h3>", unsafe_allow_html=True)
    for article in cluster_articles:
        title = translate(article["title"])
        st.markdown(f"<a href='{article['link']}' target='_blank'>{title}</a>", unsafe_allow_html=True)
        st.markdown(f"<div class='caption'>Bias: {article['bias']} | Reliability: {article['reliability']} | Score: 0.8</div>", unsafe_allow_html=True)
        with st.expander("Summary / Fact Check / Cross-Source Info"):
            summary_text = translate(article["summary"])
            st.write(summary_text)
            st.write("Fact check: AI analysis pending")
            st.write("Cross-source cluster info: placeholder")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Monetization placeholders
# -----------------------------
st.sidebar.header("Subscription Tiers (Placeholder)")
st.sidebar.write("Free: Limited headlines")
st.sidebar.write("Pro: Full access + translation + clustering")
st.sidebar.write("Enterprise: Custom feeds + API access")
