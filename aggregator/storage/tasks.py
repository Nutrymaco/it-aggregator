from aggregator.celery import app
from .models import Vacancy
import pymorphy2
from word_parse.parse import delete_tags
import requests
from datetime import datetime
import redis
import json

@app.task
def write_to_cache(r, text, text_index):
    morph = pymorphy2.MorphAnalyzer()
    text = delete_tags(text)
    for word in text.split(' '):
        if word.isalpha():
            result = morph.parse(word)[0]
            if any(word_type in result.tag for word_type in
                   ['PREP', 'INTJ', 'PRCL', 'PRED', 'CONJ']):
                continue
            normal_word = result.normal_form
            if r.exists(normal_word):
                if r.hexists(normal_word, text_index):
                    r.hincrby(normal_word, text_index, 1)
                else:
                    r.hset(normal_word, text_index, 1)
            else:
                r.hset(normal_word, text_index, 1)


# TODO: set up settings.py for redis
@app.task
def hh_scrapper(base_url='https://api.hh.ru/vacancies', start_shift=24*3600, specialization_list=[1]):
    now_datetime = datetime.now()
    time = now_datetime.timestamp()
    date = now_datetime.strftime("%Y-%m-%dT%H:%M:%S").__str__()
    response = requests.get(base_url, params={'specialization': specialization_list, 'per_page': 100}).json()
    vacancy_count = response['found']
    actual_id_vacancies_list = []
    r = redis.Redis()

    if vacancy_count <= 2000:
        vacancy_list = response['items']
        vacancy_pages = response['pages']
        for page in range(1, vacancy_pages):
            response = requests.get(
                base_url, params={'page': page, 'specialization': specialization_list, 'per_page': 100}).json()
            vacancy_list[-1:] = response
            for vac in response['items']:
                response = json.loads(requests.get(vac['url']).json())

                if not Vacancy.objects.filter(name=response['name'], company=response['company']):
                    # TODO: refactor db
                    vacancy = Vacancy.objects.create(name=response['name'], long_description=response['description'])
                    vacancy.save()

                    # adding to redis cache
                    text_index = vacancy.id
                    text = vacancy.long_description

                    write_to_cache(r, text, text_index).delay()
                    actual_id_vacancies_list.append(text_index)

    else:
        vacancy_list = []
        while vacancy_count > 0:
            while True:
                response = requests.get(
                    base_url, params=
                    {'specialization': specialization_list,
                     'per_page': 100,
                     'date_from': datetime.fromtimestamp(time - start_shift).strftime("%Y-%m-%dT%H:%M:%S"),
                     'date_to': date
                     }).json()
                if response['found'] > 2000:
                    start_shift -= 3600
                else:
                    break

            for page in range(response['pages']):
                response = requests.get(
                    base_url, params=
                    {'specialization': specialization_list,
                     'per_page': 100,
                     'page': page,
                     'date_from': datetime.fromtimestamp(time - start_shift).strftime("%Y-%m-%dT%H:%M:%S"),
                     'date_to': date
                     }).json()
                vacancy_list[-1:] = response['items']
                vacancy_count -= len(response['items'])

                # final point
                for vac in response['items']:
                    response = requests.get(vac['url']).json()

                    if not Vacancy.objects.filter(name=response['name'], company=response['company']):
                        # TODO: refactor db
                        vacancy = Vacancy.objects.create(name=response['name'], long_description=response['description'])
                        vacancy.save()

                        # adding to redis cache
                        text_index = vacancy.id
                        text = vacancy.long_description

                        write_to_cache(r, text, text_index).delay()
                        actual_id_vacancies_list.append(text_index)

            date = datetime.fromtimestamp(time - start_shift).strftime("%Y-%m-%dT%H:%M:%S")
            time -= start_shift
            start_shift = 24*3600


    all_id_list = Vacancy.objects.values_list('id')
    id_to_delete = [id_v for id_v in all_id_list if id_v not in actual_id_vacancies_list]
    index(r, id_to_delete)


@app.task
def scraper2():
    ...


def index(r, id_to_delete):
    # транзакционно удаляем из редиса
    keys = r.keys('*')  # возможно потом тут будет word_
    for key in keys:
        for id in id_to_delete:
            r.hdel(key, id)


    # подчищаем бд
    for vacancy_id in id_to_delete:
        Vacancy.objects.get(id=vacancy_id).delete()






@app.task
def scrape_and_index():
    hh_scrapper.delay()

@app.task
def recovery():
    ...
