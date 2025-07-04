from radboy.DB.db import *
from radboy.DB.Prompt import *
from radboy.FB.FBMTXT import *
from radboy.FB.FormBuilder import *
from radboy.DB.DatePicker import *
import asyncio
import pandas as pd
import csv
from datetime import datetime
from pathlib import Path
from colored import Fore,Style,Back
from barcode import Code39,UPCA,EAN8,EAN13
import barcode,qrcode,os,sys,argparse
from datetime import datetime,timedelta
import zipfile,tarfile
import base64,json
from ast import literal_eval
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base as dbase
from sqlalchemy.ext.automap import automap_base
from pathlib import Path
import upcean
from copy import deepcopy
from radboy.RNE.dateAhead import dateAhead

def detectGetOrSet(name,value,setValue=False):
		value=str(value)
		with Session(ENGINE) as session:
			q=session.query(SystemPreference).filter(SystemPreference.name==name).first()
			ivalue=None
			if q:
				try:
					if setValue:
						q.value_4_Json2DictString=json.dumps({name:eval(value)})
						session.commit()
						session.refresh(q)
					ivalue=json.loads(q.value_4_Json2DictString)[name]
				except Exception as e:
					q.value_4_Json2DictString=json.dumps({name:eval(value)})
					session.commit()
					session.refresh(q)
					ivalue=json.loads(q.value_4_Json2DictString)[name]
			else:
				q=SystemPreference(name=name,value_4_Json2DictString=json.dumps({name:eval(value)}))
				session.add(q)
				session.commit()
				session.refresh(q)
				ivalue=json.loads(q.value_4_Json2DictString)[name]
			return ivalue

class Expiry(BASE,Template):
	__tablename__="Expiry"
	eid=Column(Integer,primary_key=True)
	#if none,see barcode
	EntryId=Column(Integer)
	#in case there is no entry id associated for Barcode entered
	Barcode=Column(String)
	#in case something needs to be noted about it
	Note=Column(String)
	Name=Column(String)
	#datetime of product being worked
	DTOE=Column(DateTime)
	#best by or expiry of product
	BB_Expiry=Column(DateTime)
	#when the product was last rotated by you
	Poll=Column(Float)
	#how many seconds after BB_Expiry to Critical Tell You that there are expireds on the counter before silencing it
	PastPoll=Column(Float)
	#how many seconds after BB_Expiry to Critical Tell You that there are expireds on the counter before auto-removing it
	DelPoll=Column(Float)

	def rebar(self):
		rebar=[]
		steps=4
		r=range(0,len(self.Barcode),steps)
		for num,i in enumerate(r):
			if num == len(r)-1:
					chunk=self.Barcode[i:i+steps]
					primary=chunk[:-1]
					lastChar=chunk[-1]
					if (num % 2) == 0:
						m=f"{Fore.light_steel_blue}{primary}{Fore.dark_goldenrod}{lastChar}{Style.reset}"
					else:
						m=f"{Fore.light_sea_green}{primary}{Fore.dark_goldenrod}{lastChar}{Style.reset}"
					rebar.append(m)
			elif (num % 2) == 0:
				rebar.append(Fore.light_steel_blue+self.Barcode[i:i+steps]+Style.reset)
			else:
				rebar.append(Fore.light_sea_green+self.Barcode[i:i+steps]+Style.reset)
		
		rebar=''.join(rebar)

		return rebar

	def __init__(self,**kwargs):
		for k in kwargs.keys():
			if k in [s.name for s in self.__table__.columns]:
				setattr(self,k,kwargs.get(k))

class Expiration:
	def next_barcode(self):
		with Session(ENGINE) as session:
			next_barcode=session.query(SystemPreference).filter(SystemPreference.name=="next_barcode").first()
			
			state=False
			
			if next_barcode:
					try:
						state=json.loads(next_barcode.value_4_Json2DictString).get("next_barcode")
					except Exception as e:
						print(e)
						next_barcode.value_4_Json2DictString=json.dumps({'next_barcode':False})
						session.commit()
						session.refresh(next_barcode)
						state=json.loads(next_barcode.value_4_Json2DictString).get("next_barcode")
			else:
				next_barcode=db.SystemPreference(name="next_barcode",value_4_Json2DictString=json.dumps({'next_barcode':False}))
				session.add(next_barcode)
				session.commit()
				session.refresh(next_barcode)
				state=json.loads(next_barcode.value_4_Json2DictString).get("next_barcode")
			f=deepcopy(state)
			print(f,"NEXT BARCODE")
			next_barcode.value_4_Json2DictString=json.dumps({'next_barcode':False})
			session.commit()
			return f


	def getUpcomingExpiry(self,oldest=False):
		print(f"{'*'*5}getUpcomingExpiry(){'*'*5}")
		with Session(ENGINE) as session:
			limit=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Limit results to?",helpText="an integer",data="integer")
			if limit in [None,0]:
				return
			elif limit in ['d',]:
				limit=1
			elif limit < 0:
				limit*=-1
			if not oldest:
				results=session.query(Expiry).order_by(Expiry.BB_Expiry.asc()).limit(limit).all()
			else:
				results=session.query(Expiry).order_by(Expiry.BB_Expiry.desc()).limit(limit).all()
			ct=len(results)
			for num,i in enumerate(results):
				bb=i.BB_Expiry.strftime("%m/%d/%Y")
				doe=i.BB_Expiry.strftime("%m/%d/%Y")
				print(f"{Fore.light_green}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct}{Fore.dark_goldenrod} -> {Fore.light_magenta}{i.Name}|{Fore.plum_2}{i.rebar()}|{Fore.cyan}{bb}|{Fore.medium_violet_red}{doe}{Fore.orange_red_1}|eid={i.eid}{Style.reset}")
			msg=f"{Fore.light_green}Zero-Index/{Fore.light_yellow}Number of {Fore.light_red}Total{Fore.dark_goldenrod} -> {Fore.light_magenta}Name|{Fore.plum_2}Barcode|{Fore.cyan}BB_Expiry|{Fore.medium_violet_red}DTOE|{Fore.orange_red_1}eid{Style.reset}"
			print(msg)



	def updateExpFromEntry(self):
		with Session(ENGINE) as session:
			results=session.query(Expiry).filter(Expiry.Name=="New Item").all()
			for num,r in enumerate(results):
				entry=session.query(Entry).filter(Entry.Barcode==r.Barcode).first()
				if entry:
					setattr(r,'Name',entry.Name)
					if (num % 100) == 0:
						session.commit()
			session.commit()


	def scan(self,ewol=False):
		with Session(ENGINE) as session:
			while True:
				detectGetOrSet('next_barcode',True,setValue=False)
				try:
					EntryId=None
					#Barcode=barcode

					Note=''
					DTOE=datetime.now()
					'''
					search=session.query(Entry).filter(
							or_(
								Entry.Barcode==barcode,
								Entry.Code==barcode,
								Entry.Barcode.icontains(barcode),
								Entry.Code.icontains(barcode)
								)
							).first()
					if search != None:
						EntryId=search.EntryId
						Barcode=search.Barcode
					'''
					#BB=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Best-By/Expiry:",helpText="write any comments related to this item mm/dd/yy|yyyy",data="datetime")
					#if BB in [None,]:
					#	return
					Poll=detectGetOrSet("Expiration_Poll",value=30*24*60*60)
					PastPoll=detectGetOrSet("Expiration_PastPoll",value=365*24*60*60)
					DelPoll=detectGetOrSet("Expiration_DelPol",value=2*365*24*60*60)
					barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Barcode:",helpText="Product Barcode Only",data="string")
					if barcode in [None,'d']:
						v=detectGetOrSet('next_barcode',True)
						if v == False:
							continue
						else:
							v=detectGetOrSet('next_barcode',True,setValue=False)
							return
					dates=session.query(Expiry).filter(or_(Expiry.Barcode==barcode,Expiry.Barcode.icontains(barcode))).group_by(Expiry.BB_Expiry).all()
					dates_ct=len(dates)
					if not ewol:
						ENTRYS=session.query(Entry).filter(or_(Entry.Barcode==barcode,Entry.Barcode.icontains(barcode),Entry.Code==barcode,Entry.Code.icontains(barcode),Entry.Name.icontains(barcode))).all()
						ENTRYS_CT=len(ENTRYS)
						if ENTRYS_CT >= 1:
							while True:
								try:
									detectGetOrSet('next_barcode',True,setValue=False)
									found_update=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Update Expiry Scans from one of {ENTRYS_CT} results?",helpText="do want to update all expiry's with this barcode with the selected name?",data="boolean")
									if found_update in ['d',]:
										break
									elif found_update in [None,]:
										v=detectGetOrSet('next_barcode',True)
										if v == False:
											continue
										else:
											v=detectGetOrSet('next_barcode',True,setValue=False)
											return
									elif found_update:
										for num,i in enumerate(ENTRYS):
											msg=f"""{num}/{num+1} of {ENTRYS_CT} -> {i.seeShort()}"""
											print(msg)
										detectGetOrSet('next_barcode',True,setValue=False)
										which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Which index?",helpText="please type the number of your selection at the far left before the first slash",data="Integer")
										if which in [None,]:
											v=detectGetOrSet('next_barcode',True)
											if v == False:
												continue
											else:
												v=detectGetOrSet('next_barcode',True,setValue=False)
												return
										elif which in ['d',]:
											which=0
										try:
											for num,i in enumerate(dates):
												i.Name=ENTRYS[which].Name
												if num % 10 == 0:
													session.commit()
													session.flush()
											session.commit()
											session.flush()
										except Exception as e:
											print(e)
										pass
									break
								except Exception as e:
									print(e)
					ct=len(dates)
					for num,i in enumerate(dates):
						session.refresh(i)
						bb=i.BB_Expiry.strftime("%m/%d/%Y")
						doe=i.BB_Expiry.strftime("%m/%d/%Y")
						print(f"{Fore.light_green}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct}{Fore.dark_goldenrod} -> {Fore.light_magenta}{i.Name}|{Fore.plum_2}{i.rebar()}|{Fore.cyan}{bb}|{Fore.medium_violet_red}{doe}{Style.reset}")
					msg=f"{Fore.light_green}Zero-Index/{Fore.light_yellow}Number of {Fore.light_red}Total{Fore.dark_goldenrod} -> {Fore.light_magenta}Name|{Fore.plum_2}Barcode|{Fore.cyan}BB_Expiry|{Fore.medium_violet_red}DTOE{Style.reset}"
					print(msg)
					data={
					'BB_Expiry':{
					'type':'datetime',
					'default':datetime.now()
					},
					'Note':{'type':'string',
					'default':'',
					}
					,
					'Name':{'type':'string',
					'default':'New Item',
					}
					}
					detectGetOrSet('next_barcode',True,setValue=False)
					print(f"{Fore.orange_red_1}Type {Fore.light_red}#b{Fore.orange_red_1} to go to previous menu; Type {Fore.light_yellow}b{Fore.orange_red_1} to Restart{Style.reset}")
					exp=FormBuilder(data=data)
					if exp in [None,]:
						if not self.next_barcode():
							continue
						else:
							return
					pdate=date(
						exp['BB_Expiry'].year,
						exp['BB_Expiry'].month,
						exp['BB_Expiry'].day
						)
					t=date(
						datetime.today().year,
						datetime.today().month,
						datetime.today().day
						)
					if pdate == t:
						changeIt=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Today's date ({t}) was used for BB_Expiry({pdate}). Change it to?...",helpText="hit 'b' to continue using it or re-enter the date.",data="datetime-")
						if isinstance(changeIt,datetime):
							exp['BB_Expiry']=changeIt

					if exp != None:
						exp['Barcode']=barcode
					if exp in [None,]:
						v=detectGetOrSet('next_barcode',True)
						if v == False:
							continue
						else:
							v=detectGetOrSet('next_barcode',True,setValue=False)
							return
					search=session.query(Entry).filter(
							or_(
								Entry.Barcode==exp['Barcode'],
								Entry.Code==exp['Barcode'],
								Entry.Barcode.icontains(exp['Barcode']),
								Entry.Code.icontains(exp['Barcode'])
								)
							).first()
					
					if search != None:
						exp['EntryId']=search.EntryId
						exp['Barcode']=search.Barcode
						exp['Name']=search.Name
					exp['Poll']=Poll
					exp['PastPoll']=PastPoll
					exp['DelPoll']=DelPoll
					exp['DTOE']=datetime.now()					
					nexp=Expiry(**exp)
					session.add(nexp)
					session.commit()
					session.flush()
					session.refresh(nexp)
					print(nexp)
					#self.show_warnings(code=exp['Barcode'],regardless=True)
				except Exception as e:
					print(e)
	def diff(self):
		exp={
		'Start Date':{
			'default':datetime.now(),
			'type':'datetime'
			},
		'End Date':{
			'default':datetime.now(),
			'type':'datetime'
			}
		}
		dt=FormBuilder(data=exp)
		if dt in [None,]:
			return
		
		END=dt['Start Date']
		EXPIRED=dt['End Date'] < END
		TIME_LEFT=dt['End Date'] - END
		print(f"{Fore.light_green}{END.ctime()}({Fore.cyan}{END.strftime('%m/%d/%Y')}|{Fore.green_yellow}{END.strftime('%B/%d/%Y')}{Fore.light_green}) Date Difference is {Fore.light_red}{Style.bold}{Style.underline}{EXPIRED}({Fore.light_yellow}{dt['End Date'].strftime('%m/%d/%Y')}|{Fore.green_yellow}{dt['End Date'].strftime('%B/%d/%Y')}{Fore.light_red}){Style.reset}, {Fore.light_yellow}The Time Left for Expiration is({Fore.plum_2}A Negative(-) Value means Time Passed By,{Fore.light_magenta}while a Positive(+) Value means Time Until {Fore.light_yellow}) {Fore.dark_goldenrod}{TIME_LEFT}{Style.reset}")
		print(f"{Fore.light_sea_green}"+("-"*10)+f"{Style.reset}")
		for i in range(1,13):
			state=[]
			if END.month == i:
				state.append(' '.join([f"{Fore.light_green}{END.strftime('%B|%m/%d/%Y')}{Style.reset}","Start Date"]))
			else:
				state.append(' '.join([f"{Fore.cyan}{datetime(END.year,i,1).strftime('%B|%m/%d/%Y')}{Style.reset}"]))

			dur=dt['End Date']-END
			if dt['End Date'] < END and i == dt['End Date'].month:
				state.append(f'{Fore.light_red} End Date{Style.reset}')
				state.append(f"{Fore.orange_red_1}{dt['End Date'].strftime('%B|%m/%d/%Y')}{Fore.light_cyan}[{Fore.medium_violet_red}{dur}{Fore.light_cyan}]{Style.reset}")
			elif dt['End Date'] >= END and i == dt['End Date'].month:
				state.append(f'{Fore.light_red} End Date{Style.reset}')
				state.append(f"{Fore.orange_red_1}{dt['End Date'].strftime('%B|%m/%d/%Y')}{Fore.light_cyan}[{Fore.medium_violet_red}{dur}{Fore.light_cyan}]{Style.reset}")
			print(' '.join(state))

	def isExpired(self):
		exp={
		'BB_Expiry':{
			'default':datetime.now(),
			'type':'datetime'
			}
		}
		dt=FormBuilder(data=exp)
		if dt in [None,]:
			return
		
		EXPIRED=dt['BB_Expiry'] < datetime.now()
		TIME_LEFT=dt['BB_Expiry'] - datetime.now()
		print(f"{Fore.light_green}{datetime.now().ctime()}({Fore.cyan}{datetime.now().strftime('%m/%d/%Y')}|{Fore.green_yellow}{datetime.now().strftime('%B/%d/%Y')}{Fore.light_green}) Being Expired is {Fore.light_red}{Style.bold}{Style.underline}{EXPIRED}({Fore.light_yellow}{dt['BB_Expiry'].strftime('%m/%d/%Y')}|{Fore.green_yellow}{dt['BB_Expiry'].strftime('%B/%d/%Y')}{Fore.light_red}){Style.reset}, {Fore.light_yellow}The Time Left for Expiration is({Fore.plum_2}A Negative(-) Value means Time Expired By,{Fore.light_magenta}while a Positive(+) Value means Time Until Expired{Fore.light_yellow}) {Fore.dark_goldenrod}{TIME_LEFT}{Style.reset}")
		print(f"{Fore.light_sea_green}"+("-"*10)+f"{Style.reset}")
		for i in range(1,13):
			state=[]
			if datetime.now().month == i:
				state.append(' '.join([f"{Fore.light_green}{datetime.now().strftime('%B|%m/%d/%Y')}{Style.reset}","Today"]))
			else:
				state.append(' '.join([f"{Fore.cyan}{datetime(datetime.now().year,i,1).strftime('%B|%m/%d/%Y')}{Style.reset}"]))

			dur=dt['BB_Expiry']-datetime.now()
			if dt['BB_Expiry'] < datetime.now() and i == dt['BB_Expiry'].month:
				state.append(f'{Fore.light_red} Expired{Style.reset}')
				state.append(f"{Fore.orange_red_1}{dt['BB_Expiry'].strftime('%B|%m/%d/%Y')}{Fore.light_cyan}[{Fore.medium_violet_red}{dur}{Fore.light_cyan}]{Style.reset}")
			elif dt['BB_Expiry'] >= datetime.now() and i == dt['BB_Expiry'].month:
				state.append(f'{Fore.light_red} Expired{Style.reset}')
				state.append(f"{Fore.orange_red_1}{dt['BB_Expiry'].strftime('%B|%m/%d/%Y')}{Fore.light_cyan}[{Fore.medium_violet_red}{dur}{Fore.light_cyan}]{Style.reset}")
			print(' '.join(state))


	def dates4barcode(self):
		with Session(ENGINE) as session:
			while True:
				barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Barcode:",helpText="Product Barcode Only",data="string")
				if barcode in [None,'d']:
					v=detectGetOrSet('next_barcode',True)
					if v == False:
						continue
					else:
						v=detectGetOrSet('next_barcode',True,setValue=False)
						return
				dates=session.query(Expiry).filter(or_(Expiry.Barcode==barcode,Expiry.Barcode.icontains(barcode))).group_by(Expiry.BB_Expiry).all()
				dates_ct=len(dates)
				for num,i in enumerate(dates):
					bb=i.BB_Expiry.strftime("%m/%d/%Y")
					doe=i.BB_Expiry.strftime("%m/%d/%Y")
					m=f"{Fore.light_green}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct}{Fore.dark_goldenrod} -> {Fore.light_magenta}{i.Name}|{Fore.plum_2}{i.rebar()}|{Fore.cyan}{bb}|{Fore.medium_violet_red}{doe}{Style.reset}"
					print(m)
				msg=f"{Fore.light_green}Zero-Index/{Fore.light_yellow}Number of {Fore.light_red}Total{Fore.dark_goldenrod} -> {Fore.light_magenta}Name|{Fore.plum_2}Barcode|{Fore.cyan}BB_Expiry|{Fore.medium_violet_red}DTOE{Style.reset}"
				print(msg)

	def show_all(self,returnable=False,export=False):
		with Session(ENGINE) as session:
			query=session.query(Expiry)
			results=query.order_by(Expiry.BB_Expiry.desc()).all()
			ct=len(results)
			if returnable:
				return results
			if ct == 0:
				print(f"{Fore.orange_red_1}There are No Entries in the Expiry Table!")
			else:
				htext=f'''{Fore.light_steel_blue}Of Total Expiry Entries Checked So Far/ [X]
{Fore.light_yellow}Nearing/Past Entries Total/ [Y]
{Fore.light_red}Total Expiry Entries to Check [Z]
{Fore.light_steel_blue}X/{Fore.light_yellow}Y/{Fore.light_red}Z'''
				headers=f'{htext} -> {Fore.light_green}Name|{Fore.cyan}Barcode|{Fore.light_yellow}Note|{Fore.orange_red_1}EntryId|{Fore.light_magenta}eid|{Fore.light_red}BB_Expiry|{Fore.medium_violet_red}DTOE (DateTime of Entry){Style.reset}'
				print(headers)
				bcds=[]
				for num,entry in enumerate(results):
					bcds.append(str(entry.Barcode)[:-1]+f"|len({len(str(entry.Barcode)[:-1])})")
					msg=f'''{Fore.light_yellow}{num}/{Fore.dark_goldenrod}{num+1}/{Fore.light_red}{ct}{Fore.light_magenta} -> {Fore.light_green}{entry.rebar()}|{Fore.green_yellow}{entry.Name}|{Fore.orange_red_1}{Style.bold}{entry.BB_Expiry}|{Fore.medium_violet_red}{entry.DTOE}{Style.reset}'''
					print(msg)
			if export == True:
				if len(results) < 1:
					print("Nothing To Export")
				else:
					df=pd.DataFrame([row.__dict__ for row in results])
					df.insert(len(df.columns),"No Check Digit Barcode",bcds,True)
					toDrop=['DelPoll','Poll','PastPoll','_sa_instance_state','eid','EntryId']
					df.drop(toDrop, axis=1, inplace=True)
					try:
						f=Path("expired.csv")
						df.to_csv(f,index=False)
						print(f"successfuly export to {f}")
					except Exception as e:
						print(e)
					
					try:
						f=Path("expired.xlsx")
						df.to_excel(f,index=False)
						print(f"successfuly export to {f}")
					except Exception as e:
						print(e)

	def search_expo(self,returnable=False,code=None,group=True,past_due_only=False):
		with Session(ENGINE) as session:
			while True:
				if code != None:
					barcode=code
				else:
					barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Barcode|Name|EntryId|Expiry.eid|Date:",helpText="search for to select",data="string")
					if barcode in [None,]:
						return
					elif barcode in ['d','']:
						continue
				eid_=None
				try:
					eid_=int(barcode)
				except Exception as e:
					print(e)
					eid_=None

				entryid=None
				try:
					entryid=int(barcode)
				except Exception as e:
					print(e)
					entryid=None
				dt=FormBuilderMkText(barcode,"datetime-")
				query=session.query(Expiry).filter(
					or_(
						Expiry.Barcode==barcode,
						Expiry.Barcode.icontains(barcode),
						Expiry.Name==barcode,
						Expiry.Name.icontains(barcode),
						Expiry.Note==barcode,
						Expiry.Note.icontains(barcode),
						Expiry.eid==eid_,
						Expiry.EntryId==entryid,
						Expiry.BB_Expiry==dt,
						)
					)
				if group:
					results=query.order_by(Expiry.DTOE.asc()).order_by(Expiry.BB_Expiry.asc()).group_by(Expiry.Barcode)
				else:
					results=query.order_by(Expiry.DTOE.asc()).order_by(Expiry.BB_Expiry.asc())
				
				print(past_due_only)
				#exit()
				if past_due_only == True:
					tdy=datetime.today()
					tdy=datetime(tdy.year,tdy.month,tdy.day)
					results=results.filter(Expiry.BB_Expiry<=tdy)

				state=db.detectGetOrSet('list maker lookup order',False,setValue=False,literal=False)
				if state == True:
					results=results.order_by(Expiry.BB_Expiry.asc())
				else:
					results=results.order_by(Expiry.BB_Expiry.desc())

				results=results.all()
				ct=len(results)
				if returnable:
					return results
				if ct == 0:
					print(f"{Fore.orange_red_1}There are No Entries in the Expiry Table!")
				else:
					for num,entry in enumerate(results):
						msg=f'''{Fore.light_yellow}{num}/{Fore.dark_goldenrod}{num+1}/{Fore.light_red}{ct}{Fore.light_magenta} -> [BARCD]={Fore.light_green}{entry.rebar()}|[NM]={Fore.green_yellow}{entry.Name}|{entry.Note}|[BB_EXP]={Fore.orange_red_1}{Style.bold}{entry.BB_Expiry}|[DTOE]={Fore.medium_violet_red}{Style.bold}{entry.DTOE}|{Fore.magenta}[eid]={entry.eid}{Style.reset}'''
						print(msg)

	def rm_expo(self,short=True):
		group=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Group results by Barcode[default=True/Yes]?",helpText="results will be grouped by barcode",data="boolean")
		if group is None:
			return
		elif group in ['d',]:
			group=True

		protect_unexpired=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Do not delete/'display for delete' non-past-due expiry's?",helpText="if its not expired, dont show it",data="boolean")
		if protect_unexpired is None:
			return
		elif protect_unexpired in ['d',True]:
			protect_unexpired=True

		toRm=self.search_expo(group=group,returnable=True,past_due_only=protect_unexpired)
		if toRm is None:
			print(f"{Fore.orange_red_1}User Cancelled Early{Style.reset}")
			return
		ct=len(toRm)
		if ct == 0:
			print("Nothing to remove")
			return
		for num,entry in enumerate(toRm):
			if short == False:
				msg=f'''{Fore.light_yellow}{num}/{Fore.dark_goldenrod}{num+1}/{Fore.light_red}{ct}{Fore.light_magenta} -> {entry}{Style.reset}'''
			else:
				msg=f'''{Fore.light_yellow}{num}/{Fore.dark_goldenrod}{num+1}/{Fore.light_red}{ct}{Fore.light_magenta} -> [BARCD]={Fore.light_green}{entry.rebar()}|[NM]={Fore.green_yellow}{entry.Name}|{entry.Note}|[BB_EXP]={Fore.orange_red_1}{Style.bold}{entry.BB_Expiry}|[DTOE]={Fore.medium_violet_red}{Style.bold}{entry.DTOE}|{Fore.magenta}[eid]={entry.eid}{Style.reset}'''
				#msg=f'''{Fore.light_yellow}{num}/{Fore.dark_goldenrod}{num+1}/{Fore.light_red}{ct}{Fore.light_magenta} -> {Fore.light_green}{entry.Barcode}|{Fore.green_yellow}{entry.Name}|{entry.Note}|{Fore.orange_red_1}{Style.bold}{entry.BB_Expiry}|{Fore.medium_violet_red}{Style.bold}{entry.DTOE}|{Fore.magenta}{entry.eid}{Style.reset}'''				
			print(msg)
		which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="delete what numbers, being the first of the x/x/x? separated by commas if multiples.",helpText="use commas to separate selections",data="list")
		if which in [None,'d']:
			if which == 'd':
				print("A number must be provided here!")
			return
		else:
			select=[]
			for i in which:

				try:
					ii=int(i)
					print(i,toRm[ii],"to remove!")
					select.append(toRm[ii].eid)
				except Exception as e:
					print(e,"processing will continue")
			print(select)
			with Session(ENGINE) as session:
				for s in select:
					r=session.query(Expiry).filter(Expiry.eid==s).first()
					print(r)
					if r:
						session.delete(r)
						session.commit()
						session.flush()

	def rm_expo_bar(self):
		protect_unexpired=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Do not delete/'display for delete' non-past-due expiry's?",helpText="if its not expired, dont show it",data="boolean")
		if protect_unexpired is None:
			return
		elif protect_unexpired in ['d',True]:
			protect_unexpired=True
		while True:
			try:
				fieldname='Remove Expiry by Barcode'
				mode='REB'
				h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
				barcode=Prompt.__init2__(self,func=FormBuilderMkText,ptext=f"{h} Barcode to Purge:",helpText="barcode to purge from Expiry Completely!",data="string")
				if barcode in [None,]:
					return
				elif barcode.lower() in ['d',]:
					continue
				else:
					with Session(ENGINE) as session:
						done=session.query(Expiry).filter(Expiry.Barcode==barcode)
						if protect_unexpired:
							tdy=datetime.today()
							tdy=datetime(tdy.year,tdy.month,tdy.day)
							done=done.filter(Expiry.BB_Expiry<=tdy)
						done.delete()
						session.commit()
						session.flush()
						print(f"{Fore.light_red}Done Deleting {Fore.cyan}{done}{Fore.light_red} Expiration Barcodes!{Style.reset}")


			except Exception as e:
				print(e)
				return

	async def show_warnings_async(self):
		await asyncio.to_thread(lambda self=self:self.show_warnings(boot=True))


	def show_warnings(self,barcode=None,export=False,regardless=False,code=None,boot=False):
		with Session(ENGINE) as session:
			if not boot:
				group=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Group results by Barcode[default=True/Yes]?",helpText="results will be grouped by barcode",data="boolean")
				if group is None:
					return
				elif group in ['d',]:
					group=True

				page=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Show results 1 at a time[default=True/Yes]?",helpText="one result at a time",data="boolean")
				if page is None:
					return
				elif group in ['d',]:
					page=True
			else:
				group=True
				page=False

			if barcode == None:
				if group:
					results=session.query(Expiry).group_by(Expiry.Barcode)
				else:
					results=session.query(Expiry)
				state=db.detectGetOrSet('list maker lookup order',False,setValue=False,literal=False)
				if state == True:
					results=results.order_by(Expiry.BB_Expiry.asc())
				else:
					results=results.order_by(Expiry.BB_Expiry.desc())

				results=results.all()
			else:
				results=self.search_expo(returnable=True,code=code,group=group)
			if results in [None,]:
				return
			ct=len(results)
			counter=0
			if ct == 0:
				print(f"{Fore.orange_red_1}No Expiry Results to check...")
				return
			htext=f'''{Fore.light_steel_blue}Of Total Expiry Entries Checked So Far/ [X]
{Fore.light_yellow}Nearing/Past Entries Total/ [Y]
{Fore.light_red}Total Expiry Entries to Check [Z]
{Fore.light_steel_blue}X/{Fore.light_yellow}Y/{Fore.light_red}Z'''
			headers=f'{htext} -> {Fore.light_green}Name|{Fore.cyan}Barcode|{Fore.light_yellow}Note|{Fore.orange_red_1}EntryId|{Fore.light_magenta}eid|{Fore.light_red}BB_Expiry|{Fore.medium_violet_red}DTOE (DateTime of Entry){Style.reset}'
			print(headers)
			exportable=[]
			bcds=[]
			num=0
			for num2,i in enumerate(results):
				warn_date=i.BB_Expiry+timedelta(seconds=i.Poll)
				past_warn_date=i.BB_Expiry+timedelta(seconds=i.PastPoll)
				del_date=i.BB_Expiry+timedelta(seconds=i.DelPoll)
				if ( datetime.now() >= i.BB_Expiry ) or ( regardless == True ):
					exportable.append(i)
					bcds.append(str(i.Barcode)[:-1]+f"|len({len(str(i.Barcode)[:-1])})")
					counter+=1
					iformat=f'{Fore.light_green}{i.Name}|{Fore.cyan}{i.rebar()}|{Fore.light_yellow}{i.Note}|{Fore.orange_red_1}{i.EntryId}|{Fore.light_magenta}{i.eid}|{Fore.light_red}{i.BB_Expiry}|{Fore.medium_violet_red}{i.DTOE}{Style.reset}'
					msg=f'''{Fore.light_steel_blue}{num}/{Fore.light_yellow}{counter}/{Fore.light_red}{ct}-> {iformat}'''
					print(msg)
					if datetime.now() <= warn_date:
						print(f'''{Back.plum_2}{Fore.dark_red_1}{warn_date}: Expiration Warn Date{Style.reset}''')
					elif datetime.now() > warn_date:
						print(f'''{Back.plum_2}{Fore.dark_red_1}{warn_date}: Expiration Warn Date{Fore.dark_green}{Style.bold}*{Style.reset}''')
					if datetime.now() >= warn_date:
						if datetime.now() <= past_warn_date:
							print(f'{Back.chartreuse_2a}{Fore.dark_blue}{Style.bold}{past_warn_date}: Expiration Past Warn Date{Style.reset}')
						elif datetime.now() > past_warn_date:
							print(f'{Back.chartreuse_2a}{Fore.dark_blue}{Style.bold}{past_warn_date}: Expiration Past Warn Date{Fore.dark_red_2}{Style.underline}***{Style.reset}')
					if datetime.now() >= past_warn_date:
						if datetime.now() <= del_date:
							print(f'{Back.dark_red_2}{Fore.orange_1}{del_date}: Expiration Deletion Date{Style.reset}')
						elif datetime.now() > del_date:
							print(f'{Back.dark_red_2}{Fore.orange_1}{del_date}: Expiration Deletion Date{Fore.light_green}{Style.bold}***{Style.reset}')
							delete=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Delete it?",helpText="yes or no",data="boolean")
							if delete in [None,]:
								continue
							elif delete == True:
								session.delete(i)
								session.commit()
								session.flush()
							else:
								pass
					if page:
						nxt=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Next?",helpText="enter",data="string")
						if nxt is None:
							return
						elif nxt in ['d',True]:
							print(headers)
							continue
						else:
							break
					num+=1
				#postMsg=f'''{warn_date}: Warn Date
				#{past_warn_date}: Past Warn Date
				#{del_date}: Deletion Date'''

			if export == True:
				if len(exportable) < 1:
					print("Nothing To Export")
				else:
					df=pd.DataFrame([row.__dict__ for row in exportable])
					df.insert(len(df.columns),"No Check Digit Barcode",bcds,True)
					toDrop=['DelPoll','Poll','PastPoll','_sa_instance_state','eid','EntryId']
					df.drop(toDrop, axis=1, inplace=True)
					try:
						f=Path("expired.csv")
						df.to_csv(f,index=False)
						print(f"successfuly export to {f}")
					except Exception as e:
						print(e)
					
					try:
						f=Path("expired.xlsx")
						df.to_excel(f,index=False)
						print(f"successfuly export to {f}")
					except Exception as e:
						print(e)


	def clear_all(self):
		with Session(ENGINE) as session:
			session.query(Expiry).delete()
			session.commit()
			session.flush()

	def __init__(self,init_only=False):
		#dates are first numeric using 102693 as the string
		#where first 2 digits are month,z-filled if len of month number is less than 2
		#where 3rd-4th digits are day,z-filled if len of day number is less than 2
		#where last 2 digits are year; this is not four digits, as expo is looking ahead only, and i dont
		#expect to be around into the 2100's;z-filled if len of year number is less than 2
		helpText=f'''
{Style.bold}{Fore.orange_red_1}Expiration Menu Options{Style.reset}
	{Fore.light_steel_blue}'get upcoming expiry','gue'{Fore.light_green}get upcoming expiry{Style.reset}
	{Fore.light_steel_blue}'get oldest expiry','goe'{Fore.light_green}get oldest expiry{Style.reset}
	{Fore.light_steel_blue}'scan wl','expireds wl','ewl'{Fore.light_green} -{Fore.cyan} set date for best-by/expiration-date for scanned upc using numeric data provided by label for code/barcode{Style.reset}
	{Fore.light_steel_blue}'scan wol','expireds wol','ewol','e'{Fore.light_green} -{Fore.cyan} set date for best-by/expiration-date for scanned upc using numeric data provided by label for code/barcode with {Fore.orange_red_1}lookup updates disabled{Style.reset}
	{Fore.light_steel_blue}'scane','expireds edit','edit','edit exps'{Fore.light_green} -{Fore.cyan} edit date for best-by/expiration-date for scanned upc using numeric data provided by label for code/barcode and selected by prompt{Style.reset}
	{Fore.light_steel_blue}'dates4barcode','d4bcd','dts4bcd'{Fore.light_green} -{Fore.cyan}display dates for barcode{Style.reset}
	{Fore.light_steel_blue}sw,show-warns,show-warnings,show_warns,show_warnings{Fore.light_green} -{Fore.cyan} prompt for barcode and show warnings; cleans anything past due by prompt{Style.reset}
	{Fore.light_steel_blue}sw*,show-warns*,show-warnings*,show_warns*,show_warnings*{Fore.light_green} -{Fore.cyan} prompt for barcode and show warnings; cleans anything past due by prompt *regardless of BB_Expiry,show entries{Style.reset}
	{Fore.light_steel_blue}swa,show-all-warns,show-all-warnings,show_all_warns,show_all_warnings{Fore.light_green} -show{Fore.cyan} anything within PollDates, where PollDates are [Warn of Upcoming(Poll),Past BB/Expo Date(Past_Warn_Date),cleanup date(De[letion] Date)] cleans anything past due by prompt{Style.reset}
	{Fore.light_steel_blue}'sa','show all','show_all','showall','show-all'{Fore.light_green} -{Fore.cyan} show all expirations and warning{Style.reset}
	{Fore.light_steel_blue}'sea','show export all','show_export_all','showexportall','show-export-all'{Fore.light_green} -{Fore.cyan} show & export all expirations and warning{Style.reset}
	{Fore.light_steel_blue}'re','rm exp','rm_exp','rm-exp','rme'{Fore.light_green} -{Fore.cyan} remove expirations and warnings{Style.reset}
	{Fore.light_steel_blue}reb,re b,rm barcode,rm batch{Fore.light_green} -{Fore.cyan}without confirmation, remove all Expiry with barcode{Style.reset}
	{Fore.light_steel_blue}'search','sch','look','where\'s my key bitch?'{Fore.light_green} -{Fore.cyan} search for a product to see if it was logged by Barcode|Name|EntryId|Expiry.eid|Date{Style.reset}
	{Fore.light_steel_blue}ca,clear all,clear_all{Fore.light_green} -{Fore.cyan} removes all items contained here{Style.reset}
	{Fore.light_steel_blue}'epst','edit past','ep'{Fore.light_green} -{Fore.cyan} edit expireds user==False{Style.reset}
	{Fore.light_steel_blue}'update expiry from entry barcode','uefeb'{Fore.light_green} -{Fore.cyan} look for Expiry with Name=='New Item' and checks Entry Table for product and updates the name by First result{Style.reset}
	{Fore.light_steel_blue}'is','is expired','ise'{Fore.light_green} -{Fore.cyan}is the input date expired!{Style.reset}
	{Fore.light_steel_blue}'ddiff','date diff','datediff'{Fore.light_green} -{Fore.cyan}display the difference between dates!{Style.reset}
	{Fore.light_steel_blue}'date forwards','forwards date','dt+','date+'{Fore.light_green} -{Fore.cyan}calculate a future date by adding values to the date relatively!{Style.reset}
{Style.bold}{Fore.orange_red_1}Notes{Style.reset} {Fore.orange_red_1}Dates{Fore.grey_70}
	Dates can be provided as DD{Fore.light_green}#SEPCHAR#{Fore.grey_70}MM{Fore.light_green}#SEPCHAR#{Fore.grey_70}YY|YYYY
	where {Fore.light_green}#SEPCHAR#{Fore.grey_70} can be any of the punctuation-chars, save for '%'.
	MM - 2-Digit Month
	DD - 2-Digit Day
	YY|YYYY - 2-Digit or 4-Digit Year
	{Fore.light_yellow}10.28/26 {Fore.light_magenta}10.28.26 {Fore.orange_red_1}10/26.93{Fore.cyan} - are valid, and ONLY touch the tip of the glacier{Fore.grey_70}
	if {Fore.light_red}No Day{Fore.grey_70} is provided in {Fore.light_magenta}BB/Exp Date{Fore.grey_70}, then assume day is {Fore.orange_red_1}01
{Style.reset}'''
		while not init_only:
			#for use with header
			fieldname='RotationAndExpiration'
			mode='RNE'
			h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
			doWhat=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} Do What?",helpText=helpText,data="String")
			if doWhat in [None,]:
				return
			elif doWhat in ['d',]:
				print(helpText)
				continue
			elif doWhat.lower() in ['get upcoming expiry','gue']:
				self.getUpcomingExpiry()
			elif doWhat.lower() in ['get oldest expiry','goe']:
				self.getUpcomingExpiry(oldest=True)
			elif doWhat.lower() in ['scan wl','expireds wl','ewl']:
				self.scan()
			elif doWhat.lower() in ['scan wol','expireds wol','ewol','e']:
				self.scan(ewol=True)
			elif doWhat.lower() in ['sa','show all','show_all','showall','show-all']:
				self.show_all()
			elif doWhat.lower() in ['sea','show export all','show_export_all','showexportall','show-export-all']:
				self.show_all(export=True)
			elif doWhat.lower() in ['re','rm exp','rm_exp','rm-exp','rme']:
				self.rm_expo(short=True)
			elif doWhat.lower() in ['rel','rm exp long','rm_exp_long','rm-exp-long','rmel']:
				self.rm_expo(short=False)
			elif doWhat.lower() in ['search','sch','look','where\'s my key bitch?']:
				self.search_expo()
			elif doWhat.lower() in 'swa,show-all-warns,show-all-warnings,show_all_warns,show_all_warnings'.split(','):
				self.show_warnings()
			elif doWhat.lower() in 'sw,show-warns,show-warnings,show_warns,show_warnings'.split(","):
				self.show_warnings(barcode=True)
			elif doWhat.lower() in 'sw*,show-warns*,show-warnings*,show_warns*,show_warnings*'.split(","):
				self.show_warnings(barcode=True,regardless=True)
			elif doWhat.lower() in 'esw,export-show-warns,export-show-warnings,export_show_warns,export_show_warnings'.split(","):
				self.show_warnings(barcode=True,export=True)	
			elif doWhat.lower() in 'ca,clear all,clear_all'.split(','):
				self.clear_all()
			elif doWhat.lower() in 'reb,re b,rm barcode,rm batch'.split(","):
				self.rm_expo_bar()
			elif doWhat.lower() in ['dates4barcode','d4bcd','dts4bcd']:
				self.dates4barcode()
			elif doWhat.lower() in ['scane','expireds edit','edit','edit exps']:
				self.edit_expireds()
			elif doWhat.lower() in ['epst','edit past','ep']:
				self.edit_expireds(user_search=False)
			elif doWhat.lower() in ['update expiry from entry barcode','uefeb']:
				self.updateExpFromEntry()
			elif doWhat.lower() in ['is','is expired','ise']:
				self.isExpired()
			elif doWhat.lower() in ['ddiff','date diff','datediff']:
				self.diff()
			elif doWhat.lower() in ['date forwards','forwards date','dt+','date+']:
				dateAhead()
			else:
				print(helpText)

	def edit_expireds(self,user_search=True):
		while True:
			try:
				with Session(ENGINE) as session:
					if user_search == True:
						results=self.search_expo(returnable=True,code=None)
					else:
						results=session.query(Expiry).filter(Expiry.BB_Expiry<=datetime.now()).all()
					if results == None:
						break
					ct=len(results)
					if ct == 0:
						print("Nothing to edit")
						break
					else:
						for num,i in enumerate(results):
							iformat=f'{Fore.light_green}{i.Name}|{Fore.cyan}{i.rebar()}|{Fore.light_yellow}{i.Note}|{Fore.orange_red_1}{i.EntryId}|{Fore.light_magenta}{i.eid}|{Fore.light_red}{i.BB_Expiry}|{Fore.medium_violet_red}{i.DTOE}{Style.reset}'
							msg=f"{num}/{num+1} of {ct} -> {iformat}"
							print(msg)
						which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Which index(es):",helpText="can be a list(,) or/and range(1-10)",data="list")
						if which in [None,]:
							return
						try:
							ct2=len(which)
							for num2,i2 in enumerate(which):
								i2=int(i2)
								print(f"committing {num2}/{num2+1} of {ct2} -> {results[i2]}")
								excludes="eid"
								data={str(x.name):{'default':getattr(results[i2],str(x.name)),'type':str(x.type)} for x in results[i2].__table__.columns if str(x.name) not in excludes}
								fd=FormBuilder(data=data)
								if fd in [None,]:
									return
								upd8=session.query(Expiry).filter(Expiry.eid==results[i2].eid).first()
								if upd8 != None:
									for i in fd:
										setattr(upd8,i,fd[i])
										session.commit()
								session.flush()
								print(f"{Back.grey_30}committed {num2}/{num2+1} of {ct2} -> {results[i2]}{Style.reset}")
						except Exception as e:
							print(e)


				break
			except Exception as e:
				print(e)