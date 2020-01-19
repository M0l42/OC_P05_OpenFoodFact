import requests
import os
import json
import argparse
import mysql.connector
from models import Product, Category, Favorite


def set_params(arg_value, default_value):
    """
    put the default value in the argument if the users didn't put one
    :param arg_value:
    :param default_value:
    :return:
        Value of the argument or the default
    """
    if arg_value:
        return arg_value
    else:
        return default_value


def check_error(check_data, first_arg, second_arg, encode=False):
    """
    Check if the json tags are valid
    :param check_data:
    :param first_arg:
    :param second_arg:
    :param encode:
    :return:
        Value of the tags or None
    """
    try:
        if second_arg:
            return check_data[first_arg][second_arg]
        else:
            if encode:
                return check_data[first_arg].encode("ascii", "ignore")
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

    host = set_params(args.host, 'localhost')
    user = set_params(args.user, 'nathan')
    pwd = args.pwd
    db = set_params(args.database, 'pure-beurre')

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
    Favorite().save(my_cursor)

    # Load the categories stock in a json file,

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
        category_url = categories_url + tags + ".json"
        # Get the number of product available in this category ( can change )
        r = requests.get(category_url, headers=headers)
        product = r.json()["count"]
        my_cursor.execute(sql_formula_category, (name, tags, product))
        mydb.commit()

    my_cursor.execute('Select Id, tags, products FROM Categories')

    my_result = my_cursor.fetchall()

    search_url = "https://fr.openfoodfacts.org/cgi/search.pl?"
    sql_formula_product = "INSERT INTO Products (name, ingredients, nutrition_grade, url, code," \
                          "fat_100, fat_lvl, saturated_fat_100, saturated_fat_lvl," \
                          "sugar_100, sugar_lvl, salt_100, salt_lvl, store, Categories_id) " \
                          "VALUES (%s, %s, %s, %s, %s," \
                          "%s, %s, %s, %s," \
                          "%s, %s, %s, %s, %s, %s)"

    for Id, tags, products in my_result:
        # Load all the product of the category and put in database

        payload = {"action": "process",
                   "tagtype_0": "categories",
                   "tag_contains_0": "contains",
                   "tag_0": tags,
                   "page_size": 50,
                   "sort_by": "unique_scans_n",
                   "json": 1}
        for i in range(int(products/payload["page_size"])):
            payload['page'] = i
            r = requests.get(search_url, headers=headers, params=payload)
            data = r.json()
            for product in data["products"]:
                name = check_error(product, 'product_name', '')
                print(name)
                ingredients = check_error(product, 'ingredients_text_fr', '', True)
                url = product['url']
                code = str(product['code'])

                stores = check_error(product, 'stores', '', True)
                category_id = Id

                nutrition_grade = check_error(product, 'nutrition_grades', '')

                salt_100 = check_error(product, 'nutriments', 'salt_100g')
                salt_level = check_error(product, 'nutrient_levels', 'salt')

                sugars_100 = check_error(product, 'nutriments', 'sugars_100g')
                sugars_level = check_error(product, 'nutrient_levels','sugars')

                fat_100 = check_error(product, 'nutriments', 'fat_100g')
                fat_level = check_error(product, 'nutrient_levels', 'fat')

                saturated_fat_100 = check_error(product, 'nutriments', 'saturated-fat_100g')
                saturated_fat_level = check_error(product, 'nutrient_levels', 'saturated-fat')

                my_cursor.execute(sql_formula_product, (name, ingredients, nutrition_grade, url, code,
                                                        fat_100, fat_level,
                                                        saturated_fat_100, saturated_fat_level,
                                                        sugars_100, sugars_level,
                                                        salt_100, salt_level,
                                                        stores, category_id))
                mydb.commit()


if __name__ == '__main__':
    main()
