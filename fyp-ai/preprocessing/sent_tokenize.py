import nltk

nltk.download('punkt')

def sent_tokenize(text):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = sent_detector.tokenize(text, realign_boundaries=True)
    return [s.strip() for s in sentences if len(s) > 25]
