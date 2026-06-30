import pandas as pd
from nltk.tokenize import word_tokenize
from gensim.models import Word2Vec

# Load the saved Word2Vec model
model_path = "training/word2vec_model.model"
model = Word2Vec.load(model_path)

def get_vector(word):
    return model.wv[word]

def get_similar_words(word):
    return model.wv.most_similar(word)



