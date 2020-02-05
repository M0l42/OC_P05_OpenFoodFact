# Welcome !

## This is my version of the 5th Project of OpenClassroom's Django path.

### Settings your Database
You need to have MySQL installed and set

You can modify the file settings.py to your right settings

```
DB_CONFIG = {
    'name': 'name_of_your_database',
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
}
```

or you can use arguments when running the scripts.

   * '--host' to define the host
   * '-U' or '--username' to define the user
   * '-p' or '--password' to define the password
   * '-d' or '--database' to define the database name

If you're using arguments, you need to use it for script_db.py and main.py.

The database will be created if needed.

### Populating your database

Run script.py

Will Create database and the tables Categories, Products, Favorite and Substitute if it doesn't exist.

Will populate Categories with the file "categories.json" ( to have limited product and have a lighter database ).

Then it will populate the Category's Product via the API of OpenFoodFact sorted by their popularity.

### The User Interface

Run main.py

You have tree choice:
   * Search a product to find a healthier substitute.
     ```
     It will show all the categories for the user to choose
     then show the 5 more populate product of this category.
     The user will select a product and it will show the
     5 first product with a better grade and it will save 
     the one the user choose.
     ```

   * Show all the Favorite.
     ```
     It will show a product and its substitute with some details.
     ```
     
   * Quit