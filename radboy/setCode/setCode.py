from radboy.DB.db import *
from radboy.FB.FormBuilder import *
from radboy.DB.Prompt import *
from radboy.DB.Prompt import prefix_text
from datetime import datetime
from radboy.Lookup2.Lookup2 import *
from copy import deepcopy

import radboy.TasksMode as TM

class SetCode:
	def advanced_search_and_create(self):
		results=Lookup(init_only=True).SearchAuto(returnable=True)
		if results not in [None,]:
			while True:
				which=Prompt.__init2__(self,func=FormBuilderMkText,ptext="Which result number do you wish to update the code for?",helpText="please type a number",data="integer")
				if which in [None,]:
					return
				elif isinstance(which,int):
					try:
						return [results[which],]
					except Exception as e:
						print(e)
						continue
				elif isinstance(which,str) and which in ['d','D']:
					return [results[0],]
				else:
					continue


	def setCodeFromBarcode(self):
		print("SetCode")
		if self.engine != None:
			with Session(self.engine) as session:
				self.batchMode=False
				while True:
						#batchMode=input("batch mode[y/n]: ")
						batchMode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Batch Mode[y/n]?",helpText="Yes or No",data="boolean")
						print(batchMode)
						if batchMode in [None,]:
							return
						if batchMode:
							self.batchMode=True
							break
						else:
							self.batchMode=False
							break
				while True:
					try:
						#barcode=input("barcode: ")
						barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Barcode:",helpText="Product UPC, or #qb to quit batch mode if in batch mode",data="varchar")
						if barcode in [None,]:
							continue
						if barcode.lower() == "#qb":
							break
						#checks needed here
						query=session.query(Entry).filter(Entry.Barcode==barcode,Entry.Barcode.icontains(barcode))
						results=query.all()
						if len(results) < 1:
							print("No Results")
							results=self.advanced_search_and_create()
							if results in [None,]:
								print(f"{Fore.orange_red_1}**No Results{Style.reset}")
								create_it=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Make New Entry?",helpText="Yes or No",data="boolean")
								if create_it in [None,]:
									return
								elif create_it == True:
									TM.Tasks.TasksMode(parent=self,engine=ENGINE,init_only=True).NewEntryMenu()
									print(f"{Fore.black}{Back.grey_70}**Now Look up the code again!{Style.reset}")
									continue
								else:
									continue
							else:
								tmp=deepcopy(results)
								results=[]
								for i in tmp:
									rr=session.query(Entry).filter(Entry.EntryId==i.EntryId).first()
									if isinstance(rr,Entry):
										results.append(rr)
						else:
							pass
						r=None
						if len(results) == 1:
							r=results[0]
							print(r)
						elif len(results) > 1:
							try:
								while True:
									for num,i in enumerate(results):
										print(f"{num}/{len(results)} -> {i}")
									#select=input("which Entry: ")
									select=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Which Entry?",helpText="please which item number",data="integer")
									if select in [None,]:
										continue
									if select.lower() == 'd':
										select=0
										r=results[select]
										break
									if select == "#qb":
										r=None
										break	
									#select=int(select)
									r=results[select]
									#print(self.batchMode)
									#if not self.batchMode:
									break
							except Exception as e:
								print(e)
						if r != None:
							ncode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="New Code, or #qb = quit batchMode?",helpText="new code to set, or #qb to quit batch mode",data="varchar")
							if ncode in [None,]:
								return
							if ncode.lower() == "#qb":
								break
							if ncode.lower() == 'd':
								ncode=''
							r.Code=ncode
							r.user_updated=True
							session.commit()
							session.flush()
							session.refresh(r)
							print(r,self.batchMode)
						if not self.batchMode:
							break
					except Exception as e:
						print(e)

	def __init__(self,engine=None):
		self.engine=engine
		cmds={
		'setCode from Barcode':{
								'cmds':['cfb','1','code<bc'],
								'exec':self.setCodeFromBarcode,
								'desc':"set Code from Barcode"
			},
		}

		while True:
			htext='\n'.join([f'{Fore.light_magenta}{cmds[i]["cmds"]} - {Fore.light_steel_blue}{cmds[i]["desc"]}{Style.reset}' for i in cmds])
			print(htext)
			fieldname='Menu'
			mode='setCode'
			h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
			action=Prompt.__init2__(self,func=FormBuilderMkText,ptext=f"{h} Do What? : ",helpText=htext,data="string")
			if action in [None,]:
				return
			for cmd in cmds:
				try:
					if action.lower() in cmds[cmd]['cmds'] and cmds[cmd]['exec']!=None:
						cmds[cmd]['exec']()
						break
					elif action.lower() in cmds[cmd]['cmds'] and cmds[cmd]['exec']==None:
						return
					else:
						raise Exception(f"Invalid Command! {action}")
				except Exception as e:
					print(f"{e}\n{str(e)}\n{repr(e)}\n{Fore.light_red}Testing {cmds[cmd]['cmds']} options against input text, '{action.lower()}' != ")

if __name__ == "__main__":
	SetCode()