import requests
from bs4 import BeautifulSoup
import json
from gradio_client import Client
import streamlit as st

# Initialize Gradio Client for the Pegasus model
client = Client("yuvrajmonga/google-pegasus-cnn_dailymail")


def fetch_rss_feed(rss_url):
    response = requests.get(rss_url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, "xml")  # Parse as XML
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
        return result[0] if isinstance(result, list) and result else "No summary available."
    except Exception as e:
        return f"Failed to summarize the article: {e}"


rss_url = 'https://www.cbsnews.com/latest/rss/main'

# Fetch and process RSS feed
try:
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
                "full_article": full_article
            })

    # Summarize articles
    for item in news_items:
        item['summary'] = summarize_article(item['full_article'])

    # Streamlit App
    st.title("CBS News Articles")

    if news_items:
        for item in news_items:
            st.subheader(item['title'])
            st.write(f"Published on: {item['published']}")
            st.write(item['description'])
            st.image(item['image'], use_column_width=True)
            st.write("[Read Full Article]({})".format(item['link']))
            st.write("### Summary")
            st.write(item['summary'])
            st.markdown("---")
    else:
        st.write("No valid articles found.")

except Exception as e:
    st.error(str(e))
