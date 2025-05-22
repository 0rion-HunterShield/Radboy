from colored import Fore,Back,Style
PO_DEF={'what':0,'of':100,'print_value':True,'base_percent':100}

class what_ovr_of_float(float):
    def __new__(self, what, of):
        return float.__new__(self, (what/of)*100)
    
class what_ovr_of_int(int):
    def __new__(self, what, of):
        return int.__new__(self, (what/of)*100)

class what_percent_of_int(int):
    def __new__(self,percent, of):
        return int.__new__(self,(percent/100)*of)

class what_percent_of_float(float):
    def __new__(self,percent, of):
        return float.__new__(self,(percent/100)*of)

def mathClasses():
    classes=f'''
{Fore.light_green}#gets the percent of a total using a denominator over the of{Style.reset}
{Fore.light_steel_blue}
class what_ovr_of_float(float):
    def __new__(self, what, of):
        return float.__new__(self, (what/of)*100)
    
class what_ovr_of_int(int):
    def __new__(self, what, of):
        return int.__new__(self, (what/of)*100)
{Style.reset}
{Fore.light_green}#gets the denominator of the percent of a total{Style.reset}
{Fore.light_steel_blue}
class what_percent_Of_int(int):
    def __new__(self,percent, of):
        return int.__new__(self,percent*of)

class what_percent_Of_float(float):
    def __new__(self,percent, of):
        return float.__new__(self,percent*of)
{Style.reset}
    '''
    print(classes)