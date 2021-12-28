import newspaper
import psycopg2
import hashlib
import time
from datetime import datetime
import json
import os

dbname = os.environ['DB_NAME']
user = os.environ['DB_USERNAME']
password = os.environ['DB_PASSWORD']
host = os.environ['DB_HOST']

conn = psycopg2.connect(
    f'dbname={dbname} user={user} password={password} host={host}')
cursor = conn.cursor()

records_processed = 0
news_processed = 0

news_number_limit = 20
text_limit = 500


def process_article(news_article, pageId):
    global text_limit
    url_hash = hashlib.md5(str.encode(news_article.url)).hexdigest()

    cursor.execute(cursor.mogrify((
        'INSERT INTO public.news_summaries ('
        'date_published,'
        'date_obtained,'
        'title,'
        'main_text,'
        'main_image_url,'
        'news_source_url,'
        'url_hash,'
        'news_page_id)'
        'VALUES (%s, %s, %s, %s, %s, %s, %s)'), (
        news_article.publish_date,
        datetime.now(),
        news_article.title,
        news_article.text[0:text_limit],
        news_article.top_image,
        news_article.url,
        url_hash,
        pageId,
    )))
    conn.commit()


def scrape_news_website(pageId, pageUrl):
    global news_processed
    global news_number_limit

    news_page = newspaper.build(pageUrl)
    news_counter = 0

    print(f'Total news qty for {pageUrl}: {len(news_page.articles)}.')

    for article in news_page.articles:
        article.download()
        article.parse()

        process_article(article, pageId)

        news_counter += 1
        news_processed += 1
        if(news_counter >= news_number_limit):
            break


def handler(event, context):
    global records_processed
    if('Records' not in event):
        return 'Unsuccesfull. Records not present.'

    for record in event['Records']:
        if('body' in record):
            try:
                content = json.loads(record['body'])
                if('pageId' in content and 'pageUrl' in content):
                    pageId = content['pageId']
                    pageUrl = content['pageUrl']

                    scrape_news_website(pageId, pageUrl)

                    records_processed += 1

            except Exception as e:
                print(e)

    return f'Successfully processed {records_processed} records and {news_processed} news'
