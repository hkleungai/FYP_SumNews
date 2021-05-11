import configparser
from random import randrange
import time

from db_io import *
from NewsScraper import NewsScraper

start_time = time.time()
print('Program Start\n')

print('Getting Database path...')
config = configparser.ConfigParser()
config.read("config/default.ini")
DB_LOCATION = config["Database"]["path"]
print('Successfully retrieve Database path.\n')

with NewsScraper() as news_scraper_instance:
    print('Getting article urls from Database...')
    existing_article_urls = news_scraper_instance.get_article_urls_from_db_location(db_location = DB_LOCATION)
    print('Successfully retrieve article urls from Database.\n')

    print('Scraping a new set of article urls...')
    new_article_urls = news_scraper_instance.scrape_article_urls(existing_article_urls = existing_article_urls)
    print('Successfully scrape a new set of article urls.\n')

    print('Downloading news articles from the scraped urls...')
    articles = news_scraper_instance.download_articles_by_urls(article_urls = new_article_urls)
    print('Successfully download news articles from the scraped urls.\n')

    # Around 500 to 600 articles would be scraped in each round,
    # which in total takes 3-4 minutes for the program to terminate.
    print(f'There are {len(articles)} scraped in this round.\n')
    # Randomly picking 20 articles in the scraped results.
    # NOT guaranteed to output articles from all 10 sources for now. 
    for i in range(20):
        article = articles[randrange(len(articles))]
        print(f'---------------- Article {i + 1} ----------------')
        print(f'title: {article.title}')
        print(f'text: {article.text}')
        print(f'date_added: {article.date_added}')
        print(f'url: {article.url}')
        print(f'source: {article.source}')
        print(f'photos_url: {article.photos_url}')
        print(f'is_grouped: {article.is_grouped}')
        print(f'upvotes: {article.upvotes}')
        print(f'downvotes: {article.downvotes}')
        print()

end_time = time.time()
run_time = end_time - start_time 
run_time_in_min, run_time_in_sec = int(run_time) // 60, round(run_time % 60)
print(f"---- The program takes {run_time_in_min} minutes and {run_time_in_sec} seconds to terminate ----")
