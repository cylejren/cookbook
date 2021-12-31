#!/usr/bin/python3

from classes import *

def getting_recipe_name(x):
    # x can have 1 or 2 value
    recipe_name = {
        1: lambda: input("Podaj nazwe przepisu: "),
        2: lambda: input("Taki przepis istnieje juz w bazie danych. Podaj inna nazwe: ")
    }.get(x,"ccc")()

    while recipe_name == "":
        recipe_name = input("Nie podales zadnej nazwy.\nPodaj tytul przepisu lub wpisz 'K' aby wyjsc z programu: ")
        if recipe_name == "k" or recipe_name == "K":
            break

    return recipe_name


print("KSIAZKA KUCHARSKA\n")
#MAIN MENU
print("""Opcje do wyboru:
    1 - dodaj przepis
    2 - edytuj przepis
    3 - usun przepis
    4 - dodaj kategorie
    5 - koniec
""")

recipe_name = ""
choice = True

while choice:
    try:
        user_choice = int(input("Co wybierasz? "))
    except:
        print("Zly wybor. Podaj ponownie swoj wybor")
        continue

    if user_choice == 1:
        # ADDING RECIPE

        recipe_name = getting_recipe_name(1)
        if recipe_name in "Kk":
            continue
        recipe_instance = Recipe(recipe_name)

        # adding recipe to DB by recipe_name
        try:
            recipe_instance.add_recipe()
        except sqlite3.IntegrityError:
            recipe_name = getting_recipe_name(2)
            if recipe_name in "Kk":
                continue
            recipe_instance = Recipe(recipe_name)

        recipe_tags = input("Podaj tagi do przepisu: ")
        recipe_instance.edit_recipe("tagi", recipe_tags, recipe_name)

        recipe_ingredients = input("Podaj skladniki: ")
        recipe_instance.edit_recipe("skladniki", recipe_ingredients, recipe_name)

        recipe_description = input("Podaj opis: ")
        recipe_instance.edit_recipe("opis", recipe_description, recipe_name)


    elif user_choice == 2:
        # EDITING RECIPE

        recipe_name = getting_recipe_name()
        if recipe_name in "Kk":
            continue
        recipe_instance = Recipe(recipe_name)

        edit_user_choice = input("""Ktore pole chcesz edytowac?:
            1 - nazwa
            2 - tagi
            3 - skladniki
            4 - kategoria
            5 - opis
        """)

        if edit_user_choice not in "12345":
            print("Podales zla wartosc, nie ma takiej opcji edycji")
            continue

        new_value = input("Podaj nowa wartosc: ")

        editing_recipe_functions = {
            "1": lambda: recipe_instance.edit_recipe("nazwa", new_value, recipe_name),
            "2": lambda: recipe_instance.edit_recipe("tagi", new_value, recipe_name),
            "3": lambda: recipe_instance.edit_recipe("skladniki", new_value, recipe_name),
            "4": lambda: recipe_instance.edit_recipe("kategorie", new_value, recipe_name),
            "5": lambda: recipe_instance.edit_recipe("opis", new_value, recipe_name)
            }#.get(edit_user_choice, lambda: print("NIE MA"))

        editing_recipe_functions[edit_user_choice]()


    elif user_choice == 3:
        # DELETING RECIPE

        recipe_name = getting_recipe_name()
        if recipe_name in "Kk":
            continue
        recipe_instance = Recipe(recipe_name)

        recipe_instance.delete_recipe(recipe_name)

    elif user_choice == 4:
        # ADDING CATEGORY
        pass

    elif user_choice == 5 or user_choice == "k" or user_choice == "K":
        # EXIT
        choice = False
        # recipe_instance.close()
        print("KONIEC")
    else:
        print("Zly wybor. Podaj ponownie swoj wybor")
