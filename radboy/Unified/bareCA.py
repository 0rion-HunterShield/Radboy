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

def bare_ca(self,inList=False):
	print("-"*10)
	with Session(db.ENGINE) as session:
			if inList:
				result=session.query(db.Entry).filter(db.Entry.InList==True).update({
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
			session.commit()
			session.flush()
			print(result)
	print("-"*10)
