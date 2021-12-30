# -*- coding: utf-8 -*-

'''
This program allow to download recipe from pepperplate.com website and put the data into database in sqlite. 
The format of the db matches the cookbook_by_renia applucation
'''

import requests
import bs4
import os
import urllib
import urllib.request
import database_methods


def download_page(from_where, source):
    if from_where == 'website':
        recipe_page_url = source

        # download the web page (as a single string value)
        download_page = requests.get(recipe_page_url)
        download_page.raise_for_status()  # we want to be sure that the download has actually worked before the program continues
        result = download_page.text
    else: # source == 'disk':
        # load website from hard drive
        # result = open('html_files/babeczki_z_kremem.html')
        with open(source, encoding='utf-8') as fh:
            result = fh.read()
    return result

def get_title():
    # select() - retrieve a web page element
    get_title = recipe_content.select('#cphMiddle_cphMain_lblTitle') # search for this ID
    title = get_title[0].getText() # get text from the found data
    return title

def get_source():
    get_source = recipe_content.find('a', id = 'cphMiddle_cphMain_hlSource')
    if get_source:
        try:
            source = get_source.attrs['href']
        except KeyError:
            source = get_source.text
    else:
        source = ''
    return source

def get_ingredients():
    ing_tag = recipe_content.find('ul', class_='inggroups')

    # save text to the file
    all_text_from_ing = ing_tag.text.strip()

    with open('przepis.txt', 'w+') as fh_old, open('przepisy_new.txt', 'w+') as fh_new:
        fh_old.write(all_text_from_ing)
        fh_old.seek(0,0)

        for line in fh_old:
            if line.isspace(): # sprawdza czy wszystkie znaki są białymi znakami
                pass
            else:
                line = str(line.strip())

                if line.isnumeric():  # if its only a number
                    fh_new.write(line + ' ')
                else: # if its has some letters
                    if line.rfind(':') == -1: # if its a header
                        fh_new.write(line + '\n')
                    else:
                        fh_new.write('\n'+ line + '\n')

    with open('przepisy_new.txt') as fh:
        ing_list = ''
        for i in fh.readlines():
            ing_list += i

    os.remove('przepis.txt')
    os.remove('przepisy_new.txt')

    return ing_list

def get_description():
    desc = recipe_content.find('ul', class_= 'dirgroups')
    notes = recipe_content.find('span', id = 'cphMiddle_cphMain_lblNotes')
    all_text_from_desc = desc.text.strip()
    all_text_from_notes = notes.text.strip()

    with open('opis.txt', 'w+') as fh_old, open('opis_new.txt', 'w+') as fh_new:
        fh_old.write(all_text_from_desc)
        fh_old.seek(0,0)

        for line in fh_old:
            if line.isspace(): # sprawdza czy wszystkie znaki są białymi znakami
                pass
            else:
                line = line.strip()
                fh_new.write(line + '\n')

        fh_new.write(all_text_from_notes)


    with open('opis_new.txt') as fh:
        description = ''
        for i in fh.readlines():
            description += i

    os.remove('opis.txt')
    os.remove('opis_new.txt')

    return description

def get_image():
    images_path = '../cookbook_gui/recipe_images'

    # creating name for the img file
    extenstion = '.jpg'
    img_title = 'pepperplate' + '_' + get_title().replace(' ', '_') + extenstion

    # getting the url of the image
    img = recipe_content.find('img', id = 'cphMiddle_cphMain_imgRecipeThumb')
    if img:
        img_link = img.attrs['src']

        # download the file
        recipe_image_path = os.path.join(images_path, img_title)
        urllib.request.urlretrieve(img_link, recipe_image_path) # download the file
    else:
        recipe_image_path = ''
    return recipe_image_path


db = database_methods.DatabaseManager('../cookbook_gui/databes_files/pepperplate.sqlite')

for file in os.listdir('./html_files/'):
    recipe_source = download_page('disk', os.path.join('./html_files/', file))
    recipe_content = bs4.BeautifulSoup(recipe_source, 'html5lib') # parse download page with bs4

    title = get_title()
    check_if_exist = db.get_values_from_table('nazwa', 'przepisy')
    if title not in [i[0] for i in check_if_exist]:
        print('Dodawanie przepisu {}...'.format(title))

        source = get_source()
        ingredients = get_ingredients()
        description = get_description()
        image = get_image()


        db.adding_to_db('przepisy', 'nazwa', title)
        db.update_db('przepisy', 'zrodlo', source, 'nazwa', title)
        db.update_db('przepisy', 'opis', description, 'nazwa', title)
        db.update_db('przepisy', 'skladniki', ingredients, 'nazwa', title)
        db.update_db('przepisy', 'zdjecie', image, 'nazwa', title)

        print('Przepis {} został dodany'.format(title))
    else:
        pass


print('KONIEC')