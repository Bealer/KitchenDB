import csv, json, yaml, sys, logging, re, copy
import requests as rq
from contextlib import suppress
logger = logging.getLogger('Debug Log')

class recipe:
    dataFields = ['title string', 'prep_time integer', 'cook_time integer', 'yield string', 'category string',\
      'rating integer', 'ingredients json', 'directions json', 'source string']
    ugly_fields = ['title', 'prep_time', 'cook_time', 'yield', 'category', 'rating', 'ingredients', 'directions', 'source']
    pretty_fields = ['Title', 'Prep Time', 'Cook Time', 'Total Time','Yield', 'Category', 'Rating', 'Ingredients', 'Directions', 'Source']
    firstDigits = re.compile(r'\s*(\d+)(.*)')
    def __init__(self, data=None, file=None, copyme=None):
        self.multiplied = 1.0
        if copyme:
            self.edit(copy.deepcopy(copyme).guts())
        elif data:
            self.edit(data)
        elif file:
            self.readIn(file)
        else:
            self.new()


    def __str__(self):
        ingr = ''
        dir = ''
        info = f'{self.title}\nYields: {self.yieldAmnt} | Category: {self.category} | Rating: {self.rating}\n' +\
            f'Time - Prep: {self.prep_time} | Cook: {self.cook_time} | Total: {self.prep_time + self.cook_time}'
        for food, id, amount in self.ingredients:
            ingr += f'{food}: {amount}\n'
        for direction in self.directions:
            dir += f'{direction}\n'
        if self.multiplied != 1.0:
            dir += f'\n\n*This recipe has been multiplied by {self.multiplied}, cooking times may be affected*'

        return f'{info}\n\n{ingr}\n{dir}'

    def guts(self):
        return {"Title": self.title,
                "Prep Time": self.prep_time,
                "Cook Time": self.cook_time,
                "Total Time": self.total_time,
                "Yield": self.yieldAmnt,
                "Category": self.category,
                "Rating": self.rating,
                "Ingredients": self.ingredients,
                "Directions": self.directions,
                "Source": self.source}

    def meta(self):
        return tuple(recipe.pretty_fields)

    def edit(self, data):
        """Function that builds the recipe object from DB entry.
        expects data in this format:
        [('Peanut Butter Sandwich', 5, 0, '1 Sandwich', 'Lunch', -1,
          "[('BREAD', 473832, '2 Slices'), ('Peanut butter', 784416, '3 T'),
              ('JAM', 389529, '3 T')]",
          "['1. Spread PB on Sandwich', '2. Spread Jam on Sandwich', '3. Enjoy!']",
        '')]"""

        if isinstance(data, list) or isinstance(data, tuple):
            self.title = data[0]
            if len(self.title) <= 0:
                print('Error creating recipe, creating default')
                self.new()
                return
            self.prep_time = int(data[1]) # if len(data[1]) > 0 else 0
            self.cook_time = int(data[2]) # if len(data[2]) > 0 else 0
            self.total_time = self.prep_time + self.cook_time
            self.yieldAmnt = data[3]
            self.category = data[4]
            self.rating = int(data[5]) # if len(data[5]) > 0 else -1
            self.ingredients = self.interp(data[6])
            self.directions = self.interp(data[7])
            self.source = data[8]
        elif isinstance(data, dict):
            self.title = data['Title']
            if len(self.title) <= 0:
                print('Error creating recipe, creating default')
                self.new()
                return
            self.prep_time = int(data['Prep Time']) if len(data['Prep Time']) > 0 else 0
            self.cook_time = int(data['Cook Time']) if len(data['Cook Time']) > 0 else 0
            self.total_time = self.prep_time + self.cook_time
            self.yieldAmnt = data['Yield']
            self.category = data['Category']
            self.rating = int(data['Rating']) if len(data['Rating']) > 0 else -1
            self.ingredients = self.interp(data['Ingredients'])
            self.directions = self.interp(data['Directions'])
            self.source = data['Source']

    def new(self):
        self.title = ""
        self.prep_time = 0
        self.cook_time = 0
        self.total_time = self.prep_time + self.cook_time
        self.yieldAmnt = ""
        self.category = ""
        self.rating = 0
        self.ingredients = []
        self.directions = []
        self.source = ""

    def readIn(self, fname):
        with open(fname, 'r') as f:
            type = fname.split('.')[-1]
            if type == 'yaml':
                tab = yaml.load(f,Loader=yaml.FullLoader)
                self.edit(tab['fields'])

    def __mul__(self, factor):
        if float(factor) == 1.0:
            return self
        return self.multiplyBy(float(factor))


    def multiplyBy(self, factor:float):
        self.multiplied = factor
        yieldAmnt = recipe.firstDigits.match(self.yieldAmnt)
        newYield = int(yieldAmnt.group(1)) * factor
        self.yieldAmnt = f'{newYield}{yieldAmnt.group(2)}'

        new_ingredients = []
        for ing in self.ingredients:
            amnt = recipe.firstDigits.match(ing[2])
            newAmnt = f'{int(amnt.group(1))*factor}{amnt.group(2)}'
            new_ingredients.append((ing[0],ing[1],newAmnt))
        self.ingredients = new_ingredients
        return self

    def cli_new(self):
        """Function that builds the recipe.yaml file from user input"""
        self.title = input('Please enter the recipe name: ')
        if self.title == 'q':
            exit()
        # FIXME: error checking on input
        self.prep_time = int(input('Please enter the prep time (minutes): '))
        self.cook_time = int(input('Please enter the cook time (minutes): '))
        self.total_time = self.prep_time + self.cook_time
        self.yieldAmnt = input('Please enter the yield for this recipe: ')
        self.category = input('Please enter the category for this recipe: ')
        self.rating = -1 # unrated
        self.ingredients = getIng()
        self.directions = getDir()
        self.source = input('Add a source, or leave blank: ')
        # self.outputToYaml()

    def outputToYaml(self):
        """function that generates a recipe.yaml file from given parameters"""
        tabfields = ''
        for v in recipe.dataFields:
            tabfields += f'{v}, '
        tabfields = tabfields[:-2]
        # 'tabfields': tabfields,\
        yam = {'tabname': 'recipes', \
                  'fields': [self.title, self.prep_time, self.cook_time, self.yieldAmnt, self.category, self.rating, self.ingredients, self.directions, self.source]
                }
        # with open(filename,'a') as f:
        #     f.truncate(0) # clear file
        #     f.write('---\n')
        #     yaml.dump(yam, f)
        #     logger.debug(f'Output to Yaml completed. File: {filename}')
        return yam

    def outputToTxt(self, filename='recipe.yaml'):
        """function that generates a recipe.txt file from given parameters"""
        with open(filename,'a') as f:
            f.truncate(0) # clear file
            f.write(self.__str__())
            logger.debug(f'Output to Yaml completed. File: {filename}')

    @staticmethod
    def topLevelSplit(line):
        """Helper function for interp, splits on every comma that is on the top level.
        any commas that are nested within parens or brackets are skipped"""
        # list of the locations of the commas
        # preloaded with a -1 which resolves to location 0 in the end
        splits = [-1]
        # iterate through each character
        index = 0
        while index < len(line):
            # if we have a open bracket, skip to the closing bracket
            if line[index] == '[':
                index = line.find(']', index+1)
            # if we have a open paren, skip to the closing paren
            elif line[index] == '(':
                index = line.find(')', index+1)
            elif line[index] == '"':
                index = line.find('"', index+1)
            elif line[index] == "'":
                index = line.find("'", index+1)
            # if we have a comma, record the location
            elif line[index] == ',':
                splits.append(index)
            # increment to next character
            index += 1

        # list of the different splits
        lines = []
        # add the last location to the end
        splits.append(len(line))

        # for n - 1 splits
        for index in range(len(splits) - 1):
            # record the string from current index + 1 to the next index
            # this way commas are ignored
            start = splits[index]+1
            end = splits[index+1]
            lines.append(line[start:end])
        # logging.debug(f'Split returns: {lines}')
        return lines

    @staticmethod
    def interp(line):
        """Fairly complicated function, used to interpret my stringified list
        it takes a string and outputs a list"""

        if not isinstance(line, str):
            return line
        # this iterates through each character, so last is the last character
        last = len(line)
        for index in range(last):
            # if the character is open bracket, we've started a list
            if line[index] == '[':
                # recursive call, returns a list of everything between the open bracket to close bracket
                return [recipe.interp(item) for item in recipe.topLevelSplit(line[index+1:line.find(']')])]
            # if the character is close bracket, we've started a tuple
            elif line[index] == '(':
                # recursive call, returns a tuple of everything between the open paren to close paren
                return tuple(recipe.interp(item) for item in recipe.topLevelSplit(line[index+1:line.find(')')]))
            # if the character is an apostrophe, we have a string
            elif line[index] == "'":
                # return the string of everything in between
                return str(line[index+1:line.find("'", index+1)])
            # if the character is an quotation, we have a string
            elif line[index] == '"':
                # return the stirng of everything in between
                return str(line[index+1:line.find('"', index+1)])
            # if the character is a number, we've started a number
            elif line[index].isdigit():
                start = index
                # continue until the digits end
                while index < last and line[index].isdigit():
                    index+=1
                # return the int of the digits
                return int(line[start:index+1])
        # if we reach the end, we return empty string
        return ''




if __name__ == "__main__":
    # with open('recipes.yaml') as f:
    #     yam = yaml.load(f,Loader=yaml.FullLoader)
    # inyam = yam['fields']
    # outputToYaml(inyam['name'],inyam['prep_time'],inyam['cook_time'],inyam['yield'],\
    # inyam['ingredients'],inyam['directions'],inyam['rating'])
    # getIng()
    pass

"""
fields as a dictionary
'fields': {\
    'name': name,\
    'prep_time': prep_time,\
    'cook_time': cook_time,\
    'yield': yieldAmnt,\
    'ingredients': ingredients,\
    'directions': directions,\
    'rating': rating
    }
"""
