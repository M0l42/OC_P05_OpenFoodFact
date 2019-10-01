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

# payload = {"action": "process",
#            "tag_01": "France",
#            "page_size": 50,
#            "json": 1}


def put_data(url, path):
    with open(path, 'w') as json_file:
        headers = {"user-agent": "python-app/0.0.1"}
        r = requests.get(url, headers=headers, params=payload)
        print(r.status_code)
        print(r.url)
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
    new_product = get_data(chosen_categories['url']+".json",
                           os.path.join(dir_path_product, chosen_categories['name']+'.json'))


with open(json_path) as file:
    categories = json.load(file)


def get_france_data(url, path):
    for i in range(1, 603):
        with open(os.path.join(path, "france_" + str(i) + ".json" ), 'w') as json_file:
            payload = {"action": "process",
                       "tag_01": "France",
                       "page_size": 1000,
                       "page": i,
                       "json": 1}
            headers = {"user-agent": "python-app/0.0.1"}
            r = requests.get(url, headers=headers, params=payload)
            print(r.status_code)
            print(r.url)
            data = r.json()
            json.dump(data, json_file, indent=2)
    return data


france_categories = get_france_data('https://fr.openfoodfacts.org/cgi/search.pl', dir_path_json)

# nutella = get_data("https://world.openfoodfacts.org/api/v0/product/3017620425400.json",
#                    os.path.join(dir_path_product, 'nutella.json'))

with open(os.path.join(dir_path_product, "assortiments_de_sushi.json")) as file:
    product = json.load(file)

print(len(categories['tags']))
print(len(product['products']))

mydb = mysql.connector.connect(
    host='localhost',
    user="nathan",
    passwd="123password",
    database='testdb'
)

print(mydb)

my_cursor = mydb.cursor()

try:
    my_cursor.execute("CREATE DATABASE secondtest")
except mysql.connector.errors.DatabaseError:
    print('database already exist')

my_cursor.execute('SHOW DATABASES')

for db in my_cursor:
    print(db)

my_cursor.execute("SHOW TABLES")

for tb in my_cursor:
    print(tb)
