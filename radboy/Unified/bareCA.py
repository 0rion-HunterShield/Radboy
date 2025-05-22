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
import radboy.DB.db as db



def bare_ca(self,inList=False,protect_unassigned=True):
	def detectGetOrSet(name,value,setValue=False,literal=False):
		value=str(value)
		with Session(db.ENGINE) as session:
			q=session.query(db.SystemPreference).filter(db.SystemPreference.name==name).first()
			ivalue=None
			if q:
				try:
					if setValue:
						if not literal:
							q.value_4_Json2DictString=json.dumps({name:eval(value)})
						else:
							q.value_4_Json2DictString=json.dumps({name:value})
						session.commit()
						session.refresh(q)
					ivalue=json.loads(q.value_4_Json2DictString)[name]
				except Exception as e:
					if not literal:
						q.value_4_Json2DictString=json.dumps({name:eval(value)})
					else:
						q.value_4_Json2DictString=json.dumps({name:value})
					session.commit()
					session.refresh(q)
					ivalue=json.loads(q.value_4_Json2DictString)[name]
			else:
				if not literal:
					q=db.SystemPreference(name=name,value_4_Json2DictString=json.dumps({name:eval(value)}))
				else:
					q=db.SystemPreference(name=name,value_4_Json2DictString=json.dumps({name:value}))
				session.add(q)
				session.commit()
				session.refresh(q)
				ivalue=json.loads(q.value_4_Json2DictString)[name]
			return ivalue
	'''
	x_today=datetime.now()
	x_day=x_today.day
	x_month=x_today.month
	x_year=x_today.year
	bypass_clear_time_clear_protection=detectGetOrSet("bypass_clear_time_clear_protection",False,setValue=False,literal=False)
	cleared_date=datetime.strptime(detectGetOrSet("cleared_date",f"{x_month}/{x_day}/{x_year}",setValue=True,literal=True),"%m/%d/%Y")
	cleared_times=detectGetOrSet("cleared_times",0,setValue=True)

	print("-"*10)
	if not bypass_clear_time_clear_protection:
		if (datetime.now()-cleared_date) > timedelta(seconds=24*60*60):
			new_date=datetime.now()
			new_date=datetime.now()
			x_day=new_date.day
			x_month=new_date.month
			x_year=new_date.year
			new_cleared_date=detectGetOrSet("cleared_date",f"{x_month}/{x_day}/{x_year}",setValue=True,literal=True)
			cleared_times=detectGetOrSet("cleared_times",detectGetOrSet("cleared_times",0,setValue=False),setValue=False)
			cleared_times=detectGetOrSet("cleared_times",cleared_times+1,setValue=True)
		else:
			print(f"cleared at {cleared_date} : clear protection is enabled and you have to wait {Fore.light_cyan}{datetime.now()-cleared_date}{Fore.orange_red_1} to clear data to zero to {Fore.light_yellow}prevent {Fore.light_red}duplicate logs!{Style.reset}")
			return
	'''
	print(f"{Fore.dark_goldenrod}InList={Fore.green_yellow}{inList}, {Fore.dark_goldenrod}protect_unassigned={Fore.green_yellow}{protect_unassigned}{Style.reset}")
	with Session(db.ENGINE) as session:
			if inList:
				if not protect_unassigned:
					result=session.query(db.Entry).filter(db.Entry.InList==True).update({
						'InList':False,
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
				else:
					result=session.query(db.Entry).filter(db.Entry.InList==True,db.Entry.Code!="UNASSIGNED_TO_NEW_ITEM").update({
						'InList':False,
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
			else:
				if not protect_unassigned:
					result=session.query(db.Entry).update(
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
				else:
					result=session.query(db.Entry).filter(db.Entry.Code!="UNASSIGNED_TO_NEW_ITEM").update(
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
			
			#none type codes
			query=session.query(db.Entry).filter(and_(db.Entry.InList==True,db.Entry.Code==None))
			query.update({'InList':False,
						'Code':"UNASSIGNED_TO_NEW_ITEM",
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
						'CHKSTND_SPLY':0,})
			session.commit()
			session.flush()
			r=query.all()
			query2=session.query(db.Entry).filter(db.Entry.Code==None)
			query2.update(
				{'InList':False,
						'Code':"UNASSIGNED_TO_NEW_ITEM",
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
						'CHKSTND_SPLY':0,}
				)
			session.commit()
			session.flush()
			#print(len(r))
			#print(r,'#len')
			#print(query)
	print("-"*10)
