class Model:
    models = {}
    command = ""

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def save(self, my_cursor):
        self.command = "CREATE TABLE IF NOT EXISTS %s (Id INT PRIMARY KEY AUTO_INCREMENT," % self.get_classname()
        for key in self.models:
            if self.models[key] == CharField:
                self.command += ",%s VARCHAR(%d)" % (key, self.models[key].max_length)
            if self.models[key] == TextField:
                self.command += ",%s TEXT" % key
            if self.models[key] == IntField:
                self.command += ",%s INTEGER(%d)" % (key, self.models[key].length)
            if self.models[key] == ForeignKey:
                self.command += ",%s INTEGER, FOREIGN KEY(%s) REFERENCES %s(Id) ON DELETE CASCADE" % \
                                (key, key, self.models[key].models)
        my_cursor.execute(self.command)


class CharField:
    def __init__(self, max_length, text=None):
        self.max_length = max_length
        self.text = text


class TextField:
    def __init__(self, text=None):
        self.test = text


class IntField:
    def __init__(self, length, value=None):
        self.length = length
        self.value = value


class ForeignKey:
    def __init__(self, models):
        self.models = models


class Product(Model):
    model = {
        "name": CharField(max_length=255),
        "code": IntField(length=20),
        "ingredients": TextField()
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