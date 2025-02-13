from radboy.DB.db import *

class ListMode2:
	def __init__(self,engine,parent):
		self.engine=engine
		self.parent=parent
		code=''
		options=['q - quit - 1','2 - b - back','skip','?']
		while True:
			fail=False
			code=input(f"{Style.reset}{Fore.green}Code|Barcode{Style.reset}{options}{Style.bold}\n: ")
			print(f"{Style.reset}")
			if code.lower() in ['q','quit','1']:
				exit('user quit!')
			elif code in ['2','b','back']:
				return
			elif code.lower() in ['?']:
				self.parent.help()
				self.code_other_cmds=True
			elif self.parent.Unified(code):
				self.code_other_cmds=True
			elif code == '':
				#code='0'*8
				pass
			elif code == 'tlm':
				self.listMode=not self.listMode
				print(f"ListMode is now: {Fore.red}{self.listMode}{Style.reset}")
			elif code == 'slm':
				print(f"ListMode is: {Fore.red}{self.listMode}{Style.reset}")
			else:
				with Session(self.engine) as session:
					query=session.query(Entry).filter(or_(Entry.Barcode==code,Entry.Code==code))
					item=query.first()
					if item:
						item.InList=True
						print(item.ListQty)
						item.ListQty+=1
						session.commit()
						session.refresh(item)
						print(item)
					else:
						print(f"{Fore.misty_rose1}{Style.bold}No Item exists with the barcode|code =ing '{Style.blink}{Style.underline}{code}{Style.reset}'")