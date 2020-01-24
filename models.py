class Model:

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def save(self, my_cursor):
        command = "CREATE TABLE IF NOT EXISTS %s (Id INT PRIMARY KEY AUTO_INCREMENT" % self.get_classname()
        for key in self.__dict__:
            attr = getattr(self, key)
            if type(attr) == CharField:
                command += ",%s VARCHAR(%d)" % (key, attr.max_length)
            if type(attr) == TextField:
                command += ",%s TEXT" % key
            if type(attr) == IntField:
                command += ",%s INTEGER(%d)" % (key, attr.length)
            if type(attr) == ForeignKey:
                command += ",%s INTEGER, FOREIGN KEY(%s) REFERENCES %s(Id) ON DELETE CASCADE" % \
                                (key, key, attr.models)
        command += ") CHARACTER SET utf8 COLLATE utf8_bin"
        print(command)
        my_cursor.execute(command)

    def insert_data(self, my_cursor):
        command = "INSERT INTO %s (" % self.get_classname()
        keys = []
        values = []
        for key in self.__dict__:
            if key != "id":
                attr = getattr(self, key)
                if attr.value:
                    print(key)
                    keys.append(key)
                    print(attr.value)
                    values.append(attr.value)
        command += ",".join("%s" % key for key in keys)
        command += ") Value (" + ",".join('"%s"' % value for value in values) + ")"
        print(command)
        my_cursor.execute(command)


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
    def __init__(self):
        self.id = int()
        self.name = CharField(max_length=255)
        self.code = CharField(max_length=100)
        self.url = TextField()
        self.ingredients = TextField()
        self.nutrition_grade = CharField(max_length=10)
        self.fat_100 = IntField(length=10)
        self.fat_lvl = CharField(max_length=10)
        self.saturated_fat_100 = IntField(length=10)
        self.saturated_fat_lvl = CharField(max_length=10)
        self.sugar_100 = IntField(length=10)
        self.sugar_lvl = CharField(max_length=10)
        self.salt_100 = IntField(length=10)
        self.salt_lvl = CharField(max_length=10)
        self.store = TextField()
        self.category = ForeignKey("Category")


class Category(Model):
    def __init__(self):
        self.id = int()
        self.name = CharField(max_length=255)
        self.tags = CharField(max_length=255)
        self.products = IntField(length=10)


class Favorite(Model):
    def __init__(self):
        self.id = int()
        self.product_id = ForeignKey("Product")
        self.substitute_id = IntField(length=15)


def get_all(models, mycursor):
    keys = ["Id"]
    filter_command = []
    for key in models.__dict__:
        if key != "id":
            keys.append(key)
    command = "SELECT " + ",".join("%s" % key for key in keys)
    command += " FROM " + models.get_classname()
    for key in keys:
        if key == "Id":
            if models.id:
                filter_command.append("%s = %s" % (key, models.id))
        else:
            attr = getattr(models, key)
            if attr.value:
                filter_command.append('%s = "%s"' % (key, attr.value))
    if filter_command:
        command += " WHERE " + " AND ".join("%s" % value for value in filter_command)
    print(command)
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
                test = getattr(query[-1], keys[i])
                test.value = value
                # setattr(test, "value", value)

    return query
