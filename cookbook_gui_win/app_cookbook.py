#!/usr/bin/python3

from database_methods import DatabaseManager
import sys
import subprocess
from subprocess import Popen,PIPE
import os
import shutil
import urllib
import urllib.request
from datetime import datetime
import logging

# collecting logs when error will occur
if '_logs_files' not in [i for i in os.listdir('.')]:
    os.mkdir('_logs_files')
log_path = '.' + '\\_logs_files\\'
time_stamp = datetime.now().strftime('logfile_%Y-%m-%d_%H-%M-%S.log')
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(log_path, time_stamp), filemode='w')

import kivy
from kivy.config import Config

kivy.require("1.9.0")
Config.set('graphics', 'window_state', 'maximized')
# Config.set('graphics', 'fullscreen', 'auto') # try later what this is doing
Config.set ('input', 'mouse', 'mouse, disable_multitouch' )

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.listview import ListItemButton
from kivy.uix.bubble import Bubble, BubbleButton, BubbleContent
from kivy.core.clipboard import Clipboard
from kivy.properties import NumericProperty


from kivy.clock import Clock
from kivy.graphics import PushMatrix, PopMatrix, Callback
from kivy.graphics.context_instructions import Transform
from kivy.animation import Animation

from kivy.uix.settings import Settings
from settingsjson import settings_json

main_databes_directory_path = '.' + '\\databes_files\\'
main_images_directory_path = '.' + '\\recipe_images\\'

def get_first_column_values(table_name):
    # first column -> unique values of the table
    # i.e. to get main catgeories list or tag list
    unique_names_list = []
    items_list = list(db.get_values_from_table('*', table_name))
    for i in items_list: # getting list with all category names
        unique_names_list.append(i[0])
    return unique_names_list

def get_category_subcategory_list():
    # getting catgeory and asubcategory list
    items_list = list(db.get_values_from_table('*', 'kategorie'))
    category_list =[]
    for tuple in items_list:  # getting list with all category names
        for item in tuple:
            if item not in (None, ''):
                category_list.append(item)
    return category_list

def get_subcategory_list():
    # getting  list with all subcategories
    items_list = list(db.get_values_from_table('*', 'kategorie'))
    subcategory_list = []
    for tuple in items_list:  # getting list with all category names
        subcategory_list.extend(tuple[1:])
    for item in subcategory_list.copy():
        if item == None or item == '':
            subcategory_list.remove(item)
    return subcategory_list


class TreeViewLabelCustom(TreeViewLabel):
    # defined to set custom property (to know if node is recipe or category)
    # should be set as 'category' or 'recipe'
    node_property = StringProperty()

class TreeCategory(TreeView):
    def __init__(self, **kwargs):
        super(TreeCategory, self).__init__(**kwargs)

        # we need to set this value for good scrolling in tree view
        # this instruction means: Make sure the height is such that there is something to scroll
        self.bind(minimum_height=self.setter('height'))

        # reading already existing categories/subcategories from database
        parent_number = 0 # helps iterate over the list of nodes (root.nodes)
        for row_category in db.get_values_from_table('*', 'kategorie'):
            self.add_category_to_tree(row_category[0]) # add parent node
            for i in range(1, len(row_category)): # adding child nodes
                if row_category[i]: # if not None
                    self.add_category_to_tree(row_category[i], self.root.nodes[parent_number])
            parent_number += 1

        # reading already existing recipes from database
        # self.read_recipes_from_db(db.get_values_from_table('*', 'przepisy')) # OFF becaouse entry_search.on_text calls this method at the beggining of program run


    def read_recipes_from_db(self, lists_with_recipes_to_read):
        self.removing_recipes_from_tree() # clearing the tree

        # lists_with_recipes_to_read = db.get_values_from_table('*', 'przepisy') # ALL recipes from db

        # reading already existing recipes from database
        for row_recipe in lists_with_recipes_to_read:
            title = row_recipe[0]
            category = row_recipe[2]
            subcategory = row_recipe[3]

            for node in self.root.nodes:
                if not subcategory:  # if only MAIN category is added (subcategory is empty cell)
                    if (node.text).lower() == category:
                        self.add_recipe_to_tree(title, node)
                        break
                else:  # when subcategory id added to recipe
                    if (node.text).lower() == category:
                        for child in list(self.iterate_all_nodes(node)):
                            if (child.text).lower() == subcategory:
                                self.add_recipe_to_tree(title, child)
                                break

    def removing_recipes_from_tree(self):
        for node in list(self.iterate_all_nodes()):
            if node.node_property == 'recipe':
                self.remove_node(node)

    def add_category_to_tree(self, name, parent_category = None):
        # add category to the tree view
        self.created_node = self.add_node(TreeViewLabelCustom(text = name.upper(), bold = True, node_property = 'category'), parent_category)
        if parent_category == None:
            self.created_node.font_size = 17
        else:
            self.created_node.font_size = 15
            self.created_node.italic = True
        self.toggle_node(self.created_node) # expand node

    def add_recipe_to_tree(self, name, category):
        # add recipe to the tree view
        self.created_node = self.add_node(TreeViewLabelCustom(text = name, bold = False, font_size = 14, node_property = 'recipe'), category)

    def on_touch_up(self, touch):
        # when we click on recipe -> open recipe_view
        global recipe_view_instance
        # override existing event 'on_touch', to be fired only when node (recipe node) is selected
        node = self.get_selected_node()
        if node and node.node_property == 'recipe':
            # store the recipe that is currently viewed (we need this when we want to refresh recipe view but selected node is category)
            global current_recipe_view_node
            current_recipe_view_node = node

            main_screen_instance.ids.recipe_view.clear_widgets() #need to refer to MAON SCREEN instance; clear recipe_view_instance window
            recipe_view_instance = RecipeView(selected_recipe = node)
            main_screen_instance.ids.recipe_view.add_widget(recipe_view_instance) # need to refer to MAON SCREEN instance (need to put recipe instance to boxlayout)
            # self.on_touch_down(touch, node, recipe_view_instance)
        return super(TreeCategory, self).on_touch_up(touch)

    def on_touch_down(self, touch, after=False):
        # for RIGHT mouse click

        node = self.get_selected_node()

        if touch.button == 'right':
            if not hasattr(self, 'bubble_instance'):
            # if bubble intancje doesn't exist, show bubble (code taken from Buuble example)

                if node and node.node_property == 'category':
                    self.bubble_instance = bubble_instance = BubbleMenu()
                elif node and node.node_property == 'recipe':
                    self.bubble_instance = bubble_instance = BubbleMenu()
                else:
                    bubble_instance = None

                bubble_instance.pos = node.pos  # set buuble position the same as selected node position
                self.created_node.disabled = True
                self.created_node.add_widget(bubble_instance)
                print(bubble_instance.parent)
                print(bubble_instance.children)
            else:
                # if bubble intancje exists, close it (remove widget and kill instance)
                self.remove_widget(self.bubble_instance)
                del(self.bubble_instance)

            return True

        else: # if LEFT click
        #     # # if left click (and others) and some bubble is active, close bubble
        #     # if hasattr(self, 'buuble_instance'):
        #     #     self.remove_widget(self.buuble_instance)
        #     #     del(self.buuble_instance)
        #     pass
            return super(TreeCategory, self).on_touch_down(touch)


class BubbleMenu(Bubble):
    pass


class RecipeView(BoxLayout):
    selected_recipe = ObjectProperty() # node (recipe) which is selected and which runs the recipe_view_instance

    def __init__(self, **kwargs):
        super(RecipeView, self).__init__(**kwargs)

        # read options for the fon_size, etc CHYBA JUZ DO WYWALENIA
        # self.ids.label_ingredients.font_size = options_container.options_values_current['recipe_view_font_size_ing']
        # self.ids.label_description.font_size = options_container.options_values_current['recipe_view_font_size_desc']

        # title id readed in kv file from text: root.selected_recipe.text
        self.ids.label_category.text = self.category()
        self.ids.label_source.text = self.source()
        self.ids.label_tags.text = '[ref=text_selection]' + self.tags() + '[/ref]'
        self.ids.label_ingredients.text = '[ref=text_selection]' + self.ingredients() + '[/ref]'
        self.ids.label_description.text = '[ref=text_selection]' + self.description() + '[/ref]'
        self.ids.label_image.source = self.image()

    def category(self):
        # main_category = db.get_values_from_table('kategoria', 'przepisy', 'nazwa', self.selected_recipe.text)[0][0]
        main_category = db.get_values_from_table('kategoria', 'przepisy', 'nazwa', self.selected_recipe.text)[0]
        # subcategory = db.get_values_from_table('podkategoria', 'przepisy', 'nazwa', self.selected_recipe.text)[0][0]
        subcategory = db.get_values_from_table('podkategoria', 'przepisy', 'nazwa', self.selected_recipe.text)[0]
        if not subcategory:
            result = '[ ' + main_category.upper() + ' ]'
        else:
            result = '[ ' + main_category.upper() + ', ' + subcategory.upper() + ' ]'
        return result

    def tags(self):
        # tag = db.get_values_from_table('tagi', 'przepisy', 'nazwa', self.selected_recipe.text)[0][0]
        tag = db.get_values_from_table('tagi', 'przepisy', 'nazwa', self.selected_recipe.text)[0]
        if tag:
            t = ', '.join(tag.split(','))
        else:
            t = ''
        return t

    def source(self):
        # src = db.get_values_from_table('zrodlo', 'przepisy', 'nazwa', self.selected_recipe.text)[0][0]
        src = db.get_values_from_table('zrodlo', 'przepisy', 'nazwa', self.selected_recipe.text)[0]
        if src and src.startswith('http'):
            src =  '[ref=text_selection]' + src + '[/ref]'
        if not src:
            src = ''
        return src

    def ingredients(self):
        # ing = db.get_values_from_table('skladniki', 'przepisy', 'nazwa', self.selected_recipe.text)[0][0]
        ing = db.get_values_from_table('skladniki', 'przepisy', 'nazwa', self.selected_recipe.text)[0]
        if not ing:
            result = 'Brak podanych składników'
        else:
            result = ing
        return result

    def description(self):
        # des = db.get_values_from_table('opis', 'przepisy', 'nazwa', self.selected_recipe.text)[0][0]
        des = db.get_values_from_table('opis', 'przepisy', 'nazwa', self.selected_recipe.text)[0]
        if not des:
            result = 'Brak opisu'
        else:
            result = des
        return result

    def image(self):
        # img = db.get_values_from_table('zdjecie', 'przepisy', 'nazwa', self.selected_recipe.text)[0][0]
        img = db.get_values_from_table('zdjecie', 'przepisy', 'nazwa', self.selected_recipe.text)[0]
        if not img:
            img_path = os.path.join(main_images_directory_path, 'empty_image.png')
        else:
            img_path = img
        return img_path

    def copy_label_text(self, label_name):
        # when click on Label, copy label.text to clipboard
        if label_name == 'label_ingredients':
            text = self.ids.label_ingredients.text
        elif label_name == 'label_description':
            text = self.ids.label_description.text
        elif label_name == 'label_title':
            text = self.ids.label_title.text
        else:
            text = self.ids.label_tags.text
        text = text.replace('[ref=text_selection]', '')
        text = text.replace('[/ref]', '')
        Clipboard.copy(text)


class AddCategoryPopup(Popup):
    topwidget = ObjectProperty() # need to refer to tree instance; self.topwidget.tree_view WHERE self.topwidget is instance(self) of MainScreen
    entry_text = StringProperty() # its self.ids.entry.text only LOWER()

    def add_category_to_db(self, main_node_name, new_value):
        main_node_name = main_node_name.lower()
        # items_list = list(db.get_values_from_table('*', 'kategorie', 'kategoria_glowna', main_node_name)[0]) # getting the list of items in selected row to check if its empty cell
        items_list = list(db.get_values_from_table('*', 'kategorie', 'kategoria_glowna', main_node_name)) # getting the list of items in selected row to check if its empty cell
        if '' in items_list or None in items_list:
            # column for subcategory already exists, just put there new value
            if '' not in items_list: # only None in items_list
                subcategory_column_name = 'kategoria_{}'.format(items_list.index(None))
            elif None not in items_list: # only '' in items_list
                subcategory_column_name = 'kategoria_{}'.format(items_list.index(''))
            else:
                none_index = items_list.index(None)
                empty_index = items_list.index('')
                if none_index < empty_index: # checking if the first empty cell is None or ""
                    subcategory_column_name = 'kategoria_{}'.format(none_index)
                else:
                    subcategory_column_name = 'kategoria_{}'.format(empty_index)
        else:
            # no empty cell, we need to create new subcategory column with proper name
            column_names = db.get_column_names('*', 'kategorie') #getting the list of all column's names
            last_column = column_names[-1] # getting the last column name
            if last_column == 'kategoria_glowna': # create first subcategory column
                subcategory_column_name = 'kategoria_1'
            else:
                number = int(last_column.partition('_')[2]) # getting the number of last subcategory column
                subcategory_column_name = 'kategoria_{}'.format(str(number + 1))
            db.create_column('kategorie', subcategory_column_name)


        # checking if new_value name olready exist in db in subcategories; if yes: add suffix '_'
        subcategory_list = get_category_subcategory_list()
        suffix = ''
        while True:
            if new_value in subcategory_list:
                suffix += '_'
                new_value = new_value + suffix
            else:
                break

        db.update_db('kategorie', subcategory_column_name, new_value.lower(), 'kategoria_glowna', main_node_name)
        return new_value

    def save(self):
        selected_node = self.topwidget.tree_view.get_selected_node()
        if selected_node and selected_node.node_property == 'category':
            if selected_node.level == 1: # if main category selected, add subcategory
                value = self.add_category_to_db(selected_node.text, self.entry_text)
                self.topwidget.tree_view.add_category_to_tree(value, selected_node)
            else: # if subcategory is selected, add another subategory
                value = self.add_category_to_db(selected_node.parent_node.text, self.entry_text)
                self.topwidget.tree_view.add_category_to_tree(value, selected_node.parent_node)
        elif selected_node and selected_node.node_property == 'recipe':
            recipe_name = selected_node.text
            category = db.get_values_from_table('kategoria','przepisy', 'nazwa', recipe_name)[0]
            subcategory = db.get_values_from_table('podkategoria','przepisy', 'nazwa', recipe_name)
            value = self.add_category_to_db(category, self.entry_text)
            x = selected_node.parent_node
            self.topwidget.tree_view.add_category_to_tree(value, selected_node.parent_node)
        else:
            # add as main category when:
            # - root is selected
            # - no selection at all
            value = db.adding_to_db('kategorie', 'kategoria_glowna', self.entry_text)
            self.topwidget.tree_view.add_category_to_tree(value)  # value is like: self.ids.entry.text + suffix '_'

        # node_selected = False
        # for node in list(self.topwidget.tree_view.iterate_all_nodes()):
        #     if node.is_selected == True:
        #         node_selected = True
        #         if node.level == 0: # if root is selected, add main category
        #             # instance.add_category_to_tree(self.ids.entry.text)
        #             # self.topwidget.tree_view.add_category_to_tree(self.ids.entry.text)
        #             value = db.adding_to_db('kategorie', 'kategoria_glowna', self.entry_text)
        #             self.topwidget.tree_view.add_category_to_tree(value) # value is like: self.ids.entry.text + suffix '_'
        #             break
        #         elif node.level == 1: # if main category selected, add subcategory
        #             value = self.add_category_to_db(node.text, self.entry_text)
        #             self.topwidget.tree_view.add_category_to_tree(value, node)
        #             break
        #         else: # if subcategory is selected, add another subategory
        #             value = self.add_category_to_db(node.parent_node.text, self.entry_text)
        #             self.topwidget.tree_view.add_category_to_tree(value, node.parent_node)
        #             break
        # if not node_selected:  # if no selection at all, add as a main category
        #     value = db.adding_to_db('kategorie', 'kategoria_glowna', self.entry_text)
        #     self.topwidget.tree_view.add_category_to_tree(value)  # value is like: self.ids.entry.text + suffix '_'

        self.dismiss()

class ChangeNamePopup(Popup):
    topwidget = ObjectProperty()
    widget_name = ObjectProperty() # to check if we change category/recipe or tag or db_file name
    selected_widget = ObjectProperty() #pass which node/tag/file is selected (not need to check it again)

    def save(self):
        # what we type in textinput in popup
        new_name = self.ids.entry.text

        if self.widget_name == 'category/recipe': # WHEN WE CHANGE RECIPE/CATEGORY NAME (call from dropdownbutton Zmien nazwe)
            old_name = self.selected_widget.text
            selected_node_text = old_name.lower()
            selected_node_parent_text = (self.selected_widget.parent_node.text).lower()

            if self.selected_widget.node_property == 'recipe':
                db.update_db('przepisy', 'nazwa', new_name, 'nazwa', selected_node_text)
                self.topwidget.tree_view.selected_node.text = new_name
            else:
                # if main category is selected
                if self.selected_widget.level == 1:
                    db.update_db('kategorie', 'kategoria_glowna', new_name.lower(), 'kategoria_glowna', selected_node_text)

                    #also need to update category name in recipe table
                    for row in db.get_values_from_table('*', 'przepisy'):
                        if row[2] == selected_node_text:
                            db.update_db('przepisy', 'kategoria', new_name, 'nazwa', row[0])
                else:
                    # if subcategory is selected
                    # items_list = list(db.get_values_from_table('*', 'kategorie', 'kategoria_glowna', selected_node_parent_text)[0])  # getting the list of items in selected row
                    items_list = list(db.get_values_from_table('*', 'kategorie', 'kategoria_glowna', selected_node_parent_text))  # getting the list of items in selected row
                    for item in items_list:
                        if item == selected_node_text:
                            column_name = 'kategoria_{}'.format(str(items_list.index(item)))
                            db.update_db('kategorie', column_name, new_name.lower(), 'kategoria_glowna', selected_node_parent_text)

                            # also need to update category name in recipe table
                            for row in db.get_values_from_table('*', 'przepisy'):
                                if row[3] == selected_node_text:
                                    db.update_db('przepisy', 'podkategoria', new_name, 'nazwa', row[0])
                            break

                # change name in tree_view
                self.topwidget.tree_view.selected_node.text = new_name.upper()

        if self.widget_name == 'tag': # WHEN WE CHANGE TAG NAME (call from  tagtogglebuttons Zmien nazwe)
            old_name = self.selected_widget.text

            # change name on the tag list
            self.selected_widget.text = new_name

            # change name in db in tag table
            db.update_db('tagi', 'nazwa', new_name, 'nazwa', old_name)

            # change tag names in recipes
            for recipe in db.get_values_from_table('*', 'przepisy'):
                tag_list = [i.strip() for i in recipe[1].split(',')]  # we make list of tags, without spaces ets
                if old_name in tag_list:
                    new_tag_list = recipe[1].replace(old_name, new_name)
                    db.update_db('przepisy', 'tagi', new_tag_list, 'nazwa', recipe[0])

        if self.widget_name == 'db_file':
            os.rename(os.path.join(main_databes_directory_path, self.selected_widget), os.path.join(main_databes_directory_path, new_name + '.sqlite'))
            self.topwidget.ids.db_files_list_view.adapter.data.remove(self.selected_widget)  # Remove the matching item from list view
            self.topwidget.ids.db_files_list_view.adapter.data.extend([new_name + '.sqlite'])

        self.dismiss()

# class WarningPopup(Popup):
#     topwidget_choosefilepopup = ObjectProperty()
#     topwidget_setting_font_size = ObjectProperty()
#
#     # when warning popup is closed, set the focus on textinput image_path becaose user still wanta to enter correct path
#     def set_focus(self, event):
#         if self.topwidget_choosefilepopup: #if this event is triggered has value True
#             self.topwidget_choosefilepopup.ids.entry_image_path.focus = True
#         if self.topwidget_setting_font_size:


class FileNotFoundWarning(Popup):
    topwidget_choosefilepopup = ObjectProperty()

    # when warning popup is closed, set the focus on textinput image_path becaose user still wants to enter correct path
    def set_focus(self, event):
        self.topwidget_choosefilepopup.ids.entry_image_path.focus = True

class ChooseFilePopup(Popup):
    # this class set the value of image_label of AddRecipe class as a image path
    topwidget_addrecipe = ObjectProperty()

    def save_image_file(self, file_from_filechooser, file_from_path):
        if file_from_path and not file_from_path.startswith('http') and not os.path.isfile(file_from_path):
            # whe need to check if path given by the user is correct (when it is NOT url - we dont check url)
            popup_file_not_found_error = FileNotFoundWarning(title='Nie znaleziono pliku',
                                                             topwidget_choosefilepopup=self)
            return popup_file_not_found_error.open()
        else:
            if file_from_filechooser and not file_from_path:
                # IF ONLY FILE FROM TREE IS SELECTED
                # 'file' return list with one element - path, so we need to reference to that index
                path = file_from_filechooser[0]
            elif file_from_path and not file_from_filechooser:
                # IF ONLY FILE IS GIVEN IN TEXTINPUT
                path = file_from_path
            elif file_from_filechooser and file_from_path:
                # IF BOTH ARE CHOSEN: file selected and path given
                path = file_from_path
            else:
                # when user presses SAVE but choosed nothing
                path = ''

            self.topwidget_addrecipe.ids.image_path_label.text = path
            self.dismiss()

class CreateNewDB(Popup):
    topwidget = ObjectProperty()
    entry_text = StringProperty()

    def save(self):
        db_file = self.entry_text + '.sqlite'

        # create a file in dir
        path = os.path.join(main_databes_directory_path, db_file)
        with open(path, 'w+') as fh:
            fh.write('')

        # refresh list view
        self.topwidget.ids.db_files_list_view.adapter.data.extend([db_file])

        self.dismiss()

class UserDB(Popup):

    def create_list_with_files_from_db_file(self):
        # get the list of users db files
        list_with_db_files = []
        for file in os.listdir(main_databes_directory_path):
            list_with_db_files.append(file)
        return list_with_db_files

    def get_selected_file(self):
        # return  selected file in list view
        if self.ids.db_files_list_view.adapter.selection: # If a list item is selected
            selected_file = self.ids.db_files_list_view.adapter.selection[0].text # Get the text from the item selected
            return selected_file

    def open_db(self):
        # open another window of the app
        # if we want use same python program, must be sys.executable


        if self.get_selected_file(): # if some file is selected
            # procs = []
            new_proc = subprocess.Popen([sys.executable, 'app_cookbook.py', self.get_selected_file()], stdin=PIPE)
            # procs.append(new_proc)
            # for proc in procs:
            #     proc.wait()

            self.dismiss()

    def add_new_db(self):
        popup_create_new_db_instance = CreateNewDB(title = "Utwórz nową książkę", topwidget = self)
        popup_create_new_db_instance.ids.entry.hint_text = 'Podaj nazwę pliku'
        popup_create_new_db_instance.open()

    def remove_db_file(self):
        selected_file = self.get_selected_file()
        if selected_file:
            self.ids.db_files_list_view.adapter.data.remove(selected_file) # Remove the matching item from list view
            os.remove(os.path.join(main_databes_directory_path, selected_file)) # remove file from directory

    def rename_db_file(self):
        selected_file = self.get_selected_file()
        if selected_file:
            popup_rename_db_file_instance = ChangeNamePopup(title = 'Podaj nową nazwę pliku', topwidget = self, widget_name = 'db_file', selected_widget = selected_file)
            popup_rename_db_file_instance.open()

class TabTextInput(TextInput):
    # on_text: runs a callback when the text changes; text = on_text
    # suggestion_text - shows a suggestion text at the end of the current line

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if self.suggestion_text and keycode[1] == 'tab': # autosuggestion when TAB is pressed
            self.insert_text(self.suggestion_text)
            self.suggestion_text = ''
            return True
        return super(TabTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)


    def set_suggestion_text(self, value, type_of_field):
        """search through categories and subcategories
        when node is selected, text = node.text
        In this method we are setting the value suggestion_text"""

        # value - this parameter holds what we type in textinput; it changes with every inserted letter

        self.suggestion_text = ''
        list_of_values= []

        if type_of_field == 'category':
            # getting catgeory and asubcategory list
            # couse new categories might appned to the list, need to create in every cycle ??
            list_of_values = get_category_subcategory_list()

        if type_of_field == 'tags':
            # getting list of tags
            list_of_values = get_first_column_values('tagi')

          # setting suggestion_text value
        if value in list_of_values: #when textinput is already a category name
            return True
        else:
            for item in list_of_values:
                found_value_index = item.rfind(value)
                if found_value_index == 0: # if what we type are the first letters of some category name
                    try:
                        self.suggestion_text = item[len(value):]
                    except IndexError: # when string index out of range (self.suggestion_text = cat[len(value)])
                        self.suggestion_text = item
                    break

class AddRecipeScreen(ModalView):
    topwidget = ObjectProperty() # we need to refer to tree instance; self.topwidget.tree_view WHERE self.topwidget is instance(self) of MainScreen

    title = StringProperty()
    category = StringProperty() # already set to lower
    tags = StringProperty()
    source = StringProperty()
    ingredients = StringProperty()
    description = StringProperty()
    image_location = StringProperty()

    def save_recipe(self):
        self.add_title_and_category_to_recipe() # must be fired first, to create unique name in db table
        self.add_tags_to_recipe()
        self.add_description_to_recipe()
        self.add_ingredients_to_recipe()
        self.add_source_to_recipe()
        self.add_image(self.image_location)
        self.dismiss()

    def close(self):
        self.dismiss()

    def set_category_hint(self):
        # if user select some node and that press Add recipe, this category will be already entered in Category textinput
        if self.topwidget.tree_view.get_selected_node() and (self.topwidget.tree_view.get_selected_node()).node_property == 'category':
            # if some node is selected and has category property
            category_input = (self.topwidget.tree_view.get_selected_node()).text
        elif self.topwidget.tree_view.get_selected_node() and (self.topwidget.tree_view.get_selected_node()).node_property == 'recipe':
            # if some node is selected and has recipe property
            category_input = ((self.topwidget.tree_view.get_selected_node()).parent_node).text
        else:
            # if no node is selected
            category_input = ''
        return category_input

    def add_title_and_category_to_recipe(self):
        self.add_title() # FIRST: create recipe by name
        self.add_category_to_recipe() # SECOND: create new category if not exist, THIRD: add this recipe to tree under new category

        for node in list(self.topwidget.tree_view.iterate_all_nodes()):
            if (node.text).lower() == self.category:
                self.topwidget.tree_view.add_recipe_to_tree(self.title, node)

    def add_title(self, edit_mode = False):
        # when title is no typed, set default name
        if self.title == '':
            self.title = 'nowy przepis'

        if not edit_mode:
            value = db.adding_to_db('przepisy', 'nazwa', self.title)
        else:
            value = db.update_db('przepisy', 'nazwa', self.title, 'nazwa', self.old_value_title)
            self.node.text = self.title

        self.title = value  # we set title after adding to db and checking if title will be with suffix "_" (if already exist

    def add_category_to_recipe(self, edit_mode = False):
        category_list = get_category_subcategory_list()
        main_category_list = get_first_column_values('kategorie')

        if self.category == '':  # when category is no typed, set default name
            self.category = 'kategoria'

        # IF NEW CATEGORY IS TYPED, add new category to db as MAIN category
        if self.category not in category_list:
            db.adding_to_db('kategorie', 'kategoria_glowna', self.category)  # 1. create new category in db
            self.topwidget.tree_view.add_category_to_tree(self.category)  # 2. add category to tree as MAIN category
            db.update_db('przepisy', 'kategoria', self.category, 'nazwa', self.title)  # 3. update category in db in recipe

        # IF CATEGORY ALREADY EXIST
        else:
            # check if its main or subcategory
            if self.category in main_category_list:
                db.update_db('przepisy', 'kategoria', self.category, 'nazwa', self.title)
            else:
                db.update_db('przepisy', 'podkategoria', self.category, 'nazwa', self.title)
                for row in list(db.get_values_from_table('*', 'kategorie')):
                    if self.category in row:
                        db.update_db('przepisy', 'kategoria', row[0], 'nazwa', self.title)
                        break

        # when in edit view, move recipe to new category
        if edit_mode:
            # when EDIT recipe view, do also this:
            self.topwidget.tree_view.remove_node(self.node)  # we will move recipe to new category, so we can delete this recipe node

            for i in self.topwidget.tree_view.iterate_all_nodes():
                if (i.text).lower() == self.category:
                    self.topwidget.tree_view.add_recipe_to_tree(self.title, i)
                    break

    def add_tags_to_recipe(self):
        refactor_tags = []
        for tag in self.tags.split(','): #if user will type tags with i.e. spaces, this function assures clear tags list
            refactor_tags.append(tag.strip())
        string_tags = ', '.join(refactor_tags)
        db.update_db('przepisy', 'tagi', string_tags, 'nazwa', self.title)

        # if new tag is entered, add it to tags table
        for tag in refactor_tags:
            if tag not in get_first_column_values('tagi'):
                db.adding_to_db('tagi', 'nazwa', tag)

    def add_source_to_recipe(self):
        db.update_db('przepisy', 'zrodlo', self.source, 'nazwa', self.title)

    def add_ingredients_to_recipe(self):
        db.update_db('przepisy', 'skladniki', self.ingredients, 'nazwa', self.title)

    def add_description_to_recipe(self):
        db.update_db('przepisy', 'opis', self.description, 'nazwa', self.title)

    def choose_image_file_button(self):
        choose_fie_instance = ChooseFilePopup(title = "Wybierz zdjęcie z dysku lub podaj adres URL lub ścieżkę do pliku", topwidget_addrecipe = self)
        choose_fie_instance.open()

    def add_image(self, path):
        if path and path != 'brak zdjęcia...': # if image is given by the user; if NOT, recipe_view class will show default_empty_img (kivy logo)
            recipe_image_filename = (file_name + '_' + self.title.replace(' ', '_'))

            # extension = os.path.splitext(self.image_location)[1] # i.e. .jpg
            extension = os.path.splitext(path)[1] # i.e. .jpg
            if not extension: # when i.e. url is given without extension
                extension = '.png'

            recipe_image_path = os.path.join(main_images_directory_path, recipe_image_filename + extension)

            try:
                if path.startswith('http'):
                    # urllib.request.urlopen(self.image_location)
                    urllib.request.urlretrieve(path, recipe_image_path) # download the file
                else: #if its normal path
                    shutil.copy(path, recipe_image_path)  # copy image to recipe folder
            except FileNotFoundError: # we chack it by check_image_path_button; here we can ignore that error
                pass

            # adding to db
            db.update_db('przepisy', 'zdjecie', recipe_image_path, 'nazwa', self.title)
        else:
            # if img source is empty field, save it in db (i.e. when we edit recipe and there is a img and we want to delete it)
            db.update_db('przepisy', 'zdjecie', "", 'nazwa', self.title)

class EditRecipeScreen(AddRecipeScreen):
    topwidget = ObjectProperty() # we need to refer to tree instance; self.topwidget.tree_view WHERE self.topwidget is instance(self) of MainScreen
    node = ObjectProperty() # selected node (selected recipe), pass as value when class is call

    def __init__(self, **kwargs):
        super(EditRecipeScreen, self).__init__(**kwargs)

        # read values from db
        self.ids.entry_title.text = self.node.text
        self.ids.entry_category.text = self.node.parent_node.text
        self.ids.entry_tags.text = self.get_recipe_data('tagi')
        self.ids.entry_source.text = self.get_recipe_data('zrodlo')
        self.ids.entry_ingredients.text = self.get_recipe_data('skladniki')
        self.ids.entry_description.text = self.get_recipe_data('opis')
        self.ids.image_path_label.text = self.get_recipe_data('zdjecie')

        # store old values to check if user changed anything when editing
        self.old_value_title = self.title
        self.old_value_category = self.category
        self.old_value_tags = self.tags
        self.old_value_source = self.source
        self.old_value_ingrdients = self.ingredients
        self.old_value_descripton = self.description
        self.old_value_image = self.image_location

    def save_recipe(self):

        if self.title != self.old_value_title: # we changed title first
            self.add_title(edit_mode = True)

        if self.category != self.old_value_category:
            self.add_category_to_recipe(edit_mode = True)

        if self.source != self.old_value_source:
            self.add_source_to_recipe()

        if self.tags != self.old_value_tags:
            self.add_tags_to_recipe()

        if self.ingredients != self.old_value_ingrdients:
            self.add_ingredients_to_recipe()

        if self.description != self.old_value_descripton:
            self.add_description_to_recipe()

        if self.image_location != self.old_value_image:
            self.add_image(self.image_location)

        self.dismiss()

    def reload_recipe_view(self, event):
        main_screen_instance.reload_recipe_view()

    # WE REWRITE THIS IN MainScreen class - delete when no errors occur
    #     main_screen_instance.ids.recipe_view.clear_widgets()  # need to refer to MAON SCREEN instance; clear recipe_view_instance window
    #     recipe_view_instance = RecipeView(selected_recipe=self.node)
    #     main_screen_instance.ids.recipe_view.add_widget(recipe_view_instance)  # need to refer to MAON SCREEN instance (need to put recipe instance to
    #     for node in self.topwidget.tree_view.iterate_all_nodes():
    #         if node.text == self.title:
    #             self.topwidget.tree_view.select_node(node)

    def get_recipe_data(self, name):
        # value = list(db.get_values_from_table(name, 'przepisy', 'nazwa', self.node.text)[0])
        value = list(db.get_values_from_table(name, 'przepisy', 'nazwa', self.node.text))
        if not value[0]:
            result = ''
        else:
            result = value[0]
        return result

class DropDownMenu(DropDown):
    state = BooleanProperty(False)

class TagList(ModalView):
    # taglist are handled by TagToggleButtons
    pass

class TagToggleButtons(StackLayout):
    def __init__(self, **kwargs):
        super(TagToggleButtons, self).__init__(**kwargs)

        tags_list = get_first_column_values('tagi')

        # adding all tags to window
        for tag in tags_list:
            if tag not in (None, ''):
                self.add_widget(ToggleButton(text= tag))

    def remove_tag(self):
        for tag in self.children: # self.children - List of children of this widget
            if tag.state == 'down':
                self.remove_widget(tag)

                # deleting tag from table 'tagi
                db.delete_from_db('tagi', 'nazwa', tag.text)

                # deleting this tag from recipes
                for recipe in db.get_values_from_table('*', 'przepisy'):
                    tag_list = [i.strip() for i in recipe[1].split(',')] # we make list of tags, without spaces ets
                    if tag.text in tag_list:
                        tag_list.remove(tag.text)
                        db.update_db('przepisy', 'tagi', ', '.join(tag_list), 'nazwa', recipe[0])
                break

    def change_tag_name(self):
        for tag in self.children: # self.children - List of children of this widget
            if tag.state == 'down':
                popup_changing_name_instance = ChangeNamePopup(title='Podaj nową nazwę', topwidget = self, widget_name = 'tag', selected_widget = tag)
                return popup_changing_name_instance.open()

class MainScreen(BoxLayout):
    # this is main_screen_instance instance

    # we can delete it ???
    # def get_instance(self, id_name):
    #     global main_instance
    #     for i in self.ids.keys():
    #         if i == id_name:
    #             main_instance = self.ids[i]
    #     return main_instance

    def add_recipe_button(self):
        screen_add_recipe_instance = AddRecipeScreen(title = 'Dodaj nowy przepis', topwidget = self)
        return screen_add_recipe_instance.open()

    def remove_recipe_button(self):
        selected_node = self.ids.tree.get_selected_node()
        if selected_node and selected_node.node_property == 'recipe':
            self.ids.tree.remove_node(selected_node) # remove recipe from tree
            # img_path = db.get_values_from_table('zdjecie', 'przepisy', 'nazwa', selected_node.text)[0][0] # remove image fro directory
            img_path = db.get_values_from_table('zdjecie', 'przepisy', 'nazwa', selected_node.text)[0] # remove image fro directory
            if img_path:
                os.remove(img_path)
            db.delete_from_db('przepisy', 'nazwa', selected_node.text) # remove recipe from db
            self.ids.recipe_view.clear_widgets() # refresh tree

    def edit_recipe_button(self):
        selected_node = self.ids.tree.get_selected_node()
        if selected_node and selected_node.node_property == 'recipe':
            screen_edit_recipe_instance = EditRecipeScreen(title = "Edytuj przepis", topwidget = self, node = selected_node)
            return screen_edit_recipe_instance.open()

    def add_category_button(self):
        popup_add_category_instance = AddCategoryPopup(title = 'Dodawanie nowej kategorii', topwidget = self)
        popup_add_category_instance.ids.entry.hint_text = 'Podaj nazwę kategorii'
        return popup_add_category_instance.open()

    def remove_category_button(self):
        selected_node = self.ids.tree.get_selected_node()
        if selected_node and self.ids.tree.selected_node.node_property == 'category':
            if selected_node.level == 1:
                # when main category is selected, delete the whole row (all subcategories and recipes)
                db.delete_from_db('kategorie', 'kategoria_glowna', (selected_node.text).lower())
                db.delete_from_db('przepisy', 'kategoria', (selected_node.text).lower())
                self.ids.tree.remove_node(selected_node)
                self.ids.recipe_view.clear_widgets()
            if selected_node.level not in (0, 1):
                # when subcategory is selected, set value of this record to an empty record
                selected_value = (selected_node.text).lower()
                items_list = list(db.get_values_from_table('*', 'kategorie', 'kategoria_glowna', (selected_node.parent_node.text).lower()))  # getting the list of items in selected row
                for item in items_list:
                    if item == selected_value:
                        column_name = 'kategoria_{}'.format(str(items_list.index(item)))
                        db.update_db('kategorie', column_name, "", 'kategoria_glowna', (selected_node.parent_node.text).lower())
                        db.delete_from_db('przepisy', 'podkategoria', (selected_node.text).lower())
                        self.ids.tree.remove_node(selected_node)
                        self.ids.recipe_view.clear_widgets()

    def dropdown_button_action(self, button_value):
        if button_value == 'change_name':
            for node in list(self.ids.tree.iterate_all_nodes()):
                if node.is_selected and node.level != 0:
                    popup_changing_name_instance = ChangeNamePopup(title = 'Zmień nazwę', topwidget = self, widget_name = 'category/recipe', selected_widget = node)
                    popup_changing_name_instance.ids.entry.hint_text = 'Podaj nową nazwę'
                    return popup_changing_name_instance.open()
        if button_value == 'show_tag_list':
            tag_list_window_instance = TagList()
            return tag_list_window_instance.open()
        if button_value == 'managing_user_db':
            popup_user_db_instance = UserDB(title ='Zarządzaj własnymi książkami')
            return popup_user_db_instance.open()
        if button_value == 'settings':
            myapp.open_settings()


    def search(self):
        search_input = self.ids.entry_search.text
        title_checbox = self.ids.checkbox_title.state
        tags_checkbox = self.ids.checkbox_tags.state
        ingredients_checkbox = self.ids.checkbox_ingredients.state
        search_result = []   # list contains ALL recipes (row = recipe), that fit to the users quesry

        if search_input.startswith('\"') and search_input.endswith('\"'): # if user types search input in quotes, search the whole expression
            search_value = search_input
        else:
            search_value = search_input

        all_items_list = db.get_values_from_table('*', 'przepisy')

        if title_checbox == 'down' and tags_checkbox == 'down' and ingredients_checkbox =='down': # complete search
            for row in all_items_list:
                if search_value in row[0].lower() or search_value in row[1] or search_value in row[4].lower(): #row[0] - title, row[1] - tags, row[4] - ingredients
                    search_result.append(row)
        elif title_checbox == 'down' and tags_checkbox == 'normal' and ingredients_checkbox == 'normal': # only title
            for row in all_items_list:
                if search_value in row[0].lower():
                    search_result.append(row)
        elif tags_checkbox == 'down' and title_checbox == 'normal'and ingredients_checkbox == 'normal': # only tags
            for row in all_items_list:
                if search_value in row[1]:
                    search_result.append(row)
        elif ingredients_checkbox == 'down' and title_checbox == 'normal' and tags_checkbox == 'normal': # only ingrediensts
            for row in all_items_list:
                if search_value in row[4].lower():
                    search_result.append(row)
        elif title_checbox == 'down' and tags_checkbox == 'down' and ingredients_checkbox == 'normal': # title and tags
            for row in all_items_list:
                if search_value in row[0].lower() or search_value in row[1]:
                    search_result.append(row)
        elif title_checbox  == 'down' and ingredients_checkbox == 'down' and tags_checkbox == 'normal': # title and ingredients
            for row in all_items_list:
                if search_value in row[0].lower() or search_value in row[4].lower():
                    search_result.append(row)
        elif tags_checkbox  == 'down' and ingredients_checkbox == 'down' and title_checbox == 'normal': # tags and ingredients
            for row in all_items_list:
                if search_value in row[1] or search_value in row[4].lower():
                    search_result.append(row)
        else: # all checkboxes are off
            search_result = all_items_list

        # make new tree only with recipes from query
        self.ids.tree.read_recipes_from_db(search_result)

    def on_text_add_recipe_tp_tree(self):
        # whem search field is cleared, on_text event reads all recipes from db
        self.ids.tree.read_recipes_from_db(db.get_values_from_table('*', 'przepisy'))

    def reload_recipe_view(self):
        # refresh recipe view after some changes
        # used in: EditRecipeScreen (kv file, on_dismiss event) and when settings are changed

        # current_recipe_view_node - global variable set in TreeCategory in method: 'on_touch_up'
        try:
            self.ids.recipe_view.clear_widgets()  # clear recipe_view_instance window
            recipe_view_instance = RecipeView(selected_recipe = current_recipe_view_node)  # make new recipe_view instance
            self.ids.recipe_view.add_widget(recipe_view_instance)  # add this recipe_view instance to MAIN SCREEN layout
        except NameError:
            # name 'current_recipe_view_node' is not defined: when we didn't select any recipe yet
            pass




class CookBookApp(App):
    # this is myapp instance

    def build(self):
        self.title = "Książka kucharska" + ' - ' + file_name

        # define what panel settings I want to use
        self.settings_cls = Settings
        self.use_kivy_settings = False # get rid off KIVY panel in Settings
        # self.config.items('cookbook_settings') ??
        # some_setting = self.config.get('cookbook_settings', 'font_color_title')  # to get of some setting value

        global main_screen_instance
        main_screen_instance = MainScreen()
        return main_screen_instance
        # return MainScreen()

    # SETTINGS PANEL
    # those three following methods are for Settings panel (Settings)
    def build_config(self, config):
        config.setdefaults('cookbook_settings', {
            'main_cookbook_file': 'main',
            'font_size_ingredients': 15,
            'font_size_description': 15,
            'font_color_title': '#c5661d'
        })

    def build_settings(self, settings):
        settings.add_json_panel('OPCJE KSIĄŻKI KUCHARSKIEJ', self.config, data=settings_json)

    def display_settings(self, settings):
        # I override this method of Setting class to open settings panel in popup
        # I re-write this from example from app.py
        try:
            p = self.settings_popup
        except AttributeError:
            self.settings_popup = Popup(content=settings,
                                        title='Opcje książki kucharskiej',
                                        size_hint=(0.8, 0.8))
            p = self.settings_popup
        if p.content is not settings:
            p.content = settings
        p.open()

    def close_settings(self, *largs):
        # I re-write this from example from app.py
        try:
            p = self.settings_popup
            p.dismiss()
            main_screen_instance.reload_recipe_view()
        except AttributeError:
            pass # Settings popup doesn't exist


    # def on_config_change(self, config, section, key, value):
    #     pass
        # if key == 'font_size_ingredients' or key == 'font_size_description':
        #     if int(value) < 10 or int(value) > 40:
        #         popup_warning = WarningPopup(title='Zły rozmiar czcionki', topwidget_setting_font_size=self)
        #
        #
        #         return popup_warning.open()


    def get_recipe_options(self, setting):
        # method that read saved options in cookbook.ini file
        setting_value = self.config.get('cookbook_settings', setting)
        return setting_value


if __name__ == "__main__":
    main_screen_instance = None

    try:
        list_of_items_in_dir = [i for i in os.listdir('.')]

        # creating directories for images and additional cookbook databases created by the user
        if 'databes_files' not in list_of_items_in_dir:
            os.mkdir('databes_files')
            path = os.path.join(main_databes_directory_path, 'przepisy.sqlite')
        if 'recipe_images' not in list_of_items_in_dir:
            os.mkdir('recipe_images')

        # CREATING INSTANCE OF db
        # running main program or other db opened by the user from settings
        # sys.argv[0] - it always means the name of the running script, others arguments are additional, that why we check len to know if some paremeter was given
        file_name = ''
        if len(sys.argv) == 2: # if program is passed with some argument (might be through the open_db method in UserDB class)
            file_name = sys.argv[1] # we need to extract file_name -it is needed also for our title of app window (used in CookBookApp class)
        else:
            try: # checking if cookbook.ini (setting are saved there) exists
                with open('cookbook.ini', 'r') as fh:
                    for line in fh:
                        if line.startswith('main_cookbook_file'):
                            file_name = (line.partition('= ')[2]).strip()
                            break
                if file_name == '': # when cookbook.ini is empty, it doesn't iterate through lines and that file_name has no value
                    file_name = 'przepisy.sqlite'
            except FileNotFoundError:
                file_name = 'przepisy.sqlite'
        db = DatabaseManager(os.path.join(main_databes_directory_path, file_name))

        # GuiCookBookApp().run()
        myapp = CookBookApp()
        myapp.run()

    except: # we catch all errors to be saved in the log file
        logging.exception("Wystąpił błąd aplikacji")