import requests
import os
import json
import random
from fake_useragent.fake import UserAgent
import mysql.connector


ua = UserAgent()
dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path_json = os.path.join(dir_path, "json")
dir_path_product = os.path.join(dir_path, "product")
os.makedirs(dir_path_json, exist_ok=True)
os.makedirs(dir_path_product, exist_ok=True)
json_path = os.path.join(dir_path_json, "categories.json")


def put_data(url, path):
    with open(path, 'w') as json_file:
        r = requests.get(url, headers="OpenClassroom_P05 - Python - version 1.0 - https://github.com/M0l42/OC_P05_OpenFoodFact", auth=('m042', 'Amilo123'))
        data = r.json()
        json.dump(data, json_file, indent=2)
    return data


def get_data(url, path):
    try:
        with open(path) as json_file:
            data = json.load(json_file)
        if data is None:
            data = put_data(url, path)
    except FileNotFoundError:
        data = put_data(url, path)
    return data


def get_random_categories(data):
    # random.randint(0, data['count'])
    chosen_categories = data['tags'][random.randint(0, data['count'])]
    new_product = get_data(chosen_categories['url']+".json", os.path.join(dir_path_product, chosen_categories['name']+'.json'))


with open(json_path) as file:
    categories = json.load(file)
# categories = get_data('https://fr.openfoodfacts.org/categories.json', json_path)

with open(os.path.join(dir_path_product, "assortiments_de_sushi.json")) as file:
    product = json.load(file)

print(len(categories['tags']))
print(len(product['products']))

mydb = mysql.connector.connect(
    host='localhost',
    user="root",
    passwd="123password"
)

print(mydb)
