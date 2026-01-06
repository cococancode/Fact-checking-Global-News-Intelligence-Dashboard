# Global News Intelligence Dashboard

Hybrid FT + Guardian style dashboard built with Streamlit.

## Features
- Aggregates 30+ major global news outlets via rss2json API
- Search articles by keyword/topic
- Cross-source clustering with DBSCAN
- Translation placeholder (API optional)
- Auto-refresh and manual refresh
- Shows bias & reliability per source
- Elegant FT + Guardian hybrid design

## Deployment
1. Create a new app on [Streamlit Cloud](https://streamlit.io/cloud)
2. Upload the folder including:
   - `news_dashboard_full.py`
   - `requirements.txt`
3. Set main file to `news_dashboard_full.py`
4. Click "Deploy"

## Notes
- Some RSS feeds may require paid API tiers for full reliability
- Translation placeholder can be replaced with OpenAI or DeepL API
