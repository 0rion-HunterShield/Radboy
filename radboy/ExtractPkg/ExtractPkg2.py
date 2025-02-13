import tempfile
from pathlib import Path
import shutil
from copy import deepcopy
import json,os,base64,time
from datetime import datetime
from sqlalchemy.ext.automap import automap_base
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
import zipfile
from colored import Fore,Back,Style

from radboy.DB.db import *
from radboy.DB.Prompt import *


class ExtractPkg:
	def __str__(self):
		return "ExtractPkg and Update Config"

	def __init__(self,tbl,error_log,engine):
		self.tbl=tbl
		self.error_log=error_log
		self.engine=engine

		while True:
			try:
				path2bck=input("MobileInventoryCLI-BCK Path[filepath+filename/q/b]: ")
				if path2bck in ['q','quit']:
					exit("user quit!")
				elif path2bck in ['b','back']:
					return
				else:
					path2bck=Path(path2bck)
					if path2bck.exists():
						with zipfile.ZipFile(path2bck,"r") as zip:
							#tmpdir=Path(tempfile.mkdtemp())
							for file in zip.namelist():
								if Path(file).suffix == ".db3":
									x=zip.extract(file,path=str(Path("./system.db").absolute()))
									print(x)
									#update db
									print("opening db for updates")
									with Session(engine) as session:
										while True:
											clear_db=input("Clear DB before adding from file[Y/n/q/b]: ")
											if clear_db.lower() in ['y','yes','ye']:
												session.query(Entry).delete()
												session.commit()
												break
											elif clear_db.lower() in ['q','quit','qui','qu','exit']:
												exit("user quit!")
												break
											elif clear_db.lower() in ['b','ba','bac','back']:
												return
											else:
												break

										l_base=automap_base()
										f=f'sqlite:///{Path(x).absolute()}'
										print(f)
										l_engine=create_engine(f)
										l_base.prepare(autoload_with=l_engine)
										ltbl=l_base.classes

										with Session(l_engine) as ses:
											results=ses.query(ltbl.Item).all()
											print(dir(ltbl))
											for num,item in enumerate(results):
												n=str(item.ImagePath)
												if n != 'None':
													n=str(Path("Images")/Path(Path(n).name))

												fields=[i.name for i in Entry.__table__.columns]
												cfresults=ses.query(ltbl.CustomField).all()
												
												dt={}
												for cf in cfresults:
													#print(cf.Name)
													if cf.Name in fields:
														#item_cf_ids.append(cf.CustomFieldId)
														#print(item_cf_ids)
														cfdata=ses.query(ltbl.ItemCustomField).filter(ltbl.ItemCustomField.ItemId==item.ItemId,ltbl.ItemCustomField.CustomFieldId==cf.CustomFieldId).first()
														if cfdata != None:
															if cf.Type == 0:
																pass
																#text
															elif cf.Type == 1:
																print(cf.Name)
																if cfdata.Value in [None,'']:
																	dt[cf.Name]=float(1)
																else:
																	dt[cf.Name]=float(cfdata.Value)
															else:
																dt[cf.Name]=cfdata.Value
												dt["Name"]=item.Name
												dt["Barcode"]=item.Barcode
												dt["Code"]=item.Code
												dt["Price"]=item.Price
												dt["Image"]=n
												dt["Note"]=json.dumps({'Note':item.Note,'MeasurementUnit':item.MeasurementUnit})
												dt["Size"]=f"SIZE:{dt.get('Size')}|Unit:{dt.get('SizeUnit')}"
												if item.Tags:
													dt["Tags"]=json.dumps(item.Tags.split(","))
												entry=Entry(**dt)

												check=session.query(Entry).filter(Entry.Barcode==entry.Barcode,Entry.Code==entry.Code).first()
												print(check)
												if check:
													setattr(check,'InList',True)
													session.commit()
													print("A Duplicate was found added to InList==True for review!")
												
												#for now all duplicates will be added
												session.add(entry)
												if num % 100 == 0:
													session.commit()
												print(f'{num+1}/{len(results)}')
											session.commit()
									print("done importing")
								else:
									zip.extract(file,path=str(Path("./system.db").absolute()))
								print("Extracting {s1}{v}{e} to {s2}{vv}{e}".format(v=file,vv=str(Path("./system.db").absolute()),e=Style.reset,s1=Fore.light_green,s2=Fore.red))

					if Path("Images").exists():
						shutil.rmtree("./Images")

					shutil.move("./system.db/Images","./Images")
			except Exception as e:
				print(e)