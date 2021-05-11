import math
import numpy as np
import os
import tensorflow_hub as hub
from tensorflow.compat.v1 import reset_default_graph
from tensorflow.keras.backend import clear_session
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

from Article import Article
from preprocessing import sent_tokenize
from models import nlp

os.environ["TFHUB_CACHE_DIR"] = ".cache/tfhub_modules"

def get_article_from_sentence(sentence: str, articles: List[Article]):
    for article in articles:
        if sentence in article.sentences:
            return article

def calculate_sentence_and_centroid_embeddings(sentences):
    usel = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")
    sentence_embeddings = usel(sentences)
    centroid_embedding = np.mean(sentence_embeddings, 0)

    return sentence_embeddings, centroid_embedding

def calculate_sentence_originality_score(sns, sps, sentence_pairwise_similarities, article_sentences_range):
    sentence_pairwise_similarities = np.array(sentence_pairwise_similarities)
    print("Calculating sentence dissimilar score")
    # Sentence dissimilar score
    sds = []
    for article_title, r in article_sentences_range.items():
        for i in range(*r):
            sentence_pairwise_similarities[i][r[0]:r[1]] = -1
            sds.append(1 - np.max(sentence_pairwise_similarities[i]))

    sds = np.array(sds)

    # print("Calculating sentence length score")
    # # Sentence length score
    # max_sentence_length = max([len((sentence).split()) for sentence in sentences])
    # sls = np.array([len((sentence).split()) / max_sentence_length for sentence in sentences])

    C4, C5 = 0.9, 0.1
    originality_score = C4 * sds + C5 * sns

    originality_score_convl = np.array(originality_score)

    C6, C7 = 0.9, 0.1

    for i in range(originality_score.shape[0]):
        if i == 0:
            originality_score_convl[i] = C6 * originality_score[i] + C7 * originality_score[i+1]
        elif i == originality_score.shape[0] - 1:
            originality_score_convl[i] = C6 * originality_score[i] + C7 * originality_score[i-1]
        else:
            originality_score_convl[i] = C6 * originality_score[i] + C7 * (originality_score[i-1] + originality_score[i+1]) / 2

    return originality_score_convl

def calculate_sentence_scores(sentence_embeddings, centroid_embedding, sentences, article_sentences_range, articles):
    print("Calculating sentence content relevance score")
    # Sentence content relevance score
    centroid_embedding = np.array([centroid_embedding])
    scrs = np.array([cosine_similarity([sentence_embedding], centroid_embedding).item() for sentence_embedding in sentence_embeddings])

    print("Calculating sentence pairwise similarity")
    # Sentence pairwise similarity
    sentence_pairwise_similarities = cosine_similarity(sentence_embeddings)
    for i in range(sentence_pairwise_similarities.shape[0]):
        sentence_pairwise_similarities[i][i] = 0

    print("Calculating sentence novelty score")
    # Sentence novelty score
    sns = []
    SENTENCE_PAIRWISE_SIMILARITY_THRESHOLD = 0.95
    for i in range(sentence_embeddings.shape[0]):
        max_pairwise_similarity = np.max(sentence_pairwise_similarities[i])
        if max_pairwise_similarity < SENTENCE_PAIRWISE_SIMILARITY_THRESHOLD:
            sns.append(1)
        elif max_pairwise_similarity > SENTENCE_PAIRWISE_SIMILARITY_THRESHOLD and scrs[i] > scrs[np.argmax(sentence_pairwise_similarities[i])]:
            sns.append(1)
        else:
            sns.append(1 - max_pairwise_similarity)
    sns = np.array(sns)

    print("Calculating sentence position score")
    # Sentence position score
    sps = []
    for i in range(sentence_embeddings.shape[0]):
        article = get_article_from_sentence(sentences[i], articles)
        article_sentences = article.sentences
        sps.append(
            max(0.5, math.exp(-(article_sentences.index(sentences[i]) + 1) / len(article_sentences) ** (1 / 3)))
        )
    sps = np.array(sps)
    
    C1, C2, C3 = 0.6, 0.2, 0.2
    final_score = C1 * scrs + C2 * sns + C3 * sps


    for i in range(sentence_pairwise_similarities.shape[0]):
        sentence_pairwise_similarities[i][i] = 1

    return final_score, calculate_sentence_originality_score(sns, sps, sentence_pairwise_similarities, article_sentences_range), scrs, sns, sps, sentence_pairwise_similarities

def summarize(articles: List[Article]):
    sentences = []
    article_sentences_range = {} # Key: Article title; Value: Tuple(Starting index of the article in `sentences`, Ending index of the article in `sentences` + 1)

    for article in articles:
        sents = sent_tokenize(article.text)
        article.sentences = sents
        article_sentences_range[article.title] = (len(sentences), len(sentences) + len(sents))
        for s in sents:
            sentences.append(s)
    print("Number of sentences: ", len(sentences))
    sentence_embeddings, centroid_embedding = calculate_sentence_and_centroid_embeddings(sentences)
    final_score, originality_score, _, _, _, sentence_pairwise_similarities = calculate_sentence_scores(sentence_embeddings, centroid_embedding, sentences, article_sentences_range, articles)

    summary = {}

    # Top N most important sentences
    N = 3
    sentence_indices = []
    for i in range(N):
        max_score = -1
        max_score_index = -1
        for j in range(final_score.shape[0]):
            if final_score[j] > max_score and j not in sentence_indices:
                max_score = final_score[j]
                max_score_index = j
        sentence_indices.append(max_score_index)

    # sentence_indices.sort()

    summary["top"] = [sentences[x] for x in sentence_indices]

    original_sentence_indices = []
    for i in range(originality_score.shape[0]):
        max_score = -1
        max_score_index = -1
        for j in range(originality_score.shape[0]):
            if originality_score[j] > max_score and j not in sentence_indices and j not in original_sentence_indices:
                max_score = originality_score[j]
                max_score_index = j
        original_sentence_indices.append(max_score_index)

    original_summaries = {}
    for x in original_sentence_indices:
        article_id = get_article_from_sentence(sentences[x], articles).id
        original_summaries[article_id] = original_summaries.get(article_id, [])
        original_summaries[article_id].append(x)
    
    print(original_summaries)

    for article_id in original_summaries:
        original_summaries[article_id] = original_summaries[article_id][:2]
        original_summaries[article_id].sort()
        original_summaries[article_id] = [sentences[x] for x in original_summaries[article_id] if x != -1]

    summary["originals"] = original_summaries

    reset_default_graph()
    clear_session()

    return summary, centroid_embedding

def summarize_with_textrank(articles: List[Article]):
    sentences = [s for article in articles for s in sent_tokenize(article.text)]
    from gensim.summarization.summarizer import summarize
    summary = {}
    summary["top"] = summarize("\n".join(sentences), ratio=3/len(sentences), split=True)

    summary["originals"] = {}
    return summary
