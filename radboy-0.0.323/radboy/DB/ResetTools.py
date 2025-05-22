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
from radboy.ExtractPkg.ExtractPkg2 import *
from radboy.Lookup.Lookup import *
from radboy.DayLog.DayLogger import *
from radboy.DB.db import *
from radboy.DB.Prompt import *
from radboy.ConvertCode.ConvertCode import *
from radboy.setCode.setCode import *
from radboy.Locator.Locator import *
from radboy.ListMode2.ListMode2 import *
from radboy.TasksMode.Tasks import *
from radboy.Collector2.Collector2 import *
from radboy.LocationSequencer.LocationSequencer import *
from radboy.PunchCard.PunchCard import *
from radboy.Conversion.Conversion import *
from radboy.POS.POS import *
import radboy.possibleCode as pc
import radboy.Unified.Unified as unified


class ResetTools:
	def clearAllSelectedFieldValue(self):
		excludes=["EntryId","Timestamp"]
		fields=[str(i.name) for i in Entry.__table__.columns if str(i.type).lower() in ["integer","float"] and str(i.name) not in excludes]
		ct=len(fields)
		helpText=''
		for num,i in enumerate(fields):
			msg=f'''{num}/{num+1} of {ct} - {i}'''
			helpText+=msg+"\n"
			print(msg)
		which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Which index?",helpText=helpText,data="list")
		if which in [None,'d']:
			return
		else:
			updates={}
			try:
				for i in which:
					try:
						index=int(i)
						updates[fields[index]]=0
					except Exception as ee:
						print(ee)
			except Exception as e:
				print(e)
			with Session(ENGINE) as session:
				result=session.query(Entry).update(updates)
				session.commit()
				session.flush()

	def setSelectedField2Value(self):
		excludes=["EntryId","Timestamp"]
		fields=[str(i.name) for i in Entry.__table__.columns if str(i.type).lower() in ["integer","float"] and str(i.name) not in excludes]
		ct=len(fields)
		helpText=''
		for num,i in enumerate(fields):
			msg=f'''{num}/{num+1} of {ct} - {i}'''
			helpText+=msg+"\n"
			print(msg)
		which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Which index?",helpText=helpText,data="list")
		if which in [None,'d']:
			return
		else:
			updates={'InList':False}
			try:
				for i in which:
					try:
						index=int(i)
						updates[fields[index]]=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{fields[index]}[InList will be set to True if anything is >0] What New Value do you wish to use?",helpText="enter will use 0",data="integer")
						if updates[fields[index]] in [None,]:
							updates.pop(fields[index])
							continue
						elif updates[fields[index]] in ['d',]:
							updates[fields[index]]=1
						else:
							if updates[fields[index]] > 0:
								updates['InList']=True
					except Exception as ee:
						print(ee)
			except Exception as e:
				print(e)
			with Session(ENGINE) as session:
				result=session.query(Entry).update(updates)
				session.commit()
				session.flush()

	def __init__(self,engine,parent):
		self.parent=parent
		self.engine=engine

		def mkT(text,data):
			return text


		self.helpText=f'''
		{Fore.light_red}{Style.bold}factory_reset{Style.reset}{Fore.light_red} - {Fore.light_steel_blue}completely resets everything; best if used before updates{Style.reset}
		{Fore.light_red}iv0|int_val_0 - {Fore.light_steel_blue}sets all entry integer fields to 0{Style.reset}
		{Fore.light_red}rap|reset_all_prices - {Fore.light_steel_blue}sets all entry prices to 0{Style.reset}
		{Fore.light_red}rac|reset_all_codes - {Fore.light_steel_blue}sets all entry codes to ''{Style.reset}
		{Fore.light_red}rats|reset_all_time_stamps - {Fore.light_steel_blue}sets all timestamps to now{Style.reset}
		{Fore.light_red}sai0|reset_all_inlist0 - {Fore.light_salmon_1}set InList/ListQty to False/0 {Style.reset}
		{Fore.light_red}sai1|reset_all_inlist1 - {Fore.light_salmon_1}set InList/ListQty to True/1 {Style.reset}
		{Fore.light_red}sau0|reset_all_useruUpdated - {Fore.light_salmon_1}set userUpdated to False{Style.reset}
		{Fore.light_red}sau1|reset_all_useruUpdated - {Fore.light_salmon_1}set userUpdated to True{Style.reset}
		{Fore.light_red}ssf2v|set selected field 2 value - {Fore.light_salmon_1}set a selected integer only field to value{Style.reset}
		{Fore.light_red}casfv|clear all selected field value - {Fore.light_salmon_1}set a selected field to zero across all entry fields{Style.reset}
'''



		while True:
			cmd=Prompt.__init2__(None,func=mkT,ptext="Do What?",helpText=self.helpText)
			if cmd in [None,]:
				return
			elif isinstance(cmd,str):
				if cmd.lower() == 'factory_reset':
					reInit()
				elif cmd.lower() in ['iv0','int_val_0']:
					for f in Entry.__table__.columns:
						if f.name not in ['EntryId',] and str(f.type) == 'INTEGER':
							print(f"{Fore.chartreuse_1}Reseting {Fore.spring_green_3a}{f.name}={Fore.light_salmon_1}0{Style.reset}")
							self.setField(f.name,0)
				elif cmd.lower() in 'ssf2v|set selected field 2 value'.split("|"):
					self.setSelectedField2Value()
				elif cmd.lower() in 'casfv|clear all selected field value'.split("|"):
					self.clearAllSelectedFieldValue()
				elif cmd.lower() in ['rap','reset_all_prices']:
					self.setField('Prices',0)
				elif cmd.lower() in ['rac','reset_all_codes']:
					self.setField('Codes','')
				elif cmd.lower() in ['rats','reset_all_time_stamps']:
					self.setField('Timestamp',datetime.now().timestamp())
				elif cmd.lower() in ['sai0','reset_all_inlist0']:
					self.setField('InList',False)
					self.setField('ListQty',0)
				elif cmd.lower() in ['sai1','reset_all_inlist1']:
					self.setField('InList',True)
					self.setField('ListQty',1)
				elif cmd.lower() in ['sau0','reset_all_useruUpdated']:
					self.setField('userUpdated',False)
				elif cmd.lower() in ['sau1','reset_all_useruUpdated']:
					self.setField('userUpdated',True)

	def setField(self,field,value):
			with Session(self.engine) as session:
				results=session.query(Entry).all()
				ct=len(results)
				for num,r in enumerate(results):
					msg=f"{num}/{ct-1} -> {Fore.tan}{r.Name}|{Fore.medium_violet_red}{r.Barcode}|{Fore.light_salmon_1}{r.Code}|{Fore.light_green}{r.EntryId}|{Fore.light_yellow}{field}->{Fore.light_red}{value}{Style.reset}"
					print(msg)
					setattr(r,field,value)
					if num%50==0:
						session.commit()
				session.commit()