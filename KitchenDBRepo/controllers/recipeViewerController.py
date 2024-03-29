import logging, yaml
import numpy as np
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
from containers.recipe import recipe
from KitchenModel import KitchenModel
from controllers.controller import controller
logger = logging.getLogger('recipeViewerController log')

class recipeViewerController(controller):
    def __init__(self):
        self.model = KitchenModel.getInstance()
        self.recipeBox = None

    def setup(self):
        self.recipeBox = self.model.get("tabData", "-VIEWER-", "recipeBox")

    def handle(self, event, values):
        if event == '-VIEWER-PRINT-':
            if self.model.get('activeRecipe') == None:
                sg.PopupError("No recipe selected!", title="No Recipe")
                return True
            return True
        elif event == '-VIEWER-EXPORT-':
            if self.model.get('activeRecipe') == None:
                sg.PopupError("No recipe selected!", title="No Recipe")
                return True
            self.exportModal(self.model.get('activeRecipe'))
            return True
        elif event == '-VIEWER-SHARE-':
            if self.model.get('activeRecipe') == None:
                sg.PopupError("No recipe selected!", title="No Recipe")
                return True
            # self.model.get('activeRecipe').outputToTxt(self.model.get('prefs', 'recipeFolder') + 'text.txt')
            return True
        elif event == '-VIEWER-EDIT-':
            # navigate to editor tab
            if self.model.get('activeRecipe') == None:
                sg.PopupError("No recipe selected!", title="No Recipe")
                return True
            self.model.set('active_view', value='-EDITOR-')
            return True
        elif event == '-VIEWER-MULTBY-':
            if self.model.get('activeRecipe') == None:
                sg.PopupError("No recipe selected!", title="No Recipe")
                self.multby.update('1')
                return True
            self.fillFields(recipe(copyme=self.model.get('activeRecipe')) * float(values['-VIEWER-MULTBY-']))
            return True
        return False

    def fillFields(self, rec):
        self.recipeBox.update(rec.__str__())

    def resetMult(self):
        self.multby.update('1')

    def newRecipe(self, rec):
        self.model.set('activeRecipe', value=rec)
        self.resetMult()
        self.fillFields(rec)

    def exportModal(self, rec):
        defaultType = 'txt'
        types = {'txt': ('Text Files', '*.txt'),
                 'pdf': ('PDF Files', '*.pdf'),
                 'json':('JSON Files', '*.json'),
                 'yaml':('YAML Files', '*.yaml')}
        recTitle = rec.title.replace(' ', '-')
        defaultSave = self.model.get('prefs', 'recipeFolder') + recTitle + f'.{defaultType}'
        layout = [[sg.Text('Export Details')],
          [
            sg.T('Destination'),
            sg.In(default_text=defaultSave, key='-EXPORT-FOLDER-'),
            sg.FileSaveAs('Browse',
                initial_folder=self.model.get('prefs', 'recipeFolder'))
          ],
          [
            sg.T('Format'),
            sg.Combo(default_value=defaultType, values=['txt', 'pdf', 'yaml', 'json'],
                    size=(20, 12), key='-FORMAT-LIST-', enable_events=True)
          ],
          [sg.Button('Export'), sg.Button('Cancel')]]

        window = sg.Window('Export Details', layout, modal=True)

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
