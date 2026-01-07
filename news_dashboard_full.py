import streamlit as st
import feedparser
from datetime import datetime

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Global News Intelligence Dashboard", layout="wide")

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "articles" not in st.session_state:
    st.session_state.articles = []

# -------------------------------------------------
# DARK MODE
# -------------------------------------------------
st.markdown("""
<style>
body, .stApp { background:black; color:white; }
a { color:#4da3ff; }
[data-testid="stSidebar"] { background:#111; }
.stButton button { background:#4da3ff; color:black; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# VERIFIED HTTPS RSS FEEDS (CRITICAL)
# -------------------------------------------------
OUTLETS = [
    {
        "name": "Reuters",
        "rss": "https://feeds.reuters.com/reuters/topNews",
        "bias": "center",
    },
    {
        "name": "AP News",
        "rss": "https://apnews.com/apf-topnews.rss",
        "bias": "center",
    },
    {
        "name": "BBC News",
        "rss": "https://feeds.bbci.co.uk/news/rss.xml",
        "bias": "center",
    },
    {
        "name": "Al Jazeera",
        "rss": "https://www.aljazeera.com/xml/rss/all.xml",
        "bias": "center-left",
    },
]

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.header("Controls")

selected_outlets = st.sidebar.multiselect(
    "Select outlets",
    [o["name"] for o in OUTLETS],
)

articles_per_outlet = st.sidebar.slider(
    "Articles per outlet", 1, 10, 5
)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("🌍 Global News Intelligence Dashboard")
st.caption(datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))

# -------------------------------------------------
# FETCH FUNCTION (WITH DEBUG)
# -------------------------------------------------
def fetch_rss(url):
    feed = feedparser.parse(url)
    return feed.entries, feed.bozo, feed.bozo_exception if feed.bozo else None

# -------------------------------------------------
# LOAD ARTICLES BUTTON
# -------------------------------------------------
if st.sidebar.button("Load Articles"):
    st.session_state.articles = []

    for outlet in OUTLETS:
        if outlet["name"] not in selected_outlets:
            continue

        entries, bozo, error = fetch_rss(outlet["rss"])

        # DEBUG OUTPUT
        st.sidebar.write(f"📡 {outlet['name']}: {len(entries)} items")

        if bozo:
            st.sidebar.error(f"{outlet['name']} feed error")
            st.sidebar.write(error)
            continue

        for e in entries[:articles_per_outlet]:
            st.session_state.articles.append({
                "title": e.get("title", "No title"),
                "summary": e.get("summary", ""),
                "link": e.get("link", "#"),
                "source": outlet["name"],
                "bias": outlet["bias"],
            })

# -------------------------------------------------
# EMPTY STATE
# -------------------------------------------------
if not st.session_state.articles:
    st.warning("⬅️ Select outlets and click **Load Articles**")
    st.stop()

# -------------------------------------------------
# DISPLAY ARTICLES
# -------------------------------------------------
st.subheader(f"📰 {len(st.session_state.articles)} articles loaded")

for a in st.session_state.articles:
    st.markdown(f"### [{a['title']}]({a['link']})")
    st.caption(f"{a['source']} | Bias: {a['bias']}")
    if a["summary"]:
        with st.expander("Summary"):
            st.write(a["summary"])
    st.divider()
