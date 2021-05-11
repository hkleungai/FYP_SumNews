import os
import pathlib
import json
from Article import Article
from NewsGroup import NewsGroup

def import_news_group(news_folder_path: str, news_id: str):
    export_path = os.path.join(news_folder_path, "news", f"news{news_id}")
    article_file_names = [filename for filename in os.listdir(export_path) if filename.endswith(".json")]
    articles = []
    for article_file_name in article_file_names:
        with open(os.path.join(export_path, article_file_name), "r", encoding="utf-8") as file:
            article = Article(article = json.load(file))
            articles.append(article)
            
    return NewsGroup(articles, news_id)
