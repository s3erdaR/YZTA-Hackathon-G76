import random
import os
import pickle
from fastapi import APIRouter

router = APIRouter()

_SENTENCES = [
    "Kedi ağaçta uyuyor.",
    "Çocuklar parkta oynuyor.",
    "Bugün hava çok güzel.",
    "Ayşe 5 tane elma yedi.",
    "Top yuvarlandı.",
    "Efe kitap okuyor.",
    "Anne yemek yapıyor.",
    "Babam işe gidiyor.",
    "Kalem kutuda duruyor.",
    "Kapı açık kaldı.",
    "Araba kırmızı renkli.",
    "Kuşlar gökyüzünde uçuyor.",
    "Masa üstünde 3 defter var.",
    "Sınıf çok sessizdi.",
    "Kalemle resim çizdim.",
    "Oyuncak ayım yatağımda.",
    "Çiçekler bahçede açtı.",
    "Yemekte makarna vardı.",
    "Deniz çok mavi görünüyor.",
    "Kardeşimle oyun oynadım."
]

_USED_SENTENCES = set()

def get_random_sentence():
    global _USED_SENTENCES
    available = list(set(_SENTENCES) - _USED_SENTENCES)
    if not available:
        _USED_SENTENCES = set()
        available = _SENTENCES.copy()
    choice = random.choice(available)
    _USED_SENTENCES.add(choice)
    save_used_sentences()
    return choice

def save_used_sentences():
    with open('used_sentences.pickle', 'wb') as f:
        pickle.dump(_USED_SENTENCES, f)

def load_used_sentences():
    global _USED_SENTENCES
    if os.path.exists('used_sentences.pickle'):
        with open('used_sentences.pickle', 'rb') as f:
            _USED_SENTENCES = pickle.load(f)

load_used_sentences()

@router.get("/sentence")
def get_sentence():
    sentence = get_random_sentence()
    return {"sentence": sentence}