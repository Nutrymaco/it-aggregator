from word_parse.parse import lemmatization
import redis
from aggregator.settings import INVERT_TEXT_INDEX_REDIS_DB, \
    INVERT_KEY_WORD_INDEX_REDIS_DB, \
    COUPLE_WORD_REDIS_DB, REDIS_HOST


# TODO: improve alghoritm with NLP
def get_id_dict_from_key_words(key_words) -> dict:
    r = redis.Redis(db=INVERT_KEY_WORD_INDEX_REDIS_DB, host=REDIS_HOST)
    id_set = r.sinter([key_word for key_word in key_words])
    id_dict = dict()
    for id in id_set:
        id_dict[id] = get_text_score_by_id(id, key_words)

    return id_dict


def get_text_score_by_id(text_id, base_key_words):
    score = 0
    r_invert = redis.Redis(db=INVERT_TEXT_INDEX_REDIS_DB, host=REDIS_HOST)
    r_couple = redis.Redis(db=COUPLE_WORD_REDIS_DB, host=REDIS_HOST)
    couple_key_words = []
    for base_key_word in base_key_words:
        couple_key_words.append(r_couple.smembers(base_key_word))

    text_key_words = r_invert.smembers(text_id)
    for text_key_word in text_key_words:
        if text_key_word in couple_key_words:
            score += 1

    return score
