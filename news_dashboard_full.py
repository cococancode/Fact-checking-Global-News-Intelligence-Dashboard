import streamlit as st
import requests
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Global News Intelligence Dashboard",
    layout="wide"
)

NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "")  # set in Streamlit secrets

# -----------------------------
# GLOBAL DARK THEME
# -----------------------------
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    a {
        color: #00bfff !important;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# HEADER
# -----------------------------
st.title("🌍 Global News Intelligence Dashboard")
st.caption(f"Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

# -----------------------------
# NEWS OUTLETS (JSON REGISTRY)
# -----------------------------
OUTLETS = {
    "Associated Press": "associated-press",
    "Reuters": "reuters",
    "BBC News": "bbc-news",
    "CNN": "cnn",
    "Al Jazeera": "al-jazeera-english",
    "The New York Times": "the-new-york-times",
    "The Guardian": "the-guardian-uk",
    "Bloomberg": "bloomberg",
    "CNBC": "cnbc",
    "Fox News": "fox-news",
    "NPR": "npr"
}

# -----------------------------
# SIDEBAR CONTROLS
# -----------------------------
st.sidebar.header("Search Controls")

selected_outlets = st.sidebar.multiselect(
    "Select news outlets",
    list(OUTLETS.keys())
)

search_query = st.sidebar.text_input(
    "Search topic",
    placeholder="e.g. Ukraine, AI, Inflation"
)

load_articles = st.sidebar.button("Load articles")

# -----------------------------
# FETCH FUNCTION (JSON API)
# -----------------------------
def fetch_articles(outlet_ids, query):
    if not NEWS_API_KEY:
        st.error("❌ NEWS_API_KEY not set in Streamlit secrets")
        return []

    params = {
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "pageSize": 50,
    }

    if query:
        params["q"] = query

    if outlet_ids:
        params["sources"] = ",".join(outlet_ids)

    response = requests.get(
        "https://newsapi.org/v2/everything",
        params=params,
        timeout=10
    )

    if response.status_code != 200:
        st.error(f"API Error: {response.status_code}")
        return []

    return response.json().get("articles", [])

# -----------------------------
# MAIN ACTION
# -----------------------------
if load_articles:
    outlet_ids = [OUTLETS[o] for o in selected_outlets]

    articles = fetch_articles(outlet_ids, search_query)

    if not articles:
        st.warning("No articles found.")
    else:
        st.subheader(f"📰 {len(articles)} Articles Found")

        for a in articles:
            st.markdown(f"### [{a['title']}]({a['url']})")
            st.caption(
                f"{a.get('source', {}).get('name', 'Unknown')} — "
                f"{a.get('publishedAt', '')[:10]}"
            )

            if a.get("description"):
                st.write(a["description"])

            with st.expander("Full context"):
                st.write(a.get("content", "No additional content available."))

            st.divider()

# -----------------------------
# FOOTER
# -----------------------------
st.caption("Powered by NewsAPI.org · JSON-based · Streamlit Cloud Safe")
