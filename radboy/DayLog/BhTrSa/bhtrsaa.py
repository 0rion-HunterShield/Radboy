from . import *
import uuid
class BhTrSa_Gui:

	def next_saa(self):
		with Session(ENGINE) as session:
			now=datetime.now()
			query=session.query(Scheduled_And_Appointments)
			date_filtered_query=query.filter(or_(
				and_(Scheduled_And_Appointments.StartDate!=None,Scheduled_And_Appointments.StartDate>=date(now.year,now.month,now.day)),
				and_(Scheduled_And_Appointments.StartDateTime !=None,Scheduled_And_Appointments.StartDateTime>=datetime(now.year,now.month,now.day))
				)
			)

			#ordered_query=date_filtered_query.order_by(Scheduled_And_Appointments.StartDate.asc(),Scheduled_And_Appointments.StartDateTime.asc())

			most_recent_x=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"How many results(default=3)?:",helpText="an integer",data="integer")
			if most_recent_x is None:
				return
			elif most_recent_x in ['d']:
				most_recent_x=3
			
			offset=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Offset to First, or Last, of Results by X(default=0):",helpText="an integer",data="integer")
			if offset is None:
				return
			elif offset in ['d']:
				offset=0

			lu_state=db.detectGetOrSet('list maker lookup order',False,setValue=False,literal=False)
			if not lu_state:	
				ordered_query=date_filtered_query.order_by(Scheduled_And_Appointments.StartDate.asc(),Scheduled_And_Appointments.StartDateTime.asc())
			else:
				ordered_query=date_filtered_query.order_by(Scheduled_And_Appointments.StartDate.desc(),Scheduled_And_Appointments.StartDateTime.desc())
			limited_query=ordered_query.limit(most_recent_x)
			offset_query=limited_query.offset(offset)
			results=offset_query.all()
			ct=len(results)
			for num,i in enumerate(results):
				print(i.colorize(i,num,ct))


	def search_saa(self,returnable=False):
		display_past_due=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Display past due SAA's[False==Default]?",helpText="boolean yes or no[default]",data="boolean")
		if display_past_due is None:
			return
		elif display_past_due in ['d',False]:
			display_past_due=False
		else:
			display_past_due=True

		most_recent_x=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Limit to First, or Last, of Results by X(default={sys.maxsize}):",helpText="an integer",data="integer")
		if most_recent_x is None:
			return
		elif most_recent_x in ['d']:
			most_recent_x=sys.maxsize
		
		offset=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Offset to First, or Last, of Results by X(default=0):",helpText="an integer",data="integer")
		if offset is None:
			return
		elif offset in ['d']:
			offset=0

		stext=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What are you looking for?",helpText="a textwise search, but may include saa_id",data="string")
		if stext in  [None,]:
			return
		lu_state=db.detectGetOrSet('list maker lookup order',False,setValue=False,literal=False)
		includes=["varchar","string","str","text"]
		sfields=[str(i.name) for i in BusinessHours.__table__.columns if str(i.type).lower() in includes]
		with Session(ENGINE) as session:
			def mquery(lu_state,display_past_due,squery,offset,most_recent_x):
				if not lu_state:	
					sorted_query=squery.order_by(Scheduled_And_Appointments.StartDate.asc(),Scheduled_And_Appointments.StartDateTime.asc(),Scheduled_And_Appointments.DTOE.asc())
				else:
					sorted_query=squery.order_by(Scheduled_And_Appointments.StartDate.desc(),Scheduled_And_Appointments.StartDateTime.desc(),Scheduled_And_Appointments.DTOE.desc())
				now=datetime.now()
				if not display_past_due:
					sorted_query=sorted_query.filter(or_(
						and_(Scheduled_And_Appointments.StartDate!=None,Scheduled_And_Appointments.StartDate>=date(now.year,now.month,now.day)),
						and_(Scheduled_And_Appointments.StartDateTime !=None,Scheduled_And_Appointments.StartDateTime>=datetime(now.year,now.month,now.day))
						)
					)
				else:
					sorted_query=sorted_query.filter(or_(
						and_(Scheduled_And_Appointments.StartDate!=None,Scheduled_And_Appointments.StartDate<=date(now.year,now.month,now.day)),
						and_(Scheduled_And_Appointments.StartDateTime !=None,Scheduled_And_Appointments.StartDateTime<=datetime(now.year,now.month,now.day))
						)
					)
				limited_query=sorted_query.offset(offset).limit(most_recent_x)
				
				return limited_query

			query=session.query(Scheduled_And_Appointments)
			
			def stage2(query,sfields,stext):
				q=[]
				if stext != 'd':
					for i in sfields:
						q.append(getattr(Scheduled_And_Appointments,i).icontains(stext))
					squery=query.filter(or_(*q))
				else:
					squery=query
				return squery

			try:
				print(stext)
				if stext != 'd':
					print(stext)
					SAA_id=int(stext)
					squery=query.filter(Scheduled_And_Appointments.saa_id==SAA_id)
				else:
					squery=stage2(query,sfields,stext)
					squery=mquery(lu_state,display_past_due,squery,offset,most_recent_x)
			except Exception as e:
				print(f"{Fore.light_red}could not use '{stext}' as saa_id{Fore.light_steel_blue} this is not a failure{Style.reset}",e,repr(e))
				squery=stage2(query,sfields,stext)
				squery=mquery(lu_state,display_past_due,squery,offset,most_recent_x)
			
			results=squery.all()	
			#sorted_query.all()
			ct=len(results)
			htext=[]
			if ct == 0:
				print("No Results were found")
				return
			for num,i in enumerate(results):
				htext.append(i.colorize(i,num,ct))
			htext='\n'.join(htext)
			print(htext)
			if returnable:
				while True:
					try:
						which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which index(es) to yield?",helpText=htext,data="list")
						if which in [None,'d']:
							return
						for i in which:
							try:
								index=int(i)
								yield results[index].saa_id
							except Exception as e:
								print(e)
						break
					except Exception as e:
						print(e)

	def search_business_hours(self,returnable=False):
		stext=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What are you looking for?",helpText="a textwise search",data="string")
		if stext in  [None,]:
			return
		lu_state=db.detectGetOrSet('list maker lookup order',False,setValue=False,literal=False)
		includes=["varchar","string","str","text"]
		sfields=[str(i.name) for i in BusinessHours.__table__.columns if str(i.type).lower() in includes]
		with Session(ENGINE) as session:
			query=session.query(BusinessHours)
			q=[]
			print(stext)
			if stext != 'd':
				for i in sfields:
					q.append(getattr(BusinessHours,i).icontains(stext))
				squery=query.filter(or_(*q))
			else:
				squery=query

			if lu_state:	
				sorted_query=squery.order_by(BusinessHours.DTOE.asc())
			else:
				sorted_query=squery.order_by(BusinessHours.DTOE.desc())

			results=sorted_query.all()
			ct=len(results)
			htext=[]
			if ct == 0:
				print("No Results were found")
				return
			for num,i in enumerate(results):
				htext.append(i.colorize(i,num,ct))
			htext='\n'.join(htext)
			print(htext)
			if returnable:
				while True:
					try:
						which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which index(es) to yield?",helpText=htext,data="list")
						if which in [None,'d']:
							return
						for i in which:
							try:
								index=int(i)
								yield results[index].bhid
							except Exception as e:
								print(e)
						break
					except Exception as e:
						print(e)

	def search_taxrates(self,returnable=False):
		stext=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What are you looking for?",helpText="a textwise search",data="string")
		if stext in  [None,]:
			return
		lu_state=db.detectGetOrSet('list maker lookup order',False,setValue=False,literal=False)
		includes=["varchar","string","str","text"]
		sfields=[str(i.name) for i in TaxRates.__table__.columns if str(i.type).lower() in includes]
		with Session(ENGINE) as session:
			query=session.query(TaxRates)
			q=[]
			if stext != 'd':
				for i in sfields:
					q.append(getattr(TaxRates,i).icontains(stext))
				squery=query.filter(or_(*q))
			else:
				squery=query
			if lu_state:	
				sorted_query=squery.order_by(TaxRates.DTOE.asc())
			else:
				sorted_query=squery.order_by(TaxRates.DTOE.desc())

			results=sorted_query.all()
			ct=len(results)
			htext=[]
			if ct == 0:
				print("No Results were found")
				return
			for num,i in enumerate(results):
				htext.append(i.colorize(i,num,ct))
			htext='\n'.join(htext)
			print(htext)
			if returnable:
				while True:
					try:
						which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which index(es) to yield?",helpText=htext,data="list")
						if which in [None,'d']:
							return
						for i in which:
							try:
								index=int(i)
								yield results[index].trid
							except Exception as e:
								print(e)
						break
					except Exception as e:
						print(e)

	def edit_taxrates(self):
		excludes=['trid','DTOE']
		with Session(ENGINE) as session:
			ids=self.search_taxrates(returnable=True)
			if ids is None:
				return
			for ID in ids:
				newBH=session.query(TaxRates).filter(TaxRates.trid==ID).first()
				fields={
				i.name:{'default':getattr(newBH,i.name),'type':str(i.type).lower()} for i in newBH.__table__.columns if str(i.name) not in excludes
				}
				fd=FormBuilder(data=fields)
				if fd is None:
					return
				for i in fd:
					setattr(newBH,i,fd[i])
				session.commit()
				session.refresh(newBH)
				print(newBH.colorize(newBH,0,1))

	def edit_business_hours(self):
		excludes=['bhid','DTOE']
		with Session(ENGINE) as session:
			ids=self.search_business_hours(returnable=True)
			if ids is None:
				return
			for ID in ids:
				newBH=session.query(BusinessHours).filter(BusinessHours.bhid==ID).first()
				fields={
				i.name:{'default':getattr(newBH,i.name),'type':str(i.type).lower()} for i in newBH.__table__.columns if str(i.name) not in excludes
				}
				fd=FormBuilder(data=fields)
				if fd is None:
					return
				for i in fd:
					setattr(newBH,i,fd[i])
				session.commit()
				session.refresh(newBH)
				print(newBH.colorize(newBH,0,1))	

	def edit_saa(self):
		excludes=['saa_id','DTOE']
		with Session(ENGINE) as session:
			ids=self.search_saa(returnable=True)
			if ids is None:
				return
			for ID in ids:
				newBH=session.query(Scheduled_And_Appointments).filter(Scheduled_And_Appointments.saa_id==ID).first()
				fields={
				i.name:{'default':getattr(newBH,i.name),'type':str(i.type).lower()} for i in newBH.__table__.columns if str(i.name) not in excludes
				}
				fd=FormBuilder(data=fields)
				if fd is None:
					return
				for i in fd:
					setattr(newBH,i,fd[i])
				session.commit()
				session.refresh(newBH)
				print(newBH.colorize(newBH,0,1))	


	def protect(self):
		h=self.__class__.__name__
		code=''.join([str(random.randint(0,9)) for i in range(10)])
		verification_protection=detectGetOrSet("Protect From Delete",code,setValue=False,literal=True)
		while True:
			try:
				really=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h}Really Delete this BusinessHours entry?",helpText="yes or no boolean,default is NO",data="boolean")
				if really in [None,]:
					print(f"{Fore.light_steel_blue}Nothing was {Fore.orange_red_1}{Style.bold}Deleted!{Style.reset}")
					return True
				elif really in ['d',False]:
					print(f"{Fore.light_steel_blue}Nothing was {Fore.orange_red_1}{Style.bold}Deleted!{Style.reset}")
					return True
				else:
					pass
				really=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"To {Fore.orange_red_1}Delete it completely, {Fore.light_steel_blue}what is today's date?[{'.'.join([str(int(i)) for i in datetime.now().strftime("%m.%d.%y").split(".")])}]{Style.reset}",helpText="type y/yes for prompt or type as m.d.Y",data="datetime")
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
		return True

	def rm_business_hours(self):
		excludes=['bhid','DTOE']
		with Session(ENGINE) as session:
			ids=self.search_business_hours(returnable=True)
			if ids is None:
				return
			state=None
			for ID in ids:
				if state == None:
					state=self.protect()
				if state != True:
					break
				newBH=session.query(BusinessHours).filter(BusinessHours.bhid==ID).first()
				session.delete(newBH)
				session.commit()
					
	def rm_taxrates(self):
		excludes=['trid','DTOE']
		with Session(ENGINE) as session:
			ids=self.search_taxrates(returnable=True)
			if ids is None:
				return
			state=None
			for ID in ids:
				if state == None:
					state=self.protect()
				if state != True:
					break
				newBH=session.query(TaxRates).filter(TaxRates.trid==ID).first()
				session.delete(newBH)
				session.commit()

	def rm_saa(self):
		excludes=['saa_id','DTOE']
		with Session(ENGINE) as session:
			ids=self.search_saa(returnable=True)
			if ids is None:
				return
			state=None
			for ID in ids:
				if state == None:
					state=self.protect()
				if state != True:
					break
				newBH=session.query(Scheduled_And_Appointments).filter(Scheduled_And_Appointments.saa_id==ID).first()
				session.delete(newBH)
				session.commit()


	def new_business_hours(self):
		with Session(ENGINE) as session:
			newBH=BusinessHours()
			excludes=['bhid','DTOE']
			fields={
			i.name:{'default':getattr(newBH,i.name),'type':str(i.type).lower()} for i in newBH.__table__.columns if str(i.name) not in excludes
			}
			fd=FormBuilder(data=fields)
			if fd is None:
				return
			for i in fd:
				setattr(newBH,i,fd[i])
			session.add(newBH)
			session.commit()
			session.refresh(newBH)
			print(newBH.colorize(newBH,0,1))

	def new_taxrates(self):
		with Session(ENGINE) as session:
			newBH=TaxRates()
			excludes=['trid','DTOE']
			fields={
			i.name:{'default':getattr(newBH,i.name),'type':str(i.type).lower()} for i in newBH.__table__.columns if str(i.name) not in excludes
			}
			fd=FormBuilder(data=fields)
			if fd is None:
				return
			for i in fd:
				setattr(newBH,i,fd[i])
			session.add(newBH)
			session.commit()
			session.refresh(newBH)
			print(newBH.colorize(newBH,0,1))

	def new_saa(self):
		with Session(ENGINE) as session:
			newBH=Scheduled_And_Appointments()
			excludes=['saa_id','DTOE']
			fields={
			i.name:{'default':getattr(newBH,i.name),'type':str(i.type).lower()} for i in newBH.__table__.columns if str(i.name) not in excludes
			}
			fd=FormBuilder(data=fields)
			if fd is None:
				return
			
			for i in fd:
				setattr(newBH,i,fd[i])

			session.add(newBH)
			session.commit()
			session.refresh(newBH)
			print(newBH.colorize(newBH,0,1))

	def saa_proxy(self):
		for i in self.search_saa():
			print(i)

	def str_proxy(self):
		for i in self.search_taxrates():
			print(i)
	
	def sbh_proxy(self):
		for i in self.search_business_hours():
			print(i)

	def __init__(self):
		print(Entry.cfmt(None,self.__class__.__name__))
		cmds={
			uuid.uuid1():{
			'cmds':['sbh','search business hours'],
			'exec':self.sbh_proxy,
			'desc':"search and list business hours"
			},
			uuid.uuid1():{
			'cmds':['nbh','new business hours'],
			'exec':self.new_business_hours,
			'desc':"create a business hours entry"
			},
			uuid.uuid1():{
			'cmds':['ebh','edit business hours'],
			'exec':self.edit_business_hours,
			'desc':"edit a business hours entry"
			},
			uuid.uuid1():{
			'cmds':['rmbh','rm business hours'],
			'exec':self.rm_business_hours,
			'desc':"remove a business hours entry"
			},

			uuid.uuid1():{
			'cmds':['str','search tax rates'],
			'exec':self.str_proxy,
			'desc':"search and list tax rates "
			},
			uuid.uuid1():{
			'cmds':['ntr','new tax rates'],
			'exec':self.new_taxrates,
			'desc':"create a  tax rates entry"
			},
			uuid.uuid1():{
			'cmds':['etr','edit  '],
			'exec':self.edit_taxrates,
			'desc':"edit a  tax rates entry"
			},
			uuid.uuid1():{
			'cmds':['rmtr','rm  '],
			'exec':self.rm_taxrates,
			'desc':"remove a tax rates  entry"
			},

			uuid.uuid1():{
			'cmds':['ssaa','search schedules and appointments'],
			'exec':self.saa_proxy,
			'desc':"search and list schedules and appointments "
			},
			uuid.uuid1():{
			'cmds':['nsaa','new schedules and appointments'],
			'exec':self.new_saa,
			'desc':"create a  schedules and appointments entry"
			},
			uuid.uuid1():{
			'cmds':['esaa','edit schedules and appointments'],
			'exec':self.edit_saa,
			'desc':"edit a chedules and appointments entry"
			},
			uuid.uuid1():{
			'cmds':['rmsaa','rm schedules and appointments'],
			'exec':self.rm_saa,
			'desc':"remove a schedules and appointments entry"
			},
			uuid.uuid1():{
			'cmds':['nxt saa','next schedules and appointments'],
			'exec':self.next_saa,
			'desc':"display next x of schedules and appointments entry that are not past due"
			},
		}
		htext=[]
		for cmd in cmds:
			msg=f"{Fore.cornflower_blue}{','.join(cmds[cmd]['cmds'])} {Fore.grey_70}-{Fore.cyan} {cmds[cmd]['desc']}{Style.reset}"
			htext.append(msg)
		htext='\n'.join(htext)
		while True:
			doWhat=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{self.__class__.__name__}:Do What",helpText=htext,data="string")
			if doWhat in [None,]:
				return
			elif doWhat.lower() in ['d',]:
				print(htext)
				continue
			for cmd in cmds:
				if doWhat.lower() in [i.lower() for i in cmds[cmd]['cmds']]:
					if callable(cmds[cmd]['exec']):
						cmds[cmd]['exec']()


		