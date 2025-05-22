from radboy.DB.db import *
from radboy.DB.RandomStringUtil import *
import radboy.Unified.Unified as unified
import radboy.possibleCode as pc
from radboy.DB.Prompt import *
from radboy.DB.Prompt import prefix_text
from radboy.TasksMode.ReFormula import *
from radboy.TasksMode.SetEntryNEU import *
from radboy.FB.FormBuilder import *
from radboy.FB.FBMTXT import *
from radboy.RNE.RNE import *
from radboy.Lookup2.Lookup2 import Lookup as Lookup2
from radboy.DayLog.DayLogger import *
from radboy.DB.masterLookup import *
from collections import namedtuple,OrderedDict
import nanoid,qrcode,io
from password_generator import PasswordGenerator
import random
from pint import UnitRegistry
import pandas as pd
import numpy as np
from datetime import *
from colored import Style,Fore
import json,sys,math,re,calendar

class HealthLogUi:
	def new_health_log(self):
		with Session(ENGINE) as session:
			hl=HealthLog()
			excludes=['HLID','DTOE',]
			def retVal(i):
				if i == None:
					return None
				else:
					return i.arg
			fields={
			str(i.name):{
				'default':retVal(i.default),
				'type':str(i.type).lower(),
				} for i in hl.__table__.columns if str(i.name) not in excludes
			}
			data=FormBuilder(data=fields)
			if data in [None,]:
				return
			for i in data:
				setattr(hl,i,data[i])
			session.add(hl)
			session.commit()
			session.refresh(hl)
			print(hl)

	def add_healthlog_specific(self,useColumns=[]):
		if 'Comments' not in useColumns:
			useColumns.append('Comments')
		excludes=['HLID','DTOE',]
		barcode=''
		with Session(ENGINE) as session:
			entry=None
			if 'EntryBarcode' in useColumns:
				h=f'{Fore.light_red}HealthLog{Fore.light_yellow}@{Style.bold}{Fore.deep_sky_blue_3b}AHS{Fore.light_yellow} : '
				barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h}Barcode|Code|Name: ",helpText="what was consumed?",data="string")
				if barcode not in [None,]:
					while True:
						try:
							entry=session.query(Entry).filter(or_(Entry.Barcode==barcode,Entry.Barcode.icontains(barcode),Entry.Name.icontains(barcode),Entry.Code==barcode,Entry.Code.icontains(barcode))).all()
							ct=len(entry)
							if ct >= 0:
								for num, i in enumerate(entry):
									msg=f"{Fore.light_red}{num}/{Fore.medium_violet_red}{num+1} of {Fore.light_sea_green}{ct} -> {i.seeShort()}"
									print(msg)
								which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Which {Fore.light_red}index?{Fore.light_yellow}",helpText=f"{Fore.light_red}number{Fore.light_yellow} farthest to left of screen{Style.reset}",data="integer")
								if which not in [None,]:
									excludes.extend(["EntryBarcode","EntryName","EntryId"])
									if which == 'd':
										entry=entry[0]
									else:
										entry=entry[which]
								else:
									entry=None
									break
							break
						except Exception as e:
							print(e)

			hl=HealthLog()
			
			def retVal(i):
				if i == None:
					return None
				else:
					return i.arg
			fields={
			str(i.name):{
				'default':retVal(i.default),
				'type':str(i.type).lower(),
				} for i in hl.__table__.columns if str(i.name) not in excludes and str(i.name) in useColumns
			}
			if fields in [{},None]:
				print(fields,"empty!")
				return
			data=FormBuilder(data=fields)
			if 'LongActingInsulinName' in useColumns or 'ShortActingInsulinName' in useColumns:
				def searchNames(code):
					with Session(ENGINE) as session:
						query=session.query(Entry)
						filters=[
							Entry.Barcode.icontains(code),
							Entry.Code.icontains(code),
							Entry.Name.icontains(code)
						]
						results=query.filter(or_(*filters)).all()
						ct=len(results)
						if ct == 0:
							msg=f"{Fore.orange_red_1}Nothing was found to match {Fore.grey_15}'{code}'{Style.reset}"
							print(msg)
							return code
						htext=[]
						for num,i in enumerate(results):
							msg=f"{Fore.light_cyan}{num}/{Fore.light_magenta}{num+1} of {Fore.light_red}{ct} {Fore.medium_violet_red} -> {i.seeShort()}"
							htext.append(msg)
						htext='\n'.join(htext)
						while True:
							try:
								print(htext)
								which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Which {Fore.light_cyan}index{Fore.light_yellow}?",helpText=htext+f"\n Pick a {Fore.light_cyan}number in this color{Fore.light_yellow}. Back keeps original {Fore.grey_15}{code}{Fore.light_yellow}",data="integer")
								if which in [None,]:
									return code
								elif which in ['d',]:
									which=0
									out=f"'Name':'{results[which].Name}','BARCODE':'{results[which].Barcode}','Code':'{results[which].Code}'"
									out="{"+out+"}"
									return out
								else:
									out=f"'Name':'{results[which].Name}','BARCODE':'{results[which].Barcode}','Code':'{results[which].Code}'"
									out="{"+out+"}"
									return out
							except Exception as e:
								print(e)
								return code
				if 'LongActingInsulinName' in useColumns:
					data['LongActingInsulinName']=searchNames(data['LongActingInsulinName'])
				elif 'ShortActingInsulinName' in useColumns:
					data['ShortActingInsulinName']=searchNames(data['ShortActingInsulinName'])
				else:
					print("You Should not be having 'ShortActingInsulinName and LongActingInsulinName in add_healthlog_specific(useColumns)!")
					return
				'''search for name in entry and auto replace name'''

			if 'EntryBarcode' in useColumns and entry != None:
				data['EntryBarcode']=entry.Barcode
				data['EntryName']=entry.Name
				data['EntryId']=entry.EntryId

			if data in [None,]:
				return
			for i in data:
				setattr(hl,i,data[i])
			session.add(hl)
			session.commit()
			session.refresh(hl)
			print(f"{Fore.light_steel_blue}HLID={Fore.light_green}{hl.HLID}{Fore.light_steel_blue}/"+f"{Style.reset}{Fore.medium_violet_red}|{Fore.light_steel_blue}".join([f'{i}' for i in useColumns])+f"{Style.reset}")
			print(f"{Fore.light_steel_blue}HLID={Fore.light_green}{hl.HLID}{Fore.light_steel_blue}/"+f'{Style.reset}{Fore.medium_violet_red}|{Fore.light_steel_blue}'.join(str(getattr(hl,i)) for i in useColumns)+f"{Style.reset}")
	
	def del_hlid(self):
		try:
			with Session(ENGINE) as session:
				h=f"{Fore.light_red}HealthLog{Fore.light_yellow}@{Style.bold}{Fore.deep_sky_blue_3b}DEL{Fore.light_yellow} : "
				HLID_=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h}HLID to delete?",helpText="what id do you wish to delete, or list of ids",data="list")
				if HLID_ in [None,'d']:
					return
				for HLID in HLID_:
					try:
						HLID=int(HLID)
						x=session.query(HealthLog).filter(HealthLog.HLID==HLID).delete()
						session.commit()
						session.flush()
						x=session.query(HealthLog).filter(HealthLog.HLID==HLID).all()
					except Exception as e:
						print(e)
				print(len(x),"IDS remains!")
		except Exception as e:
			print(e)

	def showAll(self):
		try:
			with Session(ENGINE) as session:
				results=session.query(HealthLog).order_by(HealthLog.DTOE.asc()).all()
				ct=len(results)
				for num,i in enumerate(results):
					view=[]
					for x in i.__table__.columns:
						if getattr(i,str(x.name)) not in [None]:
							view.append(f'{Fore.green_3b}{Style.bold}{str(x.name)}{Fore.deep_sky_blue_1}={Fore.sea_green_2}{str(getattr(i,str(x.name)))}{Style.reset}')
					msg=f"{Fore.light_green}{num}{Fore.light_yellow}/{num+1} of {Fore.light_red}{ct} ->{'|'.join(view)}"
					print(msg)
		except Exception as e:
			print(e)

	def export_log(self):
		output=Path("HealthLogAll.xlsx")
		with Session(ENGINE) as session:
			query=session.query(HealthLog)
			df=pd.read_sql(query.statement,session.bind)
			df.to_excel(output,index=False)
			print(output.absolute())

	def export_log_field(self,fields=[],not_none=[]):
		if 'DTOE' not in fields:
			fields.append('DTOE')
		if 'Comments' not in fields:
			fields.append('Comments')
		output=Path(f"HealthLog-{'_'.join(fields)}.xlsx")
		not_none=[i for i in HealthLog.__table__.columns if str(i.name) in not_none]
		with Session(ENGINE) as session:
			query=session.query(HealthLog).filter(or_(*[i!=None for i in not_none]))
			df=pd.read_sql(query.statement,session.bind)
			df=df[fields]
			df.to_excel(output,index=False)
			print(output.absolute())


	def fixtable(self):
		HealthLog.__table__.drop(ENGINE)
		HealthLog.metadata.create_all(ENGINE)

	def showAllField(self,fields=[],not_none=[]):
		try:
			fields.extend(["DTOE","HLID","Comments"])
			fields=[i for i in HealthLog.__table__.columns if str(i.name) in fields]
			not_none=[i for i in HealthLog.__table__.columns if str(i.name) in not_none]
			with Session(ENGINE) as session:
				results=session.query(HealthLog).filter(or_(*[i!=None for i in not_none])).order_by(HealthLog.DTOE.asc()).all()
				ct=len(results)
				for num,i in enumerate(results):
					view=[]
					for x in fields:
						if getattr(i,str(x.name)) == None:
							color=f"{Fore.grey_15}"
							color_date=f"{Fore.grey_15}"
						else:
							color=f"{Fore.sea_green_2}"
							color_date=f"{Fore.green_3b}"
						view.append(f'{color_date}{Style.bold}{str(x.name)}{Fore.deep_sky_blue_1}={color}{str(getattr(i,str(x.name)))}{Style.reset}')
					msg=f"{Fore.light_green}{num}{Fore.light_yellow}/{num+1} of {Fore.light_red}{ct} ->{'|'.join(view)}"
					print(msg)
		except Exception as e:
			print(e)

	def __init__(self):
		#this cmd extension format is so later i can add a findcmd equivalent here as well
		self.cmds={
			'fix table':{
			'cmds':['fix table','fixtable','fxtbl'],
			'desc':'Drop table and all data in table and regenerate new table; most useful when a new column is added/removed',
			'exec':self.fixtable
			},
			'export all':{
			'cmds':['xpt all','export all','xpta'],
			'desc':'Export HealthLog to excel',
			'exec':self.export_log
			},
			'nhl all':{
			'cmds':['nhla','nhl all','nhla','new health log all','new healthlog all','new healthlogall','newhealthlogall','newhealthlog all'],
			'desc':'Create a NEW HealthLog with ALL fields available',
			'exec':self.new_health_log
			},
			'add blood sugar':{
			'cmds':['abs','add bld sgr','add blood sugar','+bs','+bg','add bld glcs','add blood glucose','ad bld glcs'],
			'desc':'Create a NEW HealthLog for JUST Blood Sugar/Glucose Levels',
			'exec':lambda self=self:self.add_healthlog_specific(useColumns=['BloodSugar','BloodSugarUnitName'])
			},
			'add short insulin':{
			'cmds':['asai','add short acting insulin','add short insulin',],
			'desc':'Create a NEW HealthLog for JUST Short Acting Insulin Intake',
			'exec':lambda self=self:self.add_healthlog_specific(useColumns=['ShortActingInsulinName','ShortActingInsulinTaken','ShortActingInsulinUnitName'])
			},
			'add long insulin':{
			'cmds':['alai','add long acting insulin','add long insulin',],
			'desc':'Create a NEW HealthLog for JUST long Acting Insulin Intake',
			'exec':lambda self=self:self.add_healthlog_specific(useColumns=['LongActingInsulinName','LongActingInsulinTaken','LongActingInsulinUnitName'])
			},
			'add hr':{
			'cmds':['ahr','add heart rate','add hrt rt',],
			'desc':'Create a NEW HealthLog for JUST Heart Rate',
			'exec':lambda self=self:self.add_healthlog_specific(useColumns=['HeartRate','HeartRateUnitName'])
			},
			'show all':{
			'cmds':['sa','show all','showall',],
			'desc':'Show all HealthLogs',
			'exec':self.showAll
			},
			'add height':{
			'cmds':['aht','add height','add ht',],
			'desc':'Create a NEW HealthLog for JUST Height',
			'exec':lambda self=self:self.add_healthlog_specific(useColumns=['Height','HeightUnitName'])
			},
			'add weight':{
			'cmds':['awt','add weight','add wt',],
			'desc':'Create a NEW HealthLog for JUST Weight',
			'exec':lambda self=self:self.add_healthlog_specific(useColumns=['Weight','WeightUnitName'])
			},
			'add consumed':{
				'cmds':['afd','add fd','add food','adfd','add fuel','ad fl','afl'],
				'desc':'Create a NEW HealthLog for JUST Weight',
				'exec':lambda self=self:self.add_healthlog_specific(
					useColumns=["EntryBarcode",
								"EntryName",
								"CarboHydrateIntake",
								"CarboHydrateIntakeUnitName",
								"ProtienIntake",
								"ProtienIntakeUnitName",
								"FiberIntake",
								"FiberIntakeUnitName",
								"TotalFat",
								"TotalFatUnitName",
								"SodiumIntake",
								"SodiumIntakeUnitName",
								"CholesterolIntake",
								"CholesterolIntakeUnitName",])
			},
			'del hlid':{
			'cmds':['del','del hlid','rm','rm hlid'],
			'desc':'Delete a healthlog entry',
			'exec':self.del_hlid
			},
			'lsbs':{
			'cmds':['ls bs','lsbs','list blood sugars'],
			'desc':'list blood sugars',
			'exec':lambda self=self:self.showAllField(fields=['BloodSugar','BloodSugarUnitName'],not_none=['BloodSugar',])
			},
			'lsdrug':{
			'cmds':['ls drug','ls dg','list drug','lsdrug','lsdrg'],
			'desc':'list drug data',
			'exec':lambda self=self:self.showAllField(fields=['DrugConsumed','DrugQtyConsumed','DrugQtyConsumedUnitName'],not_none=['DrugQtyConsumed',])
			},
			'xpt drug':{
			'cmds':['xpt drug','xpt dg','export drug','xptdrug','xptdrg'],
			'desc':'export drug data to excel',
			'exec':lambda self=self:self.export_log_field(fields=['DrugConsumed','DrugQtyConsumed','DrugQtyConsumedUnitName'],not_none=['DrugQtyConsumed',])
			},
			'add drug':{
			'cmds':['adrg','add drug','add drg','adddrug','adrug'],
			'desc':'Add a new drug consumption entry',
			'exec':lambda self=self:self.add_healthlog_specific(useColumns=['DrugConsumed','DrugQtyConsumed','DrugQtyConsumedUnitName'])
			},
			'ls lai':{
			'cmds':['ls lai','lslai','list long insulin','list long acting insulin'],
			'desc':'list long acting insulin intake',
			'exec':lambda self=self:self.showAllField(fields=['LongActingInsulinName','LongActingInsulinTaken','LongActingInsulinUnitName'],not_none=['LongActingInsulinTaken',])
			},
			'ls sai':{
			'cmds':['ls sai','lssai','list short insulin','list short acting insulin'],
			'desc':'list long acting insulin intake',
			'exec':lambda self=self:self.showAllField(fields=['ShortActingInsulinName','ShortActingInsulinTaken','ShortActingInsulinUnitName'],not_none=['ShortActingInsulinTaken',])
			},
			'ls heart rate':{
			'cmds':['lshr','ls heart rate','ls hrt rt'],
			'desc':'list heart rate',
			'exec':lambda self=self:self.showAllField(fields=['HeartRate','HeartRateUnitName'],not_none=['HeartRate',])
			},
			'ls weight':{
			'cmds':['lswt','ls weight','ls wt',],
			'desc':'list weight',
			'exec':lambda self=self:self.showAllField(fields=['Weight','WeightUnitName'],not_none=['Weight',])
			},
			'ls height':{
			'cmds':['lsht','ls height','ls ht',],
			'desc':'list height',
			'exec':lambda self=self:self.showAllField(fields=['Height','HeightUnitName'],not_none=['Height',])
			},
			'ls consumed':{
				'cmds':['lsfd','ls fd','ls food','lfd','ls fuel','ls fl','lfl'],
				'desc':'list food',
				'exec':lambda self=self:self.showAllField(
					fields=["EntryBarcode",
								"EntryName",
								"CarboHydrateIntake",
								"CarboHydrateIntakeUnitName",
								"ProtienIntake",
								"ProtienIntakeUnitName",
								"FiberIntake",
								"FiberIntakeUnitName",
								"TotalFat",
								"TotalFatUnitName",
								"SodiumIntake",
								"SodiumIntakeUnitName",
								"CholesterolIntake",
								"CholesterolIntakeUnitName",],
								not_none=[
								"CarboHydrateIntake",
								"ProtienIntake",
								"FiberIntake",
								"TotalFat",
								"SodiumIntake",
								"CholesterolIntake",
								]
								)
			},
			'xptbs':{
			'cmds':['xpt bs','xptbs','export blood sugars'],
			'desc':'export blood sugars',
			'exec':lambda self=self:self.export_log_field(fields=['BloodSugar','BloodSugarUnitName'],not_none=['BloodSugar',])
			},
			'xpt lai':{
			'cmds':['xpt lai','xptlai','export long insulin','export long acting insulin'],
			'desc':'export long acting insulin intake',
			'exec':lambda self=self:self.export_log_field(fields=['LongActingInsulinName','LongActingInsulinTaken','LongActingInsulinUnitName'],not_none=['LongActingInsulinTaken',])
			},
			'xpt sai':{
			'cmds':['xpt sai','xptsai','export short insulin','export short acting insulin'],
			'desc':'export long acting insulin intake',
			'exec':lambda self=self:self.export_log_field(fields=['ShortActingInsulinName','ShortActingInsulinTaken','ShortActingInsulinUnitName'],not_none=['ShortActingInsulinTaken',])
			},
			'xpt heart rate':{
			'cmds':['xpthr','xpt heart rate','xpt hrt rt'],
			'desc':'export heart rate',
			'exec':lambda self=self:self.export_log_field(fields=['HeartRate','HeartRateUnitName'],not_none=['HeartRate',])
			},
			'xpt weight':{
			'cmds':['xptwt','xpt weight','xpt wt',],
			'desc':'export weight',
			'exec':lambda self=self:self.export_log_field(fields=['Weight','WeightUnitName'],not_none=['Weight',])
			},
			'xpt height':{
			'cmds':['xptht','xpt height','xpt ht',],
			'desc':'export height',
			'exec':lambda self=self:self.export_log_field(fields=['Height','HeightUnitName'],not_none=['Height',])
			},
			'xpt consumed':{
				'cmds':['xptfd','xpt fd','xpt food','lfd','xpt fuel','xpt fl','xlfl'],
				'desc':'export food',
				'exec':lambda self=self:self.export_log_field(
					fields=["EntryBarcode",
								"EntryName",
								"CarboHydrateIntake",
								"CarboHydrateIntakeUnitName",
								"ProtienIntake",
								"ProtienIntakeUnitName",
								"FiberIntake",
								"FiberIntakeUnitName",
								"TotalFat",
								"TotalFatUnitName",
								"SodiumIntake",
								"SodiumIntakeUnitName",
								"CholesterolIntake",
								"CholesterolIntakeUnitName",],
								not_none=[
								"CarboHydrateIntake",
								"ProtienIntake",
								"FiberIntake",
								"TotalFat",
								"SodiumIntake",
								"CholesterolIntake",]
								)
			},
		}
		helpText='\n'.join([
		'-'.join(
					[
						"* "+f"{Fore.light_sea_green}{f'{Fore.dark_goldenrod},{Style.reset}{Fore.light_sea_green}'.join(self.cmds[i]['cmds'])}{Style.reset}",
						f"{Fore.light_steel_blue}{self.cmds[i]['desc']}{Style.reset}",
					]
				) for i in self.cmds])
		while True:
			doWhat=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{Fore.light_red}HealthLog{Fore.light_yellow}@{Style.bold}{Fore.deep_sky_blue_3b}Menu{Fore.light_yellow} : Do What?",helpText=helpText,data="string")
			if doWhat not in [None,]:
				if doWhat.lower() in ['d',]:
					print(helpText)
					continue
				for i in self.cmds:
					if doWhat.lower() in  self.cmds[i]['cmds']:
						if callable(self.cmds[i]['exec']):
							self.cmds[i]['exec']()
			elif doWhat in [None,]:
				return

