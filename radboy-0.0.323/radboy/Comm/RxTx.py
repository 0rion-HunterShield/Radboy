from radboy.DB.db import *
from radboy.DB.RandomStringUtil import *
import radboy.Unified.Unified as unified
import radboy.possibleCode as pc
from radboy.DB.Prompt import *
from radboy.DB.Prompt import prefix_text
from radboy.TasksMode.ReFormula import *
from radboy.FB.FormBuilder import *
from radboy.FB.FBMTXT import *
from radboy.RNE.RNE import *
from radboy.Lookup2.Lookup2 import Lookup as Lookup2
from collections import namedtuple,OrderedDict
import nanoid
from password_generator import PasswordGenerator
import random
from pint import UnitRegistry
import pandas as pd
import numpy as np
from datetime import *
from colored import Style,Fore
import json,sys,math,re,calendar
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def today():
    dt=datetime.now()
    return date(dt.year,dt.month,dt.day)

#use this to store contacts
class MailBoxContacts(BASE,Template):
	__tablename__="MailBoxContacts"
	mbcid=Column(Integer,primary_key=True)
	#name
	FName=Column(String)
	MName=Column(String)
	LName=Column(String)
	Suffix=Column(String)

	#Email GMAIL ONLY for sending
	Email_Address=Column(String)
	app_password=Column(String)
	#Phone
	Phone_Number=Column(String)
	DTOE=Column(DateTime)

	def __init__(self,**kwargs):
		for k in kwargs.keys():
			if k in [s.name for s in self.__table__.columns]:
				setattr(self,k,kwargs.get(k))

#use this to store messages

class MailBox(BASE,Template):
	__tablename__="MailBox"
	mbid=Column(Integer,primary_key=True)

	Title=Column(String)
	MsgText=Column(String)
	
	#when the entry was made
	DTOE=Column(DateTime)
	
	#when the entry is due
	DUE_DTOE=Column(DateTime)
	
	#email addressing options
	Addressed_To_email=Column(String)
	Addressed_From_email=Column(String)
	

	#Phone messaging options
	Addressed_To_Phone=Column(String)
	Addressed_From_Phone=Column(String)

	def __init__(self,**kwargs):
		for k in kwargs.keys():
			if k in [s.name for s in self.__table__.columns]:
				setattr(self,k,kwargs.get(k))


class RxTx:
	htext=f"""{Fore.light_red}To send a GMAIL, your MUST have a GMAIL and a GMAIL App-Password\n{Fore.cyan}Please Note Commands can be guessed from the first match of a partial so a doWhat == 'new c' will EQUAL doWhat == 'new contact'\nGMAIL app passwords @ {Fore.light_magenta}https://myaccount.google.com/apppasswords{Style.reset}\n"""
	def print_help(self):
		print(self.htext)

	def resend(self):
		print(f"{Fore.light_yellow}Re-Send Message General [From Email Address MUST be {Fore.orange_red_1}GMAIL{Fore.light_yellow}]{Style.reset}")
		nmb={}
		nmb['Addressed_To_email']=''
		nmb['Addressed_From_email']=''

		while nmb['Addressed_To_email'] == '':
			print(f"{Fore.light_yellow}Please Select your addressee(s)/{Fore.green}To{Fore.light_yellow} ['b' key key throws everything out and goes back a menu]{Style.reset}")
			Addressed_To_email=self.searchContact(returnable=True)
			if Addressed_To_email == None:
				print(f"{Fore.light_red}No Contacts to use!{Style.reset}")
				return
			if len(Addressed_To_email) < 1:
				print(f"{Fore.light_red}No Contacts to use!{Style.reset}")
				return
			with Session(ENGINE) as session:
				which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{Fore.light_red}which contact {Fore.light_yellow}Number(s){Style.reset}",helpText="use a dash between numbers to specify a range,commas can be between numbers or ranges",data="list")
				if which in [None,'d']:
					return
				for i in which:
					try:
						val=int(i)
						if nmb['Addressed_To_email'].split(",") == ['',]:
							nmb['Addressed_To_email']=','.join(list((Addressed_To_email[val].Email_Address,)))

						else:
							nmb['Addressed_To_email']=list(nmb['Addressed_To_email'].split(","))
							nmb['Addressed_To_email'].append(Addressed_To_email[val].Email_Address)
							nmb['Addressed_To_email']=','.join(list((Addressed_To_email[val].Email_Address,)))
					except Exception as e:
						print(repr(e),e,f"couldn't use {i},try next...")
						print(Addressed_To_email)
						print(i,type(i),)
		ap=''
		while nmb['Addressed_From_email'] == '':
			print(f"{Fore.light_yellow}Please Select your addresser/{Fore.green}From{Fore.light_yellow}  ['b' key throws everything out and goes back a menu]{Style.reset}")
			Addressed_From_email=self.searchContact(returnable=True)
			if Addressed_From_email == None:
				print(f"{Fore.light_red}No Contacts to use!{Style.reset}")
				return
			if len(Addressed_From_email) < 1:
				print(f"{Fore.light_red}No Contacts to use!{Style.reset}")
				return
			with Session(ENGINE) as session:
				which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{Fore.light_red}which contact {Fore.light_yellow}Number(s){Style.reset}",helpText="use a dash between numbers to specify a range,commas can be between numbers or ranges",data="integer")
				if which in [None,'d']:
					return
				
				try:
					val=int(i)
					ap=Addressed_From_email[val].app_password
					if nmb['Addressed_From_email'].split(",") == ['',]:
						nmb['Addressed_From_email']=','.join(list((Addressed_From_email[val].Email_Address,)))
					else:
						nmb['Addressed_From_email']=list(nmb['Addressed_From_email'].split(","))
						nmb['Addressed_From_email'].append(Addressed_From_email[val].Email_Address)
						nmb['Addressed_From_email']=','.join(nmb['Addressed_From_email'])
				except Exception as e:
					print(repr(e),e,f"couldn't use {i},try next...")
					print(Addressed_From_email)
					print(i,type(i),)
		print(f"{Fore.orange_red_1}Let's look for that email to resend.")
		whiches=self.showSent(returnable=True)
		if whiches == None:
			print(f"{Fore.light_red}User canceled!{Style.reset}")
			return
		elif len(whiches) < 1:
			print(f"{Fore.light_red}No Results!{Style.reset}")
			return
		which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{Fore.light_red}which MailBox {Fore.light_yellow}Number(s){Style.reset}",helpText="use a dash between numbers to specify a range,commas can be between numbers or ranges",data="integer")
		if which in [None,'d']:
			return
		
		try:
			val=int(which)

			print(nmb)
			NewMailBox=whiches[val]
			session.add(NewMailBox)
			session.commit()
			session.refresh(NewMailBox)
			print(NewMailBox)
			#time to make the email
			msg=MIMEMultipart()
			msg['Subject']=NewMailBox.Title
			msg['From']=NewMailBox.Addressed_From_email
			msg['To']=NewMailBox.Addressed_To_email
			body=MIMEText(NewMailBox.MsgText)
			msg.attach(body)
			msg.preamble=NewMailBox.MsgText

			s=smtplib.SMTP_SSL('smtp.gmail.com',465)
			app_password=Prompt.__init2__(self,func=FormBuilderMkText,ptext="Gmail App Password",helpText="type your app password from gmail",data="string")
			if app_password in [None,]:
				print(f"{Fore.light_red}No Password; No Msg Sent!")
				return
			elif app_password.lower() == 'd':
				app_password=ap
			print(app_password)
			s.login(NewMailBox.Addressed_From_email,app_password)
			s.sendmail(NewMailBox.Addressed_From_email,NewMailBox.Addressed_To_email,msg.as_string())
			s.quit()
		except Exception as e:
			print(e)

	def newEmail(self):
		print(f"{Fore.light_yellow}New Message General [From Email Address MUST be {Fore.orange_red_1}GMAIL{Fore.light_yellow}]{Style.reset}")
		data={
		'Title':{
			'type':'str',
			'default':'',
			},
		'MsgText':{
			'type':'str+',
			'default':'',
			},
		'DUE_DTOE':{
			'type':'datetime',
			'default':datetime.now(),
			},

		}
		nmb=FormBuilder(data=data)
		nmb['DTOE']=datetime.now()
		nmb['Addressed_To_email']=''
		nmb['Addressed_From_email']=''

		while nmb['Addressed_To_email'] == '':
			print(f"{Fore.light_yellow}Please Select your addressee(s)/{Fore.green}To{Fore.light_yellow} ['b' key key throws everything out and goes back a menu]{Style.reset}")
			Addressed_To_email=self.searchContact(returnable=True)
			if Addressed_To_email == None:
				print(f"{Fore.light_red}No Contacts to use!{Style.reset}")
				return
			if len(Addressed_To_email) < 1:
				print(f"{Fore.light_red}No Contacts to use!{Style.reset}")
				return
			with Session(ENGINE) as session:
				which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{Fore.light_red}which contact {Fore.light_yellow}Number(s){Style.reset}",helpText="use a dash between numbers to specify a range,commas can be between numbers or ranges",data="list")
				if which in [None,'d']:
					return
				for i in which:
					try:
						val=int(i)
						if nmb['Addressed_To_email'].split(",") == ['',]:
							nmb['Addressed_To_email']=','.join(list((Addressed_To_email[val].Email_Address,)))

						else:
							nmb['Addressed_To_email']=list(nmb['Addressed_To_email'].split(","))
							nmb['Addressed_To_email'].append(Addressed_To_email[val].Email_Address)
							nmb['Addressed_To_email']=','.join(list((Addressed_To_email[val].Email_Address,)))
					except Exception as e:
						print(repr(e),e,f"couldn't use {i},try next...")
						print(Addressed_To_email)
						print(i,type(i),)
		ap=''
		while nmb['Addressed_From_email'] == '':
			print(f"{Fore.light_yellow}Please Select your addresser/{Fore.green}From{Fore.light_yellow}  ['b' key throws everything out and goes back a menu]{Style.reset}")
			Addressed_From_email=self.searchContact(returnable=True)
			if Addressed_From_email == None:
				print(f"{Fore.light_red}No Contacts to use!{Style.reset}")
				return
			if len(Addressed_From_email) < 1:
				print(f"{Fore.light_red}No Contacts to use!{Style.reset}")
				return
			with Session(ENGINE) as session:
				which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{Fore.light_red}which contact {Fore.light_yellow}Number(s){Style.reset}",helpText="use a dash between numbers to specify a range,commas can be between numbers or ranges",data="integer")
				if which in [None,'d']:
					return
				
				try:
					val=int(i)
					ap=Addressed_From_email[val].app_password
					if nmb['Addressed_From_email'].split(",") == ['',]:
						nmb['Addressed_From_email']=','.join(list((Addressed_From_email[val].Email_Address,)))
					else:
						nmb['Addressed_From_email']=list(nmb['Addressed_From_email'].split(","))
						nmb['Addressed_From_email'].append(Addressed_From_email[val].Email_Address)
						nmb['Addressed_From_email']=','.join(nmb['Addressed_From_email'])
				except Exception as e:
					print(repr(e),e,f"couldn't use {i},try next...")
					print(Addressed_From_email)
					print(i,type(i),)

			print(nmb)
			NewMailBox=MailBox(**nmb)
			session.add(NewMailBox)
			session.commit()
			session.refresh(NewMailBox)
			print(NewMailBox)
			#time to make the email
			msg=MIMEMultipart()
			msg['Subject']=NewMailBox.Title
			msg['From']=NewMailBox.Addressed_From_email
			msg['To']=NewMailBox.Addressed_To_email
			body=MIMEText(NewMailBox.MsgText)
			msg.attach(body)
			msg.preamble=NewMailBox.MsgText

			s=smtplib.SMTP_SSL('smtp.gmail.com',465)
			app_password=Prompt.__init2__(self,func=FormBuilderMkText,ptext="Gmail App Password",helpText="type your app password from gmail",data="string")
			if app_password in [None,]:
				print(f"{Fore.light_red}No Password; No Msg Sent!")
				return
			elif app_password.lower() == 'd':
				app_password=ap
			print(app_password)
			s.login(NewMailBox.Addressed_From_email,app_password)
			s.sendmail(NewMailBox.Addressed_From_email,NewMailBox.Addressed_To_email,msg.as_string())
			s.quit()


	
	def newContact(self):
		data={
		'FName':{
			'type':'str',
			'default':'',
			},
		'MName':{
			'type':'str',
			'default':'',
		},
		'LName':{
			'type':'str',
			'default':'',
		},
		'Suffix':{
			'type':'str',
			'default':'',
		},
		'Email_Address':{
			'type':'str',
			'default':'',
		},
		'app_password':{
			'type':'str',
			'default':'',
		},
		'Phone_Number':{
			'type':'str',
			'default':'',
		},
		}
		newContactDict=FormBuilder(data)
		newContactDict['DTOE']=datetime.now()
		with Session(ENGINE) as session:
			nc=MailBoxContacts(**newContactDict)
			session.add(nc)
			session.commit()
			session.flush()
			session.refresh(nc)
			print(nc)

	def searchContact(self,returnable=False):
		try:
			while True:
				results=[]
				dateSearch=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Date Search?",helpText="If this is a date search type the date, or 'y' for a date prompt",data='datetime')
				if dateSearch in [None,]:
					return
				elif dateSearch in ['d',]:
					search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search?",helpText="Search text in anything else",data="string")
					print(search)
					if search in [None,]:
						return
					elif search in ['d',]:
						continue
					elif search in ['*',' ']:
						with Session(ENGINE) as session:
							results=session.query(MailBoxContacts)
							results=results.order_by(MailBoxContacts.LName.asc()).all()
					else:
						with Session(ENGINE) as session:
							results=session.query(MailBoxContacts)
							results=results.filter(or_(
								MailBoxContacts.FName.icontains(search.lower()),
								MailBoxContacts.MName.icontains(search.lower()),
								MailBoxContacts.LName.icontains(search.lower()),
								MailBoxContacts.Suffix.icontains(search.lower()),
								MailBoxContacts.Email_Address.icontains(search.lower()),
								MailBoxContacts.Phone_Number.icontains(search.lower())
								)
							).order_by(MailBoxContacts.LName.asc()).all()
					ct=len(results)
					for num,i in enumerate(results):
						msg=f'''{Fore.light_yellow}{num}/{Fore.light_green}{num+1}/{Fore.light_red}{ct}{Style.reset} -> {i}'''
						print(msg)
					if returnable:
						return results
					#ask for search details as user wants anything but date search
				else:
					with Session(ENGINE) as session:
						tmp=[]
						DATE=date(dateSearch.year,dateSearch.month,dateSearch.day)
						results=session.query(MailBoxContacts).all()
						for num,i in enumerate(results):
							DTC=date(i.DTOE.year,i.DTOE.month,i.DTOE.day)
							if DTC == DATE:
								tmp.append(i)
						for num,i in enumerate(tmp):
							msg=f'''{Fore.light_yellow}{num}/{Fore.light_green}{num+1}/{Fore.light_red}{len(tmp)}{Style.reset} -> {i}'''
							print(msg)
						if returnable:
							return tmp

		except Exception as e:
			print(e)

	def rmContact(self):
		try:
			toRm=self.searchContact(returnable=True)
			if toRm in [[],None,'d']:
				return
			else:
				with Session(ENGINE) as session:
					which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{Fore.light_red}Remove {Fore.light_yellow}Number(s){Style.reset}",helpText="use a dash between numbers to specify a range,commas can be between numbers or ranges",data="list")
					for i in which:
						try:
							val=int(i)
							item=session.query(MailBoxContacts).filter(MailBoxContacts.mbcid==toRm[val].mbcid).first()
							session.delete(item)
							print(item,"Deleted!")
							session.commit()
							session.flush()
						except Exception as e:
							print(e,"moving on to next index...")
		except Exception as e:
			print(e)

	def editContact(self):
		try:
			excludes=['mbcid',]
			toEdit=self.searchContact(returnable=True)
			if toEdit in [[],None,'d']:
				return
			else:
				with Session(ENGINE) as session:
					which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{Fore.light_red}Edit {Fore.light_yellow}Number(s){Style.reset}",helpText="use a dash between numbers to specify a range,commas can be between numbers or ranges",data="list")
					for i in which:
						try:
							val=int(i)
							item=session.query(MailBoxContacts).filter(MailBoxContacts.mbcid==toEdit[val].mbcid).first()
							print(item,"To Edit!")
							data={}
							for cols in item.__table__.columns:
								#print(cols.name)
								name=str(cols.name)
								if name in excludes:
									continue
								data[name]={}
								data[name]['type']=str(cols.type).lower()
								data[name]['default']=getattr(item,name)
							upd8=FormBuilder(data=data)
							session.query(MailBoxContacts).filter(MailBoxContacts.mbcid==toEdit[val].mbcid).update(upd8)
							session.commit()
							session.flush()
							session.refresh(item)

							print(item,"Updated!")
						except Exception as e:
							print(e,"moving on to next index...")
		except Exception as e:
			print(e)

	def showSent(self,returnable=True):
		try:
			while True:
				results=[]
				dateSearch=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Date Search?",helpText="If this is a date search type the date, or 'y' for a date prompt",data='datetime')
				if dateSearch in [None,]:
					return
				elif dateSearch in ['d',]:
					search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search?",helpText="Search text in anything else",data="string")
					print(search)
					if search in [None,]:
						return
					elif search in ['d',]:
						continue
					elif search in ['*',' ']:
						with Session(ENGINE) as session:
							results=session.query(MailBox)
							results=results.all()
					else:
						with Session(ENGINE) as session:
							results=session.query(MailBox)
							results=results.filter(or_(
								MailBox.Title.icontains(search.lower()),
								MailBox.MsgText.icontains(search.lower()),
								MailBox.Addressed_From_email.icontains(search.lower()),
								MailBox.Addressed_To_email.icontains(search.lower()),
								)
							).all()
					ct=len(results)
					for num,i in enumerate(results):
						msg=f'''{Fore.light_yellow}{num}/{Fore.light_green}{num+1}/{Fore.light_red}{ct}{Style.reset} -> {i}'''
						print(msg)
					if returnable:
						return results
					#ask for search details as user wants anything but date search
				else:
					with Session(ENGINE) as session:
						tmp=[]
						DATE=date(dateSearch.year,dateSearch.month,dateSearch.day)
						results=session.query(MailBoxContacts).all()
						for num,i in enumerate(results):
							DTC=date(i.DTOE.year,i.DTOE.month,i.DTOE.day)
							if DTC == DATE:
								tmp.append(i)
							DTC=date(i.DUE_DTOE.year,i.DUE_DTOE.month,i.DUE_DTOE.day)
							if DTC == DATE:
								tmp.append(i) 
						for num,i in enumerate(tmp):
							msg=f'''{Fore.light_yellow}{num}/{Fore.light_green}{num+1}/{Fore.light_red}{len(tmp)}{Style.reset} -> {i}'''
							print(msg)
						if returnable:
							return tmp
		except Exception as e:
			print(e)


	def rmMailBox(self):
		try:
			toRm=self.showSent(returnable=True)
			if toRm in [[],None,'d']:
				return
			else:
				with Session(ENGINE) as session:
					which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{Fore.light_red}Remove {Fore.light_yellow}Number(s){Style.reset}",helpText="use a dash between numbers to specify a range,commas can be between numbers or ranges",data="list")
					for i in which:
						try:
							val=int(i)
							item=session.query(MailBox).filter(MailBox.mbid==toRm[val].mbid).first()
							session.delete(item)
							print(item,"Deleted!")
							session.commit()
							session.flush()
						except Exception as e:
							print(e,"moving on to next index...")
		except Exception as e:
			print(e)

	def addCmd(self,cmdName='',cmd=None,desc=''):
		self.cmds[cmdName]={}
		self.cmds[cmdName]['desc']=desc
		self.cmds[cmdName]['cmd']=cmd
		self.htext+=f"{Fore.light_yellow}{cmdName} - {Fore.light_steel_blue}{desc}{Style.reset}\n"

	def __init__(self):
		try:
			self.cmds={}
			self.addCmd(cmdName='help',cmd=self.print_help,desc='show help text')
			self.addCmd(cmdName='new contact',cmd=self.newContact,desc="make a new contact for the MailBox to use")
			self.addCmd(cmdName='search contact',cmd=self.searchContact,desc="look for a contact")
			self.addCmd(cmdName='rm contact',cmd=self.rmContact,desc="remove a contact(s)")
			self.addCmd(cmdName='rm mailbox',cmd=self.rmMailBox,desc="remove a MailBox Msg")
			self.addCmd(cmdName="edit contact",cmd=self.editContact,desc="edit a contact(s)")
			self.addCmd(cmdName="new mb",cmd=self.newEmail,desc="create and send a new email msg")
			self.addCmd(cmdName="show sent",cmd=self.showSent,desc="show sent emails")
			self.addCmd(cmdName="resend",cmd=self.resend,desc="resend a sent email")
			self.print_help()
			while True:
				keys=[i.lower() for i in self.cmds.keys()]
				real=[self.cmds[i]['cmd'] for i in self.cmds.keys()]
				fieldname='Menu'
				mode='RxTx'
				h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
				doWhat=Prompt.__init2__(self,func=FormBuilderMkText,ptext=f'{h} Do What? ',helpText=self.htext,data="string")
				if doWhat in [None,]:
					return
				elif doWhat in ['d',]:
					self.print_help()
				elif doWhat.lower() in keys:
					index=keys.index(doWhat.lower())
					real[index]()
				else:
					for num,i in enumerate(keys):
						if doWhat.lower() in i:
							real[num]()
							break


		except Exception as e:
			print(e,repr(e))

MailBox.metadata.create_all(ENGINE)
MailBoxContacts.metadata.create_all(ENGINE)
#RxTx()