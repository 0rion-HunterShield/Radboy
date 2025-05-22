from radboy.DB.db import *
from radboy.DB.Prompt import *
from radboy.DB.Prompt import Prompt
from radboy.EntryExtras.Extras import *
from colored import Style,Fore,Back
import qrcode

class Lookup:
	def entrySearchBlank(self,just_code=True,fix=False):
		print("Looking for Blank Barcode|Code")
		with Session(ENGINE) as session:
			#Entry.Code=='',Entry.Code=="UNASSIGNED_TO_NEW_ITEM"
			if just_code:
				q=session.query(Entry).filter(or_(Entry.Code=='')).all()
			else:
				q=session.query(Entry).filter(or_(Entry.Code=='',Entry.Barcode=='')).all()
			ct=len(q)
			if ct == 0:
				print(f"{Fore.light_red}No NoneType Codes Exist!{Style.reset}")
			for num,i in enumerate(q):
				msg=f"{Fore.light_red}{num}/{Fore.light_yellow}{num+1} of {Fore.cyan}{ct}{Fore.light_blue} -> {i.seeShort()}"
				print(msg)
				if fix:
					i.Code="UNASSIGNED_TO_NEW_ITEM"
					if num%200==0:
						session.commit()
			if fix:
				session.commit()

	def entrySearchNone(self,just_code=True,fix=False):
		print("Looking for NoneType Barcode|Code")
		with Session(ENGINE) as session:
			#Entry.Code=='',Entry.Code=="UNASSIGNED_TO_NEW_ITEM"
			if just_code:
				q=session.query(Entry).filter(or_(Entry.Code==None)).all()
			else:
				q=session.query(Entry).filter(or_(Entry.Code==None,Entry.Barcode==None)).all()
			ct=len(q)
			if ct == 0:
				print(f"{Fore.light_red}No NoneType Codes Exist!{Style.reset}")
			for num,i in enumerate(q):
				msg=f"{Fore.light_red}{num}/{Fore.light_yellow}{num+1} of {Fore.cyan}{ct}{Fore.light_blue} -> {i.seeShort()}"
				print(msg)
				if fix:
					i.Code="UNASSIGNED_TO_NEW_ITEM"
					if num%200==0:
						session.commit()
			if fix:
				session.commit()

	def __init__(self,init_only=False):
		self.cmds={
		'1':{
			'cmds':['q','quit'],
			'exec':lambda self=self:exit("user quit!"),
			'desc':f'{Fore.light_red}Quit the program!{Style.reset}'
		},
		'2':{
			'cmds':['b','back'],
			'exec':None,
			'desc':f'{Fore.light_red}Go Back a Menu!{Style.reset}'
		},
		'3':{
			'cmds':['3','sbc','search_bc',],
			'exec':self.search,
			'desc':f'{Fore.light_blue}Lookup Codes by Barcode|Code{Style.reset}',
		},
		'4l':{
			'cmds':['4l','search_auto_long','sal'],
			'exec':self.SearchAuto,
			'desc':f'{Fore.light_blue}Search For Product by Name,Barcode,Code,Note,Size {Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command{Style.reset}'
		},
		'4le':{
			'cmds':['4le','search_auto_long_extras','sale'],
			'exec':lambda self=self:self.SearchAuto(long_search_extras=True),
			'desc':f'{Fore.light_blue}Search For Product by Name,Barcode,Code,Note,Size,EntryDataExtras.* {Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command{Style.reset}'
		},
		'4s':{
			'cmds':['4s','search_auto_short','sas'],
			'exec':lambda self=self:self.SearchAuto(short=True),
			'desc':f'{Fore.light_blue}Search For Product by Name,Barcode,Code,Note,Size {Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command{Style.reset}'
		},
		'4se':{
			'cmds':['4se','search_auto_short_extras','sase'],
			'exec':lambda self=self:self.SearchAuto(short=True,extras=True),
			'desc':f'{Fore.light_blue}Search For Product by Name,Barcode,Code,Note,Size {Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command and includes EntryDataExtras with search and output{Style.reset}'
		},
		'5':{
			'cmds':['5','sm','search_manual'],
			'exec':self.SearchManual,
			'desc':f'{Fore.light_blue}Search For Product by Field {Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command{Style.reset}'
		},
		'6':{
			'cmds':['6','sch entry data extras short','sedes'],
			'exec':lambda self=self:self.entryDataExtrasSearch(longText=False),
			'desc':f'{Fore.light_blue}Search For Product by EntryDataExtras {Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command{Style.reset}'
		},
		'7':{
			'cmds':['7','sch entry data extras long','sedel'],
			'exec':lambda self=self:self.entryDataExtrasSearch(longText=True),
			'desc':f'{Fore.light_blue}Search For Product by EntryDataExtras {Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command{Style.reset}'
		},
		'8':{
			'cmds':['8','sch entry data extras export','sedee'],
			'exec':self.entryDataExtrasSearchExport,
			'desc':f'{Fore.light_blue}Search For Product by EntryDataExtras And Export Selected Extra Data To QrCode for inter-cellular device communication via camera{Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command{Style.reset}'
		},
		'9':{
			'cmds':['9','sch entry export','see'],
			'exec':self.entrySearchExport,
			'desc':f'{Fore.light_blue}Search For Product by Entry Data and Export Selected Entry Data To QrCode for inter-cellular device communication via camera{Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command{Style.reset}'
		},
		'10':{
			'cmds':['10','sch entry data extras export txt','sedeet'],
			'exec':lambda self=self:self.entryDataExtrasSearchExport(txt_export=True),
			'desc':f'{Fore.light_blue}Search For Product by EntryDataExtras And Export Selected Extra Data To Txt for inter-cellular device communication via camera{Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command{Style.reset}'
		},
		'11':{
			'cmds':['11','sch entry export txt','seet'],
			'exec':lambda self=self:self.entrySearchExport(txt_export=True),
			'desc':f'{Fore.light_blue}Search For Product by Entry Data and Export Selected Entry Data To QrCode for inter-cellular device communication via camera{Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command{Style.reset}'
		},
		'12':{
			'cmds':['12','sch nones','sch na','sch n/a',],
			'exec':lambda self=self:self.entrySearchNone(),
			'desc':f'{Fore.light_blue}Search For Product by Entry Data where or_(Entry.Code==None)'
		},
		'13':{
			'cmds':['13','sch blank','schblnk','sch \'\'','sch ""','sch blnk'],
			'exec':lambda self=self:self.entrySearchBlank(),
			'desc':f'{Fore.light_blue}Search For Product by Entry Data where or_(Entry.Code=="")'
		},
		'12.b':{
			'cmds':['12.b','sch nones bcd','sch na bcd','sch n/a bcd',],
			'exec':lambda self=self:self.entrySearchNone(just_code=False),
			'desc':f'{Fore.light_blue}Search For Product by Entry Data where or_(Entry.Code==None,Entry.Barcode==None)'
		},
		'13.b':{
			'cmds':['13.b','sch blank bcd','schblnk bcd','sch \'\' bcd','sch "" bcd','sch blnk bcd'],
			'exec':lambda self=self:self.entrySearchBlank(just_code=False),
			'desc':f'{Fore.light_blue}Search For Product by Entry Data where or_(Entry.Code=="",Entry.Barcode=="")'
		},
		'12.f':{
			'cmds':['12.f','sch nones fx','sch na fx','sch n/a fx',],
			'exec':lambda self=self:self.entrySearchNone(fix=True),
			'desc':f'{Fore.light_blue}Search For Product by Entry Data where or_(Entry.Code==None) and set Entry.Code=="UNASSIGNED_TO_NEW_ITEM"'
		},
		'13.f':{
			'cmds':['13.f','sch blank fx','schblnk fx','sch \'\' fx','sch "" fx','sch blnk fx'],
			'exec':lambda self=self:self.entrySearchBlank(fix=True),
			'desc':f'{Fore.light_blue}Search For Product by Entry Data where or_(Entry.Code=="") and set Entry.Code=="UNASSIGNED_TO_NEW_ITEM"'
			}
		}
		def mehelp(self):
				for k in self.cmds:
					#print(f"{Fore.medium_violet_red}{self.cmds[k]['cmds']}{Style.reset} -{self.cmds[k]['desc']}")
					yield f"{Fore.medium_violet_red}{self.cmds[k]['cmds']}{Style.reset} -{self.cmds[k]['desc']}"
		if init_only:
			return
		while True:
			def mkT(text,self):
				return text

			mode='LU'
			fieldname='ROOT'
			h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
			cmd=Prompt.__init2__(None,func=mkT,ptext=f"{h}Do What?",helpText='\n'.join([i for i in mehelp(self)]),data=self)
			if cmd in [None,]:
				return
			#cmd=input("Do What: ")
			for i in self.cmds:
				if cmd.lower() in self.cmds[i]['cmds']:
					if cmd.lower() in self.cmds['2']['cmds']:
						return
					else:
						self.cmds[i]['exec']()
						break

	def entryDataExtrasSearchExport(self,txt_export=False):
		with Session(ENGINE) as session:
			while True:
				search=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Lookup2@Search[Entry]:",helpText="Search All(*) fields",data="string")
				if search in [None,]:
					return
				query=session.query(Entry)
				filters=[
					Entry.Barcode.icontains(search),
					Entry.Code.icontains(search),
					Entry.Name.icontains(search),
				]
				query=query.filter(or_(*filters))
				results=query.all()
				ct=len(results)
				if ct == 0:
					print("No Results")
					continue
				msg=[]
				for num,i in enumerate(results):
					#print(i)
					extras=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==i.EntryId).all()
					extras_ct=len(extras)
					
					mtext=[]
					for n,e in enumerate(extras):
						mtext.append(f"\t- {Fore.orange_red_1}{e.field_name}:{Fore.light_steel_blue}{e.field_type}={Fore.light_yellow}{e.field_value} {Fore.cyan}ede_id={e.ede_id} {Fore.light_magenta}doe={e.doe}{Style.reset}")
					mtext='\n'.join(mtext)
					msg.append(f"{Fore.light_steel_blue}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct} -> {i.seeShort()}\n{mtext}")
				msgStr='\n'.join(msg)
				print(msgStr)
				while True:
					which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which entry indexes?",helpText=msgStr,data="list")
					if which in ['d',None]:
						return
					try:
						for i in which:
							try:
								i=int(i)
								#here#
								entry=results[i]
								
								extras0=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==entry.EntryId).all()
								extras_ct0=len(extras0)
								msgStrExtra=[]
								for n,e in enumerate(extras0):
									msgStrExtra.append(f"{Fore.light_cyan}{n}/{Fore.light_yellow}{n+1} of {extras_ct0} -> {e.field_name}:{e.field_type}={e.field_value} ede_id={e.ede_id} doe={e.doe}")
								msgStrExtra='\n'.join(msgStrExtra)
								print(msgStrExtra)								
								whichExtra=Prompt.__init2__(None,func=FormBuilderMkText,ptext="export which extra index?",helpText=msgStrExtra,data="integer")
								if whichExtra in ['d',None]:
									return
								try:
									if txt_export:
										efile=detectGetOrSet("ExportExtraFileTXT","ExtraTXT.txt",setValue=False,literal=True)
										with open(efile,"w") as out:
											out.write(extras0[whichExtra].field_value)
									else:
										efile=detectGetOrSet("ExportExtraFile","ExtraQR.png",setValue=False,literal=True)
										qr=qrcode.make(extras0[whichExtra].field_value)
										qr.save(efile)
									print(f"saved {extras0[whichExtra].field_name} to {efile}!")
								except Exception as eee:
									print(eee)
							except Exception as ee:
								print(ee)
						break
					except Exception as e:
						print(e)

	def entrySearchExport(self,txt_export=False):
		with Session(ENGINE) as session:
			while True:
				search=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Lookup2@Search[Entry]:",helpText="Search All(*) fields",data="string")
				if search in [None,]:
					return
				query=session.query(Entry)
				filters=[
					Entry.Barcode.icontains(search),
					Entry.Code.icontains(search),
					Entry.Name.icontains(search),
				]
				query=query.filter(or_(*filters))
				results=query.all()
				ct=len(results)
				if ct == 0:
					print("No Results")
					continue
				msg=[]
				for num,i in enumerate(results):
					#print(i)
					extras=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==i.EntryId).all()
					extras_ct=len(extras)
					
					mtext=[]
					for n,e in enumerate(extras):
						mtext.append(f"\t- {Fore.orange_red_1}{e.field_name}:{Fore.light_steel_blue}{e.field_type}={Fore.light_yellow}{e.field_value} {Fore.cyan}ede_id={e.ede_id} {Fore.light_magenta}doe={e.doe}{Style.reset}")
					mtext='\n'.join(mtext)
					msg.append(f"{Fore.light_steel_blue}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct} -> {i.seeShort()}\n{mtext}")
				msgStr='\n'.join(msg)
				print(msgStr)
				which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which Entry index?",helpText=msgStr,data="integer")
				if which in ['d',None]:
					return
				try:
					entry=results[which]							
					try:
						
						data={i.name:getattr(entry,i.name) for i in entry.__table__.columns}
						extras=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==entry.EntryId)
						for i in extras:
							data[i.field_name]={'type':i.field_type,
												'value':i.field_value,
												}
						if txt_export:
							efile=detectGetOrSet("EntryExportTXT","EntryTXT.txt",setValue=False,literal=True)
							with open(efile,"w") as out:
								out.write(json.dumps(data))
						else:
							efile=detectGetOrSet("EntryExportQR","EntryQR.png",setValue=False,literal=True)
							qr=qrcode.make(json.dumps(data))
							qr.save(efile)
						print(f"saved {entry.seeShort()} to {efile}!")
					except Exception as eee:
						print(eee)
				except Exception as ee:
					print(ee)

	def entryDataExtrasSearch(self,longText=False):
		while True:
			with Session(ENGINE) as session:
				search=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Lookup2@Search[EntryDataExtras[Field_Name is:*,Field_Value=]]:",helpText="Search All(*) fields",data="string")
				if search in [None,]:
					return
				fieldnames=[]
				fields=[]
				ttl=session.query(EntryDataExtras).group_by(EntryDataExtras.field_name).all()
				for i in ttl:
					if i not in fieldnames:
						fieldnames.append(i.field_name)
				ct=len(fieldnames)
				fieldnamestr=[f"{num}/{num+1} of {ct} -> {i}" for num,i in enumerate(fieldnames)]
				fieldnamestr='\n'.join(fieldnamestr)
				print(fieldnamestr)
				select=Prompt.__init2__(None,func=FormBuilderMkText,ptext="what fieldnames would you like to search?",helpText=fieldnamestr,data="list")
				if select in [None,]:
					return

				query=session.query(EntryDataExtras)
				q=[]
				try:
					if select == 'd':
						select=[num for num,i in enumerate(fieldnames)]
					for i in select:
						try:
							i=int(i)
							q.append(and_(EntryDataExtras.field_name==fieldnames[i],EntryDataExtras.field_value.icontains(search)))
						except Exception as e:
							print(e)
				except Exception as e:
					print(e)
				results=session.query(EntryDataExtras).filter(or_(*q)).all()
				xct=len(results)
				disp=[]
				there=[]
				for num,i in enumerate(results):
					entry=session.query(Entry).filter(Entry.EntryId==i.EntryId).first()
					if entry:
						if entry.EntryId not in there:
							there.append(entry.EntryId)
							if longText:
								msg=f"""{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{xct} -> {entry} """
							else:
								msg=f"""{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{xct} -> {entry.seeShort()}"""
								extras=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==entry.EntryId).all()
								extras_ct=len(extras)
								if extras_ct == 0:
									print("no extras found")
								mtext=[]
								for n,e in enumerate(extras):
									mtext.append(f"\t- {Fore.orange_red_1}{e.field_name}:{Fore.light_steel_blue}{e.field_type}={Fore.light_yellow}{e.field_value} {Fore.cyan}ede_id={e.ede_id} {Fore.light_magenta}doe={e.doe}{Style.reset}")
								mtext='\n'.join(mtext)
								msg+="\n"+mtext
							if msg not in disp:
								disp.append(msg)
				print(f"\n{'-'*(os.get_terminal_size().columns-1)}\n".join(disp))
				print(f"There are {len(disp)} results found!")



	def SearchAuto(self,short=False,returnable=False,extras=False,long_search_extras=False):
		with Session(ENGINE) as session:
			while True:
				try:
					def mkT(text,self):
						return text
					fields=[i.name for i in Entry.__table__.columns if str(i.type) == "VARCHAR"]
					if not short:
						mode='SEARCH_ALL_INFO'
					else:
						mode='SEARCH_BASIC_INFO'
					fieldname='LU_ROOT'
					h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
					stext=Prompt.__init2__(None,func=mkT,ptext=f"{h}Search[*]:",helpText="Search All(*) fields",data=self)
					if stext in [None,]:
						return
					query=session.query(Entry)
					if not stext:
						break
					
					q=[]
					for f in fields:
						q.append(getattr(Entry,f).icontains(stext.lower()))

					eid=None
					try:
						eid=int(stext)
						q.append(getattr(Entry,'EntryId')==eid)
					except Exception as e:
						print(e)

					query=query.filter(or_(*q))
					results=query.all()
					
					if extras or long_search_extras:
						print(f"{Fore.orange_red_1}Extras In Use{Style.reset}"*5)
						fields2=[i.name for i in EntryDataExtras.__table__.columns if str(i.type) == "VARCHAR"]
						q2=[]
						for f in fields2:
							q2.append(getattr(EntryDataExtras,f).icontains(stext.lower()))
						results2=session.query(EntryDataExtras).filter(or_(*q2)).all()

						entry_ids_from_extras=[]
						for i in results2:
							entry_ids_from_extras.append(i.EntryId)

					finalList=[]
					if extras or long_search_extras:
						for i in entry_ids_from_extras:
							entry=session.query(Entry).filter(Entry.EntryId==i).first()
							if entry not in results:
								finalList.append(entry)
					for i in results:
						finalList.append(i)
					results=finalList
					ct=len(results)
					for num,r in enumerate(results):
						if num < round(0.25*ct,0):
							color_progress=Fore.green
						elif num < round(0.50*ct,0):
							color_progress=Fore.light_green
						elif num < round(0.75*ct,0):
							color_progress=Fore.light_yellow
						else:
							color_progress=Fore.light_red
						if num == ct - 1:
							color_progress=Fore.red
						if num == 0:
							color_progress=Fore.cyan	
						if not short:
							msg=f"{color_progress}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} ->{r}\n"
							'''
							extras=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==r.EntryId).all()
							extras_ct=len(extras)
							if extras_ct == 0:
								print("no extras found")
							mtext=[]
							for n,e in enumerate(extras):
								mtext.append(f"\t -{Fore.orange_red_1}{e.field_name}:{Fore.light_steel_blue}{e.field_type}={Fore.light_yellow}{e.field_value} {Fore.cyan}ede_id={e.ede_id} {Fore.light_magenta}doe={e.doe}{Style.reset}")
							mtext='\n'.join(mtext)
							msg+=mtext
							'''
						else:
							msg=f"{color_progress}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} ->{r.seeShort()}\n"
							if extras:
								extras_items=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==r.EntryId).all()
								extras_ct=len(extras_items)
								mtext=[]
								for n,e in enumerate(extras_items):
									mtext.append(f"\t- {Fore.orange_red_1}{e.field_name}:{Fore.light_steel_blue}{e.field_type}={Fore.light_yellow}{e.field_value} {Fore.cyan}ede_id={e.ede_id} {Fore.light_magenta}doe={e.doe}{Style.reset}")
								mtext='\n'.join(mtext)
								msg+=mtext
						print(msg)
					print(f"{Fore.light_yellow}There are {Fore.light_red}{ct}{Fore.light_yellow} Total Results for search {Fore.medium_violet_red}'{stext}'{Style.reset}{Fore.light_yellow}.{Style.reset}")
					print(f"{Fore.light_red}Fields Searched in {Fore.cyan}{fields}{Style.reset}")
					if returnable:
						return results
					session.flush()
				except Exception as e:
					print(e)

	def SearchManual(self):
		while True:
			try:
				with Session(ENGINE) as session:
					def mkT(text,self):
						return text
					fields=[i.name for i in Entry.__table__.columns if str(i.type) == "VARCHAR"]
					fields=[i.name for i in Entry.__table__.columns if str(i.type) == "VARCHAR"]
					mode='SEARCH_MNL_SRCH_TXT'
					fieldname='LU_ROOT'
					h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
					stext=Prompt.__init2__(None,func=mkT,ptext=f"{h}Search[Field(s)]:",helpText="Search for Entry by field(s)",data=self)
					if stext in [None,]:
						return
					query=session.query(Entry)
					if not stext:
						break
					
					def mkTList(text,self):
						try:
							total=[]
							f=text.split(",")
							for i in f:
								if i in self:
									if i not in total:
										total.append(i)
							return total
						except Exception as e:
							return None
					mode='SEARCH_MNL_SRCH_FLD_NMS'
					fieldname='LU_ROOT'
					h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
					to_search=f"{Fore.light_red}Fields available to Search in {Fore.cyan}{fields}{Style.reset}"
					sfields=Prompt.__init2__(None,func=mkTList,helpText=f"fields separated by a comma, or just a field from fields [Case-Sensitive]{to_search}",ptext=f"{h}fields? ",data=fields)
					if sfields in [None,]:
						return
					if not sfields:
						break


					q=[]
					
					for f in sfields:
						q.append(getattr(Entry,f).icontains(stext.lower()))

					query=query.filter(or_(*q))
					results=query.all()
					ct=len(results)
					for num,r in enumerate(results):
						if num < round(0.25*ct,0):
							color_progress=Fore.green
						elif num < round(0.50*ct,0):
							color_progress=Fore.light_green
						elif num < round(0.75*ct,0):
							color_progress=Fore.light_yellow
						else:
							color_progress=Fore.light_red
						if num == ct - 1:
							color_progress=Fore.red
						if num == 0:
							color_progress=Fore.cyan	
						msg=f"{color_progress}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} ->{r}"
						print(msg)
					print(f"{Fore.light_yellow}There are {Fore.light_red}{ct}{Fore.light_yellow} Total Results for search {Fore.medium_violet_red}'{stext}'{Style.reset}{Fore.light_yellow}.{Style.reset}")
					print(f"{Fore.light_red}Fields Searched in {Fore.cyan}{sfields}{Style.reset}")
			except Exception as e:
				print(e)

	def search(self):
		while True:
			try:
				mode='SEARCH_BY_BCD_OR_SHF'
				fieldname='LU_ROOT'
				h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
				def mkT(text,self):
					return text
				code=Prompt.__init2__(None,func=mkT,ptext=f"{h}Code/Barcode To Search For?",helpText="b/q/code/barcode",data=self)
				if code in [None,]:
					return
				print(f"{Fore.green}{Style.underline}Lookup Initialized...{Style.reset}")
				if code.lower() in self.cmds['1']['cmds']:
					self.cmds['1']['exec']()
				elif code.lower() in self.cmds['2']['cmds']:
					break
				else:
					with Session(ENGINE) as session:	
						query=session.query(Entry).filter(or_(Entry.Barcode==code,Entry.Code==code,Entry.ALT_Barcode==code))
						results=query.all()
						for num,r in enumerate(results):
							print(f'{Fore.red}{num}{Style.reset}/{Fore.green}{len(results)}{Style.reset} -> {r}')
						print(f"{Fore.cyan}There were {Fore.green}{Style.bold}{len(results)}{Style.reset} {Fore.cyan}results.{Style.reset}")
			except Exception as e:
				print(e)