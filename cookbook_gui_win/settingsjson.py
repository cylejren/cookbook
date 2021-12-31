import json
import os

main_databes_directory_path = '.' + '\\databes_files\\'

# define names of user's cookbooks file
# method copy from UserDB class
def create_list_with_files_from_db_file():
    # get the list of users db files
    list_with_db_files = []
    for file in os.listdir(main_databes_directory_path):
        list_with_db_files.append(file)
    return list_with_db_files

list_with_db_files = create_list_with_files_from_db_file()

settings_json = json.dumps([
    {'type': 'title',
     'title': 'OGÓLNE'},

    {'type': 'options',
     'title': 'Początkowa książka',
     'desc': 'Ze swoich zapisanych książek wybierz tą, która będzie otwierana przy starcie programu',
     'section': 'cookbook_settings',
     'key': 'main_cookbook_file',
     'options': list_with_db_files
     },

    {'type': 'title',
     'title': 'CZCIONKA'
    },

    {'type': 'numeric',
     'title': 'Rozmiar czcionki - Składniki',
     'desc': 'Podaj rozmiar czcionki w polu Składniki',
     'section': 'cookbook_settings',
     'key': 'font_size_ingredients'
    },

    {'type': 'numeric',
     'title': 'Rozmiar czcionki - Opis',
     'desc': 'Podaj rozmiar czcionki w polu Opis',
     'section': 'cookbook_settings',
     'key': 'font_size_description'
     },

    {'type': 'string',
     'title': 'Kolor czcionki - Tytuł',
     'desc': 'Podaj kolor nazwy przepisu',
     'section': 'cookbook_settings',
     'key': 'font_color_title'
     }

])