Welcome !

This is my version of the 5th project OpenClassroom's Django path.

This project is divided in two part :
-The Creation and the population of the database
    You need to have MySQL installed and set
    Then run the python's script "script_db.py"
        '--host' to define the host ( default : localhost )
        '-U', '--username' to define the user ( default : nathan )
        '-p', '--password' to define the password ( default : None )
        '-d', '--database' to define the database name ( default : pure-beurre )
    It will Create database and the tables Categories, Products, Favorite if it doesn't exist
    and it will populate Categories with the file "categories.json" ( to have limited product and have a lighter database )
    then it will populate the Category's Product via the API of OpenFoodFact sorted by their popularity

-The User Interface
    This part is in main.py
    At first the user have two choice :
        -Search a product to find a healthier substitute
        it will show all the categories for the user to choose
        then show the 5 more populate product of this category
        The user will select an product and it will show the
        5 first product with a better grade and it will save the one the user choose.

        -Show all the product and their substitute with their details.