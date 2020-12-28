import logging
logger = logging.getLogger('dailyMenu Log')
from recipeCreator import *
from shoppingList import *

class dailyMenu:
    def __init__(self, date):
        self.date = date
        # self.name = date
        # if name:
        #     self.name = name
        self.shopping = shoppingList()
        self.data = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'misc': []
        }

    def add_category(self, group):
        if group in self.data.keys():
            logger.debug('Tried adding category that already exists')
        else:
            self.data[group] = []

    def add(self, group, rec):
        if group.lower() in ['breakfast']:
            self.data['breakfast'].append(rec)
        elif group.lower() in ['lunch']:
            self.data['lunch'].append(rec)
        elif group.lower() in ['dinner']:
            self.data['dinner'].append(rec)
        elif group.lower() in ['misc']:
            self.data['snacks'].append(rec)
        elif group.lower() in self.data.keys():
            self.data[group].append(rec)
        else:
            logger.debug("group not supported")
            raise Exception(f"Unsupported group given {group}")
        self.updateShoppingList(rec)

    def newShoppingList(self):
        self.shopping = shoppingList()
        self.shopping.add_ingredients(*self.data.values())

    def updateShoppingList(self, data):
        self.shopping.add_ingredients(data)

    def get(self, key):
        return self.data[key]
