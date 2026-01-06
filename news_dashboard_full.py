import streamlit as st
import json
import feedparser
from datetime import datetime

# -----------------------------
# Load registry
# -----------------------------
with open("news_registry.json", "r", encoding="utf-8") as f:
    outlets = json.load(f)

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Global News Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Settings")

language = st.sidebar.selectbox(
    "Preferred language",
    ["Original", "EN", "DE", "FR", "ES", "ZH"],
    index=0
)

auto_refresh = st.sidebar.checkbox("Auto refresh", True)
refresh_interval = st.sidebar.slider(
    "Refresh interval (seconds)",
    min_value=30,
    max_value=300,
    value=60
)

# -----------------------------
# Auto refresh (SAFE)
# -----------------------------
if auto_refresh:
    st.autorefresh(
        interval=refresh_interval * 1000,
        key="news_refresh"
    )

# -----------------------------
# App header
# -----------------------------
st.title("🌍 Global News Intelligence Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# -----------------------------
# Render news
# -----------------------------
for outlet in outlets:
    feed = feedparser.parse(outlet["rss"])

    st.subheader(outlet["name"])

    for entry in feed.entries[:3]:
        st.markdown(f"### [{entry.title}]({entry.link})")
        st.caption(
            f"Bias: {outlet.get('bias', 'N/A')} | "
            f"Reliability: {outlet.get('reliability', 'N/A')}"
        )

        with st.expander("Summary · Fact check · Opposing views"):
            st.write(entry.get("summary", "No summary available"))
            st.write("Fact check: automated analysis pending")
            st.write("Opposing views: cross-source comparison pending")

    st.divider()
