"""Tu wykorzystalam ramki Frame jako zmienne"""

#!/usr/bin/env python

import tkinter as tk
from tkinter import *
from tkinter import messagebox
import sqlite3

class Cookbook():
    """Create main window of the application"""
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(master)
        self.frame.grid()
        self.main_label = tk.Label(self.frame, text = "KSIAZKA KUCHARSKA", font = ("Vileda", 15, "bold")).grid(columnspan = 2)
        self.create_widgets()

    def create_widgets(self):
        self.search_label = tk.Label(self.frame, text = "Szukaj tytulu: ").grid(row = 1, column = 0, sticky = W)
        self.search_entry = tk.Entry(self.frame).grid(row = 1, column = 1, sticky = W)
        self.search_button = tk.Button(self.frame, text = "Szukaj", command = self.show_results).grid(row = 1, column = 2)

        #creates text box for new recipie
        self.text_box = tk.Text(self.frame, width = 5, height = 1, wrap = WORD).grid()

        #creates button for adding recipe, categories
        self.add_recipe_button = tk.Button(self.frame, text = "Dodaj przepis", command = self.add_recipe).grid(row = 2)
        self.add_category_button = tk.Button(self.frame, text="Dodaj kategorie", command=self.add_category).grid(row=2, column = 2)

    def show_results(self):
        """Shows search result"""
        pass
        # title = self.search_entry.get() #pobieram text z pola szukaj
        # self.text_box.delete(0.0, END) #czyszcze pole tekstowe
        # self.text_box.inster(0.0, xxxxx) #wstawiam cos do pola textowego

    def add_recipe(self):
        """Opens new window for adding recipe"""
        self.root_add_recipe = tk.Toplevel(self.master)
        self.root_add_recipe.title("Dodawanie nowego przepisu")
        self.root_add_recipe.geometry("700x400")
        self.app = AddRecipe(self.root_add_recipe)

    def add_category(self):
        """Opens new window for adding new category"""
        self.root_add_category = tk.Toplevel(self.master)
        self.root_add_category.title("Dodaj nowa kategorie")
        self.root_add_category.geometry("300x100")
        add_category_window = AddCategory(self.root_add_category)


class AddRecipe():
    """Creates window for adding recipe"""
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(master)
        self.frame.grid()
        self.main_label = tk.Label(self.frame, text="Dodaj przepis", font=("Vileda", 15, "bold")).grid(columnspan=2, sticky = W)
        self.create_widgets()

    def create_widgets(self):
        self.title_label = tk.Label(self.frame, text = "Tytul: ").grid(row = 1, column = 0, sticky = W)
        self.title_entry = tk.Entry(self.frame)
        self.title_entry.grid(row = 1, column = 0, columnspan = 20)

        self.ingredient_label = tk.Label(self.frame, text = "Skladniki: ").grid(row = 2, column = 0, sticky = W)
        self.ingredient_text = tk.Text(self.frame, width = 35, height = 5, wrap = WORD)
        self.ingredient_text.grid(row = 3, column = 0, columnspan = 2)

        self.description_label = tk.Label(self.frame, text = "Opis: ").grid(row = 4, column = 0, sticky = W)
        self.description_text = tk.Text(self.frame, width = 35, height = 5, wrap = WORD)
        self.description_text.grid(row = 5, column = 0, columnspan = 2)

        self.save_button = tk.Button(self.frame, text = "Zapisz", command = self.save_recipe).grid(row = 7, column = 0, columnspan = 2)

    def save_recipe(self):
        """add data of new recipe to database"""
        title = self.title_entry.get()
        ingredient = self.ingredient_text.get(0.0, END)
        description = self. description_text.get(0.0, END)
        cursor.execute("INSERT INTO przepisy VALUES (?, ?, ?)", (title, ingredient, description))
        self.master.destroy()

class AddCategory():
    """Creates in main window button for new cateogory"""
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(master)
        self.frame.grid()
        #self.main_label = tk.Label(self.frame, text="Dodaj kategorie", font=("Vileda", 15, "bold")).grid(columnspan=2, sticky = W)
        self.create_widgets()

        main_window.row_category_icon = 5
        main_window.column_category_icon = 0

    def create_widgets(self):
        self.add_category_label = tk.Label(self.frame, text = "Nazwa kategorii: ").grid(row = 0, column = 0)
        self.add_category_entry = tk.Entry(self.frame)
        self.add_category_entry.grid(row = 0, column = 1)

        self.add_category_button = tk.Button(self.frame, text = "Zapisz", command = self.save_category).grid(row = 1, column = 0)

    def save_category(self):
        """adds new category to database"""
        self.category = self.add_category_entry.get()
        try:
            cursor.execute("INSERT INTO kategorie VALUES (?)", [self.category])
        except sqlite3.IntegrityError:
            messagebox.showinfo("Bledna nazwa kategorii", "Podana nazwa kategorii juz istnieje w bazie. Prosze podac inna nazwe")

        self.add_category_icon()
        self.master.destroy()

    def add_category_icon(self):
        """adds new category icon to main window"""
        main_window.category_icon = tk.Button(main_window.frame, text = self.category)
        main_window.category_icon.grid(row = main_window.row_category_icon)


root = tk.Tk()
root.title("Cookbook - Renia")
root.geometry("700x500")


#connect with my database
db = sqlite3.connect("db_cookbook.sqlite")
cursor = db.cursor()
db.row_factory = sqlite3.Row #access to columns trough the names (not only index)

cursor.execute("""
        CREATE TABLE IF NOT EXISTS kategorie (
            nazwa PRIMARY KEY
            )""")

cursor.execute("""
        CREATE TABLE IF NOT EXISTS przepisy (
            tytul PRIMARY KEY,
            skladniki,
            opis,
            FOREIGN KEY(tytul) REFERENCES kategorie(nazwa)
            )""")

main_window = Cookbook(root)
root.mainloop()

db.commit()
cursor.close()

