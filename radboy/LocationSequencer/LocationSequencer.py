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
from radboy.ExportList.ExportListCurrent import *
from radboy.TouchStampC.TouchStampC import *
from radboy import VERSION
import radboy.possibleCode as pc


class LocationSequencer:
	def __init__(self,engine,parent):
		self.engine=engine
		self.parent=parent

		self.helpText=f"""
{Fore.magenta}#code is one of:{Style.reset}
{Fore.tan}e.$code {Style.reset}- {Fore.light_blue}Entry.EntryId{Style.reset}
{Fore.tan}c.$code {Style.reset}- {Fore.light_blue}Entry.Code{Style.reset}
{Fore.tan}b.$code {Style.reset}- {Fore.light_blue}Entry.Barcode{Style.reset}
{Fore.tan}$code {Style.reset}- {Fore.light_blue}first of result of checking from c.$code and b.$code{Style.reset}

[{Style.bold}{Fore.yellow}Manual{Style.reset}] - {Fore.grey_70}prompt for Aisle No. -> Shelf Mod. No. -> Item No. -> #code{Style.reset}
[{Style.bold}{Fore.yellow}Semi-Auto{Style.reset}] - {Fore.grey_70}prompt for Aisle No. -> Shelf Mod. No. -> start No. (default=0) -> #code{Style.reset}
once code is captured, generate location text
save location text to Entry.Location found from #code
increment Start No.
Loop Back to #code capture and repeat until user requests
{Fore.light_blue}
cmds:
{Style.reset}
	{Fore.light_yellow}q|quit{Style.reset} -{Fore.green_yellow} quit program{Style.reset}
	{Fore.light_yellow}b|back{Style.reset} -{Fore.green_yellow} return to previous menu{Style.reset}
	{Fore.light_yellow}mnl|m|manual{Style.reset} -{Fore.green_yellow} Manual Mode{Style.reset}
	{Fore.light_yellow}sa|semi-auto|semi_auto{Style.reset} -{Fore.green_yellow} Semi-Auto Mode{Style.reset}
	{Fore.light_yellow}///2list{Style.reset} -{Fore.green_yellow} Set Entry.InList=True with Entry.Location==/// or Entry.Location==''{Style.reset}
	{Fore.light_yellow}!///2list{Style.reset} -{Fore.green_yellow} Set Entry.InList=True with Entry.Location!=/// or Entry.Location!=''{Style.reset}
	{Fore.light_yellow}validate2list|v2l{Style.reset} -{Fore.green_yellow} Set Entry.InList=True for Entry's that are not potentially correct{Style.reset}
	{Fore.light_yellow}clear_locations|CL@{Style.reset} -{Fore.green_yellow} Set Entry.InList=False,Entry.ListQty=0 && Entry.Location='' for all Entry's{Style.reset}

"""

		while True:
			#what=input(f"{Fore.light_red}do what? : {Style.reset}")
			def mkT(text,self):
				return text
			mode='Location LocationSequencer'
			fieldname='Menu'
			h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
			what=Prompt.__init2__(None,func=mkT,ptext=f"{h}{Fore.light_red}Do what[h|help]?{Style.reset}",helpText=self.helpText,data=self)
			if what:
				if what.lower() in ['mnl','m','manual']:
					self.manual()
				elif what.lower() in ['sa','semi-auto','semi_auto',]:
					self.semi_auto()
				elif what.lower() in ['///2list']:
					self.nis_inlist()
				elif what.lower() in ['!///2list']:
					self.not_nis_inlist()
				elif what.lower() in ['validate2list','v2l']:
					self.validate2list()
				elif what.lower() in ['clear_locations','cl@']:
					self.clear_locations()
			else:
				return

		#self.semi_auto()
		#self.manual()
	def nis_inlist(self):
		with Session(self.engine) as session:
			query=session.query(Entry).filter(or_(Entry.Location=='///',Entry.Location==''))
			results=query.all()
			ct=len(results)
			for num,r in enumerate(results):
				print(f"Setting {num}/{ct-1}:{r.EntryId}:InList==True")
				r.InList=True
				if num%50==0:
					session.commit()
				session.commit()

	def clear_locations(self):
		with Session(self.engine) as session:
			query=session.query(Entry)
			results=query.all()
			ct=len(results)
			if ct <= 0:
				print(f"{Fore.light_yellow}No Entries Resulted:{Style.reset} {Fore.light_red}{ct}{Style.reset}")
			for num,r in enumerate(results):
				print(f"{Fore.green}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} ->{Fore.cyan}{r.EntryId}|{r.Name}|{r.Barcode}|{r.Code}{Style.reset}|{Fore.magenta}{r.Location} ->''{Style.reset}")
				r.Location=''
				r.InList=False
				r.ListQty=0
				if num%50==0:
					session.commit()
			session.commit()
			if ct >= 1:
				print(f"{Fore.light_yellow}Locations were changed for{Style.reset} {Fore.light_red}{ct} {Style.bold}Entry's{Style.reset}")

	def not_nis_inlist(self):
		with Session(self.engine) as session:
			query=session.query(Entry).filter(or_(Entry.Location!='///',Entry.Location!=''))
			results=query.all()
			ct=len(results)
			for num,r in enumerate(results):
				print(f"Setting {num}/{ct-1}:{r.EntryId}:InList==True")
				r.InList=True
				if num%50==0:
					session.commit()
				session.commit()

	def validate2list(self):
		with Session(self.engine) as session:
			query=session.query(Entry)
			results=query.all()
			ct=len(results)
			for num,r in enumerate(results):
				if len(str(r.Location).split("/")) == 3 and str(r.Location).split("/") != ['','','']:
					print(f"Setting {num}/{ct-1}:{r.EntryId}:InList==True")
					r.InList=True
					if num%50==0:
						session.commit()
					session.commit()

	def manual(self):
		try:
			aisle_no=str(input(f"Aisle No.: "))

			if aisle_no.lower() in ['q','quit']:
				exit("user quit!")
			elif aisle_no.lower() in ['b','back']:
				return
			elif aisle_no.lower() in ['?','help']:
				print(self.helpText)
			shelf_mod_no=str(input(f"Shelf Module No.: "))
			if shelf_mod_no.lower() in ['q','quit']:
				exit("user quit!")
			elif shelf_mod_no.lower() in ['b','back']:
				return
			elif shelf_mod_no.lower() in ['?','help']:
				print(self.helpText)
			while True:
				try:
					start_seq=input(f"Shelf Mod. Item No.: ")
					if start_seq.lower() in ['q','quit']:
						exit("user quit!")
					elif start_seq.lower() in ['b','back']:
						return
					elif start_seq.lower() in ['?','help']:
						print(self.helpText)
				except Exception as e:
					raise e
				location_text=f"{str(aisle_no).zfill(3)}/{str(shelf_mod_no).zfill(3)}/{str(start_seq).zfill(3)}"

				code=input("code: ")
				if code.lower() in ['q','quit']:
					exit("user quit!")
				elif code.lower() in ['b','back']:
					return
				elif code.lower() in ['?','help']:
					print(self.helpText)
				cdspl=code.split(".")
				cdspl_ct=len(cdspl)
				prefix=cdspl[0].lower()
				bar=cdspl[-1]
				print(cdspl_ct,bar)
				with Session(self.engine) as session:
					result=None
					if cdspl_ct == 1:
						result=session.query(Entry).filter(or_(Entry.Barcode==bar,Entry.Code==bar)).all()
					elif cdspl_ct == 2:
						if prefix == 'c':
							result=session.query(Entry).filter(Entry.Code==bar).all()
						elif prefix == 'b':
							result=session.query(Entry).filter(Entry.Barcode==bar).all()
						elif prefix == 'e':
							result=session.query(Entry).filter(Entry.EntryId==int(bar)).all()
						else:
							print("unsupported prefix {prefix}")
					
					if result:
						if len(result) > 0:
							ct=len(result)
							for num,i in enumerate(result):
								print(f"{num}/{ct-1} -> {i}")
							entry=input(f"""
Which {Fore.light_yellow}Entry No.{Style.reset} Do You want to attach
the {Fore.light_blue}location{Style.reset} code {Fore.light_blue}'{location_text}'{Style.reset} to? 
{Fore.light_red}Total Results{Style.reset}={Fore.green}{ct}{Style.reset}: """)
							if entry.lower() in ['q','quit']:
								exit("user quit!")
							elif entry.lower() in ['b','back']:
								return
							elif entry.lower() in ['?','help']:
								print(self.helpText)
							else:
								if entry == '':
									entry=0
								entry=int(entry)
								result[entry].Location=location_text
								result[entry].InList=True
								result[entry].Note+=f"\nLocation Added {datetime.now().ctime()}\n"
								session.commit()
								session.flush()
								session.refresh(result[entry])
								print(result[entry])
						else:
							print(f"No Item Could be Found to Satisfy {bar}")
					else:
						print(f"No Item Could be Found to Satisfy {bar}")
		except Exception as e:
			print(e)




	def semi_auto(self):
		try:
			aisle_no=str(input(f"Aisle No.: "))

			if aisle_no.lower() in ['q','quit']:
				exit("user quit!")
			elif aisle_no.lower() in ['b','back']:
				return
			elif aisle_no.lower() in ['?','help']:
				print(self.helpText)
			shelf_mod_no=str(input(f"Shelf Module No.: "))
			if shelf_mod_no.lower() in ['q','quit']:
				exit("user quit!")
			elif shelf_mod_no.lower() in ['b','back']:
				return
			elif shelf_mod_no.lower() in ['?','help']:
				print(self.helpText)
			try:
				start_seq=input(f"Start Seq No.: ")
				if start_seq.lower() in ['q','quit']:
					exit("user quit!")
				elif start_seq.lower() in ['b','back']:
					return
				elif start_seq.lower() in ['?','help']:
					print(self.helpText)
				start_seq=int(start_seq)
			except Exception as e:
				start_seq=1

			location_text=f"{str(aisle_no).zfill(3)}/{str(shelf_mod_no).zfill(3)}/{str(start_seq).zfill(3)}"
			while True:
				code=input("code: ")
				if code.lower() in ['q','quit']:
					exit("user quit!")
				elif code.lower() in ['b','back']:
					return
				elif code.lower() in ['?','help']:
					print(self.helpText)
				cdspl=code.split(".")
				cdspl_ct=len(cdspl)
				prefix=cdspl[0].lower()
				bar=cdspl[-1]
				print(cdspl_ct,bar)
				with Session(self.engine) as session:
					result=None
					if cdspl_ct == 1:
						result=session.query(Entry).filter(or_(Entry.Barcode==bar,Entry.Code==bar)).all()
					elif cdspl_ct == 2:
						if prefix == 'c':
							result=session.query(Entry).filter(Entry.Code==bar).all()
						elif prefix == 'b':
							result=session.query(Entry).filter(Entry.Barcode==bar).all()
						elif prefix == 'e':
							result=session.query(Entry).filter(Entry.EntryId==int(bar)).all()
						else:
							print("unsupported prefix {prefix}")
					
					if result:
						if len(result) > 0:
							ct=len(result)
							for num,i in enumerate(result):
								print(f"{num}/{ct-1} -> {i}")
							entry=input(f"""
Which {Fore.light_yellow}Entry No.{Style.reset} Do You want to attach
the {Fore.light_blue}location{Style.reset} code {Fore.light_blue}'{location_text}'{Style.reset} to? 
{Fore.light_red}Total Results{Style.reset}={Fore.green}{ct}{Style.reset}: """)
							if entry.lower() in ['q','quit']:
								exit("user quit!")
							elif entry.lower() in ['b','back']:
								return
							elif entry.lower() in ['?','help']:
								print(self.helpText)
							else:
								if entry == '':
									entry=0
								entry=int(entry)
								result[entry].Location=location_text
								result[entry].InList=True
								result[entry].Note+=f"\nLocation Added {datetime.now().ctime()}\n"
								session.commit()
								session.flush()
								session.refresh(result[entry])
								print(result[entry])
								start_seq+=1
								location_text=f"{str(aisle_no).zfill(3)}/{str(shelf_mod_no).zfill(3)}/{str(start_seq).zfill(3)}"
						else:
							print(f"No Item Could be Found to Satisfy {bar}")
					else:
						print(f"No Item Could be Found to Satisfy {bar}")
		except Exception as e:
			print(e)
