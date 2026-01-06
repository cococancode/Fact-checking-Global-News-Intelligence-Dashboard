import streamlit as st
import json
import feedparser
from datetime import datetime

# -----------------------------
# Load registry
# -----------------------------
with open("news_registry.json", "r", encoding="utf-8") as f:
    outlets = json.load(f)

st.set_page_config(page_title="Global News Intelligence", layout="wide")

# Sidebar controls
st.sidebar.header("Controls")
selected_outlets = st.sidebar.multiselect(
    "Select outlets",
    [o["name"] for o in outlets],
    default=[o["name"] for o in outlets[:5]]
)

# Manual refresh button
if st.sidebar.button("Refresh News"):
    st.experimental_rerun()

# App header
st.title("🌍 Global News Intelligence Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Render news
for outlet in outlets:
    if outlet["name"] not in selected_outlets:
        continue

    st.subheader(outlet["name"])
    feed = feedparser.parse(outlet["rss"])

    for entry in feed.entries[:3]:
        st.markdown(f"### [{entry.title}]({entry.link})")
        st.caption(f"Bias: {outlet.get('bias', 'N/A')} | Reliability: {outlet.get('reliability', 'N/A')}")

        with st.expander("Summary · Fact check · Opposing views"):
            st.write(entry.get("summary", "No summary available"))
            st.write("Fact check: automated analysis pending")
            st.write("Opposing viewpoints: cross-source comparison pending")

    st.divider()
