"""Tu wykorzystalam ramki Frame jako obiekty (a nie zmienne)"""


#!/usr/bin/env python

from tkinter import *
import tkinter as tk
import sqlite3


class Cookbook(tk.Frame):
    """Create main window of the application"""
    def __init__(self, master):
        super(Cookbook, self).__init__(master)
        self.grid()
        self.main_label = tk.Label(self, text = "KSIAZKA KUCHARSKA", font = ("Vileda", 15, "bold")).grid(columnspan = 2)
        self.create_widgets()

    def create_widgets(self):
        self.search_label = tk.Label(self, text = "Szukaj tytulu: ").grid(row = 1, column = 0, sticky = W)
        self.search_entry = tk.Entry(self).grid(row = 1, column = 1, sticky = W)
        self.search_button = tk.Button(self, text = "Szukaj", command = self.show_results).grid(row = 1, column = 2)

        #creates text box for new recipie
        self.text_box = tk.Text(self, width = 5, height = 1, wrap = WORD).grid()

        #creates button for adding recipe
        self.add_button = tk.Button(self, text = "Dodaj przepis", command = self.add_recipe).grid(row = 2)

    def show_results(self):
        """Shows search result"""
        pass
        # title = self.search_entry.get() #pobieram text z pola szukaj
        # self.text_box.delete(0.0, END) #czyszcze pole tekstowe
        # self.text_box.inster(0.0, xxxxx) #wstawiam cos do pola textowego

    def add_recipe(self):
        """Opens new window for adding recipe"""
        # self.root_add_recipe = Tk()
        # self.root_add_recipe.title("Dodawanie nowego przepisu")
        # self.root_add_recipe.geometry("700x400")
        # app_add = AddRecipe(self.root_add_recipe)
        self.root_add_recipe = tk.Toplevel(self.master)
        self.app = AddRecipe(self.root_add_recipe)


class AddRecipe(Frame):
    """Creates window for adding recipe"""
    def __init__(self, master1):
        """Inicjalizacja ramnki"""
        super(AddRecipe, self).__init__(master1)
        self.grid()
        self.main_label = tk.Label(self, text="Dodaj przepis", font=("Vileda", 15, "bold")).grid(columnspan=2, sticky = W)
        self.create_widgets()


    def create_widgets(self):
        self.title_label = tk.Label(self, text = "Tytul: ").grid(row = 1, column = 0, sticky = W)
        self.title_entry = tk.Entry(self)
        self.title_entry.grid(row = 1, column = 0, columnspan = 20)

        self.ingredient_label = tk.Label(self, text = "Skladniki: ").grid(row = 2, column = 0, sticky = W)
        self.ingredient_text = tk.Text(self, width = 35, height = 5, wrap = WORD)
        self.ingredient_text.grid(row = 3, column = 0, columnspan = 2)

        self.description_label = tk.Label(self, text = "Opis: ").grid(row = 4, column = 0, sticky = W)
        self.description_text = tk.Text(self, width = 35, height = 5, wrap = WORD)
        self.description_text.grid(row = 5, column = 0, columnspan = 2)

        self.save_button = tk.Button(self, text = "Zapisz", command = self.save_recipe).grid(row = 7, column = 0, columnspan = 2)

    def save_recipe(self):
        """add data of new recipe to database"""
        title = self.title_entry.get()
        ingredient = self.ingredient_text.get(0.0, END)
        description = self. description_text.get(0.0, END)
        cursor.execute("INSERT INTO przepisy VALUES (?, ?, ?)", (title, ingredient, description))
        self.master.destroy()

root = tk.Tk()
root.title("Coockbook - Renia")
root.geometry("700x500")


#connect with my database
db = sqlite3.connect("coockbook.sqlite")
cursor = db.cursor()
db.row_factory = sqlite3.Row #access to columns trough the names (not only index)

cursor.execute("""
        CREATE TABLE IF NOT EXISTS kategorie (
            id INTEGER,
            nazwa CHAR PRIMARY KEY
            )""")

cursor.execute("""
        CREATE TABLE IF NOT EXISTS przepisy (
            id INTEGER,
            tytul PRIMARY KEY,
            skladniki,
            opis,
            FOREIGN KEY(tytul) REFERENCES kategorie(nazwa)
            )""")

app = Cookbook(root)
root.mainloop()
db.commit()
cursor.close()

