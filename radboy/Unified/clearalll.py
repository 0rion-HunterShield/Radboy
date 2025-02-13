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
	def mkBool(text,self):
		try:
			if text.lower() in ['','y','yes','ye','true','1']:
				return True
			elif text.lower() in ['n','no','false','0']:
				return False
			else:
				return eval(text)
		except Exception as e:
			print(e)

	fieldname='TaskMode'
	mode='ClearAll'
	h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
	htext=f"""{Fore.light_red}Type one of the following between commas:
{Fore.light_yellow}y/yes/ye/true/1 {Fore.green} to continue, this is the default so <Enter>/<return> will also result in this!!!
{Fore.light_green}n/no/false/0 {Fore.green} to cancel delete{Style.reset}"""
	really=True
	while True:
		try:
			really=Prompt.__init2__(None,func=mkBool,ptext=f"{h}Really Clear All Lists, and set InList=0?",helpText=htext,data=self)
			break
		except Exception as e:
			print(e)
	if really in [False,None]:
		print(f"{Fore.light_steel_blue}Nothing was {Fore.orange_red_1}{Style.bold}Deleted!{Style.reset}")
		return True
	else:
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