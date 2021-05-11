from Article import Article
from typing import List
from datetime import datetime, timezone

from similarity import find_related_news 

class NewsGroup():
    def __init__(self, articles: List[Article], id_: str):
        self.id: str = id_
        self.articles: List[Article] = articles
        self.summary: dict = {
            "top": [],
            "originals": {},
        }
        self.photos = []
        self.creation_datetime: datetime = str(datetime.now(timezone.utc))
        self.update_datetime: datetime = self.creation_datetime
        self.vector = []
        self.related_news_groups: List[str] = []
    
    def add_article(self, article: Article):
        self.articles.append(article)
        self.update_datetime = str(datetime.now(timezone.utc))

    def process(self, API_URL):
        self._summarize()
        self._find_best_photos()
        self._find_related_news_groups(API_URL)
        self.update_datetime = str(datetime.now(timezone.utc))
    
    def _summarize(self):
        from summarization import summarize
        articles = self.articles
        self.summary, self.vector = summarize(articles)
        self.vector = self.vector.tolist()
    
    def _find_best_photos(self):
        pass

    def _find_related_news_groups(self, API_URL):
        self.related_news_groups = find_related_news(API_URL, self.id, self.vector)

