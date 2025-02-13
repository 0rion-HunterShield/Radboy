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
from radboy.ConvertCode.ConvertCode import *
from radboy.setCode.setCode import *
from radboy.Locator.Locator import *
from radboy.ListMode2.ListMode2 import *
from radboy.TasksMode.Tasks import *
import radboy.possibleCode as pc
import radboy.Unified.Unified as unified

class ExportListCSV:
	def printHeaders(self,headers):
		if not headers:
			return
		m='|'.join(headers)
		br=16*'-'
		print(br+f" {Style.bold}{Style.underline}HEADERS{Style.reset} "+br)
		print(m)
		print(br+f" {Style.bold}{Style.underline}HEADERS{Style.reset} "+br)
	def printData(self,up=False):
		if up:
			print(f"{'-'*16}Data Start {'-'*16}")
		else:
			print(f"{'-'*16}Data End {'-'*16}")

	def __init__(self,engine,parent):
		with Session(engine) as session:
			query=session.query(Entry).filter(Entry.InList==True)
			result=query.all()
			while True:
				try:
					default=Path(".")/Path("exported_list.csv")
					export_file=input(f"Export File [{default}]: ")
					if export_file == '':
						export_file=default
					elif export_file.lower() in ['q','quit']:
						exit("user quit!")
					elif export_file.lower() in ['b','back']:
						return
					elif export_file.lower() in ['r','review_export','read']:
						export_file=input(f"Export File to Review [{default}]: ")
						if export_file == '':
							export_file=default
						elif export_file.lower() in ['q','quit']:
							exit("user quit!")
						elif export_file.lower() in ['b','back']:
							return
						if Path(export_file).exists():
							print(export_file)
							with open(export_file,"r") as ef:
								reader=csv.reader(ef,delimiter=";")
								headers=None
								for num,line in enumerate(reader):
									for nnum,item in enumerate(line):
										if nnum%2==0:
											line[nnum]=f"{Fore.green_yellow}{item}{Style.reset}"
										else:
											line[nnum]=f"{Fore.orange_red_1}{item}{Style.reset}"
									if num == 0:
										headers=line
										self.printHeaders(headers)
									elif num == 1:
										self.printData(up=True)
									print(f"{Fore.red}{num}{Style.reset}|"+"|".join(line))
									self.printData()
								self.printHeaders(headers)
						continue
					
					with open(export_file,"w") as ef:
						writer=csv.writer(ef,delimiter=";")
						for num,r in enumerate(result):
							if num == 0:
								writer.writerow(r.csv_headers())
							writer.writerow(r.csv_values())
					print(f"{export_file} written!")
					break
				except Exception as e:
					print(e)