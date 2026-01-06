import streamlit as st
import json
import feedparser
from deep_translator import GoogleTranslator
from datetime import datetime

# -----------------------------
# Load news registry
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
# Sidebar settings
# -----------------------------
st.sidebar.header("Settings")

language = st.sidebar.selectbox(
    "Preferred language",
    ["EN", "DE", "FR", "ES", "ZH"],
    index=0
)

auto_refresh = st.sidebar.checkbox(
    "Auto refresh",
    value=True
)

# -----------------------------
# Translation helper
# -----------------------------
def translate_text(text: str) -> str:
    try:
        return GoogleTranslator(
            source="auto",
            target=language.lower()
        ).translate(text)
    except Exception:
        return text

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
        headline = translate_text(entry.title)

        st.markdown(f"### [{headline}]({entry.link})")
        st.caption(
            f"Bias: {outlet['bias']} | "
            f"Reliability: {outlet['reliability']}"
        )

        with st.expander("Summary · Fact check · Opposing views"):
            summary = entry.get("summary", "No summary available.")
            st.write(translate_text(summary))

            st.markdown("**Fact check**")
            st.write("Automated verification pending.")

            st.markdown("**Opposing viewpoints**")
            st.write("Cross-source comparison will appear here.")

    st.divider()

# -----------------------------
# Auto refresh
# -----------------------------
if auto_refresh:
    st.experimental_rerun()
