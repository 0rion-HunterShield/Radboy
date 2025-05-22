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
from radboy.DB.SMLabelImporter import *
from radboy.DB.ResetTools import *

from radboy.ConvertCode.ConvertCode import *
from radboy.setCode.setCode import *
from radboy.Locator.Locator import *
from radboy.ListMode2.ListMode2 import *
from radboy.TasksMode.Tasks import *
from radboy.ExportList.ExportListCurrent import *
from radboy.TouchStampC.TouchStampC import *
from radboy import VERSION
import radboy.possibleCode as pc

def clear_all(self):
	fieldname='TaskMode'
	mode='ClearAll'
	h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
	
	code=''.join([str(random.randint(0,9)) for i in range(10)])
	verification_protection=detectGetOrSet("Protect From Delete",code,setValue=False,literal=True)
	while True:
		try:
			really=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h}Really Clear All Lists, and set InList=0?",helpText="yes or no boolean,default is NO",data="boolean")
			if really in [None,]:
				print(f"{Fore.light_steel_blue}Nothing was {Fore.orange_red_1}{Style.bold}Deleted!{Style.reset}")
				return True
			elif really in ['d',False]:
				print(f"{Fore.light_steel_blue}Nothing was {Fore.orange_red_1}{Style.bold}Deleted!{Style.reset}")
				return True
			else:
				pass
			really=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"To {Fore.orange_red_1}Delete everything completely,{Fore.light_steel_blue}what is today's date?[{'.'.join([str(int(i)) for i in datetime.now().strftime("%m.%d.%y").split(".")])}]{Style.reset}",helpText="type y/yes for prompt or type as m.d.Y",data="datetime")
			if really in [None,'d']:
				print(f"{Fore.light_steel_blue}Nothing was {Fore.orange_red_1}{Style.bold}Deleted!{Style.reset}")
				return True
			today=datetime.today()
			if really.day == today.day and really.month == today.month and really.year == today.year:
				really=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Please type the verification code {Style.reset}'{Entry.cfmt(None,verification_protection)}'?",helpText=f"type '{Entry.cfmt(None,verification_protection)}' to finalize!",data="string")
				if really in [None,]:
					print(f"{Fore.light_steel_blue}Nothing was {Fore.orange_red_1}{Style.bold}Deleted!{Style.reset}")
					return True
				elif really in ['d',False]:
					print(f"{Fore.light_steel_blue}Nothing was {Fore.orange_red_1}{Style.bold}Deleted!{Style.reset}")
					return True
				elif really == verification_protection:
					break
			else:
				pass
		except Exception as e:
			print(e)

	print(f"{Fore.orange_red_1}Deleting {Fore.light_steel_blue}{Style.bold}All Location Field Values,{Fore.light_blue}{Style.underline} and Setting InList=0!{Style.reset}")
	print("-"*10)
	with Session(ENGINE) as session:
			result=session.query(Entry).update(
				{'InList':False,
				'ListQty':0,
				'Shelf':0,
				'Note':'',
				'BackRoom':0,
				'Distress':0,
				'Display_1':0,
				'Display_2':0,
				'Display_3':0,
				'Display_4':0,
				'Display_5':0,
				'Display_6':0,
				'Stock_Total':0,
				'CaseID_BR':'',
				'CaseID_LD':'',
				'CaseID_6W':'',
				'SBX_WTR_DSPLY':0,
				'SBX_CHP_DSPLY':0,
				'SBX_WTR_KLR':0,
				'FLRL_CHP_DSPLY':0,
				'FLRL_WTR_DSPLY':0,
				'WD_DSPLY':0,
				'CHKSTND_SPLY':0,
				})
			session.commit()
			session.flush()
			print(result)
	print("-"*10)