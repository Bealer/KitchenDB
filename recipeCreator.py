from libs import *
from config import *
global dataFields

class recipe:
    def __init__(self, data=None):
        if not data:
            self.new()
        else:
            self.edit(data)

    def __str__(self):
        ingr = ''
        dir = ''
        info = f'{self.name}\nYields: {self.yieldAmnt} | Category: {self.category} | Rating: {self.rating}\n' +\
            f'Time - Prep: {self.prep_time} | Cook: {self.cook_time} | Total: {self.prep_time + self.cook_time}'
        for food, id, amount in self.ingredients:
            ingr += f'{food}: {amount}\n'
        for direction in self.directions:
            dir += f'{direction}\n'

        return f'{info}\n\n{ingr}\n{dir}'

    def guts(self):
        return ({self.name}, {self.prep_time}, {self.cook_time}, {self.yieldAmnt}, {self.category}, {self.rating}, {self.ingrdients}, {self.directions})

    def meta(self):
        return ('Title', 'Prep Time', 'Cook Time', 'Yield', 'Category', 'Rating', 'Ingredients', 'Directions', 'Source')

    def edit(self, data):
        """Function that builds the recipe object from DB entry"""
        self.name = data[0]
        self.prep_time = data[1]
        self.cook_time = data[2]
        self.yieldAmnt = data[3]
        self.category = data[4]
        self.rating = data[5]
        self.ingredients = interp(data[6])
        self.directions = interp(data[7])
        self.source = data[8]


    def new(self):
        """Function that builds the recipe.yaml file from user input"""
        self.name = input('Please enter the recipe name: ')
        if self.name == 'q':
            exit()
        # FIXME: error checking on input
        self.prep_time = int(input('Please enter the prep time (minutes): '))
        self.cook_time = int(input('Please enter the cook time (minutes): '))
        self.yieldAmnt = input('Please enter the yield for this recipe: ')
        self.category = input('Please enter the category for this recipe: ')
        self.rating = -1 # unrated
        self.ingredients = self.getIng()
        self.directions = self.getDir()
        self.source = input('Add a source, or leave blank: ')
        # self.outputToYaml()

    def outputToYaml(self, filename='recipe.yaml'):
        """function that generates a recipe.yaml file from given parameters"""
        tabfields = ''
        for v in dataFields:
            tabfields += f'{v}, '
        tabfields = tabfields[:-2]
        yam = {'tabname': 'recipes', \
                'tabfields': tabfields,\
                  'fields': [self.name, self.prep_time, self.cook_time, self.yieldAmnt, self.category, self.rating, str(self.ingredients), str(self.directions)]
                }
        with open(filename,'a') as f:
            f.truncate(0) # clear file
            f.write('---\n')
            yaml.dump(yam, f)
            logger.debug(f'Output to Yaml completed. File: {filename}')


    @staticmethod
    def getIng():
        """Function that takes user input to build the ingredient list"""
        print('\nNow we will gather the ingredients. Please search for the food item')
        print('quit with "q" or a blank line')
        ingredients = []
        ingNum = 1
        while True:
            inp = input(f'\tPlease enter ingredient {ingNum}: ')
            if inp.lower() == 'q':
                logger.debug('Quiting...')
                break
            elif len(inp) == 0:
                logger.debug('Quiting...')
                break
            response = apiSearchFood(inp)
            options = response.json()['foods']
            upperLimit = len(options) - 1
            min, max = -5,0
            while True:
                if max + 5 > upperLimit - 1:
                    logger.debug('Upper Limit hit')
                    max = upperLimit
                    if max - 5 >= 0:
                        min = max - 5
                    else:
                        min = 0
                else:
                    min += 5
                    max += 5
                for i in range(min, max):
                    with suppress(KeyError):
                        print(f'\tOption {i+1}:')
                        print(f'\t{options[i]["description"]}')
                        if options[i]['dataType'] == 'Branded':
                            print(f'\t{options[i]["brandOwner"]}')
                            print(f'\t{options[i]["ingredients"]}')
                        else:
                            print(f'\t{options[i]["additionalDescriptions"]}')
                    print()

                choice = input('\t(press <Enter> for more choices, enter <discard> to search again)\n\tWhich choice looks best? ').lower()
                if len(choice) < 1:
                    continue
                elif choice[0] == 'p':
                    min = (int(choice[1:]) * 5) - 5
                    max = min + 5
                    logger.debug(f'Page Option:Showing options {min+1} to {max+1}...')
                elif choice[0] == 'd':
                    logger.debug('Discard Option: Discard previous search...')
                    ingNum -= 1
                    break
                while isinstance(choice, str):
                    try:
                        choice = int(choice)
                    except ValueError:
                        print('\tInvalid Choice, Please try again')
                        choice = input('\tWhich choice looks best? (press <Enter> for more choices) ')

                if 1 <= choice <= max:
                    amount = input('\tHow much of the ingredient does the recipe call for? ')
                    amount = aposFilter(amount)
                    print()
                    food = (aposFilter(options[choice-1]['description']), options[choice-1]['fdcId'], amount)
                    ingredients.append(food)
                    logger.debug(f'Successfully add {food} to ingrdients')
                    break
            ingNum += 1
        return ingredients

    @staticmethod
    def getDir():
        """Function that asks for user input to build the direction list"""
        directions = []
        dirNum = 1
        print('\nNow we will gather the directions. Please enter the directions')
        print('quit with "q" or a blank line')
        while True:
            inp = input(f'\tPlease enter step number {dirNum}: ')
            if inp.lower() == 'q':
                logger.debug('Quiting...')
                break
            elif len(inp) < 1:
                logger.debug('Quiting...')
                break
            else:
                directions.append(f'{dirNum}. {inp}')
                dirNum += 1
                logger.debug(f'Successfully added "{inp}" to directions')
        return directions


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
