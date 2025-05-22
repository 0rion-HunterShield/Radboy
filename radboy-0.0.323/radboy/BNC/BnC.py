
from radboy.DB.db import *
from radboy.DB.DatePicker import *
from radboy.FB.FormBuilder import *
from radboy.FB.FBMTXT import *
from password_generator import PasswordGenerator
import pint,os
from datetime import datetime,timedelta,date,time
import base64
from Crypto.Cipher import AES
#from Cryptodome.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from collections import namedtuple
import re
from copy import deepcopy

#for totaling on-hand cash that is not in the bank
#items csv for when util ui is made
CashPoolStarter='''Name,Value,Qty
Quarter,0.25,0
Nickel,0.05,0
Dime,0.10,0
Penny,0.01,0
1$Bill,1,0
2$Bill,2,0
5$Bill,5,0
10$Bill,10,0
20$Bill,20,0
50$Bill,50,0
100$Bill,100,0
'''.splitlines()
class CashPool(BASE,Template):
	__tablename__="CashPool"
	Name=Column(String)
	Value=Column(Float)
	Qty=Column(Integer)
	CPID=Column(Integer,primary_key=True)

	default={
	'Name':'',
	'Value':0.0,
	'Qty':0,
	}
	def values(self):
		mapped={}
		for i in self.__table__.columns:
			mapped[i.name]=getattr(self,i.name)
		preferences=namedtuple('CashPool',mapped.keys())
		return preferences(**mapped)

	def __init__(self,**kwargs):
		self.setDefaults(kwargs)
		for k in kwargs.keys():
			if k in [s.name for s in self.__table__.columns]:
				setattr(self,k,kwargs.get(k))

	def setDefaults(self,kwargs):
		for i in self.default.keys():
			if i not in kwargs.keys():
				setattr(self,i,self.default[i])


#for totaling non-barcoded expenses
#Name,Value,Qty,DueDate,DatePaid
class Bill(BASE,Template):
	__tablename__="Bill"
	Name=Column(String)
	Value=Column(Float)
	Qty=Column(Integer)
	DueDate=Column(Date)
	DatePaid=Column(Date)
	BID=Column(Integer,primary_key=True)

	default={
	'Name':'Generic Expense',
	'Value':0.0,
	'Qty':1,
	'DueDate':None,
	'DatePaid':None,
	}
	def values(self):
		mapped={}
		for i in self.__table__.columns:
			mapped[i.name]=getattr(self,i.name)
		preferences=namedtuple('Bill',mapped.keys())
		return preferences(**mapped)

	def __init__(self,**kwargs):
		self.setDefaults(kwargs)
		for k in kwargs.keys():
			if k in [s.name for s in self.__table__.columns]:
				setattr(self,k,kwargs.get(k))

	def setDefaults(self,kwargs):
		for i in self.default.keys():
			if i not in kwargs.keys():
				setattr(self,i,self.default[i])

class CashPoolJournal(BASE,Template):
	__tablename__="CashPoolJournal"
	DTOE=Column(DateTime,default=datetime.now())

	'''Cash Pool Id'''
	CPID=Column(Integer)
	'''Cash pool journal id'''
	CPJID=Column(Integer,primary_key=True)

	Name=Column(String)
	Value=Column(Float)
	'''The Latest Qty.'''
	Qty=Column(Integer)
	'''How Much was modified with/the delta/the changed amount.'''
	QtyDiff=Column(Float,default=0)
	PrevQty=Column(Float,default=0)
	Mode=Column(String,default='modify')

	default={
	'Name':'',
	'Value':0.0,
	'Qty':0,
	}
	def values(self):
		mapped={}
		for i in self.__table__.columns:
			mapped[i.name]=getattr(self,i.name)
		preferences=namedtuple('CashPoolJournal',mapped.keys())
		return preferences(**mapped)

	def __init__(self,**kwargs):
		self.setDefaults(kwargs)
		for k in kwargs.keys():
			if k in [s.name for s in self.__table__.columns]:
				setattr(self,k,kwargs.get(k))

	def setDefaults(self,kwargs):
		for i in self.default.keys():
			if i not in kwargs.keys():
				setattr(self,i,self.default[i])


CashPool.metadata.create_all(ENGINE)
CashPoolJournal.metadata.create_all(ENGINE)

Bill.metadata.create_all(ENGINE)

class BnCUi:
	def showJournals(self,page=False):
		fieldnames=['CPID','CPJID','Name']
		try:
			while True:
				try:
					searchName=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{self.cashpoolTotal()}{Fore.light_sea_green}{','.join(fieldnames)}{Fore.light_yellow} Search",helpText=f"search for CashPoolJournal using {Fore.light_sea_green}{','.join(fieldnames)} fields",data="string")
					if searchName in [None,]:
						return
					with Session(ENGINE) as session:
						
						results=[]
						if searchName in ['*','d','all',]:
							results=session.query(CashPoolJournal).all()
						else:
							q=[
									CashPoolJournal.Name.icontains(searchName),
									CashPoolJournal.Name==searchName,
							]
							try:
								CPID=int(searchName)
								q.append(CashPoolJournal.CPID==CPID)
							except Exception as eee:
								print(eee)

							try:
								CPJID=int(searchName)
								q.append(CashPoolJournal.CPJID==CPJID)
							except Exception as eee:
								print(eee)
								
							try:
								results=session.query(CashPoolJournal)
								results=results.filter(or_(*q)).all()
							except Exception as e:
								print(e)
								results=session.query(CashPoolJournal).all()
						ct=len(results)
						if ct < 1:
							print("No Journals Found!")
							return
						for num, i in enumerate(results):
							msg=f"{num}/{num+1} of {ct} -> {i}"
							print(msg)
							if page:
								NEXT=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Next[<ENTER>]/Delete[rm/del]?",helpText="hit enter to skip; type one of 'rm','del','delete','remove' to delete the current journal entry ",data="string")
								if NEXT in [None,]:
									return
								elif NEXT in ['d',]:
									continue
								elif NEXT.lower() in ['rm','del','delete','remove']:
									session.delete(i)
									session.commit()
									continue
								else:
									continue
				except Exception as ee:
					print(ee)
		except Exception as e:
			print(e)

	def page_journal(self,fieldname="Name",page=False):
		try:
			while True:
				try:
					searchName=Prompt.__init2__(None,func=self.mkText,ptext=f"{self.cashpoolTotal()}{fieldname} Search",helpText="search for CashPoolJournal using Name field",data=self)
					if searchName in [None,]:
						return
					else:
						with Session(ENGINE) as session:
							fields=[i.name for i in CashPool.__table__.columns]
							if fieldname not in fields:
								print(f"invalid fieldname {fieldname}")
								return
							try:
								results=session.query(CashPool).filter(getattr(CashPool,fieldname).icontains(searchName)).all()
							except Exception as e:
								print(e)
								results=session.query(CashPool).filter(getattr(CashPool,fieldname)==searchName).all()
							ct=len(results)
							if ct < 1:
								print(f"{Fore.light_red}Nothing in the Bank!{Style.reset}")
							else:
								for num,r in enumerate(results):
									msg=f'''{num}/{ct-1} -> {r}'''
									print(msg)
								which=Prompt.__init2__(self,func=self.mkint,ptext=f"{self.cashpoolTotal()}Which CashPool Item?",helpText=f"type a number between [0-{ct-1}]",data={'default':0})
								if which in [None,]:
									return
								
								selected=results[which]
								print(selected)
								jrnls=session.query(CashPoolJournal).filter(CashPoolJournal.CPID==selected.CPID).all()
								ctj=len(jrnls)
								if  ctj < 1:
									continue
								for num,i in enumerate(jrnls):
									msg=f"{num}/{num+1} of {ctj} -> {i}"
									print(msg)
									if page:
										NEXT=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Next?",helpText="hit enter",data="string")
										if NEXT in [None,]:
											return
										elif NEXT in ['d',]:
											continue
										else:
											continue
				except Exception as ee:
					print(ee)
		except Exception as e:
			print(e)



	def summarize_cp(self):
		with Session(ENGINE) as session:
			results=session.query(CashPool)
			ct=len(results.all())
			if ct < 1:
				print(f"{Fore.light_red}Nothing in the Bank!{Style.reset}")
			else:
				total=0
				for num,r in enumerate(results.all()):
					total+=(r.Value*r.Qty)
					msg=f'''{num}/{ct-1} ->[{Fore.light_green}{r.Name}{Style.reset}] {Fore.grey_50}({r.Qty}*${r.Value})=({Fore.light_yellow}${round(r.Value*r.Qty,2)}{Fore.grey_50}) of {Fore.light_red}${round(total,3)}{Style.reset}'''
					print(msg)
				session.commit()
				session.flush()
				

	def hard_reset(self):
		CashPool.__table__.drop(ENGINE)
		CashPool.metadata.create_all(ENGINE)

		Bill.__table__.drop(ENGINE)
		Bill.metadata.create_all(ENGINE)
		print(f"{Fore.orange_red_1}A restart is required!{Style.reset}")
		exit()

	def soft_reset_cp(self):
		with Session(ENGINE) as session:
			results=session.query(CashPool)
			x=results.delete()
			session.commit()
			session.flush()
			check=len(results.all())
			print(f"{Fore.light_steel_blue}There are {Fore.light_red}{check}{Fore.light_steel_blue} CashPool Items in the System{Style.reset}")

	def reset_cp_qty(self,to=0):
		with Session(ENGINE) as session:
			results=session.query(CashPool)
			ct=len(results.all())
			if ct < 1:
				print(f"{Fore.light_red}Nothing in the Bank!{Style.reset}")
			else:
				for num,r in enumerate(results.all()):
					results.Qty=to
					if num%200==0:
						session.commit()
					msg=f'''{num}/{ct-1} -> {r}'''
					print(msg)
				#which=Prompt.__init2__(self,func=self.mkint,ptext=f"{self.cashpoolTotal()}Which CashPool Item?",helpText=f"type a number between [0-{ct-1}]",data={'default':0})
				#if which in [None,]:
				#	return
				session.commit()
				session.flush()
				check=len(results.all())
			print(f"{Fore.light_steel_blue}There are {Fore.light_red}{check}{Fore.light_steel_blue} CashPool Items in the System{Style.reset}")

		

	#for mode selection
	def mkTextLower(self,text,data):
		return text.lower()

	#most everything else
	def mkText(self,text,data):
		return text

	def mkInt(self,text,data):
		try:
			if text in ['']:
				return 0
			else:
				return int(text)
		except Exception as e:
			print(e)

	def mkint(self,text,data={'default':None}):
		try:
			if text in ['',]:
				return data['default']
			else:
				try:
					return int(eval(text))
				except Exception as e:
					print(e)
				try:
					return int(text)
				except Exception as e:
					print(e)
				return data['default']
		except Exception as e:
			print(e)

	def newCashPoolItem(self):
		with Session(ENGINE) as session:
			cpi=CashPool()
			session.add(cpi)
			session.commit()
			session.refresh(cpi)
			excludes=['CPID',]
			data={
				i.name:{
					'default':getattr(cpi,str(i.name)),
					'type':str(i.type)
				} for i in cpi.__table__.columns if str(i.name) not in excludes}
			fd=FormBuilder(data=data)
			if fd is None or fd in [None,]:
				session.delete(cpi)
				session.commit()
			for num,i in enumerate(fd):
				setattr(cpi,i,fd[i])
				if num %10 == 0:
					session.commit()
			session.commit()
			session.refresh(cpi)
			selected=cpi
			mode="set"
			journal=CashPoolJournal(Name=selected.Name,Qty=selected.Qty,QtyDiff=selected.Qty,PrevQty=0,Mode=mode,Value=selected.Value,DTOE=datetime.now(),CPID=selected.CPID)
			session.add(journal)
			session.commit()
			session.refresh(journal)
			print(journal)
			print(cpi)


	def icp(self):
		with Session(ENGINE) as session:
			reader=csv.reader(CashPoolStarter,delimiter=',')
			for num,line in enumerate(reader):
				if num > 0:
					print(num,line)
					cp=CashPool(Name=line[0],Value=line[1],Qty=line[2])
					session.add(cp)
					session.commit()
					session.refresh(cp)
					print(f"created {num+1}/{len(CashPoolStarter)} -> {cp}")

	def cashpoolTotal(self):
		with Session(ENGINE) as session:
			total=0
			results=session.query(CashPool).all()
			for r in results:
				total+=(r.Qty*r.Value)
			total=round(total,3)
			return f"{Fore.light_yellow}CashPool Total ({Fore.light_sea_green}Petty Cash{Fore.light_yellow}) = {Fore.orange_red_1}${Fore.dark_goldenrod}{total}{Style.reset}\n"

	def trip_cost(self):
		data={
			"Fuel Cost per unit of volume($5.00 per Gallon): ":{
				'type':"float",
				"default":5.00
			},
			"Distance Travelled (ie 1 Mile)":{
			"type":"float",
			"default":1,
			},
			"Efficiency Per Unit Volume (ie 22 MPG)":{
			"type":"float",
			"default":22,
			},
		}
		fd=FormBuilder(data=data)
		if fd in [None,]:
			return
		result=(fd["Distance Travelled (ie 1 Mile)"]/fd["Efficiency Per Unit Volume (ie 22 MPG)"])*fd["Fuel Cost per unit of volume($5.00 per Gallon): "]
		print(f"{Fore.light_steel_blue}Your Estimated Fuel Cost Estimate is {Fore.light_red}${round(result,2)}{Style.reset}")


	def ssxq(self,fieldname='Name',delete=False):
		try:
			while True:
				try:
					searchName=Prompt.__init2__(None,func=self.mkText,ptext=f"{self.cashpoolTotal()}{fieldname} Search",helpText="search for CashPool Item using Name||value field",data=self)
					if searchName in [None,]:
						return
					else:
						with Session(ENGINE) as session:
							fields=[i.name for i in CashPool.__table__.columns]
							if fieldname not in fields:
								print(f"invalid fieldname {fieldname}")
								return
							try:
								try:
									searchValue=float(searchName)
									results=session.query(CashPool).filter(or_(getattr(CashPool,fieldname).icontains(searchName),CashPool.Value==searchValue)).all()
								except Exception as ee:
									print(ee,"...Attempting Name Resolution!")
									results=session.query(CashPool).filter(getattr(CashPool,fieldname).icontains(searchName)).all()
							except Exception as e:
								print(e)
								results=session.query(CashPool).filter(getattr(CashPool,fieldname)==searchName).all()
							ct=len(results)
							if ct < 1:
								print(f"{Fore.light_red}Nothing in the Bank!{Style.reset}")
							else:
								for num,r in enumerate(results):
									msg=f'''{num}/{ct-1} -> {r}'''
									print(msg)
								which=Prompt.__init2__(self,func=self.mkint,ptext=f"{self.cashpoolTotal()}Which CashPool Item?",helpText=f"type a number between [0-{ct-1}]",data={'default':0})
								if which in [None,]:
									return
								
								selected=results[which]
								print(selected)
								if delete:
									zz=session.query(CashPoolJournal).filter(CashPoolJournal.CPID==results[which].CPID).delete()
									session.commit()
									x=session.delete(results[which])
									session.commit()
									print("Deleting It!")
									return
								qty=Prompt.__init2__(self,func=self.mkint,ptext=f"{self.cashpoolTotal()}Qty?",helpText=f"type a qty",data={'default':1})
								if qty in [None,]:
									return
								mode=Prompt.__init2__(None,func=self.mkTextLower,ptext=f"{self.cashpoolTotal()}What are we doing [m/s]",helpText="modifying the current value(m/modify/mod(using - before the number to subtract using incrementation)), or setting the current value(s|set)",data=self)
								if mode in [None,]:
									return
								elif mode in ['m','mod','modify','']:
									mode="modify"
									selected.Qty+=qty
								elif mode in ['s','set']:
									selected.Qty=qty
									mode="set"
								session.commit()
								session.flush()
								session.refresh(selected)
								journal=CashPoolJournal(Name=selected.Name,Qty=selected.Qty,QtyDiff=qty,PrevQty=selected.Qty-qty,Mode=mode,Value=selected.Value,DTOE=datetime.now(),CPID=selected.CPID)
								session.add(journal)
								session.commit()
								session.refresh(journal)
								print(journal)
								print(selected)
								#selected.Qty
				except Exception as ee:
					print(ee)
		except Exception as e:
			print(e)
	
	def newBill(self,data=None,otherExcludes=[]):
		if data != None and 'BID' in list(data.keys()):
			data.pop('BID')
		if data == None:
			data=deepcopy(self.Bill_default)
		self.skipTo=None
		while True:  
			#print(self.skipTo,"#loop top")
			for num,f in enumerate(data):
				#print(self.skipTo,'#2',"1 loop for")
				if self.skipTo != None and num < self.skipTo:
					continue
				else:
					self.skipTo=None
				keys=['e','p','d']
				while True:
					try:
						if str(f) in otherExcludes:
							print(f"Not working on this one RN! '{f}'")
						else:
							def lclt(text,data):
								return text
							dtmp=Prompt.__init2__(None,func=lclt,ptext=f"Bill[default:{data[f]}] {f}",helpText=f"{Fore.light_steel_blue}Enter a value for {f}, or leave blank to use scanned code; 'b' goes back to 'TaskMode'; 'e' to skip/exit entry altogether! 'p' for previous ; 'd' to use default stored value, if you entered a value, then 'd' will use that value when coming back from 'p'{Style.reset}",data=self)
							if dtmp in [None,]:
								print(f"{Fore.orange_red_1}User Canceled!{Style.reset}")
								return
						if dtmp in ['',None]:
							fields={i.name:str(i.type) for i in Bill.__table__.columns}
							if f in fields.keys():
								if fields[f].lower() in ["string",]:
									data[f]=dtmp
								elif fields[f].lower() in ["float",]:
									data[f]=1.0
								elif fields[f].lower() in ["integer",]:
									data[f]=1
								elif fields[f].lower() in ["boolean",]:
									data[f]=False
								elif fields[f].lower() in ['date',]:
									if dtmp in ['y','yes','1','true','True']:
										data[f]=DatePkr()
									else:
										data[f]=None
								else:
									data[f]=dtmp
							else:
								raise Exception(f"{Fore.red}{Style.bold}Unsupported Field {Fore.light_red}'{f}'{Style.reset}")
							#data[f]=code
						elif isinstance(dtmp,str):
							if str(dtmp).lower() in ['e',]:
								return
							elif str(dtmp).lower() in ['p',]:
								#print(num,num-1,"#3 loop while")
								self.skipTo=num-1
								break
							elif str(dtmp).lower() in ['d',]:
								print(f'{Fore.light_green}{data[f]}{Style.reset}',f'{Fore.orange_red_1}using default{Style.reset}')
								pass
							else:
								fields={i.name:str(i.type) for i in Bill.__table__.columns}
								if f in fields.keys():
									if fields[f].lower() in ["string",]:
										data[f]=dtmp
									elif fields[f].lower() in ["float",]:
										data[f]=float(eval(dtmp))
									elif fields[f].lower() in ["integer",]:
										data[f]=int(eval(dtmp))
									elif fields[f].lower() in ["boolean",]:
										data[f]=bool(eval(dtmp))
									elif fields[f].lower() in ['date',]:
										if dtmp in ['y','yes','1','true','True']:
											data[f]=DatePkr()
										else:
											data[f]=None
									else:
										data[f]=dtmp
								else:
									raise Exception(f"{Fore.red}{Style.bold}Unsupported Field {Fore.light_red}'{f}'{Style.reset}")
								#data[f]=dtmp
						else:
							data[f]=dtmp
						self.skipTo=None
						break
					except Exception as e:
						print(e)
						break
				if self.skipTo != None:
					break
			if self.skipTo == None:
				break
		return data


	def __init__(self,parent):
		self.Bill_default=deepcopy(Bill.default)
		self.parent=parent
		while True:
			try:
				cmdColor=Fore.green_yellow+Style.underline
				cmdColor2=Fore.light_magenta
				expColor=Fore.grey_50
				h1=f'{Fore.light_steel_blue}{Style.bold}CashPool{Style.reset}'.center(os.get_terminal_size().columns-10)
				h2=f'{Fore.light_steel_blue}{Style.bold}Bill{Style.reset}'.center(os.get_terminal_size().columns-10)
				helpText=f'''
{h1.replace(" ",".")}
'{cmdColor}init cashpool{Style.reset}','{cmdColor}init_cashpool{Style.reset}' - {expColor}initialize CashPool table{Style.reset}
'{cmdColor}ssxq{Style.reset}','{cmdColor}search set x qty{Style.reset}',{cmdColor}'search_set_x_qty{Style.reset}' - {expColor}set CashPool Qty for CashPool x found by searching name by prompt{Style.reset}
'{cmdColor}ecpid{Style.reset}','{cmdColor}edit by cpid{Style.reset}','{cmdColor}edit cpid{Style.reset}','{cmdColor}edit_cpid{Style.reset}','{cmdColor}edit_by_cpid{Style.reset}' - {expColor}set CashPool Qty for CashPool x found by search by cpid prompt{Style.reset}
'{cmdColor}rmxq{Style.reset}','{cmdColor}remove x qty{Style.reset}','{cmdColor}remove_x_qty{Style.reset}' - {expColor}rm CashPool Item by searching for name selection{Style.reset}
'{cmdColor}rmxq{Style.reset}','{cmdColor}remove x qty{Style.reset}','{cmdColor}remove_x_qty{Style.reset}' - {expColor}rm CashPool Item by searching for CPID selection{Style.reset}
'{cmdColor}soft_reset_cp{Style.reset}' - {expColor}delete everything in the table but do not drop the table{Style.reset}
'{cmdColor}hard_reset_all{Style.reset}' - {expColor}drop both the CashPool Table & the Bill Table{Style.reset}
'{cmdColor}summarize_cp{Style.reset}','{cmdColor}scp{Style.reset}','{cmdColor}onhand{Style.reset}','{cmdColor}on-hand{Style.reset}','{cmdColor}banked{Style.reset}','{cmdColor}how much do i have?{Style.reset}' - {expColor}breakdown CashPool Contents for Display{Style.reset}
{h2.replace(" ",".")}
'{cmdColor2}nb{Style.reset}','{cmdColor2}new bill{Style.reset}','{cmdColor2}new_bill{Style.reset}' - {expColor}create a new bill{Style.reset}
'{cmdColor2}cab{Style.reset}','{cmdColor2}clear all bill{Style.reset}','{cmdColor2}del all bill{Style.reset}','{cmdColor2}dab{Style.reset}','{cmdColor2}rm all bill{Style.reset}','{cmdColor2}rab{Style.reset}' - {expColor}remove all bill items{Style.reset}

'{cmdColor2}saeb{Style.reset}','{cmdColor2}select and edit bill{Style.reset}','{cmdColor2}select_and_edit_bill{Style.reset}','{cmdColor2}select&edit bill{Style.reset}','{cmdColor2}s&eb{Style.reset}' - {expColor}print all bills for selection, select by number, and prompt for fields to edit{Style.reset}
'{cmdColor2}sarb','{cmdColor2}select and rm bill{Style.reset}','{cmdColor2}select_and_rm_bill{Style.reset}','{cmdColor2}select&rm bill{Style.reset}','{cmdColor2}s&er{Style.reset}' - {expColor}print all bills for selection, select by number, and delete it{Style.reset}
'{cmdColor2}sab{Style.reset}','{cmdColor2}show all bill{Style.reset}','{cmdColor2}show_all_bill{Style.reset}','{cmdColor2}show bill{Style.reset}','{cmdColor2}s*b{Style.reset}' - {expColor}print all bills{Style.reset}
'{cmdColor2}ssb{Style.reset}','{cmdColor2}select show bill{Style.reset}','{cmdColor2}select_show_bill{Style.reset}' - {expColor}print bill to screen via selection{Style.reset}
'{cmdColor2}tc{Style.reset}','{cmdColor2}trip cost{Style.reset}','{cmdColor2}trip_cost{Style.reset}' - {expColor}calculate cost of gas for a given trip{Style.reset}
{cmdColor2}'vj','view journal','vwjrnl','bj','bank journal','bnk jrnl'{Style.reset} - {expColor}View Cash changes Logs {Fore.orange_red_1}using CashPool{Style.reset}
{cmdColor2}'vjp','view journal paged','vwjrnlpgd','bjp','bank journal paged','bnk jrnl pgd'{Style.reset} - {expColor}View Cash Pool changes Logs with user interupts {Fore.orange_red_1}using CashPool{Style.reset}
{cmdColor2}'ncpi','new cashpool item'{Style.reset} - {expColor}make a new cashpool item/currency to use{Style.reset}
{cmdColor2}'sjs','show journals'{Style.reset} - {expColor}search and show journals {Fore.orange_red_1}using CashPoolJournals{Style.reset}
{cmdColor2}'sjsp','show journals paged'{Style.reset} - {expColor}search and show journals with user interupts and the option to delete the presently display journal entry {Fore.orange_red_1}using CashPoolJournals{Style.reset}
{'.'*20}
{self.billTotal()}
{'.'*20}
{Fore.light_green}Paid -> {Fore.grey_66}Amount of $ Paid out of total bills
{Fore.light_yellow}Un-Paid -> {Fore.grey_66}Amount of $ that has not been paid towards Bill Total
{Fore.orange_red_1}Bill Total -> {Fore.grey_66}Amount of $ that is the Total Bill, not accounting for
if the bill has been paid or not
{'.'*20}{Style.reset}
				'''
				fieldname='Menu'
				mode='BnC'
				h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
				doWhat=Prompt.__init2__(None,func=self.mkTextLower,ptext=f"{self.cashpoolTotal()}{self.billTotal()}{h}Do What ",helpText=helpText,data=self)
				if doWhat in [None,]:
					return
				elif doWhat in ['init cashpool','init_cashpool']:
					self.icp()
				elif doWhat in ['ssxq','search set x qty','search_set_x_qty']:
					#set CashPool Qty for CashPool x found by search by prompt
					self.ssxq()
				elif doWhat in ['ecpid','edit by cpid','edit cpid','edit_cpid','edit_by_cpid']:
					self.ssxq(fieldname="CPID")
				elif doWhat in ['rmxq','remove x qty','remove_x_qty']:
					#set CashPool Qty for CashPool x found by search by prompt
					self.ssxq(delete=True)
				elif doWhat in ['rm_cpid','rm by cpid','rm cpid','rm_cpid','rm_by_cpid']:
					self.ssxq(fieldname="CPID",delete=True)
				elif doWhat in ['reset_cp_qty','rcpq']:
					self.reset_cp_qty()
				elif doWhat in ['soft_reset_cp']:
					self.soft_reset_cp()
				elif doWhat in ['hard_reset_all']:
					self.hard_reset()
				elif doWhat.lower() in ['tc','trip cost','trip_cost']:
					self.trip_cost()
				elif doWhat in ['summarize_cp','scp','onhand','on-hand','banked','how much do i have?']:
					self.summarize_cp()
				elif doWhat in ['nb','new bill','new_bill']:
					self.MakeNewBill()
				elif doWhat in ['cab','clear all bill','del all bill','dab','rm all bill','rab']:
					self.rab()
				elif doWhat in ['sab','show all bill','show_all_bill','show bill','s*b']:
					self.sab()
				elif doWhat in ['ssb','select show bill','select_show_bill']:
					self.selectAndShowbill()
				elif doWhat in ['saeb','select and edit bill','select_and_edit_bill','select&edit bill','s&eb']:
					self.selectAndShowbill(edit=True)
				elif doWhat in ['sarb','select and rm bill','select_and_rm_bill','select&rm bill','s&er']:
					self.selectAndShowbill(remove=True)
				elif doWhat in ['gc','gascost']:
					self.gascost()
				elif doWhat.lower() in ['vj','view journal','vwjrnl','bj','bank journal','bnk jrnl']:
					self.page_journal(page=False)
				elif doWhat.lower() in ['vjp','view journal paged','vwjrnlpgd','bjp','bank journal paged','bnk jrnl pgd']:
					self.page_journal(page=True)
				elif doWhat.lower() in ['ncpi','new cashpool item']:
					self.newCashPoolItem()
				elif doWhat.lower() in [ 'sjs','show journals']:
					self.showJournals(page=False)
				elif doWhat.lower() in [ 'sjsp','show journals paged']:
					self.showJournals(page=True)
			except Exception as e:
				print(e)
	mod=f"{'_'*round(os.get_terminal_size().columns*0.8)}"
	def sab(self):
		with Session(ENGINE) as session:
			query=session.query(Bill)
			ct=len(query.all())
			if ct < 1:
				print(f"{Fore.light_red}No Bills Here!{Style.reset}")
				return
			results=query.all()
			
			header=f"{Fore.light_green}number/{Fore.light_yellow}of -> {Fore.dark_goldenrod}Name|{Fore.light_red}Value|{Fore.grey_50}Qty|{Fore.orange_red_1}DueDate|{Fore.light_sea_green}DatePaid|{Fore.yellow}BID{Style.reset}"
			print(header,self.mod,sep="\n")
			for num,r in enumerate(results):
				msg=f'''{Fore.light_green}{num+1}/{Fore.light_yellow}{ct} -> {Fore.dark_goldenrod}{r.Name}|{Fore.light_red}${r.Value}|{Fore.grey_50}{r.Qty}|{Fore.orange_red_1}{r.DueDate}|{Fore.light_sea_green}{r.DatePaid}|{Fore.yellow}{r.BID}{Style.reset}'''
				print(msg)
			print(self.mod,header,sep="\n")


	def selectAndShowbill(self,remove=False,edit=False):
		with Session(ENGINE) as session:
			query=session.query(Bill)
			what=Prompt.__init2__(self,func=self.mkText,ptext=f"{self.billTotal()}Bill Search?",helpText=f"type a search value for BID,Name, or Value",data={'default':0})
			if what in [None,]:
				return
			
			bid=0
			value=0

			try:
				value=float(value)
			except Exception as e:
				print(e)

			try:
				bid=int(value)
			except Exception as e:
				print(e)

			query=query.filter(or_(Bill.Name.icontains(what),Bill.BID==bid,Bill.Value==value))
			ct=len(query.all())
			if ct < 1:
				print(f"{Fore.light_red}No Bills Here!{Style.reset}")
				return
			results=query.all()
			
			header=f"{Fore.light_green}select number/{Fore.light_yellow}Total -> {Fore.dark_goldenrod}Name|{Fore.light_red}Value|{Fore.grey_50}Qty|{Fore.orange_red_1}DueDate|{Fore.light_sea_green}DatePaid|{Fore.yellow}BID{Style.reset}"
			print(header,self.mod,sep="\n")
			for num,r in enumerate(results):
				msg=f'''{Fore.light_green}{num}/{Fore.light_yellow}{ct} -> {Fore.dark_goldenrod}{r.Name}|{Fore.light_red}${r.Value}|{Fore.grey_50}{r.Qty}|{Fore.orange_red_1}{r.DueDate}|{Fore.light_sea_green}{r.DatePaid}|{Fore.yellow}{r.BID}{Style.reset}'''
				print(msg)
			print(self.mod,header,sep="\n")
			while True:
				try:
					which=Prompt.__init2__(self,func=self.mkint,ptext=f"{self.billTotal()}Which Bill?",helpText=f"type a number between [0-{ct-1}]",data={'default':0})
					if which in [None,]:
						return
					if remove:
						session.delete(results[which])
						session.commit()
					elif edit:
						update_data={i.name:getattr(results[which],i.name) for i in Bill.__table__.columns}
						update_data.pop('BID')
						nb=self.newBill(data=update_data)
						if not nb:
							return
						for k in nb:
							setattr(results[which],k,nb[k])
						session.commit()
						session.refresh(results[which])
					print(results[which])

					break
				except Exception as e:
					print(e)
	
	def billTotal(self):
		with Session(ENGINE) as session:
			query=session.query(Bill)
			paid=query.filter(Bill.DatePaid!=None)
			paid_ct=len(paid.all())
			paid_total=0
			for i in paid.all():
				paid_total+=(i.Value*i.Qty)
			unpaid=query.filter(Bill.DatePaid==None)
			unpaid_ct=len(unpaid.all())
			unpaid_total=0
			for i in unpaid.all():
				unpaid_total+=(i.Value*i.Qty)
			total=0
			for i in query.all():
				total+=(i.Value*i.Qty)
			msg=f'{Fore.light_steel_blue}Bill({Fore.light_green}Paid:${paid_total}|{Fore.light_yellow}Un-Paid:${unpaid_total}/{Fore.orange_red_1}Bill Total:${total}{Fore.light_steel_blue}){Style.reset}\n'
			return msg

	def selectAndEditBill(self):
		pass

	def gascost(self):
		tip_percent=25/100
		miles_to_gallon_decimal=1/32
		days_scheduled=5
		miles_traveled=7.7
		top_gas_price_in_area=5.5
		#days not scehduled
		non_epf=5
		non_mpf=0
		#custom pickup fee morning
		cpfm=2
		#custom pickup fee evening
		cpfe=2
		epf,mpf=(cpfe*(days_scheduled-non_epf)),(cpfm*(days_scheduled-non_mpf))
		#non_epf and non_mpf are days not picked up for subtraction from days scheduled
		#$extras are +='ed to formula so the following fees need to calculated before being used in $extras
		h=f'''
		'morning pickup fee' - "${cpfm}/day for ${mpf} for each morning pickup of days scheduled ={days_scheduled-non_mpf}"
		'evening pickup fee' - "${cpfe}/day for ${epf} for each evening pickup of days scheduled ={days_scheduled-non_epf}"
		'''
		print(h)
		def rideCost(tip_percent,miles_to_gallon_decimal,days_scheduled,miles_traveled,top_gas_price_in_area,extras={"morning pickup fee":mpf,"evening pickup fee":epf}):
			print(f"Top Gas Price: ${top_gas_price_in_area}")
			print(f"Miles To Gallon: {miles_to_gallon_decimal}")
			print(f"Miles Traveled: {miles_traveled}")
			print(f"Tip Percent: {round(tip_percent*100)}%")
			print(f"Days Scheduled: {days_scheduled}")
			print("formula=top_gas_price_in_area*(miles_traveled*miles_to_gallon_decimal)")
			print(f"No Tip | formula={top_gas_price_in_area}*({miles_traveled}*{miles_to_gallon_decimal})\n")
			formula=top_gas_price_in_area*(miles_traveled*miles_to_gallon_decimal)
			print(f"Add TIP | formula={formula}+({tip_percent}*{formula}")
			print("formula=formula+(tip_percent*formula)\n")
			formula=formula+(tip_percent*formula)
			print(f"For X Days | formula={formula}*={days_scheduled}")
			print("formula*=days_scheduled\n")
			formula*=days_scheduled
			print(f"Round to 3 Decimal Places | formula=round({formula},3)")
			print("formula=round(formula,3)\n")
			formula=round(formula,3)
			
			print("Extra Fees")
			for e in extras:
				try:
					formula+=float(extras.get(e))
					print(f"{formula}+={float(extras.get(e))}")
					print(f"formula+=float({e})\n")
				except Exception as ee:
					print(ee,f"Could not add extra '{e}'")
			print(f"Total $cost | formula=${formula}")
			return formula

		cost=rideCost(tip_percent,miles_to_gallon_decimal,days_scheduled,miles_traveled,top_gas_price_in_area)

	def mkFloat(self,text,default):
		try:
			if text in '':
				return default.get("default")
			else:
				tmp=0
				nxt=False
				try:
					tmp=float(text)
				except Exception as e:
					nxt=True
					print(e)
				if nxt:
					try:
						tmp=float(eval(text))
					except Exception as e:
						print(e)
						return default.get("default")
				return tmp
		except Exception as e:
			print(e)

	def mkInt(self,text,default):
		try:
			if text in '':
				return default.get("default")
			else:
				tmp=0
				nxt=False
				try:
					tmp=int(text)
				except Exception as e:
					nxt=True
					print(e)
				if nxt:
					try:
						tmp=int(eval(text))
					except Exception as e:
						print(e)
						return default.get("default")
				return tmp
		except Exception as e:
			print(e)

	def gascost(self):
		print(f"{Fore.light_yellow}{Style.underline}Pre-Calculate a Ride-Share Cost for Non-Uber/Non-Lyft of Personal Design{Style.reset}")
		default={"default":25}
		tip_percent=Prompt.__init2__(None,func=self.mkFloat,ptext=f"[{default}] Tip Percent",helpText="Tip Percent",data=default)
		if tip_percent in [None,]:
			return
		else:
			tip_percent=tip_percent/100
		default={"default":32}
		miles_to_gallon_decimal=Prompt.__init2__(None,func=self.mkFloat,ptext=f"[{default}] Miles To Gallon",helpText="Miles To Gallon",data=default)
		if miles_to_gallon_decimal in [None,]:
			return
		else:
			miles_to_gallon_decimal=1/miles_to_gallon_decimal

		default={"default":5}
		days_scheduled=Prompt.__init2__(None,func=self.mkInt,ptext=f"[{default}] Days Scheduled",helpText="Days Scheduled",data=default)
		if days_scheduled in [None,]:
			return

		
		default={"default":7.7}
		miles_traveled=Prompt.__init2__(None,func=self.mkFloat,ptext=f"[{default}] miles_traveled",helpText="miles_traveled",data=default)
		if miles_traveled in [None,]:
			return
		
		default={"default":5.5}
		top_gas_price_in_area=Prompt.__init2__(None,func=self.mkFloat,ptext=f"[{default}] top_gas_price_in_area",helpText="top_gas_price_in_area",data=default)
		if top_gas_price_in_area in [None,]:
			return
		#days not scehduled

		default={"default":0}
		non_epf=Prompt.__init2__(None,func=self.mkInt,ptext=f"[{default}] Days Not Schedule for Evening Pickup",helpText="Days Not Schedule for Evening Pickup",data=default)
		if non_epf in [None,]:
			return
		
		default={"default":0}
		non_mpf=Prompt.__init2__(None,func=self.mkInt,ptext=f"[{default}] Days Not Schedule for Morning Pickup",helpText="Days Not Schedule for Morning Pickup",data=default)
		if non_mpf in [None,]:
			return
		#custom pickup fee morning

		default={"default":2}
		cpfm=Prompt.__init2__(None,func=self.mkInt,ptext=f"[{default}] Morning Pickup Fee?",helpText="Morning Pickup Fee?",data=default)
		if cpfm in [None,]:
			return
		#custom pickup fee evening
		default={"default":2}
		cpfe=Prompt.__init2__(None,func=self.mkInt,ptext=f"[{default}] Evening Pickup Fee?",helpText="Evening Pickup Fee?",data=default)
		if cpfe in [None,]:
			return

		epf,mpf=(cpfe*(days_scheduled-non_epf)),(cpfm*(days_scheduled-non_mpf))
		#hourly fee settings
		default={"default":25.38}
		rate=Prompt.__init2__(None,func=self.mkInt,ptext=f"[{default}] Hourly Rate To Compensate for time used?",helpText="Hourly Rate To Compensate for time used?",data=default)
		if rate in [None,]:
			return
		default={"default":15}
		time_consumed=Prompt.__init2__(None,func=self.mkInt,ptext=f"[{default}] How long in minutes did the ride take/will take?",helpText="How long in minutes did the ride take/will take?",data=default)
		if time_consumed in [None,]:
			return
		time_consumed=(time_consumed*days_scheduled)/60
		hourly=rate*time_consumed
		#non_epf and non_mpf are days not picked up for subtraction from days scheduled
		#$extras are +='ed to formula so the following fees need to calculated before being used in $extras
		h=f'''
{Fore.light_steel_blue}{Style.bold}Extras Info.\n{'.'*len('Extras Info.')}{Style.reset}
'{Fore.dark_goldenrod}morning pickup fee{Style.reset}' - "{Fore.light_green}${cpfm}/day for ${mpf} for each morning pickup of days scheduled ={days_scheduled-non_mpf}{Style.reset}"
'{Fore.dark_goldenrod}evening pickup fee{Style.reset}' - "{Fore.light_green}${cpfe}/day for ${epf} for each evening pickup of days scheduled ={days_scheduled-non_epf}{Style.reset}"
'{Fore.dark_goldenrod}time_consumed fee{Style.reset}' - "{Fore.light_green}${round(hourly,2)} for time ({time_consumed} Hours) taken to make trip as ${rate}/Hour{Style.reset}"

{Fore.light_steel_blue}{Style.bold}Calculated as\n{'.'*len('Calculated as')}{Style.reset}'''
		print(h)
		def rideCost(tip_percent,miles_to_gallon_decimal,days_scheduled,miles_traveled,top_gas_price_in_area,extras={"time_consumed fee":hourly,"morning pickup fee":mpf,"evening pickup fee":epf}):
			print(f"\t{Fore.dark_goldenrod}Top Gas Price:{Fore.light_green} ${top_gas_price_in_area}{Style.reset}")
			print(f"\t{Fore.dark_goldenrod}Miles To Gallon:{Fore.light_green} {miles_to_gallon_decimal}{Style.reset}")
			print(f"\t{Fore.dark_goldenrod}Miles Traveled:{Fore.light_green} {miles_traveled}{Style.reset}")
			print(f"\t{Fore.dark_goldenrod}Tip Percent:{Fore.light_green} {round(tip_percent*100)}%{Style.reset}")
			print(f"\t{Fore.dark_goldenrod}Days Scheduled:{Fore.light_green} {days_scheduled}{Style.reset}")
			print(f"\t{Fore.dark_goldenrod}formula={Fore.light_green}top_gas_price_in_area*(miles_traveled*miles_to_gallon_decimal){Style.reset}")
			print(f"\t{Fore.dark_goldenrod}No Tip | formula={Fore.light_green}{top_gas_price_in_area}*({miles_traveled}*{miles_to_gallon_decimal})\n{Style.reset}")
			formula=top_gas_price_in_area*(miles_traveled*miles_to_gallon_decimal)
			print(f"\t{Fore.dark_goldenrod}Add TIP | formula={Fore.light_green}{formula}+({tip_percent}*{formula}{Style.reset}")
			print(f"\t{Fore.dark_goldenrod}formula={Fore.light_green}formula+(tip_percent*formula)\n{Style.reset}")
			formula=formula+(tip_percent*formula)
			print(f"\t{Fore.dark_goldenrod}For X Days | formula={Fore.light_green}{formula}*={days_scheduled}{Style.reset}")
			print(f"\t{Fore.dark_goldenrod}formula*={Fore.light_green}days_scheduled\n{Style.reset}")
			formula*=days_scheduled
			print(f"\t{Fore.dark_goldenrod}Round to 2 Decimal Places | formula=round({formula},2)")
			print(f"\t{Fore.dark_goldenrod}formula={Fore.light_green}round(formula,2)\n{Style.reset}")
			
			formula=round(formula,2)
			print(f"{Fore.light_steel_blue}{Style.bold}Extra Fees\n{'.'*len('Extra Fees')}{Style.reset}")
			for e in extras:
				try:
					
					formula+=float(extras[e])
					formula=round(formula,2)
					print(f"\t{Fore.dark_goldenrod}{formula}+={Fore.light_green}{round(float(extras[e]),2)}{Style.reset}")
					print(f"\t{Fore.dark_goldenrod}formula+={Fore.light_green}round(float({e}),2)\n{Style.reset}")
				except Exception as ee:
					print(ee,f"Could not add extra '{e}'")
			formula=round(formula,2)
			print(f"{Fore.dark_goldenrod}Total $cost | formula={Fore.light_green}${formula} [Rounded to 2 Places]{Style.reset}")
			return formula

		cost=rideCost(tip_percent,miles_to_gallon_decimal,days_scheduled,miles_traveled,top_gas_price_in_area)
		return cost

	def MakeNewBill(self):
		nb=self.newBill()
		if not nb:
			return
		with Session(ENGINE) as session:
			NB=Bill(**nb)
			session.add(NB)
			session.commit()
			session.refresh(NB)
			print(f"{Fore.light_green}Created!{Style.reset} {NB}")



	def rab(self):
		with Session(ENGINE) as session:
			query=session.query(Bill)
			total=len(query.all())
			query.delete()
			session.commit()
			session.flush()
			print(f"{Fore.light_red}Deleted {Fore.light_steel_blue}{total}{Fore.light_red} Bill Items!")
