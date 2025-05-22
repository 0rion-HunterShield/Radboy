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
		'type':'float',
		'default':1.0,
		},
		'newPrice':{
		'type':'float',
		'default':1.0
		},
		'newQty':{
		'type':'float',
		'default':1.0,
		}
		}
		fd=FormBuilder(data=data)
		if fd:
			ct=len(fd)
			for num,k in enumerate(fd):
				msg=f"{Fore.cyan}{num}/{Fore.light_steel_blue}{num+1} of {Fore.light_green}{ct} -> {Fore.dark_goldenrod}{k}:{type(fd[k])} = {Fore.light_magenta}{fd[k]}{Style.reset}"
				print(msg)
			price_change=(fd.get('newPrice')-fd.get('oldPrice'))/fd.get('oldPrice')*100
			price_change=round(price_change,3)
			print(f'{Fore.light_red}Price Old{Fore.light_steel_blue} -> {Fore.light_green}Price New %:{Fore.green_yellow}{price_change}{Style.reset}')
			
			qty_change=((fd.get('newQty')-fd.get('oldQty'))/fd.get('oldQty'))*100
			qty_change=round(qty_change,3)
			print(f'{Fore.light_red}Old Qty{Fore.light_steel_blue} -> {Fore.light_green}New Qty %:{Fore.green_yellow}{qty_change}{Style.reset}')

			print(f'{Fore.cyan}Price Per {Fore.light_magenta}Unit')
			ppun=round(fd.get('newPrice')/fd.get('newQty'),3)
			ppuo=round(fd.get('oldPrice')/fd.get('oldQty'),3)
			print(f'{Fore.cyan}\t- Old Price Per Unit:{Fore.light_magenta}',ppuo,f"{Style.reset}")
			print(f'{Fore.cyan}\t- New Price Per Unit:{Fore.light_magenta}',ppun,f"{Style.reset}")
			ch=(ppun-ppuo)/ppuo*100
			ch=round(ch,3)
			print(f'{Fore.medium_violet_red}Percent({Fore.red}%{Fore.medium_violet_red}) Price Per Unit Change: {Fore.dark_goldenrod}{ch}{Style.reset}')
			print(f'{Fore.light_steel_blue}Price Per Unit Difference betweent Old({Fore.light_red}{ppuo}{Fore.light_steel_blue}) and New({Fore.light_red}{ppun}{Fore.light_steel_blue}): {Fore.magenta}{round(ppun-ppuo,2)}{Style.reset}')