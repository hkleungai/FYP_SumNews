import os
import pathlib
import json
from Article import Article
from NewsGroup import NewsGroup

def create_dir_if_not_exist(dir):
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True) 

def save_news_group(news_folder_path: str, news_group: NewsGroup):
    export_path = os.path.join(news_folder_path, "processed_news")
    create_dir_if_not_exist(export_path)
    with open(os.path.join(export_path, f"news{news_group.id}.json"), "w+", encoding="utf-8") as file:
        json.dump(news_group.__dict__, file, ensure_ascii=False)
