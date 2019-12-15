from script_db import connect_to_database


def check_int(input_str):
    """
    Function to make sure the user press a number and not something else
    :param input_str:
    :return:
    """
    choice = input(input_str)
    while type(choice) is str:
        try:
            return int(choice)
        except ValueError:
            print("Veuillez entrer un chiffre")
            choice = input(input_str)


def find_substitute(my_cursor, chosen_category, sub_factor, sub_value, max=0):
    """
    Find a substitute depending depending on an certain factor like the nutrition_grades
    :param my_cursor:
    :param chosen_category:
    :param sub_factor:
    :param sub_value:
    :param max:
    :return:
    """
    select_substitute = "SELECT id, name, nutrition_grade FROM Products " \
                        "WHERE Categories_id = %s AND %s = %s" % (chosen_category, sub_factor, sub_value)
    my_cursor.execute(select_substitute)

    substitutes = my_cursor.fetchall()

    for id, name, grade in substitutes[:5-max]:
        print("%s : %s grade : %s" % (id, name, grade))
    return substitutes


def main():
    print("Bonjours !\nBienvenue chez Pur Beurre,")
    choice = 0
    mydb, my_cursor = connect_to_database()

    while choice != 3:
        choice = check_int("Entrer 1 si vous voulez chercher un nouveau produit\n"
                           "Entrer 2 si vous voulez voir vos produits Favoris\n"
                           "Entrer 3 pour partir\n")

        if choice == 1:
            # Find a product to substitute
            my_cursor.execute('Select Id, name, products FROM Categories')

            categories = my_cursor.fetchall()

            print("Voici toute les categories disponibles : ")
            for id, name, product in categories:
                print("%s : %s (%s)" % (id, name, product))

            chosen_category = check_int("Veuillez entrée le chiffre de la "
                                         "catégorie dont vous désirez voir les produits : ")
            select_category = "SELECT id, name FROM Products WHERE Categories_id = %s"
            my_cursor.execute(select_category, (chosen_category, ))

            products = my_cursor.fetchall()
            for id, name in products[:5]:
                print("%s : %s" % (id, name))

            chosen_product = check_int("Veuillez entrée le chiffre du produit que vous voulez choisir : ")

            substitutes = find_substitute(my_cursor, chosen_category, "nutrition_grade", "'a'")
            if len(substitutes) < 5:
                find_substitute(my_cursor, chosen_category, "nutrition_grade", "'b'", len(substitutes))

            chosen_substitute = check_int("Veuillez entrée le chiffre du substitute que vous voulez choisir : ")
            sql_favorite = "INSERT INTO Favorite (Product_id, Substitute_id) VALUES (%s, %s)"
            my_cursor.execute(sql_favorite, (chosen_product, chosen_substitute))
            mydb.commit()

            print("Produit sauvegardé dans Favori")

        elif choice == 2:
            # Show user's Favorite product and substitute
            my_cursor.execute("SELECT * FROM Favorite")
            favorite_result = my_cursor.fetchall()

            select_product = "SELECT name, url FROM Products WHERE Id = %s"

            for Id, product, substitutes in favorite_result:
                my_cursor.execute(select_product, (product,))
                favorite_product = my_cursor.fetchall()
                my_cursor.execute(select_product, (substitutes,))
                favorite_substitute = my_cursor.fetchall()
                print("%s, %s" % (favorite_product, favorite_substitute))


if __name__ == '__main__':
    main()
