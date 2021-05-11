import configparser
from getpass import getuser

from summarization import summarize, summarize_with_textrank
from Article import Article
from db_io import *

# TODO: Change the path
config = configparser.ConfigParser()
config.read(f"config/{getuser()}.ini")
if len(config.sections()) == 0:
    config.read("config/default.ini")
    
DB_LOCATION = config["Database"]["path"]
API_URL = "http://localhost:3000"

def print_summary(summary):
    print("************ Top ************")
    print("\n".join(summary["top"]))
    print()

    print("************ Originals ************")
    for title in summary["originals"]:
        print(title, ":")
        for s in summary["originals"][title]:
            print("\t", s)
        print()

def demo(article_group):
    print("Summarized with centroid approach and sentence embeddings")
    print_summary(article_group.summary)
    print(article_group.related_news_groups)

    # print("\n\n")
    # print("Summarized with Textrank: ")
    # textrank_summary = summarize_with_textrank(article_group)
    # print_summary(textrank_summary)

article_group_1 = import_news_group(DB_LOCATION, 1011)
article_group_1.process(API_URL)
demo(article_group_1)
# save_news_group(DB_LOCATION, article_group_1)
