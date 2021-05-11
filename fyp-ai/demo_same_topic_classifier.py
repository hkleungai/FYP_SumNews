import configparser
from getpass import getuser

from similarity import preprocess_article, belongs_to_same_topic
from Article import Article
from db_io import *

# TODO: Change the path
config = configparser.ConfigParser()
config.read(f"config/{getuser()}.ini")
if len(config.sections()) == 0:
    config.read("config/default.ini")
    
DB_LOCATION = config["Database"]["path"]

def demo(two_articles):
    p = belongs_to_same_topic(preprocess_article(two_articles[0]), preprocess_article(two_articles[1]))
    print("-" * 100)
    print("Articles:\t" + two_articles[0].title)
    print("\t\t" + two_articles[1].title)
    print(("\033[92mBelong to the same topic" if p else "\033[31mDo not belong to the same topic") + "\033[0m")
    print("-" * 100)

article_group_1 = import_news_group(DB_LOCATION, 1000)
article_group_2 = import_news_group(DB_LOCATION, 1007)
article_group_3 = import_news_group(DB_LOCATION, 1010)
article_group_4 = import_news_group(DB_LOCATION, 1012)

pairs = [
    (article_group_1.articles[0], article_group_1.articles[1]),
    (article_group_1.articles[1], article_group_2.articles[0]),
    (article_group_2.articles[0], article_group_4.articles[0]),
    (article_group_2.articles[1], article_group_4.articles[0]),
    (article_group_2.articles[0], article_group_3.articles[0]),
    (article_group_2.articles[0], article_group_4.articles[0]),
    (article_group_3.articles[0], article_group_4.articles[0]),
]

for pair in pairs:
    demo(pair)
