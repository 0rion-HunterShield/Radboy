from . import *

class Streets(BASE,Template):
	__tablename__="Streets"
	StreetId=Column(Integer,primary_key=True)
	StreetAddressRole=Column(String,default="What is this addressed used as/Business/Company/Organization Name, etc...(If Any)")
	StreetAddress=Column(String,default='Street Address(If Any)')
	StreetAddressOwner=Column(String,default='Street Address Owner(If Any)')
	StreetName=Column(String,default='Street Name(If Any)')
	City=Column(String,default='City Name(If Any)')
	State=Column(String,default='State of City(If Any)')
	ZipCode=Column(String,default='xxxxx-xxxx(If Any)')
	DTOE=Column(DateTime,default=datetime.now())

	def __init__(self,**kwargs):
		for k in kwargs.keys():
			if k in [s.name for s in self.__table__.columns]:
				setattr(self,k,kwargs.get(k))

class GeoTrip(BASE,Template):
	__tablename__="GeoTrip"
	gtid=Column(Integer,primary_key=True)

	StreetId=Column(Integer)
	TripName=Column(String)
	
	Latest=Column(Boolean,default=False)
	#none = not started
	#false = started and in progress
	#true = started and finished
	SearchState=Column(Boolean,default=None)

	#to calculate time taken
	SearchStartDT=Column(DateTime,default=None)
	SearchEndDT=Column(DateTime,default=None)

	#precise location data
	StartLatitude=Column(Integer)
	StartLongitude=Column(Integer)
	StartAltitude=Column(Integer)

	EndLatitude=Column(Integer)
	EndLongitude=Column(Integer)
	EndAltitude=Column(Integer)

	#actual distance traveled
	DistanceTraveled=Column(Float,default=0)
	#accumulated costs from trip
	TransitCostsTotal=Column(Float,default=0)

	DTOE=Column(DateTime,default=datetime.now())

	#what was used to make the trip for a vehicle, if any
	ModeOfTransit=Column(String,default="Bike")

	def __init__(self,**kwargs):
		for k in kwargs.keys():
			if k in [s.name for s in self.__table__.columns]:
				setattr(self,k,kwargs.get(k))

class TripCosts(BASE,Template):
	__tablename__="TripCosts"
	tcid=Column(Integer,primary_key=True)
	gtid=Column(Integer)
	CostName=Column(String,default="Cost Name")
	Cost=Column(Float,default=0)
	Comment=Column(String,default="blah blah blaaahhh!!!")

	def __init__(self,**kwargs):
		for k in kwargs.keys():
			if k in [s.name for s in self.__table__.columns]:
				setattr(self,k,kwargs.get(k))
TripCosts.metadata.create_all(ENGINE)
GeoTrip.metadata.create_all(ENGINE)
Streets.metadata.create_all(ENGINE)

class GeoMapClass:
	def addTripCost(self):
		with Session(ENGINE) as session:
			tcost=TripCosts()
			session.add(tcost)
			session.commit()
			session.refresh(tcost)
			gtid=self.SearchTrip(select=True,one=True,everything=True)
			data={
			'CostName':{
			'default':tcost.CostName,
			'type':'string'
			},
			'Cost':{
			'default':tcost.Cost,
			'type':"float",
			},
			"Comment":{
			"type":"String",
			"default":tcost.Comment
			}
			}
			fd=FormBuilder(data=data)
			fd['gtid']=gtid
			if data in [None,]:
				session.delete(tcost)
				session.commit()
			for i in fd:
				setattr(tcost,i,fd[i])
				session.commit()
			session.commit()
			session.refresh(tcost)
			self.updateCosts(gtid,session)

	def updateCosts(self,gtid,session):
		costs=session.query(TripCosts).filter(TripCosts.gtid==gtid).all()
		geotrip=session.query(GeoTrip).filter(GeoTrip.gtid==gtid).first()
		if geotrip:
			geotrip.TransitCostsTotal=0
			for i in costs:
				geotrip.TransitCostsTotal+=i.Cost
				session.commit()
			session.commit()
			session.refresh(geotrip)
	def rmCostFromGtid(self):
		gtid=self.SearchTrip(select=True,one=True,everything=True)
		with Session(ENGINE) as session:
			results=session.query(TripCosts).filter(TripCosts.gtid==gtid).all()
			ct=len(results)
			htext=""
			for num,i in enumerate(results):
				msg=f"""{self.colorized(i,num,ct)} {Fore.light_cyan}{i.CostName} - {i.Cost} - {i.Comment}"""
				htext+=f"{msg}\n"
				print(msg)
			which=Prompt.__init2__(self,func=FormBuilderMkText,ptext="Which index(es): ",helpText=htext,data="list")
			if which in [None,]:
				return
			try:
				for i in which:
					try:
						index=int(i)
						session.delete(results[index])
						session.commit()
					except Exception as e:
						print(e)
			except Exception as e:
				print(e)
			self.updateCosts(gtid,session)
			session.commit()

		
	def rm_trip(self):
		tripids=self.SearchTrip(select=True,everything=True)
		with Session(ENGINE) as session:
			for tripid in tripids: 
				session.query(GeoTrip).filter(GeoTrip.gtid==tripid).delete()
				session.commit()
			session.commit()

	def new_trip(self):
		with Session(ENGINE) as session:
			
			data={
			'TripName':{
				'type':'string',
				'default':f'New Trip {datetime.now()}'
				},
			'ModeOfTransit':{
				'type':'string',
				'default':'Bike'
				},
			'TransitCostsTotal':{
				'type':'float',
				'default':0,
				},
			}
			fd=FormBuilder(data=data)
			if not fd:
				print("User Cancelled!")
				return
			fd['DTOE']=datetime.now()
			while True:
				street_id=self.streetSearch(select=True,one=True)
				if street_id != None:
					break
				else:
					again=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search Again?",helpText="true or false boolean [1/t/true/yes/or any other random string that is not after the bar | 0,f,false,no]",data="boolean")
					if again in [None]:
						print("User Cancelled!")
						return
					if not again:
						return

			if street_id != None:
				fd['StreetId']=street_id
				fd['SearchState']=None
				gtrip=GeoTrip(**fd)
				session.add(gtrip)
				session.commit()
				session.refresh(gtrip)
				print(gtrip)

	def trip_colors(self,i):
		return f'''{Fore.orange_red_1}{i.TripName} [{Fore.orange_3}{i.ModeOfTransit}{Fore.orange_red_1}] {Fore.spring_green_3a}${Fore.cyan}{i.TransitCostsTotal}{Style.reset}'''

	def SearchTrip(self,select=False,one=False,everything=False):
		search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search Trip Name: ",helpText="search name",data="string")
		if search in [None,]:
			print("User Cancelled!")
			return
		with Session(ENGINE) as session:
			if search.lower() in ['*','all','','d']:
				query=session.query(GeoTrip)
			else:
				query=session.query(GeoTrip).filter(or_(GeoTrip.TripName==search.lower(),GeoTrip.TripName.icontains(search))).order_by(GeoTrip.DTOE)
			results=query.all()
			ct=len(results)
			helpText=''
			for num,i in enumerate(results):
				street=session.query(Streets).filter(Streets.StreetId==i.StreetId).first()
				if street:
					street_name=f'{Fore.medium_violet_red}{street.StreetAddress} {street.StreetName}, {street.City}, {street.State} {street.ZipCode}{Style.reset}'
				msg=f'{self.colorized(i,num,ct)} - {self.trip_colors(i)} [{street_name}]'
				if everything:
					print(i,street)
					if i.SearchStartDT and i.SearchEndDT:
						print(f'''{Fore.light_green}Transit Time was:{Fore.light_yellow}{i.SearchEndDT-i.SearchStartDT} {Style.reset}''')
				helpText+=msg+"\n"
				print(msg)
				costs=session.query(TripCosts).filter(TripCosts.gtid==i.gtid).all()
				costs_ct=len(costs)
				for num,i in enumerate(costs):
					msg=f'''{Fore.dark_goldenrod}Cost {self.colorized(i,num,costs_ct)} {Fore.light_red}{i.CostName} {Fore.light_green}${i.Cost} - {Fore.cyan}{i.Comment}{Style.reset}'''
					print(msg)
			if select:
				which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{Fore.light_green}Trip Search Select| {Fore.light_yellow}Which index(es[Comma Separated])",helpText=helpText,data="list")
				if which in [None,]:
					return
				elif which in [[],'d']:
					return []
				else:
					try:
						tmp=[]
						for i in which:
							try:
								INDEX=int(i)
								if INDEX in range(0,len(results)) and INDEX not in tmp:
									tmp.append(results[INDEX].gtid)
							except Exception as ee:
								print(ee)
						if one:
							if len(tmp) > 0:
								return tmp[0]
							else:
								return None
						return tmp
					except Exception as e:
						print(e)
					return []

	def start_trip(self):
		tripid=self.SearchTrip(select=True,one=True)
		with Session(ENGINE) as session:
			trip=session.query(GeoTrip).filter(GeoTrip.gtid==tripid).first()
			if not trip:
				return

			data={'StartLongitude':{
						'type':'float',
						'default':0,
					},
						'StartLatitude':{
						'type':'float',
						'default':0,
					},
					'StartAltitude':{
						'type':'float',
						'default':0,
					}
				}
			fd=None
			lat_long_string=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Longitude,Latitude string:",helpText="numbers separated by a commma",data="string")
			if lat_long_string in [None,]:
				print("user Cancelled")
				return
			elif lat_long_string  not in ['d',]:
				try:
					if ',' in lat_long_string and len(lat_long_string.split(",")) == 2:
						lat,loNG=lat_long_string.split(",")
						data['StartLatitude']['default']=lat
						data['StartLongitude']['default']=loNG
					fd=FormBuilder(data=data)
				except Exception as e:
					print(e)
					fd=FormBuilder(data=data)
			else:
				fd=FormBuilder(data=data)
			if fd in [None,]:
				print("user Cancelled")
				return
			fd['SearchState']=True
			fd['SearchStartDT']=datetime.now()
			for i in fd:
				setattr(trip,i,fd[i])
				session.commit()
			session.commit()
			session.refresh(trip)
			print(trip)


	def end_trip(self):
		tripid=self.SearchTrip(select=True,one=True)
		with Session(ENGINE) as session:
			trip=session.query(GeoTrip).filter(GeoTrip.gtid==tripid).first()
			if not trip:
				return

			data={'EndLongitude':{
						'type':'float',
						'default':0,
					},
						'EndLatitude':{
						'type':'float',
						'default':0,
					},
					'EndAltitude':{
						'type':'float',
						'default':0,
					},
					'TransitCostsTotal':{
					'type':'float',
					'default':trip.TransitCostsTotal,
				},
				}
			fd=None
			lat_long_string=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Longitude,Latitude string:",helpText="numbers separated by a commma",data="string")
			if lat_long_string in [None,]:
				print("user Cancelled")
				return
			elif lat_long_string  not in ['d',]:
				try:
					if ',' in lat_long_string and len(lat_long_string.split(",")) == 2:
						lat,loNG=lat_long_string.split(",")
						data['EndLatitude']['default']=lat
						data['EndLongitude']['default']=loNG
					fd=FormBuilder(data=data)
				except Exception as e:
					print(e)
					fd=FormBuilder(data=data)
			else:
				fd=FormBuilder(data=data)
			if fd in [None,]:
				print("user Cancelled")
				return
			fd['SearchState']=False
			fd['SearchEndDT']=datetime.now()
			for i in fd:
				setattr(trip,i,fd[i])
				session.commit()
			session.refresh(trip)
			trip.DistanceTraveled=haversine.haversine((trip.StartLatitude,trip.StartLongitude),(trip.EndLatitude,trip.EndLongitude),unit="mi")

			session.commit()
			session.refresh(trip)
			print(trip)
			print(f'''{Fore.light_green}Transit Time was:{Fore.light_yellow}{trip.SearchEndDT-trip.SearchStartDT} {Style.reset}''')

	#end trip - search trip name
		#trip add costs
		#distance travelled
		#end altitude
		#end latitude
		#end longitude
		#search end Datetime
		#latest == False
		#search state == false
	def import_odf(self):
		try:
			name=Path('Streets.ods')
			if name.exists():
				df=pd.read_excel(name)
				df.to_sql(Streets.__tablename__, ENGINE,if_exists='append',index=False)
			else:
				print(name,"does not exist!")
		except Exception as e:
			print(e,repr(e),str(e))


	def duplicateDelete(self):
		with Session(ENGINE) as session:
			sums=[]
			results=session.query(Streets).all()
			ct=len(results)
			
			for num,i in enumerate(results):
				SUM=hashlib.sha512()
				for col in i.__table__.columns:
					if str(col.type).lower() == "varchar":
						v=getattr(i,str(col.name))
						if not v:
							v=str(v)
						v=v.encode()
						SUM.update(v)
				if SUM.hexdigest() not in sums:
					sums.append(SUM.hexdigest())
				else:
					print(i)
					session.delete(i)
					session.commit()

	def randomStreet(self):
		with Session(ENGINE) as session:
			ALL=session.query(Streets).all()
			allCt=len(ALL)-1
			randomStreet=ALL[random.randint(0,allCt)]
			print(randomStreet)

	def add_street(self):
		excludes=[
		'StreetId',
		'DTOE'
		]
		with Session(ENGINE) as session:
			street=Streets()
			session.add(street)
			session.commit()
			session.refresh(street)
			dataCore={
				i.name:{
					'default':getattr(street,i.name),
					'type':str(i.type)
				} for i in Streets.__table__.columns if i.name not in excludes
			}
			fdata=FormBuilder(data=dataCore)
			if not fdata:
				session.delete(street)
				session.commit()
				msg="User abandoned!"
				print(msg)
				return
			
			for i in fdata:
				setattr(street,i,fdata[i])
			
			session.commit()
			session.refresh(street)
			print(street)
			self.duplicateDelete()

	def rm_street(self):
		ids=self.streetSearch(select=True)
		if ids in [None,]:
			return
		with Session(ENGINE) as session:
			for num,i in enumerate(ids):
				session.query(Streets).filter(Streets.StreetId==i).delete()
				if num % 100 == 0:
					session.commit()
			session.commit()

	def edit_street(self):
		ids=self.streetSearch(select=True)
		if ids in [None,]:
			return
		for ID in ids:
			excludes=[
			'StreetId',
			'DTOE'
			]
			with Session(ENGINE) as session:
				street=session.query(Streets).filter(Streets.StreetId==ID).first()
				if street:
					dataCore={
						i.name:{
							'default':getattr(street,i.name),
							'type':str(i.type)
						} for i in Streets.__table__.columns if i.name not in excludes
					}
					fdata=FormBuilder(data=dataCore)
					if not fdata:
						session.delete(street)
						session.commit()
						msg="User abandoned!"
						print(msg)
						return
					
					for i in fdata:
						setattr(street,i,fdata[i])
					
					session.commit()
					session.refresh(street)
					print(street)
					self.duplicateDelete()
				else:
					print(f"{Fore.light_red}Street was {Fore.orange_red_1}{street}{Style.reset}")

	def streetSearch(self,select=False,one=False):
		with Session(ENGINE) as session:
			search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What are you looking for? ",helpText="text that you are looking for",data="string")
			if search in [None,'d']:
				return
			fields=[i for i in Streets.__table__.columns if str(i.type) == "VARCHAR"]
			fields_2=[i.icontains(search) for i in fields]
			query=session.query(Streets)
			query=query.filter(or_(*fields_2))
			results=query.all()
			ct=len(results)
			if ct==0:
				print("no results!")
				return
			helpText=''
			for num,i in enumerate(results):
				msg=f'''{self.colorized(i,num,ct)}- {i}'''
				helpText+=f'{msg}\n'
				print(msg)
			if select:
				which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Which index(es[Comma Separated])",helpText=helpText,data="list")
				if which in [None,]:
					return
				elif which in [[],'d']:
					return []
				else:
					try:
						tmp=[]
						for i in which:
							try:
								INDEX=int(i)
								if INDEX in range(0,len(results)) and INDEX not in tmp:
									tmp.append(results[INDEX].StreetId)
							except Exception as ee:
								print(ee)
						if one:
							if len(tmp) > 0:
								return tmp[0]
							else:
								return None
						return tmp
					except Exception as e:
						print(e)
					return []

	def colorized(self,i,num,ct):
		return f'{Fore.light_red}{num}{Fore.orange_red_1}/{Fore.light_green}{num+1} of {Fore.cyan}{ct} {Fore.magenta}'

	def listAllStreets(self):
		with Session(ENGINE) as session:
			results=session.query(Streets).all()
			ct=len(results)
			for num,i in enumerate(results):
				msg=f'''{self.colorized(i,num,ct)}- {i}'''
				print(msg)

	def exportStreetsODF(self):
		with Session(ENGINE) as session:
			query=session.query(Streets)
			df = pd.read_sql(query.statement, query.session.bind,dtype=str)
			df.to_excel("StreetsExport.ods",index=False)
			print(f"Saved to {Fore.light_green}StreetsExport.ods{Style.reset}")

	def clrStreets(self):
		with Session(ENGINE) as session:
			q=session.query(Streets).delete()
			session.commit()
		print("Streets Cleared!")

	def __init__(self):
		helpText=f'''
{Fore.medium_violet_red}"GeoTools"{Fore.orange_3} - Explore the World{Style.reset}
{Fore.light_cyan}'random street','rndmstrt','rstrt','xplr','get lost','get?'{Fore.light_red} -{Fore.dark_goldenrod} get a random street name to look for in the real world{Style.reset}
	
{Fore.light_cyan}'add streets','adstrts'{Fore.light_red} -{Fore.dark_goldenrod} [Manual] add a new street to db if it does not already exist{Style.reset}
{Fore.light_cyan}'rm streets','rmstrts'{Fore.light_red} -{Fore.dark_goldenrod} [Manual] delete a street from db {Style.reset}
{Fore.light_cyan}'edit streets','edstrts'{Fore.light_red} -{Fore.dark_goldenrod} [Manual] edit a street in db {Style.reset}
{Fore.light_cyan}'ls streets','lsstrts','las'{Fore.light_red} -{Fore.dark_goldenrod} List All Streets{Style.reset}
{Fore.light_cyan}'export streets odf','xpt strts odf','xsodf' -{Fore.dark_goldenrod} Export All Streets to ODF{Style.reset}
{Fore.light_cyan}'import streets odf','isodf'{Fore.light_red} -{Fore.dark_goldenrod} use an odf file to import streets using using ColumnsNames and Column Values{Style.reset}
{Fore.light_cyan}'clrdups','clear duplicates'{Fore.light_red} -{Fore.dark_goldenrod} search for duplicate Text entries in Streets{Style.reset}
{Fore.light_cyan}'clrstrts','clear streets','clear all streets','cas','cs'{Fore.light_red} -{Fore.dark_goldenrod} delete all streets from db{Style.reset}
{Fore.light_cyan}'ss','street search','strtsrch','search street'{Fore.light_red} -{Fore.dark_goldenrod} lookup a street from db{Style.reset}
{Fore.light_cyan}GeoTrip{Fore.light_magenta}
{Fore.cyan}'new trip','newtrip','ntrip','ntp'{Fore.green_yellow}Add a new trip{Style.reset}
{Fore.cyan}'search trip','searchtrip','sch trp','strip','stp'{Fore.green_yellow}Search trips{Style.reset}
{Fore.cyan}'end trip','endtrip','etp','end'{Fore.green_yellow}End a trip{Style.reset}
{Fore.cyan}'start trip','starttrip','stt tp','begin'{Fore.green_yellow}Start a trip{Style.reset}
{Fore.cyan}'rm trip','rmt','remove trip','rem trip'{Fore.green_yellow}remove/delete a trip{Style.reset}
{Fore.cyan}'update costs','upd8costs','udc'{Fore.light_red}Add a cost to the trip and update the TransitCostTotal{Style.reset}
{Fore.light_cyan}"rmcost","rmc","remove cost from trip","rcft"{Fore.light_red}remove a cost from a trip{Style.reset}
{Fore.light_red}Distance Travelled is in {Fore.light_yellow}Miles{Style.reset}
		'''
		
		while True:
			action=Prompt.__init2__(None,func=FormBuilderMkText,ptext="GeoTools|Do What? ",helpText=helpText,data="string")
			if action in [None,]:
				return
			elif action in ['d',]:
				print(helpText)
			elif action.lower() in ['random street','rndmstrt','rstrt','xplr','get lost','get?']:
				self.randomStreet()
			elif action.lower() in ['add streets','adstrts']:
				self.add_street()
			elif action.lower() in ['rm streets','rmstrts']:
				self.rm_street()
			elif action.lower() in ['edit streets','edstrts']:
				self.edit_street()
			elif action.lower() in ['import streets odf','isodf']:
				self.import_odf()
				self.duplicateDelete()
			elif action.lower() in ['clrdups','clear duplicates']:
				self.duplicateDelete()
			elif action.lower() in ['clrstrts','clear streets','clear all streets','cas','cs']:
				self.clrStreets()
			elif action.lower() in ['ss','street search','strtsrch','search street']:
				self.streetSearch()
			elif action.lower() in ['ls streets','lsstrts','las']:
				self.listAllStreets()
			elif action.lower() in ['export streets odf','xpt strts odf','xsodf']:
				self.exportStreetsODF()
			elif action.lower() in ['new trip','newtrip','ntrip','ntp']:
				self.new_trip()
			elif action.lower() in ['search trip','searchtrip','sch trp','strip','stp']:
				self.SearchTrip(everything=True)
			elif action.lower() in ['start trip','starttrip','stt tp','begin']:
				self.start_trip()
			elif action.lower() in ['end trip','endtrip','etp','end']:
				self.end_trip()
			elif action.lower() in ['rm trip','rmt','remove trip','rem trip']:
				self.rm_trip()
			elif action.lower() in ['update costs','upd8costs','udc']:
				self.addTripCost()
			elif action.lower() in ["rmcost","rmc","remove cost from trip","rcft"]:
				self.rmCostFromGtid()