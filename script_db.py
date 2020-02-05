import requests
import os
import json
import argparse
import mysql.connector
from models import Product, Category, Favorite, get_all, Substitute
from settings import DB_CONFIG


def set_params(arg_value, default_key):
    """
    put the default value in the argument if the users didn't put one
    :param arg_value:
    :param default_key:
    :return:
        Value of the argument or the default
    """
    if arg_value:
        return arg_value
    else:
        return DB_CONFIG[default_key]


def check_error(check_data, first_arg, second_arg):
    """
    Check if the json tags are valid
    :param check_data:
    :param first_arg:
    :param second_arg:
    :return:
        Value of the tags or None
    """
    try:
        if second_arg:
            return check_data[first_arg][second_arg]
        else:
            return check_data[first_arg]
    except KeyError:
        return None


def connect_to_database():
    """
    connect to the database
    create database if it doens't exist
    :return:
        database
        cursor
    """
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        '--host', type=str, dest='host',
    )
    parser.add_argument(
        '-U', '--username', type=str, dest='user',
    )
    parser.add_argument(
        '-p', '--password', type=str, dest='pwd',
    )
    parser.add_argument(
        '-d', '--database', type=str, dest='database',
    )

    args = parser.parse_args()

    host = set_params(args.host, 'host')
    user = set_params(args.user, 'user')
    pwd = set_params(args.pwd, 'password')
    db = set_params(args.database, 'name')

    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=pwd,
    )

    my_cursor = mydb.cursor()

    my_cursor.execute("CREATE DATABASE IF NOT EXISTS %s" % db)

    mydb.connect(database=db)
    return mydb, my_cursor


def main():
    mydb, my_cursor = connect_to_database()

    # Creating our tables

    Category().save(my_cursor)
    Product().save(my_cursor)
    Substitute().save(my_cursor)
    Favorite().save(my_cursor)

    # Load the categories stock in a json file,

    headers = {"user-agent": "python-app/0.0.1"}
    current_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_path, "categories.json")

    with open(json_path, 'r') as file:
        data = json.load(file)

    categories_url = "https://fr.openfoodfacts.org/categorie/"
    for category in data['tags']:
        new_category = Category()
        new_category.name.value = category['name']
        new_category.tags.value = category['id']
        category_url = categories_url + new_category.tags.value + ".json"
        # Get the number of product available in this category ( can change )
        r = requests.get(category_url, headers=headers)
        new_category.products.value = r.json()["count"]
        new_category.insert_data(my_cursor)
        mydb.commit()

    categories = get_all(Category(), my_cursor)

    search_url = "https://fr.openfoodfacts.org/cgi/search.pl?"

    for category in categories:
        # Load all the product of the category and put in database

        payload = {"action": "process",
                   "tagtype_0": "categories",
                   "tag_contains_0": "contains",
                   "tag_0": category.tags.value,
                   "page_size": 50,
                   "sort_by": "unique_scans_n",
                   "json": 1}
        for i in range(int(category.products.value/payload["page_size"])):
            payload['page'] = i
            r = requests.get(search_url, headers=headers, params=payload)
            data = r.json()
            for product in data["products"]:
                new_product = Product()
                new_product.name.value = check_error(product, 'product_name', '')
                new_product.ingredients.value = check_error(product, 'ingredients_text_fr', '') # true
                new_product.url.value = product['url']
                new_product.code.value = str(product['code'])

                new_product.store.value = check_error(product, 'stores', '') # true
                new_product.category.value = category.id

                new_product.nutrition_grade.value = check_error(product, 'nutrition_grades', '')

                new_product.salt_100.value = check_error(product, 'nutriments', 'salt_100g')
                new_product.salt_lvl.value = check_error(product, 'nutrient_levels', 'salt')

                new_product.sugar_100.value = check_error(product, 'nutriments', 'sugars_100g')
                new_product.sugar_lvl.value = check_error(product, 'nutrient_levels','sugars')

                new_product.fat_100.value = check_error(product, 'nutriments', 'fat_100g')
                new_product.fat_lvl.value = check_error(product, 'nutrient_levels', 'fat')

                new_product.saturated_fat_100.value = check_error(product, 'nutriments', 'saturated-fat_100g')
                new_product.saturated_fat_lvl.value = check_error(product, 'nutrient_levels', 'saturated-fat')

                new_product.insert_data(my_cursor)

                mydb.commit()


if __name__ == '__main__':
    main()
