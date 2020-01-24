from script_db import connect_to_database
from models import Product, Category, Favorite, get_all


class UserInterface:
    def __init__(self):
        print("Bonjours !\nBienvenue chez Pur Beurre,")
        self.my_db, self.my_cursor = connect_to_database()

    def choosing_option(self):
        choice = self.check_int(input("Entrer 1 si vous voulez chercher un nouveau produit\n"
                                      "Entrer 2 si vous voulez voir vos produits Favoris\n"
                                      "Entrer 3 pour partir\n"), [1, 2, 3])
        if choice == 1:
            self.get_new_product_favorite()
        elif choice == 2:
            self.show_favorite()
        else:
            self.quit()

    def get_new_product_favorite(self):
        # Find a product to substitute

        ###############################
        #        SHOW CATEGORY        #
        ###############################

        print("Voici toute les categories disponibles : ")
        category_id = self.get_data(Category())

        chosen_category = self.check_int(input("Veuillez entrée le chiffre de la "
                                         "catégorie dont vous désirez voir les produits : \n"), category_id)

        ##############################
        #        SHOW PRODUCT        #
        ##############################

        product_id = self.get_data(Product(), ["category"], [chosen_category])

        chosen_product = self.check_int(input("Veuillez entrée le chiffre du produit que vous voulez choisir : "), product_id)

        #################################
        #        SHOW Substitute        #
        #################################

        nutrition_grades = ["a", "b", "c", "d", "e"]
        substitutes_id = []
        for grade in nutrition_grades:
            substitutes_id = self.get_data(Product(), ["category", "nutrition_grade"],
                                           [chosen_category, grade], substitutes_id)
            if len(substitutes_id) >= 5:
                break

        chosen_substitute = self.check_int(input("Veuillez entrée le chiffre du substitute "
                                           "que vous voulez choisir : \n"), substitutes_id)

        ###############################
        #        Save Favorite        #
        ###############################

        favorie = Favorite()
        favorie.product_id.value = chosen_product
        favorie.substitute_id.value = chosen_substitute
        favorie.insert_data(self.my_cursor)
        self.my_db.commit()

        print("Produit sauvegardé dans Favori")

    def show_favorite(self):
        # Show user's Favorite product and substitute
        # my_cursor.execute("SELECT * FROM Favorite")
        favorite_result = get_all(Favorite(), self.my_cursor)

        select_product = "SELECT name, url FROM Product WHERE Id = %s"

        for favorie in favorite_result:
            self.my_cursor.execute(select_product, (favorie.product_id.value,))
            favorite_product = self.my_cursor.fetchall()
            self.my_cursor.execute(select_product, (favorie.substitute_id.value,))
            favorite_substitute = self.my_cursor.fetchall()
            print("%s, %s" % (favorite_product, favorite_substitute))

    def quit(self):
        print("Au revoir !")

    def get_data(self, model, filter_by=[], value=[], ids_list=[]):
        for i, key in enumerate(filter_by):
            test = getattr(model, key)
            test.value = value[i]

        data = get_all(model, self.my_cursor)
        for prout in data[:5]:
            print("%s : %s" % (prout.id, prout.name.value))
            ids_list.append(prout.id)
        return ids_list

    @staticmethod
    def check_int(choice, value):
        while type(choice) is str:
            try:
                choice = int(choice)
                if choice in value:
                    return choice
                else:
                    choice = input("Veuillez entrer un chiffre valide")
            except ValueError:
                choice = input("Veuillez entrer un chiffre")


if __name__ == '__main__':
    UserInterface().choosing_option()
