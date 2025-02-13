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
from radboy.DB.DatePicker import *
import requests

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

class GetRemoteSource:
	source=''
	destination=''
	tmp=''

	def __init__(self,source,destination='./codesAndBarcodes.tgz',tmp='./tmp_extract',engine=None):
		self.source=source
		self.destination=destination
		self.engine=engine
		self.tmp=tmp

		dp=Path(destination)
		msg=f"Removing old detination file!!!"
		print(msg)
		if dp.exists():
			dp.unlink()

		response=requests.get(self.source)
		if response.status_code == 200:
			pass


