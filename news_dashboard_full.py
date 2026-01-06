
import streamlit as st
import json, feedparser, random
from googletrans import Translator
from datetime import datetime

with open('news_registry.json','r',encoding='utf-8') as f:
    outlets=json.load(f)

st.set_page_config(page_title='Global News Intelligence',layout='wide')
translator=Translator()

st.sidebar.header('Settings')
lang=st.sidebar.selectbox('Language',['EN','DE','FR','ES','ZH'])
auto=st.sidebar.checkbox('Auto Refresh',True)

def translate(t):
    try:
        return translator.translate(t,dest=lang.lower()).text
    except:
        return t

st.title('🌍 Global News Intelligence Dashboard')
st.caption(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

for o in outlets:
    feed=feedparser.parse(o['rss'])
    st.subheader(o['name'])
    for e in feed.entries[:3]:
        st.markdown(f"**[{translate(e.title)}]({e.link})**")
        st.caption(f"Bias: {o['bias']} | Reliability: {o['reliability']}")
        with st.expander('Summary · Fact check · Opposing views'):
            st.write(translate(e.get('summary','No summary')))
            st.write('Fact-check: AI review pending')
            st.write('Opposing viewpoints: cross-source analysis')
    st.divider()

if auto:
    st.experimental_rerun()
