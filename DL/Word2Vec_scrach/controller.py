from main import get_vector
from fastapi import FastAPI
from main import get_similar_words

api = FastAPI()

@api.get("/similar/{word}")
def similar(word):
    return get_similar_words(word)

@api.get("/vector/{word}")
def vector(word):
    return get_vector(word)