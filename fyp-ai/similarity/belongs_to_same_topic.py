from datetime import datetime, timezone
import numpy as np
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.compat.v1 import reset_default_graph
from tensorflow.keras.backend import clear_session
from tensorflow.keras.models import load_model as load_tf_model
from typing import List, Union

from models import nlp, STOP_WORDS
from Article import Article

def lemmatizer(doc):
    return " ".join([w.lemma_ for w in doc]) 

def preprocess_article(article: Article):
    ner_types = ["PERSON", "NORP", "ORG", "GPE", "LOC"]

    title = article.title
    title = re.sub("(?i)COVID-19", "coronavirus", title)
    title = re.sub("(?i)COVID19", "coronavirus", title)
    title = re.sub("(?i)COVID", "coronavirus", title)
    title = title.split()

    article.title_clean = " ".join([w for w in title if w not in STOP_WORDS])
    article.nlp_title_clean = nlp(article.title_clean)
    article.title_clean_lemmatized = lemmatizer(article.nlp_title_clean)

    text = article.text
    text = re.sub("(?i)COVID-19", "coronavirus", text)
    text = re.sub("(?i)COVID19", "coronavirus", text)
    text = re.sub("(?i)COVID", "coronavirus", text)
    text = text.split()

    article.text_clean = " ".join([w for w in text if w not in STOP_WORDS])  
    # article.nlp_text_clean = nlp(article.text_clean)
    # article.text_clean_lemmatized = lemmatizer(article.nlp_text_clean)
    # article.title_text_named_entities = [ent.text for ent in article.nlp_title_clean.ents if ent.label_ in ner_types] + [ent.text for ent in article.nlp_text_clean.ents if ent.label_ in ner_types]

    return article

def normalize_vector(v):
    norm = np.linalg.norm(v)
    return v / norm

def euclidean_distance(a, b):
    return np.linalg.norm(a - b)
    
def get_features(article1: Article, article2: Article):
    features: dict = {
        # "is_within_24_hours": None,
        "title_cosine_similarity": None,
        # "title_euclidean_distance": None,
        # "title_count_cosine": None,
        "text_count_cosine_similarity": None,
        # "text_count_euclidean_distance": None,
        # "named_entities_cosine_similarity": None,
        # "named_entities_euclidean_distance": None,
    }

    features["title_cosine_similarity"] = article1.nlp_title_clean.similarity(article2.nlp_title_clean)

    # article1_title_vec = normalize_vector(article1.nlp_title_clean.vector)
    # article2_title_vec = normalize_vector(article2.nlp_title_clean.vector)
    # features["title_euclidean_distance"] = euclidean_distance(article1_title_vec, article2_title_vec)
    
    count_vectorizer = CountVectorizer()
    m = count_vectorizer.fit_transform([article1.text_clean, article2.text_clean]).todense()

    article1_bow_vector = normalize_vector(m[0,:])
    article2_bow_vector = normalize_vector(m[1,:])

    features["text_count_cosine_similarity"] = cosine_similarity(article1_bow_vector, article2_bow_vector).item()
    # features["text_count_euclidean_distance"] = euclidean_distance(article1_bow_vector, article2_bow_vector)

    # article1_named_entities = " ".join(article1.title_text_named_entities)
    # article2_named_entities = " ".join(article2.title_text_named_entities)
    # count_vectorizer = CountVectorizer()
    # m = count_vectorizer.fit_transform([article1_named_entities, article2_named_entities]).todense()
    # article1_named_entities_bow_vector = normalize_vector(m[0,:])
    # article2_named_entities_bow_vector = normalize_vector(m[1,:])
    
    # features["named_entities_cosine_similarity"] = cosine_similarity(article1_named_entities_bow_vector, article2_named_entities_bow_vector).item()
    
    # features["named_entities_euclidean_distance"] = euclidean_distance(article1_named_entities_bow_vector, article2_named_entities_bow_vector)

    return [list(features.values())]

def load_model(model_path = "models/similarity/keras_nn/nn_0"):
    if "keras_nn" in model_path:
        return load_tf_model(model_path)

def belongs_to_same_topic(article1: Article, article2: Article, return_probability: bool = False) -> Union[bool, float]:
    if article1.date_added > article2.date_added:
        is_within_24_hours = 1 if (article1.date_added - article2.date_added).days <= 1 else 0
    else:
        is_within_24_hours = 1 if (article2.date_added - article1.date_added).days <= 1 else 0
    if not is_within_24_hours:
        return False if not return_probability else 0
    
    THRESHOLD = 0.5
    model = load_model()
    p = model.predict(get_features(article1, article2))
    p = p.item()
    result = p >= THRESHOLD if not return_probability else p
    reset_default_graph()
    clear_session()
    return result
