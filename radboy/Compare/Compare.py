from . import *

class CompareUI:
	'''Compare qty and price between two products.'''
	def __init__(self):
		data={
		'oldPrice':{
		'type':'float',
		'default':1.0
		},
		'oldQty':{
		'type':'integer',
		'default':1,
		},
		'newPrice':{
		'type':'float',
		'default':1.0
		},
		'newQty':{
		'type':'integer',
		'default':1,
		}
		}
		fd=FormBuilder(data=data)
		if fd:
		    price_change=(fd.get('newPrice')-fd.get('oldPrice'))/fd.get('oldPrice')*100
		    print(f'{Fore.light_red}Price Old{Fore.light_steel_blue} -> {Fore.light_green}Price New %:{Fore.green_yellow}{price_change}{Style.reset}')
		    
		    qty_change=(fd.get('newQty')-fd.get('oldQty'))/fd.get('oldQty')*100
		    print(f'{Fore.light_red}Old Qty{Fore.light_steel_blue} -> {Fore.light_green}New Qty %:{Fore.green_yellow}{qty_change}{Style.reset}')

		    print(f'{Fore.cyan}Price Per {Fore.light_magenta}Unit')
		    ppun=(fd.get('newPrice')/fd.get('newQty'))
		    ppuo=(fd.get('oldPrice')/fd.get('oldQty'))
		    print(f'{Fore.cyan}\t- Old Price Per Unit:{Fore.light_magenta}',ppuo,f"{Style.reset}")
		    print(f'{Fore.cyan}\t- New Price Per Unit:{Fore.light_magenta}',ppun,f"{Style.reset}")
		    ch=(ppun-ppuo)/ppuo*100
		    print(f'{Fore.medium_violet_red}Percent({Fore.red}%{Fore.medium_violet_red}) Price Per Unit Change: {Fore.dark_goldenrod}{ch}{Style.reset}')
		    print(f'{Fore.light_steel_blue}Price Per Unit Difference betweent Old({Fore.light_red}{ppuo}{Fore.light_steel_blue}) and New({Fore.light_red}{ppun}{Fore.light_steel_blue}): {Fore.magenta}{ppun-ppuo}{Style.reset}')