#!/usr/bin/python3

import sqlite3


#connect with my database
db = sqlite3.connect("db_cookbook.sqlite")
cursor = db.cursor()
db.row_factory = sqlite3.Row #access to columns trough the names (not only index)

cursor.execute("""
        CREATE TABLE IF NOT EXISTS przepisy (
            tytul,
            tagi,
            kategorie,
            skladniki,
            opis,
            FOREIGN KEY(tytul) REFERENCES kategorie(nazwa)
            )""")

cursor.execute("""
        CREATE TABLE IF NOT EXISTS kategorie (
            nazwa
            )""")

cursor.execute("""
        CREATE TABLE IF NOT EXISTS tagi (
            nazwa
            )""")

cursor.execute("INSERT INTO przepisy(tagi) VALUES ("zupy", "obiad", "ryz")")
# cursor.execute("INSERT INTO {}{} VALUES ('{}')".format("przepisy", "(tagi)", ("zupy", "obiad", "ryz")))



db.commit()
cursor.close()
db.close()