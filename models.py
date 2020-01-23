class Model:
    model = {}
    id = int()
    command = ""

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def save(self, my_cursor):
        self.command = "CREATE TABLE IF NOT EXISTS %s (Id INT PRIMARY KEY AUTO_INCREMENT" % self.get_classname()
        for key in self.model:
            if type(self.model[key]) == CharField:
                self.command += ",%s VARCHAR(%d)" % (key, self.model[key].max_length)
            if type(self.model[key]) == TextField:
                self.command += ",%s TEXT" % key
            if type(self.model[key]) == IntField:
                self.command += ",%s INTEGER(%d)" % (key, self.model[key].length)
            if type(self.model[key]) == ForeignKey:
                self.command += ",%s INTEGER, FOREIGN KEY(%s) REFERENCES %s(Id) ON DELETE CASCADE" % \
                                (key, key, self.model[key].models)
        self.command += ") CHARACTER SET utf8 COLLATE utf8_bin"
        my_cursor.execute(self.command)

    def insert_data(self, my_cursor):
        self.command = "INSERT INTO %s (" % self.get_classname()
        keys = []
        values = []
        for key in self.model:
            if self.model[key].value:
                keys.append(key)
                values.append(self.model[key].value)
        self.command += ",".join("%s" % key for key in keys)
        self.command += ") Value (" + ",".join('"%s"' % value for value in values) + ")"
        my_cursor.execute(self.command)


class CharField:
    def __init__(self, max_length, value=None):
        self.max_length = max_length
        self.value = value


class TextField:
    def __init__(self, value=None):
        self.value = value


class IntField:
    def __init__(self, length, value=None):
        self.length = length
        self.value = value


class ForeignKey:
    def __init__(self, models, value=None):
        self.models = models
        self.value = value


class Product(Model):
    model = {
        "name": CharField(max_length=255),
        "code": CharField(max_length=100),
        "url": TextField(),
        "ingredients": TextField(),
        "nutrition_grade": CharField(max_length=10),
        "fat_100": IntField(length=10), 
        "fat_lvl": CharField(max_length=10),
        "saturated_fat_100": IntField(length=10),
        "saturated_fat_lvl": CharField(max_length=10),
        "sugar_100": IntField(length=10),
        "sugar_lvl": CharField(max_length=10),
        "salt_100": IntField(length=10),
        "salt_lvl": CharField(max_length=10),
        "store": TextField(),
        "category": ForeignKey("Category")
    }


class Category(Model):
    model = {
        "name": CharField(max_length=255),
        "tags": CharField(max_length=255),
        "products": IntField(length=10)
    }


class Favorite(Model):
    model = {
        "Product_id": ForeignKey("Product"),
        "Substitute_id": IntField(length=15),
    }


def get_all(models, mycursor):
    keys = ["Id"]
    for key in models.model:
        keys.append(key)
    command = "SELECT " + ",".join("%s" % key for key in keys)
    command += " FROM " + models.get_classname()
    mycursor.execute(command)
    results = mycursor.fetchall()

    query = []

    for data in results:
        if type(models) == Product:
            query.append(Product())
        if type(models) == Category:
            query.append(Category())
        if type(models) == Favorite:
            query.append(Favorite())
        for i, value in enumerate(data):
            if keys[i] == 'Id':
                query[-1].id = value
            else:
                query[-1].model[keys[i]].value = value
    return query
