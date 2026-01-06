# Global News Intelligence Dashboard

This is a **web-based news aggregation and analysis dashboard** built with Streamlit.

## Features
- Aggregates 30+ major global news outlets via rss2json API
- Cross-source clustering (DBSCAN)
- Search articles by topic or keyword
- Placeholder for translation, fact-check, and monetization
- Auto-refresh and manual refresh options
- Shows bias & reliability per source

## How to deploy
1. Create a new app on [Streamlit Cloud](https://streamlit.io/cloud)
2. Upload this folder including:
   - `news_dashboard_full.py`
   - `requirements.txt`
3. Set app main file to `news_dashboard_full.py`
4. Click "Deploy"
5. Done! 🚀

## Notes
- Some RSS feeds may require paid API tiers for full reliability.
- Translation is a placeholder; replace with DeepL/OpenAI API as needed.
