class Model:

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def save(self, my_cursor):
        """
        Create Table according to the model
        :param my_cursor:
        """
        command = "CREATE TABLE IF NOT EXISTS %s (id INT PRIMARY KEY AUTO_INCREMENT" % self.get_classname()
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
                                (key, key, attr.models.get_classname())
        command += ") CHARACTER SET utf8 COLLATE utf8_bin"
        my_cursor.execute(command)

    def insert_data(self, my_cursor):
        """
        Insert the all the value of the model to the database

        :param my_cursor:
        :return: my_cursor.lastrowid
        """
        command = "INSERT INTO %s (" % self.get_classname()
        keys = []
        values = []
        for key in self.__dict__:
            if key != "id":
                attr = getattr(self, key)
                if attr.value:
                    keys.append(key)
                    values.append(attr.value)
        command += ",".join("%s" % key for key in keys)
        command += ") Value (" + ",".join('"%s"' % value for value in values) + ")"
        my_cursor.execute(command)
        return my_cursor.lastrowid


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
        self.category = ForeignKey(Category())


class Substitute(Product):
    pass


class Category(Model):
    def __init__(self):
        self.id = int()
        self.name = CharField(max_length=255)
        self.tags = CharField(max_length=255)
        self.products = IntField(length=10)


class Favorite(Model):
    def __init__(self):
        self.id = int()
        self.product_id = ForeignKey(Product())
        self.substitute_id = ForeignKey(Substitute())


def get_all(models, mycursor):
    """
    Doing two things:
        - Get all the data according to the model
        - Create a query of instances with the data we just got.

    :param models:
    :param mycursor:
    :return: query
    """
    keys = []
    foreign_keys = []
    filter_command = []
    join_command = []
    for key in models.__dict__:
        # get all the key in one list
        # get all the foreign key in one list
        keys.append(key)
        attr = getattr(models, key)
        if type(attr) == ForeignKey:
            foreign_model = attr.models.get_classname()
            foreign_keys.append([foreign_model])
            foreign_keys[-1].append(key)
            for foreign_key in attr.models.__dict__:
                foreign_keys[-1].append(foreign_key)

    # Create the command with its join and filter
    command = "SELECT " + ",".join("%s.%s" % (models.get_classname(), key) for key in keys)

    for key in foreign_keys:
        command += "," + ",".join("%s.%s" % (key[0], value) for value in key[2:])

    command += " FROM " + models.get_classname()
    for key in keys:
        if key == "id":
            if models.id:
                filter_command.append("%s = %s" % (key, models.id))
        else:
            attr = getattr(models, key)
            if type(attr) == ForeignKey:
                join_command.append(" INNER JOIN %s ON %s.%s = %s.Id" % (attr.models.get_classname(),
                                                                         models.get_classname(), key,
                                                                         attr.models.get_classname()))
            if attr.value:
                filter_command.append('%s = "%s"' % (key, attr.value))

    if join_command:
        command += "".join(join_command)

    if filter_command:
        command += " WHERE " + " AND ".join("%s.%s" % (models.get_classname(), value) for value in filter_command)

    mycursor.execute(command)
    results = mycursor.fetchall()

    query = []

    for data in results:
        # Creating a query of new instances
        if type(models) == Product:
            query.append(Product())
        if type(models) == Category:
            query.append(Category())
        if type(models) == Favorite:
            query.append(Favorite())
        for i, value in enumerate(data):
            # Populate the new instance with its proper values
            if i < len(keys):
                if keys[i] == "id":
                    query[-1].id = value
                else:
                    attr = getattr(query[-1], keys[i])
                    attr.value = value
            else:
                # Populate the model of the foreign key
                index = len(keys)
                index_fk = 0
                for key in foreign_keys:
                    if index+len(key[2:]) <= i:
                        index += len(key[2:])
                        index_fk += 1
                attr = getattr(query[-1], foreign_keys[index_fk][1]).models
                if foreign_keys[index_fk][2 + i-index] == "id":
                    attr.id = value
                else:
                    attr_fk = getattr(attr, foreign_keys[index_fk][2 + i-index])
                    attr_fk.value = value

    return query
