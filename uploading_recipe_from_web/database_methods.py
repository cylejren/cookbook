#!/usr/bin/python3

"""
This module containes all methods for working with database SQLITE3
"""

import sqlite3

class DatabaseManager():

    def __init__(self, database):
        self.database = database

        # connect with my database
        self.connect()

        # create main tables
        self.create_table('przepisy', 'nazwa')
        self.create_table('kategorie', 'kategoria_glowna')
        self.create_table('tagi', 'nazwa')
        self.create_column("przepisy", ["tagi", "kategoria", 'podkategoria', "skladniki", "opis", 'zrodlo', 'zdjecie'])

    def connect(self):
        """Connect to the SQLite3 database"""
        self.db = sqlite3.connect(self.database)
        # self.db.row_factory = sqlite3.Row  # access to columns trough the names (not only index)
        self.cursor = self.db.cursor()

    def close_db(self):
        """Close the SQLite3 database"""
        self.db.commit()
        self.cursor.close()
        self.db.close()

    def create_table(self, table_name, first_column_name):
        """Create table"""
        self.cursor.execute("CREATE TABLE IF NOT EXISTS {} ({} PRIMARY KEY)".format(table_name, first_column_name))

    def create_column(self, table_name, column_name):
        """Adding columns to the table"""
        try:
            if type(column_name) == list:
                for column in column_name:
                    self.cursor.execute("""
                    ALTER TABLE {} ADD COLUMN {} """.format(table_name, column))
                    self.db.commit()
            else:
                self.cursor.execute("""
                ALTER TABLE {} ADD COLUMN {} """.format(table_name, column_name))
                self.db.commit()
        except sqlite3.OperationalError:
            pass


    def adding_to_db(self, table_name, table_column, value):
        """Inserting NEW row of data(s) into table"""
        suffix = ''
        while True:
            try:
                if type(value) == str:
                    self.cursor.execute("INSERT INTO {}({}) VALUES ('{}')".format(table_name, table_column, value))
                else:
                    self.cursor.execute("INSERT INTO {}({}) VALUES {}".format(table_name, table_column, value))
                break
            except sqlite3.IntegrityError:
                # suffix += '_'
                # value = value + suffix
                pass
        self.db.commit()
        return value # we return value to check if original value was changed with suffix

    def update_db(self, table_name, table_column, new_value, unique_column_name, value_of_unique_column):
        """Updating data in EXISTING row"""
        suffix = ''
        while True:
            try:
                self.cursor.execute("UPDATE {} SET {} = '{}' WHERE {} = '{}'".format(table_name, table_column, new_value, unique_column_name, value_of_unique_column))
                break
            except sqlite3.IntegrityError:
                suffix += '_'
                new_value = new_value + suffix
        self.db.commit()
        return new_value # we return value to check if original value was changed with suffix

        #
        #
        # try:
        #     self.cursor.execute("UPDATE {} SET {} = '{}' WHERE {} = '{}'".format(table_name, table_column, new_value, unique_column_name, value_of_unique_column))
        # except sqlite3.IntegrityError:
        #     self.cursor.execute("UPDATE {} SET {} = '{}' WHERE {} = '{}'".format(table_name, table_column, new_value + '_', unique_column_name, value_of_unique_column))
        # self.db.commit()

    def delete_from_db(self, table_name, table_column, value):
        """Deleting from database row"""
        self.cursor.execute("DELETE from {} WHERE {} = '{}'".format(table_name, table_column, value))
        self.db.commit()

    def get_values_from_table(self, column_name, table_name, unique_column_name = None, value_of_unique_column = None):
        """Return list of tuples with values from the row(s)
        Each row is a tuple with vales from particular row"""
        if not unique_column_name:
            self.cursor.execute('SELECT {} from {}'.format(column_name, table_name))
            values_list = self.cursor.fetchall()
        else:
            self.cursor.execute("SELECT {} from {} WHERE {} = '{}'".format(column_name, table_name, unique_column_name, value_of_unique_column))
            values_list = self.cursor.fetchall() # [('sałatki',)]
            values_list = values_list[0] # ('sałatki',)
        return values_list


    def get_column_names(self, column_name, table_name):
        """Return the list of column's names"""
        self.db.row_factory = sqlite3.Row  # access to columns trough the names (not only index)
        self.cursor = self.db.cursor()
        self.cursor.execute("SELECT {} from {}".format(column_name, table_name))
        r = self.cursor.fetchone()
        return r.keys()
