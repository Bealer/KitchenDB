import logging
import PySimpleGUI as sg
# import PySimpleGUIWeb as sg
# import PySimpleGUIQt as sg
import KitchenGUI.searchBar as search
from database import *
from recipeCreator import *
from apiCalls import *
logger = logging.getLogger('Debug Log')

class recipeTable(sg.Tab):
    def __init__(self, title, master, *args, tableKey='-RECIPE-TABLE-', **kwargs):
        self.master = master
        self.db = self.master.db
        self.recTableDim = self.master.recTableDim
        self.tableKey = tableKey
        self.header = ['Title', 'Prep Time', 'Cook Time', 'Yield', 'Category']
        super().__init__(title, layout=self.createRecipeTable(), *args, **kwargs)

    def createRecipeTable(self):
        rowCount, colCount = self.recTableDim
        # Acquire data
        # note, the ingredients and directions are left off due to the number of columns
        # header = recipe.pretty_fields[:colCount]
        recs = self.db.recipes(first=0, count=rowCount)
        data = []
        for rec in recs:
            recInfo = rec.guts()
            temp = []
            for col in self.header:
                temp.append(recInfo[col])
            data.append(temp)
        # allData = [self.header, *data]
        self.tableData = recs
        self.master.tableData = recs
        self.recTable = sg.Table(data,
                                headings=self.header,
                                num_rows=rowCount,
                                enable_events=True,
                                col_widths=[24, 9, 9, 20, 9, 6],
                                auto_size_columns=False,
                                key=self.tableKey)
        # col = sg.Column(layout = tab, scrollable=True)
        self.master.expands['xy'].append(self.recTable)
        layout = [
            [sg.T('Sort By'), sg.Combo(values=['Title', "Category", 'Rating'], key='-FILTER-')],
            [*search.searchBar(self.master,key='RECIPE'), sg.Button('Add New Recipe', key='-ADDNEW-')],
            [self.recTable]
        ]
        # return sg.Column(layout=layout,expand_x=True,expand_y=True,justification='center')
        return layout

    def handle(self, event, values):
        if event == self.tableKey:
            # click on table, event to be handled by main
            # self.master.switchTabs('-EDITOR-')
            # self.master.deferHandle('-EDITOR-', 'fill', values)
            return False
        elif event == '-RECIPE-SBUTTON-':
            self.searchdb(values['-RECIPE-SBOX-'])
            return True
        return False

    def searchdb(self, query):
        row, col = self.recTableDim
        # get search results
        recs = self.db.search(query)
        data = []
        header = recipe.pretty_fields[:col]
        for rec in recs:
            recInfo = rec.guts()
            temp = []
            for col in header:
                temp.append(recInfo[col])
            data.append(temp)

        # preppend header list
        # data = [header, *data]
        # pass all data to update table
        self.master.state["lastTableAction"] = "search"
        self.master.state["lastSearch"] = query
        self.tableData = recs
        self.recTable.update(values = data)

    def refreshRecipeTable(self):
        logger.debug("Refreshing recipe table")
        row, col = self.recTableDim
        if self.master.state["lastTableAction"] == "default":
            logger.debug("last state was default")
            recs = self.db.recipes(count=row)
        elif self.master.state["lastTableAction"] == "search":
            logger.debug("last state was search")
            recs = self.db.search(self.master.state["lastSearch"])
        # create data matrix
        data = []
        for rec in recs:
            recInfo = rec.guts()
            temp = []
            for col in self.header:
                temp.append(recInfo[col])
            data.append(temp)

        # preppend header list
        # data = [header, *data]
        self.tableData = recs
        # chop off ing and dirs for display
        self.recTable.update(values=data)
