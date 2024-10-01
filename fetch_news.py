import requests
from bs4 import BeautifulSoup
import json
from gradio_client import Client
from pymongo import MongoClient
import streamlit as st

# MongoDB connection string
MONGO_URL = 'mongodb+srv://mirzanausadallibaig:Sahil%23123@cluster0.mhg9q.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

# Initialize MongoDB client
mongo_client = MongoClient(MONGO_URL)
db = mongo_client['news_articles']
collection = db['articles']

# Initialize the summarization model
client = Client("yuvrajmonga/google-pegasus-cnn_dailymail")

def fetch_rss_feed(rss_url):
    response = requests.get(rss_url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, "xml")
    else:
        raise Exception(f"Failed to fetch RSS feed: {response.status_code}")

def scrape_full_article(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        article_body = soup.find('section', class_='content__body')
        if article_body:
            return '\n'.join([p.get_text() for p in article_body.find_all('p')])
        return 'Full article content not found.'
    return 'Failed to retrieve the full article.'

def summarize_article(article_text):
    try:
        result = client.predict(param_0=article_text, api_name="/predict")
        if isinstance(result, str):
            import re
            match = re.search(r'SummarizationOutput\(summary_text=("[^"]*"|\'[^\']*\')\)', result)
            if match:
                summary = match.group(1).strip('\"\'')
                summary = summary.replace('<n>', ' ')
                return summary.strip()
        return "Summary not available."
    except Exception as e:
        return f"Failed to summarize the article: {e}"

def fetch_and_save_articles():
    rss_url = 'https://www.cbsnews.com/latest/rss/main'
    feed = fetch_rss_feed(rss_url)
    news_items = []

    for item in feed.find_all('item'):
        title = item.title.text
        link = item.link.text
        description = item.description.text
        published = item.pubDate.text if item.pubDate else 'No publication date'
        image = item.image.text if item.image else ''

        full_article = scrape_full_article(link)

        if full_article != 'Full article content not found.':
            news_items.append({
                "title": title,
                "link": link,
                "description": description,
                "published": published,
                "image": image,
                "full_article": full_article,
                "summary": summarize_article(full_article)  # Summarize during fetching
            })

    # Insert articles into MongoDB
    if news_items:
        collection.insert_many(news_items)

# Streamlit UI
st.title("News Articles")

# Button to fetch and save new articles
if st.button("Update News"):
    fetch_and_save_articles()
    st.success("Articles updated successfully!")

# Fetch and display articles from MongoDB
articles = collection.find()
if articles:
    for article in articles:
        st.subheader(article['title'])
        st.write(article['full_article'])
        st.write(f"[Read more]({article['link']})")
        st.write(f"Published: {article['published']}")
        st.image(article['image'])
        st.write("Summary:")
        st.write(article['summary'])
        st.write("---")
else:
    st.write("No articles found in the database.")
