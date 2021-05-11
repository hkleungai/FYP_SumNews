import requests
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.compat.v1 import reset_default_graph
from tensorflow.keras.backend import clear_session

def find_related_news(API_URL: str, news_id: str, news_vector: list):
    news_vector = np.array(news_vector)
    res = requests.get(f'{API_URL}/news?should_get_vector_and_id_only=true').json()

    news_vectors = {news["_id"]: np.array(news["vector"]) for news in res if len(news["vector"]) > 0}

    cos_sim = {n: cosine_similarity([news_vector], [news_vectors[n]]).item() for n in news_vectors}
        
    cos_sim = {k: v for k, v in sorted(cos_sim.items(), key=lambda item: item[1], reverse=True)}
    
    related_news_ids = [x for x in cos_sim if cos_sim[x] >= 0.4 and x != news_id]

    reset_default_graph()
    clear_session()
    
    return related_news_ids
