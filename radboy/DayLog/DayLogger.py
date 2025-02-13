from radboy.DB.db import *
from radboy.FB.FormBuilder import *
from radboy.FB.FBMTXT import *
from radboy.DB.Prompt import *
from radboy.DB.Prompt import prefix_text
import pandas as pd
from datetime import date
import calendar
import plotext as plt
import numpy as np
from scipy.fft import fft,fftfreq,rfft,rfftfreq,irfft
import tarfile

class DayLogger:
	helpText=f"""
{Fore.orange_red_1}{Style.bold}DayLog is your EntryChanges History, {Fore.green_yellow}should you decide to save your lists for later review{Style.reset}
{Fore.light_magenta}''|?|help{Style.reset} -{Fore.light_yellow} help info{Style.reset}
{Fore.light_magenta}q|quit{Style.reset}	  -{Fore.light_yellow} quit{Style.reset}
{Fore.light_magenta}b|back{Style.reset}    -{Fore.light_yellow} back{Style.reset}
{Fore.light_magenta}rm|del{Style.reset}	  -{Fore.light_yellow} remove a daylog{Style.reset}
{Fore.light_magenta}a|add|+{Style.reset}   -{Fore.light_yellow} store todays data values as a daylog snapshot{Style.reset}
{Fore.light_magenta}l|list|*{Style.reset}  -{Fore.light_yellow} list * entries{Style.reset}
{Fore.light_magenta}ld|list_date{Style.reset}  -{Fore.light_yellow} list * entries from DayLogDate from prompt{Style.reset}
{Fore.light_magenta}cd|clear_date{Style.reset}  -{Fore.light_yellow} clear * entries from DayLogDate from prompt for date{Style.reset}
{Fore.light_magenta}ca|clear_all{Style.reset}  -{Fore.light_yellow} clear * entries from DayLogDate{Style.reset}
{Fore.light_magenta}ed|export_date{Style.reset}  -{Fore.light_yellow} export * entries from DayLogDate from prompt{Style.reset}
{Fore.light_magenta}ea|export_all{Style.reset}  -{Fore.light_yellow} export * entries from DayLogDate from prompt{Style.reset}
{Fore.light_magenta}ec|export_code{Style.reset}  -{Fore.light_yellow} export * entries from DayLogDate by Barcode from prompt{Style.reset}
{Fore.light_magenta}lc|list_code{Style.reset}  -{Fore.light_yellow} export * entries from DayLogDate by Barcode from prompt{Style.reset}
{Fore.light_magenta}ecd|export_code_date{Style.reset}  -{Fore.light_yellow} export * entries from DayLogDate by Barcode and Date from prompt{Style.reset}
{Fore.light_magenta}lcd|list_code_date{Style.reset}  -{Fore.light_yellow} list * entries from DayLogDate by Barcode and Date from prompt{Style.reset}
{Fore.light_sea_green}sch|search{Style.reset}  -{Fore.medium_violet_red} search DayLog Fields DayLog {Fore.light_magenta}Barcode,Name,Code,Note,Description{Fore.medium_violet_red} for data relating to search term, with DateMetrics Data included [{Fore.light_steel_blue}if Any].{Style.reset}
{Fore.light_sea_green}sch ohd|search only holidays{Style.reset}  -{Fore.medium_violet_red} search DayLog Fields DayLog {Fore.light_magenta}Barcode,Name,Code,Note,Description{Fore.medium_violet_red} for data relating to search term, with DateMetrics Data included [{Fore.light_steel_blue}if Any]. by holiday date{Style.reset}
{Fore.light_red}
prefixes for #code:
		.d - daylog id
		.b - barcode
		.c - code/shelf tag barcode/cic
{Style.reset}
{Fore.light_magenta}Analisys{Style.reset}
'avg field','af', - prompt for a numeric field total an average for code/barcode
fxtbl - update table with correct columns
'avg field graph','afg' - create a graph of avg field
'fft','fast fourier transform' - create fast fourier transform of the data and graph data
'restore bckp','rfb' - restore Daylogs from backup file
"""
	def listAllDL(self):
		with Session(self.engine) as session:
			results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items!{Style.reset}")
			for r in results:
				print(r)

	def clearAllDL(self):
		while True:
			try:
				really=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Do You really want to delete everything in DayLog?",helpText="yes or no boolean,default is NO",data="boolean")
				if really in [None,]:
					return
				elif really in ['d',False]:
					return
				else:
					pass
				break
			except Exception as e:
				print(e)
		with Session(self.engine) as session:
			results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items to Clear!{Style.reset}")
			else:
				print(f"{Fore.light_magenta}Deleting {Fore.light_steel_blue}{ct}{Fore.light_magenta} Logs.{Style.reset}")
				r=session.query(DayLog).delete()
				session.commit()
				session.flush()
				print(r)

	def restoreDayLogs(self):
		filename=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What backup do you wish to use?",helpText="a file name ending with *.tar.gz",data="string")
		if filename in [None,]:
			return
		
		print('s1')
		tmp=Path("tmp")
		if tmp.exists():
			shutil.rmtree(tmp)
		
		print('s2')
		with tarfile.open(filename,"r") as tar:
			tar.extract("codesAndBarcodes.db",tmp)
		dbf="sqlite:///"+str("tmp/codesAndBarcodes.db")
		
		print(dbf)
		#import sqlite3
		#z=sqlite3.connect(filename)
		#print(z)
		print('s3')
		ENG=create_engine(dbf)
		with Session(ENG) as bck,Session(ENGINE) as session:
			src=bck.query(DayLog).all()
			srcCt=len(src)
			x=session.query(DayLog).delete()
			session.commit()
			for num,x in enumerate(src):
				msg=f"""{Fore.light_sea_green}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{srcCt} - {Fore.grey_50}{x.Barcode}|{x.Code}|{x.Name}"""
				dl=DayLog(**{i.name:getattr(x,i.name) for i in x.__table__.columns})
				session.add(dl)
				print(msg)
				if num % 50 == 0:
					session.commit()
			session.commit()
		print('s4')
		shutil.rmtree(tmp)

	def addToday(self):
		with Session(self.engine) as session:
			results=session.query(Entry).filter(Entry.InList==True).all()
			ct=len(results)
			if ct < 1:
				print(f"{Fore.light_red}No Items InList==True!{Style.reset}")
			else:
				for num,entry in enumerate(results):
					print(f"Adding Log For\n{'-'*12}{Fore.green}{num}{Style.reset}/{Fore.red}{ct}{Style.reset} -> {entry}")
					#ndl=DayLog()
					d={}
					for column in Entry.__table__.columns:
						d[column.name]=getattr(entry,column.name)
					ndl=DayLog(**d)
					session.add(ndl)
					if num % 25 == 0:
						session.commit()
				session.commit()
				session.flush()
				print(f"{Fore.light_magenta}Done Adding Log Data!{Style.reset}")

	def searchTags(self):
		with Session(ENGINE) as session:
			tags=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What do you want to search in DayLog?:",helpText="A Comma Separated List of Tag Names",data="list")
			if tags in ['d',None]:
				tags=[]
			for tag in tags:
				search=session.query(DayLog).filter(
					or_(DayLog.Tags.icontains(tag),
						DayLog.Barcode.icontains(tag),
						DayLog.Name.icontains(tag),
						DayLog.Code.icontains(tag),
						DayLog.Note.icontains(tag),
						DayLog.Description.icontains(tag)
						)
				).order_by(DayLog.Barcode,DayLog.DayLogDate.desc()).all()
				ct=len(search)
				if ct == 0:
					print("Nothing was Found")
				for num,log in enumerate(search):
					datemetrics=session.query(DateMetrics).filter(DateMetrics.date==log.DayLogDate).first()
					if not datemetrics:
						datemetrics=f'{Fore.orange_red_1}No DateMetrics Data For {Fore.light_magenta}{log.DayLogDate}{Fore.orange_red_1} Available!{Style.reset}'
					next_holi=next_holiday(today=log.DayLogDate)
					UNTIL=next_holi[0]-log.DayLogDate
					msg=f'''{num}/{num+1} of {ct} -{log}{datemetrics}
{Fore.medium_violet_red}Next Holiday:{Fore.light_steel_blue}{next_holi[1]}{Style.reset}
{Fore.medium_violet_red}Next Holiday Date:{Fore.light_steel_blue}{next_holi[0]}{Style.reset}
{Fore.light_yellow}Time{Fore.medium_violet_red} Until Holiday:{Fore.light_steel_blue}{UNTIL}{Style.reset}
{Fore.light_magenta}{log.DayLogDate}{Fore.medium_violet_red} Is Holiday:{Fore.light_steel_blue}{log.DayLogDate in holidays.USA(years=log.DayLogDate.year)}{Style.reset}
{Fore.medium_violet_red}Holiday Name:{Fore.light_steel_blue}{holidays.USA(years=log.DayLogDate.year).get(log.DayLogDate.strftime("%m/%d/%Y"))}{Style.reset}
{Fore.magenta}TAG/INDEX/Count of TTL:{Fore.light_red} {tag} - {num}/{num+1} of {ct}{Style.reset}
{Fore.light_sea_green}Name:{Fore.green_yellow}{log.Name}{Style.reset}
{Fore.light_sea_green}Barcode:{Fore.green_yellow}{log.Barcode}{Style.reset}
{Fore.light_sea_green}Code:{Fore.green_yellow}{log.Code}{Style.reset}
{Fore.light_green}DOE:{Fore.light_magenta}{log.DayLogDate}{Style.reset}'''
					print(msg)
					nxt=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Next?",helpText="hit enter",data="boolean")
					if nxt in [None,]:
						return
					elif nxt in ['d']:
						pass
					else:
						#for additional functionality
						pass



	def updateTable(engine):
		tableName="DayLog"
		fields=[]
		with Session(ENGINE) as session:
			for field in Entry.__table__.columns:
				fields.append(text(f"ALTER TABLE {tableName} ADD {field.name} {field.type}"))
			for update in fields:
				try:
					session.execute(update)
				except Exception as e:
					print(e)
			session.commit()

	def addTodayP(engine,addTag=False,tags=[]):
		if addTag == True:
			tags=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What tags do you want to add to the DayLog?:",helpText="A Comma Separated List of Tag Names",data="list")
			if tags in ['d',None]:
				tags=[]
			#tags=[''.join([ii.replace("'","_1x_quote_") for ii in i]) for i in tags]				
		print(f"{Fore.light_magenta}Backing Data up to DayLog{Style.reset}")
		with Session(engine) as session:
			results=session.query(Entry).filter(Entry.InList==True).all()
			ct=len(results)
			if ct < 1:
				print(f"{Fore.light_red}No Items InList==True!{Style.reset}")
			else:
				for num,entry in enumerate(results):
					print(f"Adding Log For\n{'-'*12}{Fore.green}{num}{Style.reset}/{Fore.red}{ct}{Style.reset} -> {entry}")
					#ndl=DayLog()
					d={}
					for column in Entry.__table__.columns:
						d[column.name]=getattr(entry,column.name)
					if d.get('Tags')==None:
						d['Tags']='[]'
					if addTag:
						for tag in tags:
							try:
								tags_tmp=json.loads(d.get("Tags"))
							except Exception as e:
								print(e)
								tags_tmp=[]
							if tag not in tags_tmp:
								tags_tmp.append(tag)
							d['Tags']=json.dumps(tags_tmp)
					ndl=DayLog(**d)
					session.add(ndl)
					if num % 25 == 0:
						session.commit()
				session.commit()
				session.flush()
				print(f"{Fore.light_magenta}Done Adding Log Data!{Style.reset}")

	def clearDate(self,month=None,day=None,year=None):
		d=self.dateParser()
		with Session(self.engine) as session:
			results=session.query(DayLog).filter(DayLog.DayLogDate==d).all()
			ct=len(results)
			#results=session.query(DayLog).all()
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items to Clear!{Style.reset}")
			for num,r in enumerate(results):
				print(f"clearing {num}/{ct} -> {r}")
				session.delete(r)
				if num % 25 == 0:
					session.commit()
			session.commit()

	def listDate(self,month=None,day=None,year=None):
		d=self.dateParser()
		with Session(self.engine) as session:
			results=session.query(DayLog).filter(DayLog.DayLogDate==d).all()
			#results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items For that Date!{Style.reset}")
			for r in results:
				print(r)


	def exportAllDL(self):
		with Session(self.engine) as session:
			results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items!{Style.reset}")
			for num,r in enumerate(results):
				r.saveItemData(num=num)

	def dateParser(self,month=None,day=None,year=None):
		if not year:
			year=input(f"Year? [{datetime.now().year}]: ")
			if year.lower()  in ['q','quit']:
				exit('user quit!')
			elif year.lower() in ['b','back']:
				raise Exception("User Request to back a menu")
			elif year == '':
				year=datetime.now().year
		try:
			year=int(year)
		except Exception as e:
			raise e

		if not month:
			month=input(f"Month?: [1..12]: ")
			if month.lower()  in ['q','quit']:
				exit('user quit!')
			elif month.lower() in ['b','back']:
				raise Exception("User Request to back a menu")
			elif month == '':
				month=datetime.now().month
		try:
			month=int(month)
			if month < 1:
				raise Exception("Month Must be within 1..12")
			if month > 12:
				raise Exception("Month Must be within 1..12")
		except Exception as e:
			raise e
		if not day:
			day=input(f"Day? [1..{calendar.monthrange(year=year,month=month)[-1]}]: ")
			if day.lower()  in ['q','quit']:
				exit('user quit!')
			elif day.lower() in ['b','back']:
				raise Exception("User Request to back a menu")
			elif day == '':
				day=datetime.now().day
		try:
			day=int(day)
			if day < 1:
				raise Exception("Month Must be within 1..31")

			#february
			if month == 2:
				if day > 28 and not calendar.isleap(year):
					raise Exception("Day Must be within 1..28")
				elif day > 29 and calendar.isleap(year):
					raise Exception("Day Must be within 1..29")
				
			else:
				if day > 28 and month in [num for num,i in enumerate(calendar.mdays) if i == 28]:
					raise Exception("Day Must be within 1..28")
				elif day > 29 and month in [num for num,i in enumerate(calendar.mdays) if i == 29]:
					raise Exception("Day Must be within 1..29")
				elif day > 30 and month in [num for num,i in enumerate(calendar.mdays) if i == 30]:
					raise Exception("Day Must be within 1..30")
				elif day > 31 and month in [num for num,i in enumerate(calendar.mdays) if i == 31]:
					raise Exception("Day Must be within 1..31")
		except Exception as e:
			raise e
		d=date(year,month,day)
		print(f"{Fore.green}Date Generated: {Style.reset}{Fore.light_yellow}{d}{Style.reset}")
		return d

	def exportDate(self,month=None,day=None,year=None):
		d=self.dateParser()
		print(d)
		with Session(self.engine) as session:
			results=session.query(DayLog).filter(DayLog.DayLogDate==d).all()
			#results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items For that Date!{Style.reset}")
			for num,r in enumerate(results):
				#print(f"{num}/{ct} -> {r}")
				r.saveItemData(num=num)

	def listCode(self,code=None):
		#d=self.dateParser()
		#print(d)
		if not code:
			code=input("Barcode|Code|ItemCode: ")
			if code.lower() in ['quit','q']:
				exit("user quit!")
			elif code.lower() in ['back','b']:
				return
		prefix=code.split(".")[0]
		cd=code.split(".")[-1]

		with Session(self.engine) as session:
			results=session.query(DayLog)
			if prefix.lower() in ['d',]:
				results=results.filter(DayLog.DayLogId==int(cd))
			elif prefix.lower() in ['b',]:
				results=results.filter(DayLog.Barcode==cd)
			elif prefix.lower() in ['c']:
				results=results.filter(DayLog.Code==cd)
			else:
				results=results.filter(or_(DayLog.Barcode==cd,DayLog.Code==cd))
			results=results.all()
			#results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items For that Code!{Style.reset}")
			for num,r in enumerate(results):
				print(f"{num}/{ct} -> {r}")
				#r.saveItemData(num=num)

	def exportCode(self,code=None):
		#d=self.dateParser()
		#print(d)
		if not code:
			code=input("Barcode|Code|ItemCode: ")
			if code.lower() in ['quit','q']:
				exit("user quit!")
			elif code.lower() in ['back','b']:
				return
		prefix=code.split(".")[0]
		cd=code.split(".")[-1]

		with Session(self.engine) as session:
			results=session.query(DayLog)
			if prefix.lower() in ['d',]:
				results=results.filter(DayLog.DayLogId==int(cd))
			elif prefix.lower() in ['b',]:
				results=results.filter(DayLog.Barcode==cd)
			elif prefix.lower() in ['c']:
				results=results.filter(DayLog.Code==cd)
			else:
				results=results.filter(or_(DayLog.Barcode==cd,DayLog.Code==cd))
			results=results.all()
			#results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items For that Code!{Style.reset}")
			for num,r in enumerate(results):
				#print(f"{num}/{ct} -> {r}")
				r.saveItemData(num=num)

	def listCodeDate(self,code=None):
		d=self.dateParser()
		#print(d)
		if not code:
			code=input("Barcode|Code|ItemCode: ")
			if code.lower() in ['quit','q']:
				exit("user quit!")
			elif code.lower() in ['back','b']:
				return
		prefix=code.split(".")[0]
		cd=code.split(".")[-1]

		with Session(self.engine) as session:
			results=session.query(DayLog)
			if prefix.lower() in ['d',]:
				results=results.filter(DayLog.DayLogId==int(cd),DayLog.DayLogDate==d)
			elif prefix.lower() in ['b',]:
				results=results.filter(DayLog.Barcode==cd,DayLog.DayLogDate==d)
			elif prefix.lower() in ['c']:
				results=results.filter(DayLog.Code==cd,DayLog.DayLogDate==d)
			else:
				results=results.filter(or_(DayLog.Barcode==cd,DayLog.Code==cd),DayLog.DayLogDate==d)
			results=results.all()
			#results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items For that Code!{Style.reset}")
			for num,r in enumerate(results):
				print(f"{num}/{ct} -> {r}")
				#r.saveItemData(num=num)

	def exportCodeDate(self,code=None):
		d=self.dateParser()
		#print(d)
		if not code:
			code=input("Barcode|Code|ItemCode: ")
			if code.lower() in ['quit','q']:
				exit("user quit!")
			elif code.lower() in ['back','b']:
				return
		prefix=code.split(".")[0]
		cd=code.split(".")[-1]

		with Session(self.engine) as session:
			results=session.query(DayLog)
			if prefix.lower() in ['d',]:
				results=results.filter(DayLog.DayLogId==int(cd),DayLog.DayLogDate==d)
			elif prefix.lower() in ['b',]:
				results=results.filter(DayLog.Barcode==cd,DayLog.DayLogDate==d)
			elif prefix.lower() in ['c']:
				results=results.filter(DayLog.Code==cd,DayLog.DayLogDate==d)
			else:
				results=results.filter(or_(DayLog.Barcode==cd,DayLog.Code==cd),DayLog.DayLogDate==d)
			results=results.all()
			#results=session.query(DayLog).all()
			ct=len(results)
			if ct == 0:
				print(f"{Style.bold}{Fore.light_red}No Items For that Code!{Style.reset}")
			for num,r in enumerate(results):
				#print(f"{num}/{ct} -> {r}")
				r.saveItemData(num=num)
	def fft(self):
		h='DayLog@Avg Field'
		includes=["integer","float"]
		integer_fields=[i.name for i in DayLog.__table__.columns if str(i.type).lower() in includes]
		ct=len(integer_fields)
		for num,i in enumerate(integer_fields):
			msg=f'''{Fore.orange_red_1}{num}{Fore.green_yellow}/{num+1}{Fore.light_sea_green}/{ct}{Fore.light_steel_blue} - {i}{Style.reset}'''
			print(msg)
		while True:
			try:
				which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} which index?",helpText="select the index for the field to avg",data="integer")
				if which in [None,]:
					return
				elif which in ['d',]:
					which=0
				field=integer_fields[which]
				with Session(ENGINE) as session:
					barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} Barcode|Code|Name: ",helpText="what are you looking to avg",data="string")
					if barcode in [None,'d']:
						return
					which_codes=session.query(DayLog).filter(or_(
						DayLog.Barcode==barcode,
						DayLog.Code==barcode,
						DayLog.Code.icontains(barcode),
						DayLog.Barcode.icontains(barcode),
						DayLog.Name.icontains(barcode)
						)).group_by(DayLog.Barcode).all()
					wc_ct=len(which_codes)
					if wc_ct == 0:
						print("nothing found to avg")
						return
					for num0,wc in enumerate(which_codes):
						msg=f"{num0}/{num0+1} of {wc_ct} - {wc.Name} | {wc.Barcode} | {wc.Code} | {getattr(wc,field)}"
						print(msg)
					#session.query(DayLog).filter(DayLog.Barcode=='')
					which0=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} which index?",helpText="select the index for the field to avg",data="integer")
					if which0 in [None,]:
						return
					elif which in ['d',]:
						which0=0
					avg_query=session.query(DayLog).filter(DayLog.Barcode==which_codes[which0].Barcode)
					df_from_records = pd.read_sql_query(avg_query.statement,session.bind)

					# Create a series
					series = df_from_records[field].to_numpy()
					frequency=1
					amplitude=1
					phase=0
					
					# Generate x-values for the sine wave
					TIME_X = np.arange(0, len(series),step=1,dtype=int)

					# Convert the series into a sine wave
					sine_wave = amplitude * np.sin(2 * np.pi * frequency * TIME_X + phase)

					sr=frequency
					dur=len(series)
					n=sr*dur
					yf = rfft(sine_wave)
					xf = rfftfreq(n, 1 / sr)
					iyf= irfft(yf)

					plt.bar(xf, np.abs(yf),label=f'fft {field} (SR={sr})')
					plt.show()
					plt.clf()

					plt.plot(iyf,label=f"ifft {field}")
					plt.show()
					plt.clf()
					# Plot the original series and the sine wave
					
					

					plt.plot(TIME_X, series, label=f'Original Data From {field} (SR={sr})')
					plt.show()
					plt.clf()

					plt.plot(TIME_X, sine_wave, label=f'Signal Generated For {field} (SR={sr})')
					plt.show()
					print("I do not even know what is going on here")
					break
			except Exception as e:
				print(e)
				break

	def avg_field(self,graph=False):
		h='DayLog@Avg Field'
		includes=["integer","float"]
		integer_fields=[i.name for i in DayLog.__table__.columns if str(i.type).lower() in includes]
		ct=len(integer_fields)
		for num,i in enumerate(integer_fields):
			msg=f'''{Fore.orange_red_1}{num}{Fore.green_yellow}/{num+1}{Fore.light_sea_green}/{ct}{Fore.light_steel_blue} - {i}{Style.reset}'''
			print(msg)
		while True:
			try:
				which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} which index?",helpText="select the index for the field to avg",data="integer")
				if which in [None,]:
					return
				elif which in ['d',]:
					which=0
				field=integer_fields[which]
				with Session(ENGINE) as session:
					barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} Barcode|Code|Name: ",helpText="what are you looking to avg",data="string")
					if barcode in [None,'d']:
						return
					which_codes=session.query(DayLog).filter(or_(
						DayLog.Barcode==barcode,
						DayLog.Code==barcode,
						DayLog.Code.icontains(barcode),
						DayLog.Barcode.icontains(barcode),
						DayLog.Name.icontains(barcode)
						)).group_by(DayLog.Barcode).all()
					wc_ct=len(which_codes)
					if wc_ct == 0:
						print("nothing found to avg")
						return
					for num0,wc in enumerate(which_codes):
						msg=f"{num0}/{num0+1} of {wc_ct} - {wc.Name} | {wc.Barcode} | {wc.Code} | {getattr(wc,field)}"
						print(msg)
					#session.query(DayLog).filter(DayLog.Barcode=='')
					which0=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} which index?",helpText="select the index for the field to avg",data="integer")
					if which0 in [None,]:
						return
					elif which in ['d',]:
						which0=0
					avg_query=session.query(DayLog).filter(DayLog.Barcode==which_codes[which0].Barcode)
					df_from_records = pd.read_sql_query(avg_query.statement,session.bind)
					if graph:
							x=df_from_records[['DayLogDate']]
							x['DayLogDate']=pd.to_datetime(x['DayLogDate'])
							x['date_str'] = x['DayLogDate'].dt.strftime('%Y-%m-%d')
							y=df_from_records[[field]]
							plt.clf()
							plt.date_form('Y-m-d')
							plt.plot(x['date_str'],y[field])
							plt.title(f"Data for '{field}'")
							plt.show()
					print(df_from_records[[field,'DayLogId','DayLogDate']])
					print(f"{Fore.dark_green}{Back.white}Total AVG:{Fore.dark_blue}{df_from_records[field].mean()} Avg Cost: ${(df_from_records['Price']*df_from_records[field]).mean()}{Style.reset}")
					tr=avg_query.all()
					split_totals={}
					split_price={}
					for i in tr:
						key=str(date(i.DayLogDate.year,i.DayLogDate.month,i.DayLogDate.day).strftime("%A"))
						#print(key)
						if split_totals.get(key) == None:
							split_totals[key]=[getattr(i,field),]
							split_price[key]=[getattr(i,'Price')]
						else:
							split_totals[key].append(getattr(i,field))
							split_price[key].append(getattr(i,'Price'))
					for i in tr:
						key=str(date(i.DayLogDate.year,i.DayLogDate.month,i.DayLogDate.day).strftime("%B"))
						#print(key)
						if split_totals.get(key) == None:
							split_totals[key]=[getattr(i,field),]
							split_price[key]=[getattr(i,'Price')]
						else:
							split_totals[key].append(getattr(i,field))
							split_price[key].append(getattr(i,'Price'))
					#print(split_totals)
										
					for i in split_totals:
						n=pd.Series(split_totals[i])
						p=pd.Series(split_price[i])*n
						b=pd.Series(split_price[i])
						all_months=[datetime(datetime.now().year,i,1).strftime("%B") for i in range(1,13)]
						all_days=[i for i in calendar.weekheader(12).split(" ") if i != '']
						if i in all_months:
							print(f"""{Fore.light_magenta}{i}{Fore.light_red}
 Avg {field}: {round(n.mean(),2)} 
 Avg BS Cst: ${round(b.mean(),2)}
 Avg Cst: ${round(p.mean(),2)}
 Max {field}: {round(n.max(),2)}
 Min {field}: {round(n.min(),2)}{Style.reset}""")
						elif i in all_days:
							print(f"""{Fore.light_yellow}{i}{Fore.light_green} 
 Avg {field}: {round(n.mean(),2)}
 Avg BS Cst: ${round(b.mean(),2)}
 Avg Cst: ${round(p.mean(),2)}
 Max {field}: {round(n.max(),2)}
 Min {field}: {round(n.min(),2)}{Style.reset}""")
				break
			except Exception as e:
				print(e)
				break

	def del_id(self):
		h='DayLog@Delete ID'
		did=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} DayLogId?",helpText="select the index for the field to avg",data="integer")
		if did in [None,'d']:
			return
		with Session(ENGINE) as session:
			toRM=session.query(DayLog).filter(DayLog.DayLogId==did).delete()
			session.commit()

	def edit_id(self):
		h='DayLog@Edit ID'
		did=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} which DayLogId?",helpText="select the index for the field to avg",data="integer")
		if did in [None,'d']:
			return
		with Session(ENGINE) as session:
			toUp=session.query(DayLog).filter(DayLog.DayLogId==did).first()
			ct=len(toUp.__table__.columns)
			for num,i in enumerate(toUp.__table__.columns):
				msg=f'{num}/{num+1}/{ct} - {i.name}({i.type})'
				print(msg)
			which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} which index?",helpText="select the index for the field to avg",data="integer")
			if which in [None,]:
				return
			elif which in ['d',]:
				which=0
			field=toUp.__table__.columns[which]
			h='DayLog@Edit ID'
			nv=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} old [{getattr(toUp,str(field.name))}] : ",helpText=f"new value of type {str(field.type)}",data=str(field.type))
			if nv in [None,'d']:
				print("Nothing was changed!")
				return
			setattr(toUp,str(field.name),nv)
			session.commit()
	def rmDayLog(self):
		with Session(ENGINE) as session:
			results=[]
			search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="what are you looking to delete?",helpText="Code|Barcode|EntryId|DayLogId|Name",data="string")
			try:
				integer_value=int(search)
				x=session.query(DayLog).filter(or_(DayLog.EntryId==integer_value,DayLog.DayLogId==integer_value))
				for i in x:
					if i not in results:
						results.append(i)
			except Exception as e:
				print(e)
			try:
				x=session.query(DayLog).filter(or_(DayLog.Barcode.icontains(search),DayLog.Code.icontains(search),DayLog.Name.icontains(search)))
				for i in x:
					if i not in results:
						results.append(i)
			except Exception as e:
				print(e)
			ct=len(results)
			mtext=[]
			for num,dl in enumerate(results):
				mtext.append(f"{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct} -> {Fore.light_steel_blue} - {dl}")
			mtext='\n'.join(mtext)
			while True:
				try:
					print(mtext)
					which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Which indexs do you wish to delete?",helpText=f"{mtext}\na comma Separated list will do",data="list")
					if which in [None,'d']:
						return
					for i in which:
						try:
							i=int(i)
							check_entry=session.query(Entry).filter(Entry.EntryId==results[i].EntryId).first()
							if not check_entry:
								'''Delete Extras if no other EntryId's are found.'''
								check_daylog=session.query(DayLog).filter(DayLog.EntryId==results[i].EntryId).all()
								if len(check_daylog) < 1:
									extras=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==results[i].EntryId).all()
									for ii in extras:
										session.delete(ii)
										session.commit()
							session.delete(results[i])
							session.commit()
						except Exception as ee:
							print(ee)

					break
				except Exception as e:
					print(e)
	def searchOnlyShowHoliday(self=None):
		with Session(ENGINE) as session:
			tags=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What do you want to search in DayLog?:",helpText="A Comma Separated List of Tag Names",data="list")
			if tags in ['d',None]:
				tags=[]
			for tag in tags:
				search=session.query(DayLog).filter(
					or_(DayLog.Tags.icontains(tag),
						DayLog.Barcode.icontains(tag),
						DayLog.Name.icontains(tag),
						DayLog.Code.icontains(tag),
						DayLog.Note.icontains(tag),
						DayLog.Description.icontains(tag)
						)
				).order_by(DayLog.Barcode,DayLog.DayLogDate.desc()).all()
				ct=len(search)
				if ct == 0:
					print("Nothing was Found")
				for num,log in enumerate(search):
					datemetrics=session.query(DateMetrics).filter(DateMetrics.date==log.DayLogDate).first()
					if log.DayLogDate not in holidays.USA():
						print(f"Skipping as not a holiday! {log.DayLogDate}")
						continue
					if not datemetrics:
						datemetrics=f'{Fore.orange_red_1}No DateMetrics Data For {Fore.light_magenta}{log.DayLogDate}{Fore.orange_red_1} Available!{Style.reset}'
					next_holi=next_holiday(today=log.DayLogDate)
					UNTIL=next_holi[0]-log.DayLogDate
					msg=f'''{num}/{num+1} of {ct} -{log}{datemetrics}
{Fore.medium_violet_red}Next Holiday:{Fore.light_steel_blue}{next_holi[1]}{Style.reset}
{Fore.medium_violet_red}Next Holiday Date:{Fore.light_steel_blue}{next_holi[0]}{Style.reset}
{Fore.light_yellow}Time{Fore.medium_violet_red} Until Holiday:{Fore.light_steel_blue}{UNTIL}{Style.reset}
{Fore.light_magenta}{log.DayLogDate}{Fore.medium_violet_red} Is Holiday:{Fore.light_steel_blue}{log.DayLogDate in holidays.USA(years=log.DayLogDate.year)}{Style.reset}
{Fore.medium_violet_red}Holiday Name:{Fore.light_steel_blue}{holidays.USA(years=log.DayLogDate.year).get(log.DayLogDate.strftime("%m/%d/%Y"))}{Style.reset}
{Fore.magenta}TAG/INDEX/Count of TTL:{Fore.light_red} {tag} - {num}/{num+1} of {ct}{Style.reset}
{Fore.light_sea_green}Name:{Fore.green_yellow}{log.Name}{Style.reset}
{Fore.light_sea_green}Barcode:{Fore.green_yellow}{log.Barcode}{Style.reset}
{Fore.light_sea_green}Code:{Fore.green_yellow}{log.Code}{Style.reset}
{Fore.light_green}DOE:{Fore.light_magenta}{log.DayLogDate}{Style.reset}'''
					print(msg)
					nxt=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Next?",helpText="hit enter",data="boolean")
					if nxt in [None,]:
						return
					elif nxt in ['d']:
						pass
					else:
						#for additional functionality
						pass

	def __init__(self,engine):
		self.engine=engine

		while True:
			try:
				mode='DayLog/History'
				fieldname='Menu'
				h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
				ptext=f"{h}{Fore.light_red}Do what? {Style.reset}[{Fore.green_yellow}h{Style.reset}|{Fore.green_yellow}help{Style.reset}]:"
				#what=input(ptext)
				what=Prompt.__init2__(None,func=FormBuilderMkText,ptext=ptext,helpText=self.helpText,data="string")
				if what in ['d',]:
					print(self.helpText)
				elif what in [None,]:
					return
				else:
					if what.lower() in ['a','add','+']:
						self.addToday()
					elif what.lower() in 'l|list|*'.split('|'):
						self.listAllDL()
					elif what.lower() in 'ld|list_date'.split('|'):
						self.listDate()
					elif what.lower() in 'cd|clear_date'.split("|"):
						self.clearDate()
					elif what.lower() in 'ca|clear_all'.split("|"):
						self.clearAllDL()
					elif what.lower() in 'ea|export_all'.split("|"):
						self.exportAllDL()
					elif what.lower() in 'ed|export_date'.split("|"):
						self.exportDate()
					elif what.lower() in 'ec|export_code'.split("|"):
						self.exportCode()
					elif what.lower() in 'lc|list_code'.split("|"):
						self.listCode()
					elif what.lower() in 'ecd|export_code_date'.split("|"):
						self.exportCodeDate()
					elif what.lower() in 'lcd|list_code_date'.split("|"):
						self.listCodeDate()
					elif what.lower() in ['avg field','af',]:
						self.avg_field()
					elif what.lower() in ['edit id',]:
						self.edit_id()
					elif what.lower() in ['del id',]:
						self.del_id()
					elif what.lower() in ['fxtbl']:
						DayLogger.updateTable(ENGINE)
					elif what.lower() in ['sch','search']:
						DayLogger.searchTags(ENGINE)
					elif what.lower() in 'sch ohd|search only holidays'.split("|"):
						DayLogger.searchOnlyShowHoliday()
					elif what.lower() in ['avg field graph','afg']:
						self.avg_field(graph=True)
					elif what.lower() in ['fft','fast fourier transform']:
						self.fft()
					elif what.lower() in 'rm|del'.split("|"):
						self.rmDayLog()
					elif what.lower() in ['restore bckp','rfb']:
						self.restoreDayLogs()
										
			except Exception as e:
				print(e)

