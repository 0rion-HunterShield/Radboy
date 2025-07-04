from . import *

class RepeatableDatesUi:
	def create_new_dt(self):
		with Session(ENGINE) as session:
			rd=RepeatableDates()
			excludes=['rd_id','DTOE','Go_By_WeekDayNames','WeekDayNames']
			fields={
				i.name:{'default':getattr(rd,i.name),'type':str(i.type).lower()} for i in rd.__table__.columns if i.name not in excludes
			}
			fd=FormBuilder(data=fields)
			

			if fd is None:
				print(f"{Fore.orange_red_1}User cancelled early!{Style.reset}")
				return
			fd['Go_By_WeekDayNames']=False
			for k in fd:
				setattr(rd,k,fd[k])
			session.add(rd)
			session.commit()
			session.flush()
			session.refresh(rd)
			print(rd)

	def create_new_wd(self):
		with Session(ENGINE) as session:
			rd=RepeatableDates()
			
			excludes=['rd_id','DTOE','DTORX','Go_By_WeekDayNames','WeekDayNames']
			weekdays=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
			ct=len(weekdays)
			weekdays_ct=len(weekdays)

			htext=[std_colorize(i,num,ct) for num,i in enumerate(weekdays)]
			htext='\n'.join(htext)
			print(htext)
			weekday_names=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which indexes?",helpText=htext,data="list")
			if weekday_names is None:
				return
			if weekday_names in ['d',[]]:
				return
			tmp=[]
			try:
				for i in weekday_names:
					try:
						index=int(i)
						tmp.append(weekdays[index])
					except Exception as e:
						print(e)
				weekday_names=tmp
			except Exception as e:
				print("Could not continue as an error occured in translating indexes to name strings",e)
				return

			#check for valid daynames
			#check to ensure its a valid list

			fields={
			i.name:{'default':getattr(rd,i.name),'type':str(i.type).lower()} for i in rd.__table__.columns if i.name not in excludes
			}
			fd=FormBuilder(data=fields)
			if fd is None:
				print(f"{Fore.orange_red_1}User cancelled early!{Style.reset}")
				return
			fd['Go_By_WeekDayNames']=True
			fd['WeekDayNames']=json.dumps(weekday_names)

			for k in fd:
				setattr(rd,k,fd[k])
			session.add(rd)
			session.commit()
			session.flush()
			session.refresh(rd)
			print(rd)

	def searchText(self,query):
		searchText=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search Text: ",helpText="text to look for",data="string")
		if searchText is None:
			return None
		elif searchText in ['d',' ','*']:
			return query

		invertSearch=Prompt.__init2__(None,func=FormBuilderMkText,ptext="do not include[y/n]: ",helpText="yes or no",data="boolean")
		if invertSearch is None:
			return None
		elif invertSearch in ['d',]:
			invertSearch=False			

		searchable=['string','varchar','text','str']
		#print("throate")
		textfields=[i.name for i in RepeatableDates.__table__.columns if str(i.type).lower() in searchable]
		q=[]
		for i in textfields:
			if not invertSearch:
				q.append(
					getattr(RepeatableDates,i).icontains(searchText)
					)
			else:
				q.append(
					not_(getattr(RepeatableDates,i).icontains(searchText)),
					)
		#print("throate 1")
		try:
			idx=int(searchText)
			if not invertSearch:
				q.append(RepeatableDates.rd_id==idx)
			else:
				q.append(not_(RepeatableDates.rd_id==idx))
		except Exception as e:
			print(e)

		if not invertSearch:
			query=query.filter(or_(*q))
		else:
			query=query.filter(and_(*q))
		return query

	def orderDisplay(self,query,asString=False,asList=False):
		tmp=[]
		tmp_list=[]
		query=orderQuery(query,RepeatableDates.DTOE,inverse=True).all()
		ct=len(query)
		if ct > 0:
			for num,i in enumerate(query):
				msg=f"{std_colorize(i,num,ct)}"
				if not asString or not asList or ( not asList and not asString):
					print(msg)
				else:
					tmp.append(msg)
					tmp_list.append(i)
			if asList and not asString:
				return tmp_list
			elif asString and not asList:
				return '\n'.join(tmp)
			elif asString and asList:
				return tmp_list,'\n'.join(tmp)
		else:
			print("Nothing is Stored!")

	def list_dtorx_upcoming(self):
		with Session(ENGINE) as session:
			today=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What is today",helpText="any date that you wish to use as the date of today",data="datetime")
			if today is None:
				return
			elif today in ['d',]:
				today=datetime.now()
			query=session.query(RepeatableDates).filter(and_(RepeatableDates.Go_By_WeekDayNames==False,RepeatableDates.DTORX>=today))
			self.orderDisplay(query)

	def list_dtorx_expired(self):
		with Session(ENGINE) as session:
			today=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What is today",helpText="any date that you wish to use as the date of today",data="datetime")
			if today is None:
				return
			elif today in ['d',]:
				today=datetime.now()
			query=session.query(RepeatableDates).filter(and_(RepeatableDates.Go_By_WeekDayNames==False,RepeatableDates.DTORX<=today))
			self.orderDisplay(query)

	def list_all(self):
		with Session(ENGINE) as session:
			query=session.query(RepeatableDates)

			query=self.searchText(query)
			if query is None:
				return

			query=orderQuery(query,RepeatableDates.DTOE,inverse=True)
			self.orderDisplay(query)

	def list_today_of_weekdays(self):
		with Session(ENGINE) as session:
			today=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What is today?",helpText="any date that you wish to use as the date of today",data="datetime")
			if today is None:
				return
			elif today in ['d',]:
				today=datetime.now()
			
			todaysDayName=today.strftime("%A").lower()
			print(f"Today is a {todaysDayName}.")
			query=session.query(RepeatableDates).filter(and_(RepeatableDates.Go_By_WeekDayNames==True,RepeatableDates.WeekDayNames.icontains(todaysDayName)))


			self.orderDisplay(query)


	def remove(self):
		with Session(ENGINE) as session:
			query=session.query(RepeatableDates)

			query=self.searchText(query)
			if query is None:
				return

			query=orderQuery(query,RepeatableDates.DTOE,inverse=True)
			searched_list,searched_str=self.orderDisplay(query,asString=True,asList=True)
			print(searched_str)
			which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Which indexes to delete?",helpText=searched_str,data="list")
			if which is None:
				return
			elif which in ['d',[]]:
				return
			try:
				for i in which:
					try:
						index=int(i)
						print(searched_list[index])
						session.delete(searched_list[index])
						session.commit()
					except Exception as ee:
						print(ee)

			except Exception as e:
				print(e)


	def fix_table(self):
		RepeatableDates.__table__.drop(ENGINE)
		RepeatableDates.metadata.create_all(ENGINE)


	def __init__(self):
		cmds={
		uuid1():{
			'cmds':generate_cmds(startcmd=['create new','cn','cnw'],endCmd=['datetime','dt','date time']),
			'desc':"create a repeatable date with datetime",
			'exec':self.create_new_dt,
			},
			uuid1():{
			'cmds':generate_cmds(startcmd=['create new','cn','cnw'],endCmd=['wd','weekdays','week days','wk dys','wkdys']),
			'desc':"create a repeatable date with datetime",
			'exec':self.create_new_wd,
			},
			uuid1():{
			'cmds':generate_cmds(startcmd=['list','ls','lst'],endCmd=['all','a','*']),
			'desc':"lists everything! orders by DTOE",
			'exec':self.list_all,
			},
			uuid1():{
			'cmds':generate_cmds(startcmd=['list','ls','lst'],endCmd=['week day daily','wdd','wk dy dly','today is day of weekdays','tdy is dy of wkdys','tidow']),
			'desc':"lists today of from weekdays! orders by DTOE",
			'exec':self.list_today_of_weekdays,
			},
			uuid1():{
			'cmds':generate_cmds(startcmd=['list','ls','lst'],endCmd=['dtorx uc','dtorx upcoming','dtorxuc','dtorx+']),
			'desc':"list upcoming with dtorx! orders by DTOE",
			'exec':self.list_dtorx_upcoming,
			},
			uuid1():{
			'cmds':generate_cmds(startcmd=['list','ls','lst'],endCmd=['dtorx exp','dtorx expired','dtorxexp','dtorxx-']),
			'desc':"list expired with dtorx! orders by DTOE",
			'exec':self.list_dtorx_expired,
			},
			uuid1():{
			'cmds':generate_cmds(startcmd=['fix','fx'],endCmd=['tbl','table']),
			'desc':"reinstall table",
			'exec':self.fix_table,
			},
			uuid1():{
			'cmds':generate_cmds(startcmd=['rm','delete','del','remove','rmv'],endCmd=['',]),
			'desc':"delete a RepeatableDate",
			'exec':self.remove,
			},

		}
		htext=[]
		ct=len(cmds)
		for num,i in enumerate(cmds):
			m=f"{Fore.light_sea_green}{cmds[i]['cmds']}{Fore.orange_red_1} - {Fore.light_steel_blue}{cmds[i]['desc']}"
			msg=f"{std_colorize(m,num,ct)}"
			htext.append(msg)
		htext='\n'.join(htext)
		while True:
			doWhat=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{self.__class__.__name__} @ Do What? ",helpText=htext,data="string")
			if doWhat is None:
				return
			elif doWhat in ['','d',]:
				print(htext)
				continue
			for i in cmds:
				if doWhat.lower() in [i.lower() for i in cmds[i]['cmds']]:
					if callable(cmds[i]['exec']):
						cmds[i]['exec']()
					else:
						print(f"{i} - {cmds[i]['cmds']} - {cmds[i]['exec']}() - {cmds[i]['desc']}")
						return