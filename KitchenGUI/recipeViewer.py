import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
from recipeCreator import *
logger = logging.getLogger('Debug Log')

class recipeViewer(sg.Tab):
    def __init__(self, title, master, *args, **kwargs):
        self.master = master
        self.activeRecipe = None
        self.recipeBox = sg.Multiline(key='-VIEWER-BOX-', size=(80,30),
                tooltip="Recipes will be displayed here when they are selected on the recipe table tab.")
        self.export = sg.Button('Export File', key='-VIEWER-EXPORT-',
                tooltip="This button causes a prompt to display that will allow you to create a recipe file")
        self.share = sg.Button('Share', key='-VIEWER-SHARE-', disabled=True,
                tooltip="This button will allow you to quickly share recipes with friends - Not In Use")
        layout = [
            [
                 sg.Button('Print', key='-VIEWER-PRINT-', disabled=True,
                        tooltip="This button will let you print the currently selected recipe"),
                 self.export,
                 self.share,
                 sg.Button('Edit', key='-VIEWER-EDIT-',
                        tooltip="Click here to edit this recipe")
            ],
            [self.recipeBox],
            [sg.HorizontalSeparator()],
            [sg.T('Nutrition', tooltip="This area will be filled with Nutrition info about the recipe - Not In Use")]
        ]
        super().__init__(title, layout=layout, *args, **kwargs)

    def handle(self, event, values):
        if event == '-VIEWER-PRINT-':
            if self.activeRecipe == None:
                sg.PopupError("No recipe selected!", title="No Recipe")
                return True
            return True
        elif event == '-VIEWER-EXPORT-':
            if self.activeRecipe == None:
                sg.PopupError("No recipe selected!", title="No Recipe")
                return True
            self.exportModal(self.activeRecipe)
            return True
        elif event == '-VIEWER-SHARE-':
            if self.activeRecipe == None:
                sg.PopupError("No recipe selected!", title="No Recipe")
                return True
            # self.activeRecipe.outputToTxt(self.master.prefs['recipeFolder'] + 'text.txt')
            return True
        elif event == '-VIEWER-EDIT-':
            # navigate to editor tab
            if self.activeRecipe == None:
                sg.PopupError("No recipe selected!", title="No Recipe")
                return True
            return False
        return False

    def fillFields(self, rec):
        self.activeRecipe = rec
        self.recipeBox.update(rec.__str__())

    def exportModal(self, rec):
        defaultType = 'txt'
        types = {'txt': ('Text Files', '*.txt'),
                 'pdf': ('PDF Files', '*.pdf'),
                 'json':('JSON Files', '*.json'),
                 'yaml':('YAML Files', '*.yaml')}
        recTitle = rec.title.replace(' ', '-')
        defaultSave = self.master.prefs['recipeFolder'] + recTitle + f'.{defaultType}'
        layout = [[sg.Text('Export Details')],
          [
            sg.T('Destination'),
            sg.In(default_text=defaultSave, key='-EXPORT-FOLDER-'),
            sg.FileSaveAs('Browse',
                initial_folder=self.master.prefs['recipeFolder'])
          ],
          [
            sg.T('Format'),
            sg.Combo(default_value=defaultType, values=['txt', 'pdf', 'yaml', 'json'],
                    size=(20, 12), key='-FORMAT-LIST-', enable_events=True)
          ],
          [sg.Button('Export'), sg.Button('Cancel')]]

        window = sg.Window('Export Details', layout)

        while True:
            event, values = window.read()
            # logger.debug(f'prefEditor event is {event}')
            if event in (sg.WIN_CLOSED, 'Cancel'):
                break
            elif event == '-FORMAT-LIST-':
                new_type = values['-FORMAT-LIST-']
                new_fname = values['-EXPORT-FOLDER-'].split('.')
                new_fname[-1] = new_type
                new_fname = '.'.join(new_fname)
                window['-EXPORT-FOLDER-'].update(value=new_fname)
            elif event == 'Export':
                # logger.debug(f'list value is {values["-LIST-"]}')
                self.exportFile(rec, type=values['-FORMAT-LIST-'], location=values['-EXPORT-FOLDER-'])
                break
            elif event == 'Cancel':
                break

        window.close()

    def exportFile(self, rec, type, location):
        with open(location, 'w') as f:
            if type == 'PDF':
                # for now will be the same as txt
                f.write(rec.__str__())
            elif type == 'txt':
                f.write(rec.__str__())
            elif type == 'yaml':
                f.write('---\n')
                yaml.dump(rec.outputToYaml(), f)
