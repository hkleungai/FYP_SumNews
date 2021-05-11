from datetime import datetime
from typing import List, Union
import json
import requests
import uuid

from Article import Article
from similarity import preprocess_article, belongs_to_same_topic

# Considering ours is a small site with only small datasets,
# the probability of articles not colliding to any group is quite high.
# Plus belongs_to_same_topic() seems to be a heavy computation,
# so instead of putting it into list comprehension to do cpmputation in each item, 
# we shall use 'raw loop' and break the calculation whenever necessary
def is_news_not_belongs_to_group(news_x, group_y):
    count_different_topic = 0
    for y in group_y:
        count_different_topic += int(x.id == y.id or not belongs_to_same_topic(x, y))
        if count_different_topic >= len(group_y) / 2:
            return True
    return False

def add_articles_to_current_clusters(API_URL, selected_ungrouped_article_id_list):
    news_groups = requests.get(f"{API_URL}/news?should_get_articles_and_id_only=true").json()
    news_groups_with_preprocessed_articles = []

    for ng in news_groups:
        news_group_with_preprocessed_articles = []
        for article_id in ng["articles"]:
            news_group_with_preprocessed_articles.append(preprocess_article(Article(requests.get(f"{API_URL}/articles/{article_id}").json())))
        news_groups_with_preprocessed_articles.append(news_group_with_preprocessed_articles)

    ungrouped_article_ids = requests.get(f"{API_URL}/articles/?is_grouped=false&should_get_features_for_preprocessing=true").json()
    ungrouped_articles = [Article(a) for a in ungrouped_article_ids if a['_id'] in selected_ungrouped_article_id_list]
    ungrouped_preprocessed_articles = [preprocess_article(a) for a in ungrouped_articles]

    updated_news_group_ids = set()
    for i in range(len(news_groups_with_preprocessed_articles)):
        for x in ungrouped_preprocessed_articles:
            if x.is_grouped or is_news_not_belongs_to_group(x, news_groups_with_preprocessed_articles[i]): 
                continue
            print(f'Has same topic, {news_groups[i]["_id"]}, {x.id}')
            updated_news_group_ids.add(news_groups[i]["_id"])
            news_groups[i]["articles"].append(x.id)
            x.is_grouped = True
    print(f'updated_news_group_ids: {list(updated_news_group_ids)}')
    
    for ng in news_groups:
        ng_id = ng["_id"]
        if ng_id in updated_news_group_ids:
            requests.put(f"{API_URL}/news/{ng_id}", json = { "articles": ng["articles"] })

    return list(updated_news_group_ids)

def cluster_ungrouped_articles(API_URL, selected_ungrouped_article_id_list):
    from NewsGroup import NewsGroup
    articles = requests.get(f'{API_URL}/articles/?is_grouped=false&should_get_features_for_preprocessing=true').json()
    articles = [Article(a) for a in articles if a['_id'] in selected_ungrouped_article_id_list]
    articles = [a for a in articles if a.date_added >= datetime.fromisoformat('2020-09-29T00:00:00.000+00:00')]

    ungrouped_preprocessed_articles = [preprocess_article(a) for a in articles]
    print(f'len(ungrouped_preprocessed_articles) in cluster_ungrouped_articles: {len(ungrouped_preprocessed_articles)}')
    clusters = []
    for article in ungrouped_preprocessed_articles:
        cluster = set()
        for another_article in ungrouped_preprocessed_articles:
            # Seem costly to compute on same id pairs
            if another_article.is_grouped or article.id == another_article.id or not belongs_to_same_topic(article, another_article):
                continue
            print(f'Has same topic, {article.id}, {another_article.id}')
            if not article.is_grouped:
                article.is_grouped = True
                cluster.add(article.id)
            another_article.is_grouped = True
            cluster.add(another_article.id)
        if (len(cluster)):
            clusters.append(cluster)

    ngs = [NewsGroup(list(cluster), str(uuid.uuid4().hex)).__dict__ for cluster in clusters]
    news_group_ids = requests.post(f"{API_URL}/news", json=ngs).json()

    return news_group_ids
