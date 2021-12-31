import sqlite3

class DatabaseManager():
    "actions on database"

    def __init__(self, database):
    # def __init__(self, database="db_cookbook.sqlite"):
        self.database = database

        # connect with my database
        self.connect()

        # create tables
        self.create_table("przepisy")
        self.create_table("kategorie")
        self.create_table("tagi")
        self.create_columns("przepisy", ["tagi", "skladniki", "kategorie", "opis"])

    def connect(self):
        """Connect to the SQLite3 database."""
        self.db = sqlite3.connect(self.database)
        self.cursor = self.db.cursor()

    def close(self):
        """Close the SQLite3 database."""
        self.db.commit()
        self.cursor.close()
        self.db.close()

    def create_table(self, table_name):
        "creating table"
        self.cursor.execute("CREATE TABLE IF NOT EXISTS {} (nazwa PRIMARY KEY)".format(table_name))

    def create_columns(self, table_name, columns):
        "adding columns(fields) to the table"
        try:
            for column_name in columns:
                self.cursor.execute("""
                ALTER TABLE {} ADD COLUMN {} """.format(table_name, column_name))
                self.db.commit()
        except sqlite3.OperationalError:
            pass

    def adding_to_db(self, table_name, table_columns, values):
        # inserting data into table
        self.cursor.execute("INSERT INTO {}({}) VALUES ('{}')".format(table_name, table_columns, values))
        self.db.commit()

    def update_db(self, table_name, table_column, new_value, unique_column_name, unique_column_value):
        # updating data in existing row
        self.cursor.execute("UPDATE {} SET {} = '{}' WHERE {} = '{}'".format(table_name, table_column, new_value, unique_column_name, unique_column_value))
        self.db.commit()

    def delete_from_db(self, table_name, table_column, column_value):
        self.cursor.execute("DELETE from {} WHERE {} = '{}'".format(table_name, table_column, column_value))
        self.db.commit()

    def query(self, search_value, table_name, table_column, column_value):
        self.cursor.execute("SELECT {} from {} WHERE {} = {}".format(search_value, table_name, table_column, column_value))
        # query_result = self.cursor.fetchall()
        return self.cursor.fetchall()


class Recipe(DatabaseManager):
    "Creating recipes"

    def __init__(self, name, database="db_cookbook.sqlite"):
        super().__init__(database)
        self.name = name

    def __str__(self):
        print("This is {} recipe.".format(self.name))

    # def opening_cookbook_db(self):
    #     # connect with my database
    #     super().connect()
    #
    #     # create tables
    #     super().create_table("przepisy")
    #     super().create_table("kategorie")
    #     super().create_table("tagi")
    #     super().create_columns("przepisy", ["tytul", "tagi", "skladniki", "kategorie", "opis"])

    def add_recipe(self):
        "adding recipe; 'name' argument is necessary"
        super().adding_to_db("przepisy", "nazwa", self.name)
        print("Przepis {} został dodany".format(self.name))

    def edit_recipe(self, table_column, new_value, name):
        super().update_db("przepisy", table_column, new_value, "nazwa", name)

    def delete_recipe(self, name):
        super().delete_from_db("przepisy", "nazwa", name)
        print("Przepis {} zostal usuniety.".format(name))

    def set_category_recipe(self):
        pass

    def check_if_recipe_exists(self):
        x = super().query("*", "przepisy", "nazwa", self.name)
        if x == None:
            print("Taki przepis nie istnieje w bazie danych")
            return x

class Category():
    def __init__(self, name):
        self.name = name

    def add_category(self):
        pass

    def del_category(self):
        pass


if __name__ == "__main__":
    print("To jest plik do importu klas")