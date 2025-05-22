from . import *

class ExportTable:
	def lsTables(self,only_return=False):
		with Session(ENGINE) as session:
			metadata=BASE.metadata
			metadata.reflect(ENGINE)
			tables=metadata.tables.keys()
			ct=len(tables)
			msgF=[]
			for num,i in enumerate(tables):
				msg=f"{self.colorized(num,ct)} - {Fore.orange_red_1}{i}{Style.reset}"
				msgF.append(msg)
			if not only_return:
				print('\n'.join(msgF))
			return '\n'.join(msgF)

	def exportSearched(self):
		folder=Path(detectGetOrSet("ExportTablesFolder",value="ExportedTables",literal=True))
		if not folder.exists():
			folder.mkdir()
		with Session(ENGINE) as session:
			search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What are you looking for with a text search to be exported?: ",helpText="searches all text columns of Entry Table",data="string")
			if search in [None,]:
				return
			keepers=["string","varchar","text"]
			text_fields=[str(i.name) for i in Entry.__table__.columns if str(i.type).lower() in keepers]			
			entries=session.query(Entry)
			fs=[getattr(Entry,i).icontains(search) for i in text_fields]
			
			try:
				entries=entries.filter(or_(*fs))
				df = pd.read_sql(entries.statement, entries.session.bind,dtype=str)
				opathname=folder/Path("EntrySearchedExport"+f"{datetime.now().strftime('_%m-%d-%Y')}.xlsx")
				df.to_excel(opathname,index=None)
				print(f"{Fore.light_red}Finished Writing '{Fore.light_green}{opathname}{Fore.light_red}': {Fore.orange_red_1}{opathname.exists()} | Exported '{Fore.light_steel_blue}{len(df)}{Fore.orange_red_1}' Results{Style.reset}")
			except Exception as e:
				print(e)

	def exportSelectedDaylogEntry(self):
		folder=Path(detectGetOrSet("ExportTablesFolder",value="ExportedTables",literal=True))
		if not folder.exists():
			folder.mkdir()
		with Session(ENGINE) as session:
			search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What are you looking to Export?: ",helpText="Searches fields in DayLog: Barcode,Code,Comments,Notes,Description,Name",data="string")
			if search in [None,]:
				return
			results=session.query(DayLog).filter(
				or_(
					DayLog.Barcode.icontains(search),
					DayLog.Code.icontains(search),
					DayLog.Name.icontains(search),
					DayLog.Description.icontains(search),
					DayLog.Note.icontains(search),
					)
				).group_by(DayLog.EntryId).order_by(DayLog.DayLogDate).all()
			ct=len(results)
			msgList=[]
			for num,i in enumerate(results):
				msgList.append(f'''{self.colorized(num,ct)} - {i.Name}|{i.Barcode}|{i.Code}|{i.Description}|{i.Note}''')
			msgText='\n'.join(msgList)
			print(msgText)
			which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Which index?: ",helpText=msgText,data='integer')
			if which in [None,'d']:
				print("User Cancelled!")
				return
			finalResult=results[which]
			entries=session.query(DayLog).filter(DayLog.EntryId==finalResult.EntryId)
			df = pd.read_sql(entries.statement, entries.session.bind)
			opathname=folder/Path("SelectedDayLogSetExport"+f"{datetime.now().strftime('_%m-%d-%Y')}.xlsx")
			df.to_excel(opathname,index=None)
			print(f"{Fore.light_red}Finished Writing '{Fore.light_green}{opathname}{Fore.light_red}': {Fore.orange_red_1}{opathname.exists()} | Exported '{Fore.light_steel_blue}{len(df)}{Fore.orange_red_1}' Results{Style.reset}")



	def exportTaggedEntry(self):
		folder=Path(detectGetOrSet("ExportTablesFolder",value="ExportedTables",literal=True))
		if not folder.exists():
			folder.mkdir()
		with Session(ENGINE) as session:
			tags=session.query(Entry).group_by(Entry.Tags).all()
			tags_list=[]
			ct_tags=len(tags)
			for num,i in enumerate(tags):
				msg=f"{self.colorized(num,ct_tags)} -{i.Tags}"
				try:
					t=json.loads(i.Tags)
					for tag in t:
						if tag not in tags_list and tag != None:
							tags_list.append(tag)
				except Exception as e:
					print(e)
			tags_list=sorted(tags_list)
			tag_ct=len(tags_list)
			tagText=[]
			for num,i in enumerate(tags_list):
				msg=f'{self.colorized(num,tag_ct)} - {i}'
				tagText.append(msg)
			tagText='\n'.join(tagText)
			print(tagText)
			entries=session.query(Entry)

			shards=[]
			t=tagText
			print(t)
			which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Export Selected Tags from Entry Table | which index(es): ",helpText=t,data="list")
			if which in [None,]:
				print("User Cancelled!")
				return
			try:
				for i in which:
					try:
						INDEX=int(i)
						shards.append(Entry.Tags.icontains(tags_list[INDEX]))
					except Exception as ee:
						print(ee)
			except Exception as e:
				print(e)
			try:
				entries=entries.filter(or_(*shards))
				df = pd.read_sql(entries.statement, entries.session.bind,dtype=str)
				opathname=folder/Path("EntryTaggedExport"+f"{datetime.now().strftime('_%m-%d-%Y')}.xlsx")
				df.to_excel(opathname,index=None)
				print(f"{Fore.light_red}Finished Writing '{Fore.light_green}{opathname}{Fore.light_red}': {Fore.orange_red_1}{opathname.exists()} | Exported '{Fore.light_steel_blue}{len(df)}{Fore.orange_red_1}' Results{Style.reset}")
			except Exception as e:
				print(e)




	def exportSelected(self):
		folder=Path(detectGetOrSet("ExportTablesFolder",value="ExportedTables",literal=True))
		if not folder.exists():
			folder.mkdir()
		with Session(ENGINE) as session:
			metadata=BASE.metadata
			metadata.reflect(ENGINE)
			tables=metadata.tables.keys()
			tables2=[]
			ct=len(tables)
			msgF=[]
			for num,i in enumerate(tables):
				tables2.append(i)
				msg=f"{self.colorized(num,ct)} - {Fore.orange_red_1}{i}{Style.reset}"
				msgF.append(msg)
			t='\n'.join(msgF)
			print(t)
			which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Export Selected Tables | which index(es): ",helpText=t,data="list")
			if which in [None,]:
				print("User Cancelled!")
				return
			try:
				for i in which:
					try:
						INDEX=int(i)
						query=session.query(metadata.tables[tables2[INDEX]])
						print(tables2[INDEX])
						df = pd.read_sql(query.statement, query.session.bind,dtype=str)
						opathname=folder/Path(tables2[INDEX]+f"{datetime.now().strftime('_%m-%d-%Y')}.xlsx")
						df.to_excel(opathname,index=None)
						print(f"{Fore.light_red}Finished Writing '{Fore.light_green}{opathname}{Fore.light_red}': {Fore.orange_red_1}{opathname.exists()} | Exported '{Fore.light_steel_blue}{len(df)}{Fore.orange_red_1}' Results{Style.reset}")
					except Exception as ee:
						print(ee)
			except Exception as e:
				print(e)

	def removeNoneBarcodes(self):
		with Session(ENGINE) as session:
			session.query(Entry).filter(Entry.Barcode=='None',Entry.Code=='None').delete()
			session.commit()

	def colorized(self,num,ct):
		return f'{Fore.light_red}{num}{Fore.orange_red_1}/{Fore.light_green}{num+1} of {Fore.cyan}{ct} {Fore.magenta}'

	def importFile(self):
		return detectGetOrSet("ImportExcel",value="ImportExcel.xlsx",literal=True)

	def importFileODF(self):
		return detectGetOrSet("ImportODF",value="ImportExcel.xlsx.ods",literal=True)
	'''
	replace=[
				['#hw#',''],
				['hw#',''],
				['Hw#',''],
			]
	'''
	replace=[]
	additives=[]
	import_fields_replace=['Barcode','Code']
	
	def addToReplace(self,additives):
		try:
			for rep,alt in additives:
				self.replace.append([rep,alt])
		except Exception as e:
			print(e)
	
	def alterDictionary(self,dictionary,key):
		tmp=[[x,''] for x in [''.join(i) for i in itertools.product(['h','w','H','W'],repeat=2)] if x.lower().startswith('h') and not x.lower().endswith('h')]
		#a list of lists with len(2)
		
		tmpFinal=[]
		self.addToReplace(self.additives)
		for rep,alt in tmp:
			#remove longest to shortest to prevent partial removal
			tmpFinal.append([f'#{rep}#',alt])
			tmpFinal.append([f'{rep}#',alt])
		self.replace=tmpFinal
		#print(self.replace)
		#exit()
		if key in self.import_fields_replace:
			for rep,alt in self.replace:
				#print(key,dictionary,dictionary[key],rep,alt.encode())
				dictionary[key]=dictionary[key].replace(rep,alt)
				#print(key,dictionary,dictionary[key],rep,alt.encode())
		return dictionary

	def importExcel(self,update=False,duplicates=False,manual=False,ods=False):
		import_file=self.importFile()
		if ods:
			import_file=self.importFileODF()
		try:
			dtype={
			'Barcode':str,
			'Code':str
			}
			df=pd.read_excel(import_file,dtype=dtype)
			if len(df) < 2:
				print("There is nothing to import")
				return
			with Session(ENGINE) as session:
				for row in df.itertuples():
					skip=False
					entryRow=row._asdict()
					entry=Entry(Barcode='',Code='')
					excludes=["EntryId","Timestamp"]
					for k in entryRow:
						print(row)
						entryRow[k]=self.alterDictionary(entryRow,k)[k]
						if k in excludes:
							continue
						try:
							setattr(entry,k,entryRow[k])
						except Exception as ee:
							print(ee)
					if not duplicates:
						r=session.query(Entry).filter(Entry.Barcode==entry.Barcode).first()
						if r:
							print(f"Not Adding Duplicate {entry.Barcode}!")
							continue
					else:
						pass

					if update:
						r=session.query(Entry).filter(Entry.Barcode==entry.Barcode).first()
						if r:
							print(f"Updating Data for {entry.Barcode}!")
							excludes=["EntryId","Timestamp"]
							for k in entryRow:
								if k in excludes:
									continue
								try:
									bools=[str(i.name) for i in Entry.__table__.columns if str(i.type) == 'BOOLEAN']
									if k in bools:
										entryRow[k]=bool(entryRow[k])
									setattr(r,k,entryRow[k])
								except Exception as ee:
									print(ee)
							session.commit()
							session.refresh(r)
							print(r,f"{Fore.light_red}{'*'*10}UPDATE-{entry.Barcode}-{entry.Code}-{entry.Name}{'*'*10}{Style.reset}")
							continue

					if manual:
						r=session.query(Entry).filter(Entry.Barcode==entry.Barcode).first()
						if r:
							print(f"Manually Intevening on Duplicate {entry.Barcode}!")
							while True:
								try:
									helpText='''
#update old
# - autocopy ( 'update','upd8','ud' )
# - manual with FormBuilder (  )
#skip ('skip','d')
#add duplicate
'exit','back',"ex","ext","e" - back a menu
enter goes to next entry row'''
									doWhat=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What would you like to do? [h/help]",helpText=helpText,data="string")
									if doWhat in [None,'skip','d']:
										skip=True
									elif doWhat.lower() in ['ad','add duplicate','a2']:
										print(f"Adding Duplicate {entry.Barcode}")
									elif doWhat.lower() in ['exit','back',"ex","ext","e"]:
										return
									elif doWhat.lower() in ['update','upd8','ud']:
										r=session.query(Entry).filter(Entry.Barcode==entry.Barcode).first()
										if r:
											print(f"Updating Data for {entry.Barcode}!")
											excludes=["EntryId","Timestamp"]
											for k in entryRow:
												if k in excludes:
													continue
												try:
													setattr(r,k,entryRow[k])
												except Exception as ee:
													print(ee)
											session.commit()
											session.refresh(r)
											print(r)
											break
									elif doWhat.lower() in ['update manual','upd8m','udm']:
										r=session.query(Entry).filter(Entry.Barcode==entry.Barcode).first()
										if r:
											data={i:{'default':getattr(entry,i),'type':str(type(getattr(entry,i))).lower()} for i in entryRow}
											upd8=FormBuilder(data=data)
											if upd8 in [None,]:
												continue
											print(f"Updating Data for {entry.Barcode}!")
											excludes=["EntryId","Timestamp"]
											for k in upd8:
												if k in excludes:
													continue
												try:
													setattr(r,k,entryRow[k])
												except Exception as ee:
													print(ee)
											session.commit()
											session.refresh(r)
											print(r)
											break


								except Exception as e:
									print(e)
								break
					if skip:
						continue

					session.add(entry)
					session.commit()
					session.refresh(entry)
					print(entry)
		except Exception as e:
			print(e)
		when=datetime.now().strftime("%d.%m.%Y")
		readfile=import_file+f".done-{when}"
		Path(import_file).rename(readfile)
		print(import_file,"->",readfile)

	def exportTemplateExcel(self):
		import_file=self.importFile()
		t=Entry(Barcode='',Code='')
		df=pd.DataFrame({i.name:[getattr(t,i.name),] for i in Entry.__table__.columns})
		df.to_excel(import_file,index=None)

	def __init__(self):
		self.cmds={
			'list tables':{
				'cmds':['ls tables','list tables','ls tbls'],
				'exec':self.lsTables,
				'desc':'list tables in db',
			},
			'export selected':{
				'cmds':['export selected table','est','xpt slct tbl'],
				'exec':self.exportSelected,
				'desc':'export specific tables'
			},
			'Export Tagged Entry':{
			'cmds':['export tagged entry','ete','xpt tgd ntry'],
			'exec':self.exportTaggedEntry,
			'desc':'export Entry\' Tagged Entries from Entry Table using selected tags'
			},
			'Export Searched Entry':{
			'cmds':['export searched entry','ese','xpt schd ntry'],
			'exec':self.exportSearched,
			'desc':'export Entry\' searched from Entry Table using selected text fields'
			},
			'Export Selected Daylog Entry Set':{
			'cmds':['esdes','exported selected daylog entry set'],
			'exec':self.exportSelectedDaylogEntry,
			'desc':'Export a specific DayLog Entry Set by search'
			},
			'import from excel no duplicates no update':{
			'cmds':['ife_0d_0u','import from excel no duplicates no update'],
			'exec':self.importExcel,
			'desc':'import from excel no duplicates no update'
			},
			'import from excel yes duplicates yes update update':{
			'cmds':['ife_1d_1u','import from excel yes duplicates yes update'],
			'exec':lambda self=self:self.importExcel(update=True,duplicates=True),
			'desc':'import from excel no duplicates yes update'
			},
			'import from excel yes duplicates no update':{
			'cmds':['ife_1d_0u','import from excel yes duplicates no update'],
			'exec':lambda self=self:self.importExcel(update=False,duplicates=True),
			'desc':'import from excel yes duplicates no update'
			},
			'import from excel with manual Intevention':{
			'cmds':['ifem','import from excel manual Intevention'],
			'exec':lambda self=self:self.importExcel(manual=True,duplicates=True),
			'desc':'import from excel with manual Intevention'
			},
			'export excel template':{
			'cmds':['export excel template','eet'],
			'exec':self.exportTemplateExcel,
			'desc':'export a blank template file'
			},
			'purge nonetype barcode and code':{
			'cmds':['pnbac','purge nonetype barcode and code'],
			'exec':self.removeNoneBarcodes,
			'desc':'remove barcodes and codes that have "None" as their data'
			},


			'import from excel no duplicates no update ODS':{
			'cmds':['ods ife_0d_0u','import from excel no duplicates no update ods'],
			'exec':lambda self=self:self.importExcel(ods=True),
			'desc':'import from excel no duplicates no update ods version'
			},
			'import from excel yes duplicates yes update update ODS':{
			'cmds':['ods ife_1d_1u','import from excel yes duplicates yes update ods'],
			'exec':lambda self=self:self.importExcel(update=True,duplicates=True,ods=True),
			'desc':'import from excel no duplicates yes update ods version'
			},
			'import from excel yes duplicates no update ODS':{
			'cmds':['ods ife_1d_0u','import from excel yes duplicates no update ods'],
			'exec':lambda self=self:self.importExcel(update=False,duplicates=True,ods=True),
			'desc':'import from excel yes duplicates no update ods version'
			},
			'import from excel with manual Intevention ODS':{
			'cmds':['ods ifem','import from excel manual Intevention ods'],
			'exec':lambda self=self:self.importExcel(manual=True,duplicates=True,ods=True),
			'desc':'import from excel with manual Intevention ods version'
			},
		}
		helpText=''
		for cmd in self.cmds:
			msg=f'{Fore.light_cyan}{self.cmds[cmd]["cmds"]} {Fore.light_yellow}{self.cmds[cmd]["desc"]}{Style.reset}\n'
			helpText+=msg
		print(helpText)
		while True:
			action=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Export Table Menu | Do what?",helpText=helpText,data="string")
			if action in [None,]:
				return
			elif action in ['d',]:
				print(helpText)
				continue
			for cmd in self.cmds:
				if action.lower() in self.cmds[cmd]['cmds']:
					if self.cmds[cmd]['exec'] != None and callable(self.cmds[cmd]['exec']):
						self.cmds[cmd]['exec']()