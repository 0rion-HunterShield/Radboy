from . import *

class CompareUI:
	def colorize(self,num,ct,msg):
		rplc=f"{Fore.deep_sky_blue_1}**({num}/{Fore.spring_green_2a}{num+1} of {Fore.dark_goldenrod}{ct})** "
		msg=msg.replace("\n",f"\n\t - {rplc}")
		return f"{rplc} --/ {Fore.light_steel_blue}{msg}{Style.reset}\n{'.'*os.get_terminal_size().columns}\n"
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
		lines=[]
		fd=FormBuilder(data=data)
		if fd:
			ct=len(fd)
			for num,k in enumerate(fd):
				msg=f"{Fore.cyan}{num}/{Fore.light_steel_blue}{num+1} of {Fore.light_green}{ct} -> {Fore.dark_goldenrod}{k}:{type(fd[k])} = {Fore.light_magenta}{fd[k]}{Style.reset}"
				lines.append(msg)
			
			price_change=(fd.get('newPrice')-fd.get('oldPrice'))/fd.get('oldPrice')*100
			price_change=round(price_change,3)
			formula_price_change=f'''{Fore.light_green}({Fore.spring_green_3a}({Fore.light_steel_blue}newPrice[$]({fd.get('newPrice'):.3f}){Fore.deep_sky_blue_2}- {Fore.light_yellow}oldPrice[$]({fd.get('oldPrice'):.3f}){Fore.spring_green_3a}){Fore.deep_sky_blue_2}/{Fore.light_yellow}oldPrice[$]({fd.get('oldPrice'):.3f}){Fore.light_green}){Fore.deep_sky_blue_2}*{Fore.green_yellow}100{Fore.deep_sky_blue_2}={Fore.light_red}PriceChangePercent[%]({price_change:.3f})
{Fore.orange_red_1}New price is % different of Old Price{Style.reset}
{Fore.light_red}Price Old{Fore.light_steel_blue} ->/To {Fore.light_green}Price New %:{Fore.green_yellow}{price_change}{Style.reset}'''
			#print(formula_price_change)
			lines.append(formula_price_change)

			qty_change=((fd.get('newQty')-fd.get('oldQty'))/fd.get('oldQty'))*100
			qty_change=round(qty_change,3)
			formula_qty_change=f'''{Fore.green}({Fore.light_green}({Fore.light_magenta}newQty({fd.get('newQty')}){Fore.deep_sky_blue_2}-{Fore.light_yellow}oldQty({fd.get('oldQty')}{Fore.light_green}){Fore.deep_sky_blue_2}/{Fore.light_yellow}oldQty({fd.get('oldQty')}){Fore.green}){Fore.deep_sky_blue_2}*{Fore.cyan}100{Fore.deep_sky_blue_2}={Fore.green_yellow}QtyChange({qty_change}){Style.reset}
{Fore.orange_red_1}New Qty is Percent(%) different of Old Qty{Style.reset}
{Fore.light_red}Old Qty{Fore.light_steel_blue} -> {Fore.light_green}New Qty Percent[%]:{Fore.green_yellow}{qty_change}{Style.reset}'''
			#print(formula_qty_change)
			#print(f'{Fore.cyan}{Style.bold}{Style.underline}Price Per Unit{Style.reset}')
			lines.append(formula_qty_change)
			
			ppun=round(fd.get('newPrice')/fd.get('newQty'),3)
			ppuo=round(fd.get('oldPrice')/fd.get('oldQty'),3)
			formula_old_price_per_unit=f"""{Fore.light_magenta}oldPricePerQty[$]({fd.get('oldPrice')}){Fore.deep_sky_blue_2}/oldQty({Fore.magenta}{fd.get('oldQty')}){Fore.deep_sky_blue_2}={Fore.green_yellow}oldPricePerUnit[$]({ppuo})
{Fore.cyan}Old Price Per Unit:{Fore.light_magenta}{ppuo}{Style.reset}"""
			#print(formula_old_price_per_unit)
			formula_new_price_per_unit=f"""{Fore.light_magenta}newPricePerQty[$]({fd.get('newPrice')}){Fore.deep_sky_blue_2}/newQty({Fore.magenta}{fd.get('newQty')}){Fore.deep_sky_blue_2}={Fore.green_yellow}newPricePerUnit[$]({ppun})
{Fore.cyan}New Price Per Unit:{Fore.light_magenta}{ppun}{Style.reset}"""
			#print(formula_new_price_per_unit)

			ch=(ppun-ppuo)/ppuo*100
			ch=round(ch,3)
			lines.append(formula_old_price_per_unit)
			lines.append(formula_new_price_per_unit)

			formula_price_per_unit_change=f"""{Fore.light_magenta}PercentPricePerUnitChange({ch}){Fore.deep_sky_blue_2}[%]={Fore.light_green}({Fore.green_yellow}newPricePerUnit[$]({ppun}){Fore.deep_sky_blue_2}-{Fore.dark_goldenrod}oldPricePerUnit[$]({ppuo}){Fore.light_green}){Fore.deep_sky_blue_2}/{Fore.dark_goldenrod}oldPricePerUnit[$]({ppuo}){Fore.deep_sky_blue_2}*{Fore.cyan}100
{Fore.medium_violet_red}Percent{Fore.red}{Fore.medium_violet_red} Price Per Unit Change[%]: {Fore.dark_goldenrod}{ch}{Style.reset}"""
			lines.append(formula_price_per_unit_change)
			#print(formula_price_per_unit_change)	
			formula_price_per_unit_difference=f"""{Fore.light_steel_blue}Price Per Unit Difference betweent Old[$]({Fore.light_red}{ppuo}{Fore.light_steel_blue}) and New[$]({Fore.light_red}{ppun}{Fore.light_steel_blue}): {Fore.magenta}{round(ppun-ppuo,2)}{Style.reset}"""
			#print(formula_price_per_unit_difference)
			lines.append(formula_price_per_unit_difference)

			ct=len(lines)
			for num,line in enumerate(lines):
				print(self.colorize(num,ct,line))