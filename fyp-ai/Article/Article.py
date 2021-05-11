import newspaper
from typing import List, Optional, Union
from datetime import datetime, timezone

'''
Article instance can be constructed in several ways.
1. By injecting a scraped 'Article' instance (under the newspaper module).
2. By a desirably well-formed dictionary.
3. (New, and hacky) By injecting individual entries one-by-one.
   Right now it is (and should only be) used for assisting (1)'s flawed newspaper formation.

**Further Note**:
    Approach (3) is NOT mearnt to be a safe or stable way for constructing newspaper instance,
    since later as the project grows, certain logics in dictionary-processing could be pushed further in __init__(),
    and bypassing those by manually setting each and every entries would then not be a good option.
'''
class Article():
    def __init__(
        self, 
        article: Union[newspaper.article.Article, dict],
        unique_id: Optional[str] = None,
        title: Optional[str] = None,
        text: Optional[str] = None,
        date_added: Optional[str] = None,
        url: Optional[str] = None,
        source: Optional[str] = None,
        photos_url: Optional[str] = None,
        is_grouped: Optional[bool] = None,
        upvotes: Optional[int] = None,
        downvotes: Optional[int] = None,
    ):
        if article == None:
            return
        if type(article) is newspaper.article.Article:
            self.title: str = title if title != None else article.title
            self.text: str = text if text != None else str(article.text)
            self.date_added: str = date_added if date_added != None else (
                str(article.publish_date.replace(tzinfo = timezone.utc)) 
                    if type(article.publish_date) is datetime 
                    else str(datetime.now(timezone.utc))
            )
            self.url: str = url if url != None else article.url
            self.source: str = source if source != None else article.meta_data['og'].get('site_name', '')
            self.photos_url: List[str] = photos_url if photos_url != None else list(article.images)
            self.is_grouped: bool = is_grouped if is_grouped != None else False
            self.upvotes: int = upvotes if upvotes != None else 0
            self.downvotes: int = downvotes if downvotes != None else 0
        elif type(article) is dict:
            self.id: str = unique_id if unique_id != None else article.get('_id', '') #TODO
            self.title: str = title if title != None else article.get('title', '')
            self.text: str = text if text != None else article.get('text', '')
            # article.get('date_added'] = date_added if date_added != None else article['date_added', None).replace('Z', '+00:00')
            self.date_added: datetime = date_added if date_added != None else (
                datetime.fromisoformat(article.get('date_added', str(datetime.now(timezone.utc))).replace('Z', '+00:00'))
            )
            self.url: str = url if url != None else article.get('url', '')
            self.source: str = source if source != None else article.get('source', '')
            self.photos_url: List[str] = photos_url if photos_url != None else article.get('photos_url', [])
            self.is_grouped: bool = is_grouped if is_grouped != None else article.get('is_grouped', False)
            self.upvotes: int = upvotes if upvotes != None else article.get('upvotes', 0)
            self.downvotes: int = downvotes if downvotes != None else article.get('downvotes', 0)
