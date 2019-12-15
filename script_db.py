import requests
import os
import json
import random
import mysql.connector


mydb = mysql.connector.connect(
    host='localhost',
    user="nathan",
    password='!Amilo!42',
    database="pure_beurre"
)

my_cursor = mydb.cursor()

my_cursor.execute('CREATE TABLE Categories (Id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(255), '
                  'tags VARCHAR(255), products INTEGER(10))')

# my_cursor.execute('CREATE TABLE Store (Id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(255), tags VARCHAR(255))')

my_cursor.execute('CREATE TABLE Products (Id INT PRIMARY KEY AUTO_INCREMENT,'
                  'name VARCHAR(255), ingredients TEXT, nutrition_grade VARCHAR(1), code INTEGER(20), url TEXT,'
                  'fat_100 INTEGER(10), fat_lvl VARCHAR(10),'
                  'saturated_fat_100 INTEGER(10), saturated_fat_lvl VARCHAR(10),'
                  'sugar_100 INTEGER(10), sugar_lvl VARCHAR(10),'
                  'salt_100 INTEGER(10), salt_lvl VARCHAR(10),'
                  'Categories_id INTEGER, FOREIGN KEY(Categories_id) REFERENCES Categories(Id) ON DELETE CASCADE)')

# my_cursor.execute('CREATE TABLE Product_Store (Id INT PRIMARY KEY AUTO_INCREMENT,'
#                   'Product_id INTEGER, FOREIGN KEY(Product_id) REFERENCES Products(Id) ON DELETE CASCADE,'
#                   'Store_id INTEGER, FOREIGN KEY(Store_id) REFERENCES Store(Id) ON DELETE CASCADE)')

my_cursor.execute('CREATE TABLE Substitute (Id INT PRIMARY KEY AUTO_INCREMENT,'
                  'Product_id INTEGER,'
                  'FOREIGN KEY(Product_id) REFERENCES Products(Id) ON DELETE CASCADE)')

my_cursor.execute('CREATE TABLE Favorite (Id INT PRIMARY KEY AUTO_INCREMENT,'
                  'Product_id INTEGER,'
                  'Substitute_id INTEGER,'
                  'FOREIGN KEY(Product_id) REFERENCES Products(Id) ON DELETE CASCADE,'
                  'FOREIGN KEY(Substitute_id) REFERENCES Substitute(Id) ON DELETE CASCADE)')


headers = {"user-agent": "python-app/0.0.1"}
current_path = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_path, "categories.json")

with open(json_path, 'r') as file:
    data = json.load(file)

sql_formula_category = "INSERT INTO Categories (name, tags, products) VALUES (%s, %s, %s)"
categories_url = "https://fr.openfoodfacts.org/categorie/"
for category in data['tags']:
    name = category['name']
    tags = category['id']
    category_url = url + tags + ".json"
    r = requests.get(category_url, headers=headers)
    product = r.json()["count"]
    my_cursor.execute(sql_formula_category, (name, tags, product))
    mydb.commit()

my_cursor.execute('Select Id, tags, products FROM Categories')

my_result = my_cursor.fetchall()

search_url = "https://fr.openfoodfacts.org/cgi/search.pl?"
sql_formula_product = "INSERT INTO Products (name, nutrition_grade, url," \
                       "fat_100, fat_lvl, saturated_fat_100, saturated_fat_lvl," \
                       "sugar_100, sugar_lvl, salt_100, salt_lvl, Categories_id) " \
                       "VALUES (%s, %s, %s," \
                       "%s, %s, %s, %s," \
                       "%s, %s, %s, %s, %s)"

for Id, tags, products in my_result:
    for i in range(int(products/50)):
        payload = {"action": "process",
                   "tagtype_0": "categories",
                   "tag_contains_0": "contains",
                   "tag_0": tags,
                   "page_size": 50,
                   "sort_by": "unique_scans_n",
                   "json": 1,
                   "page": i}
        r = requests.get(search_url, headers=headers, params=payload)
        data = r.json()
        for product in data["products"]:
            try:
                name = product['product_name']
            except KeyError:
                name = None
            try:
                ingredients = product['ingredients_text']
            except KeyError:
                ingredients = None

            try:
                nutrition_grade = product['nutrition_grades']
            except KeyError:
                nutrition_grade = ''

            url = product['url']

            # stores = product['stores'].split(", ")
            category_id = Id
            code = product['code']

            try:
                salt_100 = product['nutriments']['salt_100g']
            except KeyError:
                salt_100 = None
            try:
                salt_level = product['nutrient_levels']['salt']
            except KeyError:
                salt_level = None

            try:
                sugars_100 = product['nutriments']['sugars_100g']
            except KeyError:
                sugars_100 = None
            try:
                sugars_level = product['nutrient_levels']['sugars']
            except KeyError:
                sugars_level = None

            try:
                fat_100 = product['nutriments']['fat_100g']
            except KeyError:
                fat_100 = None
            try:
                fat_level = product['nutrient_levels']['fat']
            except KeyError:
                fat_level = None

            try:
                saturated_fat_100 = product['nutriments']['saturated-fat_100g']
            except KeyError:
                saturated_fat_100 = None
            try:
                saturated_fat_level = product['nutrient_levels']['saturated-fat']
            except KeyError:
                saturated_fat_level = None

            my_cursor.execute(sql_formula_product, (name, nutrition_grade, url,
                                                    fat_100, fat_level, saturated_fat_100, saturated_fat_level,
                                                    sugars_100, sugars_level, salt_100, salt_level, category_id))
            mydb.commit()

my_cursor.execute('Select * FROM Products')

my_result = my_cursor.fetchall()

for result in my_result:
    print(result)
