from radboy.DB.db import *
import radboy.DB.db as db
from radboy.FB.FormBuilder import *
from password_generator import PasswordGenerator
import pint,os,sys
from datetime import datetime,timedelta,date,time
import base64
from Crypto.Cipher import AES
#from Cryptodome.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from collections import namedtuple
FormBuilderMkText

from barcode import Code128
from barcode.writer import ImageWriter
import hashlib

class RandomStringPreferences(BASE,Template):
	__tablename__="RandomStringPreferences"
	RSPID=Column(Integer,primary_key=True)
	minlen=Column(Integer)
	maxlen=Column(Integer)
	minuchars=Column(Integer)
	minlchars=Column(Integer)
	minnumbers=Column(Integer)
	minschars=Column(Integer)

	default={
	'minlen':16,
	'maxlen':16,
	'minuchars':1,
	'minnumbers':1,
	'minschars':1,
	'minlchars':1
	}
	def preferences(self):
		mapped={}
		for i in self.__table__.columns:
			mapped[i.name]=getattr(self,i.name)
		preferences=namedtuple('Preferences',mapped.keys())
		return preferences(**mapped)

	def __init__(self,**kwargs):
		self.setDefaults(kwargs)
		for k in kwargs.keys():
			if k in [s.name for s in self.__table__.columns]:
				setattr(self,k,kwargs.get(k))

	def setDefaults(self,kwargs):
		for i in self.default.keys():
			if i not in kwargs.keys():
				setattr(self,i,self.default[i])


class RandomString(BASE,Template):
	__tablename__="RandomString"
	RID=Column(Integer,primary_key=True)
	RString=Column(String)
	CDateTime=Column(DateTime)
	CDate=Column(Date)
	CTime=Column(Time)
	AgeLimit=Column(Float)
	Note=Column(String)
	User=Column(String)
	
	def __init__(self,**kwargs):
		for k in kwargs.keys():
			if k in [s.name for s in self.__table__.columns]:
				setattr(self,k,kwargs.get(k))
						
RandomString.metadata.create_all(ENGINE)
RandomStringPreferences.metadata.create_all(ENGINE)

class RandomStringUtilUi:
	

	def deleteOutDated(self,RID):
		with Session(ENGINE) as session:
			q=session.query(RandomString).filter(RandomString.RID==RID).first()
			print(f"Deleting {q}")
			session.delete(q)
			session.commit()
			session.flush()

	def checkForOutDated(self):
		try:
			al=getattr(self,'ageLimit')
			if not al:
				self.ageLimit=ageLimit=float(pint.UnitRegistry().convert(2,"years","seconds"))
			with Session(ENGINE) as session:
				results=session.query(RandomString).all()
				ct=len(results)
				print(f"{Fore.light_green}RandomString len({Fore.light_salmon_3a}History{Fore.light_green}){Fore.medium_violet_red}={Fore.green_yellow}{ct}{Style.reset}")
				for num,i in enumerate(results):
					if i:
						if i.AgeLimit != self.ageLimit:
							i.AgeLimit=self.ageLimit
							session.commit()
							session.flush()
							session.refresh(i)
						if (datetime.now()-i.CDateTime).total_seconds() >= i.AgeLimit:
							print("need to delete expired! -> {num+1}/{ct} -> {i}")
							RandomStringUtilUi.deleteOutDated(self,i.RID)
		except sqlalchemy.exc.OperationalError as e:
			print(e)
			print("Table Needs fixing... doing it now!")
			self.reset()
	
	def reset(self):
		RandomStringPreferences.__table__.drop(ENGINE)
		RandomStringPreferences.metadata.create_all(ENGINE)

		RandomString.__table__.drop(ENGINE)
		RandomString.metadata.create_all(ENGINE)
		print(f"{Fore.orange_red_1}A restart is required!{Style.reset}")
		exit()



	def mkTextLower(self,text,data):
		return text.lower()

	def mkText(self,text,data):
		return text

	def mkInt(self,text,data):
		try:
			if text in ['']:
				return 0
			else:
				return int(text)
		except Exception as e:
			print(e)
	def mkBytes(self,text,data):
		self.lineClear()
		if text.encode() in b''.rjust(16):
			print(f"{Fore.orange_red_1}Password Must not be empty!{Style.reset}")
			return None
		return text.encode().rjust(16)

	def getSetPreferences(self):
		try:
			with Session(ENGINE) as session:
				preferences=session.query(RandomStringPreferences).order_by(RandomStringPreferences.RSPID.desc()).first()
				if preferences:
					self.preferences=preferences.preferences()
				else:
					preferences=RandomStringPreferences()
					session.add(preferences)
					session.commit()
					session.flush()
					session.refresh(preferences)
					self.preferences=preferences.preferences()
		except Exception as e:
			print(e)
			self.reset()

	def mkint(self,text,data={'default':None}):
		try:
			if text in ['',]:
				return data['default']
			else:
				try:
					return int(eval(text))
				except Exception as e:
					print(e)
				try:
					return int(text)
				except Exception as e:
					print(e)
				return data['default']
		except Exception as e:
			print(e)


	def print_preferences(self):
		with Session(ENGINE) as session:
			preferences=session.query(RandomStringPreferences).order_by(RandomStringPreferences.RSPID.desc()).first()
			if not preferences:
				print(f"{Fore.orange_red_1}There are no {Fore.light_red}Preferences{Fore.light_sea_green}... Making them now!")
				self.getSetPreferences()
				preferences=session.query(RandomStringPreferences).order_by(RandomStringPreferences.RSPID.desc()).first()
				print(preferences)
			else:
				print(preferences)



	def set_preferences(self,fieldname,default={'default':1}):
		fields=[i.name for i in RandomStringPreferences.__table__.columns]
		if fieldname in fields:
			with Session(ENGINE) as session:
				preferences=session.query(RandomStringPreferences).order_by(RandomStringPreferences.RSPID.desc()).first()
				value=Prompt.__init2__(None,func=self.mkint,ptext=f"{fieldname} OLD Value={getattr(preferences,fieldname)}",helpText=f"{fieldname} For RandomStringPreferences",data=default)
				if value not in [None,]:
					setattr(preferences,fieldname,value)
				session.commit()
				session.flush()
				session.refresh(preferences)
				print(preferences)
				self.getSetPreferences()
		else:
			print(f"{Fore.orange_red_1}{fieldname}{Fore.light_blue}Is not a valid fieldname for RandomStringPreferences{Style.reset}")

	def export(self):
		with Session(ENGINE) as session:
			ALL=session.query(RandomString).all()
			ct=len(ALL)
			for num,i in enumerate(ALL):
				try:
					cipher = AES.new(self.password,AES.MODE_ECB)
					decoded = unpad(cipher.decrypt(base64.b64decode(i.RString.encode())),16)
					i.RString=decoded.decode("utf-8").replace('RS="','')[:-1]
				except Exception as e:
					print(e)
				ageSeconds=(datetime.now()-i.CDateTime).total_seconds()
				ageDays=round(pint.UnitRegistry().convert(ageSeconds,"seconds","days"),3)
				#print(last,f'{Fore.orange_red_1}CurrentAge(Days){Fore.light_steel_blue}={Fore.green_yellow}{}{Style.reset}',sep="\n")
				
				data={x.name:[getattr(i,x.name),] for x in i.__table__.columns if str(x.name) != "RID"}
				data['ageDays']=[ageDays,]
				data['ageSeconds']=[ageSeconds,]
				color_data=self.color_select()
				msg=f'''{Fore.light_yellow}{num}/{Fore.light_red}{ct}{Fore.light_magenta} -> {color_data}{data}{Style.reset}'''
				df=pd.DataFrame.from_dict(data)
				print(msg)
				fname=str(Path(f"Password").absolute())
				xprtIt=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Export it?",helpText="yes or no",data="boolean")
				if xprtIt in [None,]:
					return
				elif xprtIt in [False,]:
					continue
				else:
					fmts='text/json/csv/excel/code128'.split("/")
					fmt=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Format ({fmts})?",helpText=f"{fmts}",data="string")
					end=False
					while True:
						try:
							if fmt in [None,]:
								end=True
								break
							elif fmt.lower() in fmts:
								if fmt.lower() == 'text':
									try:
										fname+=".txt"
										with open(fname,"wb") as out:
											out.write(bytes(i.RString,"utf-8"))
										print(f"exported to {fname}")
									except Exception as e:
										print(e)
										print("Nothing was exported!")
								elif fmt.lower() == 'json':
									try:
										fname+=".json"
										df.to_json(fname)
										print(f"exported to {fname}")
									except Exception as e:
										print(e)
										print("Nothing was exported!")
								elif fmt.lower() == 'excel':
									try:
										fname+=".xlsx"
										df.to_excel(fname)
										print(f"exported to {fname}")
									except Exception as e:
										print(e)
										print("Nothing was exported!")
								elif fmt.lower() == "csv":
									try:
										fname+=".csv"
										df.to_csv(fname)
										print(f"exported to {fname}")
									except Exception as e:
										print(e)
										print("Nothing was exported!")
								elif fmt.lower() == "code128":
									try:
										fname+=".png"
										cd128=Code128(i.RString,writer=ImageWriter())
										cd128.save(fname)
										print(f"exported to {fname}")
									except Exception as e:
										print(e)
										print("Nothing was exported!")
								break
						except Exception as e:
							print(e)
					if end == True:
						return

	def color_select(self):
		colors=[getattr(Fore,i) for i in Fore.__dict__ if not callable(getattr(Fore,i)) and not i.startswith("__")]
		index=random.randint(0,len(colors)-1)
		return colors[index]

	def cpudas(self,mode=None):
		global filename
		f=filename
		while True:
			seed=hashlib.sha512()
			with Path(f).open('rb') as data:
				while True:
					d=data.read(1024*1024)
					if not d:
						break
					seed.update(d)
			length=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Length: ",helpText="how long is this string to be?",data="integer")
			if length in [None,]:
				return
			elif length in ['d',]:
				length=16
			seed_hex=seed.digest()
			feeder=seed_hex,bytes(datetime.now().ctime(),"utf-8")
			random.seed(b''.join(feeder))
			characters=string.ascii_letters+string.digits+string.punctuation
			random_string = ''.join(random.choice(characters) for _ in range(length))
			db.saveHistory(random_string,float(60*60*24*90),str(self.cpudas),data="string")
			print(random_string)

	def lineClear(self):
			with open(Path("STDOUT.TXT"),"w+") as log:
				log.write("")

	def __init__(self,parent,engine,justClean=False):
		self.lineClear()
		self.getSetPreferences()
		ageLimit=float(pint.UnitRegistry().convert(2,"years","seconds"))
		self.ageLimit=ageLimit
		self.checkForOutDated()
		if justClean:
			return
		self.term_cols=os.get_terminal_size().columns
		self.term_lines=os.get_terminal_size().lines
		
		self.helpText=f'''
{Fore.light_yellow}{Style.bold}>>>{Style.reset}{Fore.light_red}Warning: {Fore.dark_goldenrod}This is NOT(!) a {Fore.orange_red_1}Password Manager{Fore.light_yellow}{Style.bold}<<<{Style.reset}
{Fore.light_magenta}Date Stored here will be deleted after {round(pint.UnitRegistry().convert(ageLimit,"seconds","days"))} days!{Style.reset}
{Fore.light_green}{'<'*(round(self.term_cols/3)-5)}{Fore.red}{'<'*(round(self.term_cols/3)-5)}{Fore.yellow}{'<'*(round(self.term_cols/3)-5)}{Style.reset}
{Fore.grey_50}ls rid,lrid,list rid,lsrid - {Fore.light_sea_green}show by id{Style.reset}
{Fore.grey_70}rm rid,rrid,rem rid,rmrid,delrid,del rid,del_rid - {Fore.green_yellow}delete by id{Style.reset}
{Fore.grey_50}last,latest,ltst - {Fore.light_sea_green}show last created{Style.reset}
{Fore.grey_70}new,n,g,gen,generate - {Fore.green_yellow}create a new RandomString{Style.reset}
{Fore.grey_70}m,manual,force,f - {Fore.green_yellow}create a new RandomString manually{Style.reset}
{Fore.grey_50}show all,show_all,all,sa - {Fore.light_sea_green}show all created RandomStrings{Style.reset}
{Fore.grey_70}delall,del all,ca,clear all,clear_all - {Fore.green_yellow}reset table completely{Style.reset}
{Fore.grey_50}fix_table - {Fore.light_sea_green}drops table from db, such as if a new column is added and the table is preventing updates{Style.reset}
{Fore.light_steel_blue}set minlen,smnl - {Fore.green_yellow}set minimum generated string length{Style.reset}
{Fore.light_steel_blue}set maxlen,smxl - {Fore.green_yellow}set minimum generated string length{Style.reset}
{Fore.light_steel_blue}set minuchars,smuc - {Fore.green_yellow}set minimum upper case chars{Style.reset}
{Fore.light_steel_blue}set minlchars,smlc - {Fore.green_yellow}set minimum lower case chars{Style.reset}
{Fore.light_steel_blue}set minnumbers,smn - {Fore.green_yellow}set minimum numbers{Style.reset}
{Fore.light_steel_blue}set minschars,smsc - {Fore.green_yellow}set minimum special chars{Style.reset}
{Fore.light_green}pp,print preferences,print_preferences,preferences - {Fore.light_blue}Show Current Settings/Preferences{Style.reset}
{Fore.light_salmon_1}rimm,random integer minumum maximum - {Fore.green_yellow}Generate a random integer between a lowest and highest number{Style.reset}
{Fore.light_salmon_1}re,random entry - {Fore.green_yellow}Get random entry from Entry Table{Style.reset}
{Fore.light_steel_blue}export,xpt - {Fore.light_red}Export Selected to either text/json/csv/excel{Style.reset}
{Fore.light_steel_blue}create pwd using data as seed,cpudas - {Fore.light_red}create pwd using data as seed with custom length{Style.reset}
'''
		self.password=Prompt.__init2__(None,func=self.mkBytes,ptext="Password",helpText="Password to Display RStrings",data=self)
		if self.password in [None,]:
			print("A password is required!")
			return
		while True:
			self.lineClear()
			fieldname='Menu'
			mode='RS'
			h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
			
			doWhat=Prompt.__init2__(None,func=self.mkTextLower,ptext=f"{h}Do What?",helpText=self.helpText,data=None)
			if doWhat in [None,]:
				return
			elif doWhat in ['rimm','random integer min max']:
				mnm=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Lowest Possible?",helpText="Lower Possible Number",data="integer")
				if mnm in ['d',]:
					mnm=0
				elif mnm in [None,]:
					continue
				mxm=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Highest Possible?",helpText="Hightest Possible Number",data="integer")
				if mxm in ['d',]:
					mxm=sys.maxsize
				elif mxm in [None,]:
					continue
				rndi=random.randint(mnm,mxm)
				zfill=Prompt.__init2__(None,func=FormBuilderMkText,ptext="ZFill?",helpText="Lengthen to length with 0's",data="integer")
				if zfill in ['d',] or zfill > 0 :
					if zfill in ['d',]:
						zfill=0
					rndi=str(rndi).zfill(zfill)
				elif zfill in [None,]:
					continue
				print(rndi)
			elif doWhat.lower() in ['export','xpt']:
				self.export()
			elif doWhat in ['r/r/r','russian random roullette']:
				rounds=0
				peopleL=[]
				rewardsL=[]
				
				people=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Number of People?",helpText="Number of people, where each number is a person's id",data="integer")
				if people in ['d',]:
					people=1
				elif people in [None,]:
					continue
				rewards=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Number of rewards to choose 1 of?",helpText="Number of rewards to choose 1 of; only the reward id'd by number will be given to person id'd by number",data="integer")
				if rewards in ['d',]:
					rewards=1
				elif rewards in [None,]:
					continue

				for i in range(people):
					peopleL.append(i)
				for i in range(rewards):
					rewardsL.append(i)
				
				while len(rewardsL) > 0:
					rounds+=1
					draw=input(f"draw round of {rounds}...")
					person=peopleL[random.randint(0,len(peopleL)-1)]
					reward=rewardsL[random.randint(0,len(rewardsL)-1)]
					msg=f'''
	{Fore.light_yellow}Person of {Fore.medium_violet_red}{people}:{Fore.light_steel_blue}{person+1}{Style.reset}
	{Fore.orange_red_1}RewardNumber of {Fore.medium_purple_3b}{rewards}:{Fore.light_green}{reward+1}{Style.reset}
					'''
					print(msg)
					peopleL.remove(person)
					rewardsL.remove(reward)
			elif doWhat in ['re','random entry']:
				with Session(ENGINE) as session:
					everything=session.query(Entry).all()
					mxm=len(everything)-1
					mnm=0
					index=random.randint(mnm,mxm)
					result=everything[index]
					print(result)
			elif doWhat in ['set minlen','smnl']:
				self.set_preferences('minlen',default={'default':16})
			elif doWhat in 'set maxlen,smxl'.split(","):
				self.set_preferences('maxlen',default={'default':16})
			elif doWhat in 'set minuchars,smuc'.split(","):
				self.set_preferences('minuchars',default={'default':1})
			elif doWhat in 'set minlchars,smlc'.split(","):
				self.set_preferences('minlchars',default={'default':1})
			elif doWhat in 'set minnumbers,smn'.split(","):
				self.set_preferences('minnumbers',default={'default':1})
			elif doWhat in 'set minschars,smsc'.split(","):
				self.set_preferences('minschars',default={'default':1})
			elif doWhat in 'pp,print preferences,print_preferences,preferences'.split(","):
				self.print_preferences()
			elif doWhat.lower() in "create pwd using data as seed,cpudas".split(","):
				self.cpudas(mode=None)
			elif doWhat in ['new','n','g','gen','generate']:
				user=Prompt.__init2__(None,func=self.mkText,ptext="User(if any)",helpText="a username name to store with this string",data=None)
				if user in [None,]:
					continue
				note=Prompt.__init2__(None,func=self.mkText,ptext="Note(if any)",helpText="commens about this string...",data=None)
				if note in [None,]:
					continue
				while True:
					try:
						x=PasswordGenerator()

						x.minlen=self.preferences.minlen
						x.maxlen=self.preferences.maxlen
						x.minschars=self.preferences.minschars
						x.minnumbers=self.preferences.minnumbers
						x.minuchars=self.preferences.minuchars
						x.minlchars=self.preferences.minlchars

						rstring=x.generate()
						RS=f'RS="{rstring}"'
						tmp=pad(RS.encode(),16)
						rstring=tmp.decode("utf-8")
						print(f"{Fore.light_sea_green}PlainText RString: '{Fore.light_green}{rstring}{Fore.light_sea_green}'{Style.reset}")
						cipher = AES.new(self.password,AES.MODE_ECB)
						encoded = base64.b64encode(cipher.encrypt(rstring.encode()))
						rstring=encoded.decode()


						cdt=datetime.now()
						ctime=time(cdt.hour,cdt.minute,cdt.second)
						cdate=date(cdt.year,cdt.month,cdt.day)
						#print(cdate,ctime,cdt,ageLimit,rstring,sep="\n")
						with Session(ENGINE) as session:
							check=session.query(RandomString).filter(RandomString.RString==rstring).first()
							if check:
								print(f"{Fore.light_yellow}A similar RString was found in the DB, let's try that again!{Style.reset}")
								continue
							npwd=RandomString(RString=rstring,AgeLimit=ageLimit,CTime=ctime,CDate=cdate,CDateTime=cdt,Note=note,User=user)
							session.add(npwd)
							session.commit()
							session.refresh(npwd)
							print(npwd,"Created!")
						break
					except Exception as e:
						print(e)
						break
			elif doWhat in ['m','manual','force','f']:
				user=Prompt.__init2__(None,func=self.mkText,ptext="User(if any)",helpText="a username name to store with this string",data=None)
				if user in [None,]:
					continue
				note=Prompt.__init2__(None,func=self.mkText,ptext="Note(if any)",helpText="comments about this string...",data=None)
				if note in [None,]:
					continue
				rstring=Prompt.__init2__(None,func=self.mkText,ptext="Password(if any)",helpText="password...NOT SMART!",data=None)
				if rstring in [None,]:
					continue
				while True:
					try:
						RS=f'RS="{rstring}"'
						tmp=pad(RS.encode(),16)
						rstring=tmp.decode("utf-8")
						print(f"{Fore.light_sea_green}PlainText RString: '{Fore.light_green}{rstring}{Fore.light_sea_green}'{Style.reset}")
						cipher = AES.new(self.password,AES.MODE_ECB)
						encoded = base64.b64encode(cipher.encrypt(rstring.encode()))
						rstring=encoded.decode()


						cdt=datetime.now()
						ctime=time(cdt.hour,cdt.minute,cdt.second)
						cdate=date(cdt.year,cdt.month,cdt.day)
						#print(cdate,ctime,cdt,ageLimit,rstring,sep="\n")
						with Session(ENGINE) as session:
							check=session.query(RandomString).filter(RandomString.RString==rstring).first()
							if check:
								print(f"{Fore.light_yellow}A similar RString was found in the DB, let's try that again!{Style.reset}")
								continue
							npwd=RandomString(RString=rstring,AgeLimit=ageLimit,CTime=ctime,CDate=cdate,CDateTime=cdt,Note=note,User=user)
							session.add(npwd)
							session.commit()
							session.refresh(npwd)
							print(npwd,"Created!")
						break
					except Exception as e:
						print(e)
						break
			elif doWhat in ['last','latest','ltst']:
				with Session(ENGINE) as session:
					last=session.query(RandomString).order_by(RandomString.RID.desc()).first()
					if not last:
						print(f"{Fore.light_red}Nothing to see!{Style.reset}")
						continue
					try:
						cipher = AES.new(self.password,AES.MODE_ECB)
						decoded = unpad(cipher.decrypt(base64.b64decode(last.RString.encode())),16)
						last.RString=decoded.decode("utf-8")
					except Exception as e:
						print(e)
					age=(datetime.now()-last.CDateTime).total_seconds()
					print(last,f'{Fore.orange_red_1}CurrentAge(Days){Fore.light_steel_blue}={Fore.green_yellow}{round(pint.UnitRegistry().convert(age,"seconds","days"),3)}{Style.reset}',sep="\n")
			elif doWhat in ['show all','show_all','all','sa']:
				with Session(ENGINE) as session:
					everything=session.query(RandomString).order_by(RandomString.RID.asc()).all()
					ct=len(everything)
					
					for num,last in enumerate(everything):
						try:
							cipher = AES.new(self.password,AES.MODE_ECB)
							decoded = unpad(cipher.decrypt(base64.b64decode(last.RString.encode())),16)
							#decoded = cipher.decrypt(base64.b64decode(last.RString.encode()))
							last.RString=decoded.decode("utf-8")
						except Exception as e:
							print(e)
						age=(datetime.now()-last.CDateTime).total_seconds()
						msg=f'''{'-'*round(self.term_lines/2)}
{Fore.light_green}{num+1}/{Fore.light_red}{ct}{Style.reset} -> {last}
{Fore.orange_red_1}CurrentAge(Days){Fore.light_steel_blue}={Fore.green_yellow}{round(pint.UnitRegistry().convert(age,"seconds","days"),3)}{Style.reset} 
'''
						print(msg)
			elif doWhat in ['ls rid','lrid','list rid','lsrid']:
				with Session(ENGINE) as session:
					mode='RS'
					h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
					rid=Prompt.__init2__(None,func=self.mkInt,ptext=f"{h}RID",helpText=self.helpText,data=None)
					if rid not in  [None,] and not isinstance(rid,tuple):
						last=session.query(RandomString).filter(RandomString.RID==rid).first()
						if last != None:
							try:
								cipher = AES.new(self.password,AES.MODE_ECB)
								#decoded = cipher.decrypt(base64.b64decode(last.RString.encode()))
								decoded = unpad(cipher.decrypt(base64.b64decode(last.RString.encode())),16)
								last.RString=decoded.decode("utf-8")
							except Exception as e:
								print(e)
							age=(datetime.now()-last.CDateTime).total_seconds()
							print(last,f'{Fore.orange_red_1}CurrentAge(Days){Fore.light_steel_blue}={Fore.green_yellow}{round(pint.UnitRegistry().convert(age,"seconds","days"),3)}{Style.reset}',sep="\n")
						else:
							print(f"{Fore.light_red}No {Fore.orange_red_1}Results{Fore.light_yellow}!{Style.reset}")

			elif doWhat in ['rm rid','rrid','rem rid','rmrid','delrid','del rid','del_rid']:
				with Session(ENGINE) as session:
					mode='RS'
					h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
					rid=Prompt.__init2__(None,func=self.mkInt,ptext=f"{h}RID",helpText=self.helpText,data=None)
					if rid not in  [None,] and not isinstance(rid,tuple):
						last=session.query(RandomString).filter(RandomString.RID==rid).first()
						if last != None:
							try:
								cipher = AES.new(self.password,AES.MODE_ECB)
								decoded = cipher.decrypt(base64.b64decode(last.RString.encode()))
								last.RString=decoded.decode("utf-8")
							except Exception as e:
								print(e)
							age=(datetime.now()-last.CDateTime).total_seconds()
							print("Deleting",last,f'{Fore.orange_red_1}CurrentAge(Days){Fore.light_steel_blue}={Fore.green_yellow}{round(pint.UnitRegistry().convert(age,"seconds","days"),3)}{Style.reset}',sep="\n")
							session.delete(last)
							session.commit()
							session.flush()
						else:
							print(f"{Fore.light_red}No {Fore.orange_red_1}Results{Fore.light_yellow}!{Style.reset}")
			elif doWhat in ['fix_table',]:
				self.reset()
			elif doWhat in ['delall','del all','ca','clear all','clear_all']:
				with Session(ENGINE) as session:
					status=session.query(RandomString).delete()
					session.commit()
					print(f"There are {len(session.query(RandomString).all())} RandomStrings Left!")
			self.lineClear()