from datetime import datetime,timedelta
from colored import Style,Fore


from radboy.DB.DatePicker import *
from radboy.DB.Prompt import *

class Gross2Net:
	tax_rate=0.178
	union=10
	def __init__(self,_gross=None):
		while True:
			try:
				def mkTax(text,data):
					if text == '':
						return self.tax_rate
					return float(text)/100
				tax=Prompt.__init2__(None,func=mkTax,ptext="Tax %",helpText="tax rate as a decimal and no '%',i.e. 17.8",data=self)
				if tax in [None,]:
					return

				def mkUnion(text,data):
					if text == '':
						return self.union
					return float(text)
				union=Prompt.__init2__(None,func=mkUnion,ptext="Union Dues",helpText="Union Dues for the weekly check.",data=self)
				if tax in [None,]:
					return


				def mkGross(text,data):
					if text == '':
						return 0
					return float(text)
				if _gross == None:
					gross=Prompt.__init2__(None,func=mkGross,ptext="Gross Earnings",helpText="how much have you made without taxes/union dues?",data=self)
					if gross in [None,]:
						return
				else:
					gross=_gross

				net=(gross-(gross*tax))-union
				msg=f'''
{Fore.light_green}Gross={Fore.light_yellow}{gross}{Style.reset}
{Fore.cyan}Tax={Fore.light_yellow}{(tax*gross)}{Style.bold}({tax*100}%){Style.reset}
{Fore.light_red}Union={Fore.light_magenta}{-union}{Style.reset}
{Fore.sea_green_1a}Net={Style.bold}{Fore.medium_violet_red}{net}{Style.reset}
				'''
				print(msg)
				break
			except Exception as e:
				print(e)


class CalcNetFrom2Pt:
	tax_rate=0.178
	def __init__(self,rate=False):
		print("END DATETIME")
		try:
			end=DateTimePkr()
		except Exception as e:
			print(e)
			return
		print("START DATETIME")
		try:
			start=DateTimePkr()
		except Exception as e:
			print(e)
			return
		print(f"{Fore.light_green}A break of {Fore.dark_goldenrod}60 Minutes is {Fore.light_yellow}Subtracted from {Fore.light_red}{Style.bold}{Style.underline}Total Duration{Style.reset}")
		breakt=timedelta(seconds=60*60)
		print(f'{Fore.spring_green_2a}{(end-start)-breakt}{Style.reset}')

		print(f"{Fore.light_red}{Style.bold}{Style.underline}Be Aware {Fore.light_yellow} that 30M will be paid in check for shorter lunch!{Style.reset}\n{Fore.light_green}A break of {Fore.dark_goldenrod}30 Minutes is {Fore.light_yellow}Subtracted from {Fore.light_red}{Style.bold}{Style.underline}Total Duration{Style.reset}")
		breakt30=timedelta(seconds=60*30)
		print(f'{Fore.light_magenta}{(end-start)-breakt30}{Style.reset}')
		
		if not rate:
			return
			
		def mkFloat(text,data):
			try:
				if text == '':
					return data
				return float(eval(text))
			except Exception as e:
				print(e)
		while True:
		 rate=Prompt.__init2__(None,func=mkFloat,ptext='Rate of pay $/Hr',helpText="How Much do you make an hour?",data=1)
		 if rate in (None,):
		 	break
		 gross=round(((((end-start)-breakt).total_seconds()/60)/60)*rate,2)
		 print(gross)
		 tax=gross*self.tax_rate
		 print(gross-tax)
		 wwd=Prompt.__init2__(None,func=mkFloat,ptext='days in work week(to calculate union dues per day)',helpText="How Many days are in your work week?",data=4)
		 if wwd in (None,):
		 	break
		 union=10/wwd
		 net=gross-tax
		 net-=union

		 gross30=round(((((end-start)-breakt30).total_seconds()/60)/60)*rate,2)
		 tax30=gross30*self.tax_rate
		 net30=gross30-tax30-union
		 endC=Style.reset
		 value=Fore.light_green
		 add30value=Fore.sea_green_1a
		 add30name=Fore.light_yellow
		 fieldname=Fore.dark_goldenrod
		 m='Your Rate Calculation Results are below'
		 header=f"{Fore.light_magenta}{Style.bold}{Style.underline}{m}{Style.reset}\n{Style.bold}{Fore.red_3a}{'.'*len(m)}{Style.reset}"
		 msg=f'''{header}
{fieldname}gross{endC} ({add30name}+30M={add30value}{gross30}{endC}):{value} {gross}{endC}
{fieldname}net income{endC}({add30name}+30M={add30value}{net30}{endC}):{value} {net}{endC}
{fieldname}tax{endC}({add30name}+30M={add30value}{tax30}{endC}):{value} {-tax}{endC}
{fieldname}union dues{endC}:{value} {-union}{endC}
{fieldname}duration{endC}({add30name}+30M={add30value}{(end-start)-breakt30}{endC}):{value}{(end-start)-breakt}{endC}\n{Style.bold}{Fore.cyan}{'.'*len(m)}{Style.reset}'''

		 print(msg)
		 break
		 
		 #how many days in work week
		 #divide 10 by work week days
		 #subtract from gross-tax
		
if __name__=='__main__':
	state=True
	CalcNetFrom2Pt(rate=state)