from script_db import connect_to_database
from models import Product, Category, Favorite, get_all, Substitute


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

        chosen_product = self.check_int(input("Veuillez entrée le chiffre du produit que vous voulez choisir : "),
                                        product_id)

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

        #################################
        #        Save Substitute        #
        #################################

        substitute = Product()
        substitute.id = chosen_substitute
        new_substitute = Substitute()
        result = get_all(substitute, self.my_cursor)
        for key in result[0].__dict__:
            if key != "id":
                value = getattr(result[0], key).value
                getattr(new_substitute, key).value = value
        sub_id = new_substitute.insert_data(self.my_cursor)

        ###############################
        #        Save Favorite        #
        ###############################

        favorite = Favorite()
        favorite.product_id.value = chosen_product
        favorite.substitute_id.value = sub_id
        favorite.insert_data(self.my_cursor)
        self.my_db.commit()

        print("Produit sauvegardé dans les Favories")
        self.choosing_option()

    def show_favorite(self):
        #################################
        #        SHOW Substitute        #
        #################################

        # Show user's Favorite product and substitute
        self.get_data(Favorite())

        self.choosing_option()

    @staticmethod
    def quit():
        print("Au revoir !")

    def get_data(self, model, filter_by=[], value=[], ids_list=[]):
        for i, key in enumerate(filter_by):
            test = getattr(model, key)
            test.value = value[i]

        data = get_all(model, self.my_cursor)
        for new_model in data[:10]:
            if type(model) == Favorite:
                product = new_model.product_id.models
                sub = new_model.substitute_id.models
                info = "Produit : %s note %s, Substitue : %s note %s" % (product.name.value,
                                                                         product.nutrition_grade.value,
                                                                         sub.name.value, sub.nutrition_grade.value)
            else:
                info = "Id : %s, Name : %s" % (new_model.id, new_model.name.value)
                if type(model) == Product:
                    info += ", Note : %s" % new_model.nutrition_grade.value
            print(info)
            ids_list.append(new_model.id)
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
