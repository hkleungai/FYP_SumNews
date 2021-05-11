import os
import pathlib
import json
import uuid
from Article import Article

def create_dir_if_not_exist(dir):
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True) 
        
def save_article(article: Article, news_folder_path: str, news_index: int):
    export_path = os.path.join(news_folder_path, "news", "news" + f"{news_index}".zfill(3))
    create_dir_if_not_exist(export_path)
    with open(os.path.join(export_path, f"{str(uuid.uuid4().hex)}.json"), "w+", encoding="utf-8") as file:
        json.dump(article.__dict__, file, ensure_ascii=False)

