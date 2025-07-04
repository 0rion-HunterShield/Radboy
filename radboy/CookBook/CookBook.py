from . import *


class CookBookUi:
	def total_rcp(self):
		with Session(ENGINE) as session:
			rcp=self.ls_rcp_names(asSelector=True,whole=True,names=True)
			if rcp is None:
				print("User returned, or no results!")
				return
			ct=len(rcp[0])
			htext=[]
			for i in rcp[0]:
				htext.append(i)
			htext='\n'.join(htext)
			print(htext)
			which=Prompt.__init2__(self,func=FormBuilderMkText,ptext="which index",helpText=f"{htext}\nindex of rcp to edit",data="integer")
			if which in [None,'d']:
				return
			try:
				totals={				
	"carb_per_serving":None,
    "fiber_per_serving":None,
    "protien_per_serving":None,
    "total_fat_per_serving":None,
    "saturated_fat_per_serving":None,
    "trans_fat_per_serving":None,
    "sodium_per_serving":None,
    "cholesterol_per_serving":None,
    "vitamin_d":None,
    "calcium":None,
    "iron":None,
    "potassium":None,
				}
				ingredients=session.query(CookBook).filter(CookBook.recipe_uid==rcp[-1][which].recipe_uid).all()
				last_unit=None
				for i in ingredients:
					for num,k in enumerate(totals):
						try:
							qty=getattr(i,k)
							unit=getattr(i,f'{k}_unit')
							QTY=pint.Quantity(qty,unit)
							
							used=pint.Quantity(i.IngredientQty,i.IngredientQtyUnit)
							servingSize=pint.Quantity(i.Serving_Size,i.Serving_Size_unit)
							ck=Fore.orange_red_1
							if (num%2)!=0 and num != 0:
								ck=Fore.light_steel_blue
							print(f"{ck}{i.recipe_name}|{i.IngredientName}|{k}={QTY}|amount used={used}|servingSize={servingSize}|used/servingSize={used/servingSize}|QTY*(used/servingSize)={QTY*(used/servingSize)}{Style.reset}")
							if totals[k] is None:
								totals[k]=QTY*(used/servingSize)
							else:
								totals[k]+=(QTY*(used/servingSize))
								
						except Exception as e:
							print(e,f"'{Fore.cyan}{k}{Style.reset}'wont be added to totals")
				ct=len(totals)
				for num,k in enumerate(totals):
					print(std_colorize(f"{k} = {totals[k]}",num,ct))
				print("Done Totaling!")
			except Exception as e:
				print(e)
		#edit everything found by searchtext using recipe_uid as the final selection parameter
	def create_new_rcp(self):
		with Session(ENGINE) as session:
			uid=uuid1()
			uid=str(uid)
			excludes=['cbid','DTOE','recipe_uid','Instructions','recipe_name']
			while True:
				try:
					cb=CookBook()
					cb.recipe_uid=uid
					session.add(cb)
					session.commit()
					entry=None
					while True:
						try:
							barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Barcode|Code|Name of Ingredient[enter=skip]:",helpText="what to search for in Entry",data="string")
							if barcode is None:
								print("User Cancelled Early")
								return
							elif barcode in ['d',]:
								break
							entry=session.query(Entry).filter(or_(Entry.Barcode==barcode,Entry.Barcode.icontains(barcode),Entry.Name.icontains(barcode),Entry.Code==barcode,Entry.Code.icontains(barcode)))

							entry=orderQuery(entry,Entry.Timestamp)
							entry=entry.all()
							ct=len(entry)
							if ct > 0:
								htext=[]
								for num, i in enumerate(entry):
									msg=f"{Fore.light_red}{num}/{Fore.medium_violet_red}{num+1} of {Fore.light_sea_green}{ct} -> {i.seeShort()}"
									htext.append(msg)
									print(msg)
								htext='\n'.join(htext)
								which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Which {Fore.light_red}index?{Fore.light_yellow}",helpText=f"{htext}\n{Fore.light_red}number{Fore.light_yellow} farthest to left of screen{Style.reset}",data="integer")
								if which not in [None,]:
									if which == 'd':
										entry=entry[0]
									else:
										entry=entry[which]
								else:
									htext=f"{Fore.orange_red_1}No Results for '{Fore.cyan}{barcode}{Fore.orange_red_1}'{Style.reset}"
									again=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Try another search?[yes/no=default]",helpText=htext,data="boolean")
									if again is None:
										return
									elif again in [False,'d']:
										entry=None
										break
									else:
										barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h}Barcode|Code|Name[b=skips search]: ",helpText="what was consumed?",data="string")
										continue
							else:
								entry=None
								htext=f"{Fore.orange_red_1}No Results for '{Fore.cyan}{barcode}{Fore.orange_red_1}'{Style.reset}"
								again=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Try another search?[yes/no=default]",helpText=htext,data="boolean")
								if again is None:
									return
								elif again in [False,'d']:
									break
								else:
									barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h}Barcode|Code|Name[b=skips search]: ",helpText="what was consumed?",data="string")
									continue
							break
						except Exception as e:
							print(e)
							return

					fields={i.name:{'default':getattr(cb,i.name),"type":str(i.type).lower()} for i in cb.__table__.columns if str(i.name) not in excludes}
					if entry is not None:
						fields['IngredientName']['default']=entry.Name
						fields['IngredientBarcode']['default']=entry.Barcode
						fields['IngredientCode']['default']=entry.Code
						if entry.Price is None:
							entry.Price=0
						if entry.Tax is None:
							entry.Tax=0
						if entry.CRV is None:
							entry.CRV=0
						fields['IngredientPricePerPurchase']['default']=float(Decimal(entry.Price+entry.CRV+entry.Tax).quantize(Decimal("0.00")))
					fd=FormBuilder(data=fields)
					if fd is None:
						session.delete(cb)
						session.commit()
						print("User Cancelled Early")
						return
								
					for k in fd:
						setattr(cb,k,fd[k])
					session.commit()
					htext="Add another ingredient?"
					again=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Try another search?[yes/no=default]",helpText=htext,data="boolean")
					if again is None:
						return
					elif again in [False,'d']:
						break
					else:
						continue
				except Exception as eee:
					print(eee)
					return
			instructions={
			'Instructions':{'default':'','type':'text'},
			'recipe_name':{'default':'','type':'string'}}
			fdi=FormBuilder(data=instructions)
			if fdi is None:
				print("User Quit Early, so all work has been deleted!")
				r=session.query(CookBook).filter(CookBook.recipe_uid==uid).delete()
				session.commit()
			else:
				session.query(CookBook).filter(CookBook.recipe_uid==uid).update(fdi)
				session.commit()

			results=session.query(CookBook).filter(CookBook.recipe_uid==uid)
			results=orderQuery(results,CookBook.DTOE,inverse=True)
			results=results.all()
			ctt=len(results)
			for num,i in enumerate(results):
				msg=std_colorize(i,num,ctt)
				print(msg)


	def fix_table(self):
		CookBook.__table__.drop(ENGINE)
		CookBook.metadata.create_all(ENGINE)


	def rm_rcp(self):
		with Session(ENGINE) as session:
			rcp=self.ls_rcp_names(asSelector=True,whole=True,names=True)
			if rcp is None:
				print("User returned, or no results!")
				return
			ct=len(rcp[0])
			htext=[]
			for i in rcp[0]:
				htext.append(i)
			htext='\n'.join(htext)
			print(htext)
			which=Prompt.__init2__(self,func=FormBuilderMkText,ptext="which index",helpText=f"{htext}\nindex of rcp to delete",data="integer")
			if which in [None,'d']:
				return
			try:
				query_2=session.query(CookBook).filter(CookBook.recipe_uid==rcp[-1][which].recipe_uid).delete()
				session.commit()
				print("Done Deleting!")
			except Exception as e:
				print(e)
		#delete everything found by searchtext using recipe_uid as the final selection parameter
		
	def edit_rcp(self):
		with Session(ENGINE) as session:
			rcp=self.ls_rcp_names(asSelector=True,whole=True,names=True)
			if rcp is None:
				print("User returned, or no results!")
				return
			ct=len(rcp[0])
			htext=[]
			for i in rcp[0]:
				htext.append(i)
			htext='\n'.join(htext)
			print(htext)
			which=Prompt.__init2__(self,func=FormBuilderMkText,ptext="which index",helpText=f"{htext}\nindex of rcp to edit",data="integer")
			if which in [None,'d']:
				return
			try:
				query_2=session.query(CookBook).filter(CookBook.recipe_uid==rcp[-1][which].recipe_uid).first()
				fields={
				'recipe_name':{'default':getattr(query_2,'recipe_name'),'type':"string"},
				'Instructions':{'default':getattr(query_2,'Instructions'),'type':"string"},
				}
				fd=FormBuilder(data=fields)
				if fd is not None:
					r=session.query(CookBook).filter(CookBook.recipe_uid==query_2.recipe_uid)
					r.update(fd)
					session.commit()
				print("Done Editing!")
			except Exception as e:
				print(e)
		#edit everything found by searchtext using recipe_uid as the final selection parameter

	def rm_ingredient(self):
		with Session(ENGINE) as session:
			rcp=self.ls_rcp_names(asSelector=True,whole=True,names=True)
			if rcp is None:
				print("User returned, or no results!")
				return
			ct=len(rcp[0])
			htext=[]
			for i in rcp[0]:
				htext.append(i)
			htext='\n'.join(htext)
			print(htext)
			which=Prompt.__init2__(self,func=FormBuilderMkText,ptext="which index",helpText=f"{htext}\nindex of rcp to delete its ingredients",data="integer")
			if which in [None,'d']:
				return
			try:
				query_2=session.query(CookBook).filter(CookBook.recipe_uid==rcp[-1][which].recipe_uid)
				ordered_2=orderQuery(query_2,CookBook.DTOE)
				results_2=ordered_2.all()
				ct=len(results_2)
				for num,i in enumerate(results_2):
					print(std_colorize(i,num,ct))
					delete=Prompt.__init2__(self,func=FormBuilderMkText,ptext="Delete[default=False]?",helpText="delete it, yes or no?",data="boolean")
					if delete in [None,]:
						return
					elif delete in ['d',]:
						continue
					elif delete == True:
						session.delete(i)
						session.commit()
			except Exception as e:
				print(e)
		#find a recipe, list its ingredients, select ingredients to delete, delete selected ingredients

	#asSelector==False,whole==True,names==False - print selector_string_whole
	#asSelector==False,whole==False,names==True - print selector_string_names
	#asSelector==False,whole==True,names==True - print selector_string_whole,selector_string_names
	#asSelector==True,whole==True,names==False - return selector_string_whole,selector_list
	#asSelector==True,whole==False,names==True - return selector_string_names,selector_list
	#asSelector==True,whole==True,names==True - return selector_string_names,selector_string_whole,selector_list
	def ls_rcp_names(self,asSelector=False,whole=False,names=False):
		with Session(ENGINE) as session:
			selector_list=[]
			selector_string_names=[]
			selector_string_whole=[]

			searchText=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What are you looking for?",helpText="text to search for",data="string")
			if searchText is None:
				return
			includes=["string","varchar","text"]
			excludes=['cbid','DTOE']
			fields=[i.name for i in CookBook.__table__.columns if str(i.name) not in excludes and str(i.type).lower() in includes]
			q=[]
			for i in fields:
				q.append(getattr(CookBook,i).icontains(searchText))
			query=session.query(CookBook).filter(or_(*q))
			grouped=query.group_by(CookBook.recipe_uid)
			ordered=orderQuery(grouped,CookBook.DTOE,inverse=True)

			results=ordered.all()
			ct=len(results)
			if ct <= 0:
				print("No Results")
				return None
			for num,i in enumerate(results):
				selector_list.append(i)
				selector_string_whole.append(std_colorize(i,num,ct))
				selector_string_names.append(std_colorize(f"{i.recipe_name} - {i.recipe_uid}",num,ct))
				if not asSelector:
					if whole:
						print(selector_string_whole[num])
					if names:
						print(selector_string_names[num])
			if asSelector:
				if whole and not names:
					return selector_string_whole,selector_list
				elif names and not whole:
					return selector_string_names,selector_list
				elif names and whole:
					return selector_string_names,selector_string_whole,selector_list

	def ls_rcp_ingredients(self):
		with Session(ENGINE) as session:
			rcp=self.ls_rcp_names(asSelector=True,whole=True,names=True)
			if rcp is None:
				print("User returned, or no results!")
				return
			ct=len(rcp[0])
			htext=[]
			for i in rcp[0]:
				htext.append(i)
			htext='\n'.join(htext)
			print(htext)
			which=Prompt.__init2__(self,func=FormBuilderMkText,ptext="which index",helpText=f"{htext}\nindex of rcp to view its ingredients",data="integer")
			if which in [None,'d']:
				return
			try:
				query_2=session.query(CookBook).filter(CookBook.recipe_uid==rcp[-1][which].recipe_uid)
				ordered_2=orderQuery(query_2,CookBook.DTOE)
				results_2=ordered_2.all()
				ct=len(results_2)
				for num,i in enumerate(results_2):
					print(std_colorize(i,num,ct))
			except Exception as e:
				print(e)

	def edit_rcp_ingredients(self):
		with Session(ENGINE) as session:
			rcp=self.ls_rcp_names(asSelector=True,whole=True,names=True)
			if rcp is None:
				print("User returned, or no results!")
				return
			ct=len(rcp[0])
			htext=[]
			for i in rcp[0]:
				htext.append(i)
			htext='\n'.join(htext)
			print(htext)
			which=Prompt.__init2__(self,func=FormBuilderMkText,ptext="which index",helpText=f"{htext}\nindex of rcp to view its ingredients",data="integer")
			if which in [None,'d']:
				return
			try:
				query_2=session.query(CookBook).filter(CookBook.recipe_uid==rcp[-1][which].recipe_uid)
				ordered_2=orderQuery(query_2,CookBook.DTOE)
				results_2=ordered_2.all()
				ct=len(results_2)
				for num,i in enumerate(results_2):
					print(std_colorize(i,num,ct))
					edit=Prompt.__init2__(self,func=FormBuilderMkText,ptext="Edit[default=False]?",helpText="Edit it, yes or no?",data="boolean")
					if edit in [None,]:
						return
					elif edit in ['d',]:
						continue
					elif edit == True:
						excludes=['cbid','recipe_uid','recipe_name','DTOE']
						fields={ii.name:{'default':getattr(i,ii.name),'type':str(ii.type).lower()} for ii in CookBook.__table__.columns if ii.name not in excludes}
						fd=FormBuilder(data=fields)
						if fd is not None:
							for k in fd:
								setattr(i,k,fd[k])
							session.commit()
						else:
							continue
			except Exception as e:
				print(e)
					

	def __init__(self):
		cmds={
			str(uuid1()):{
				'cmds':generate_cmds(startcmd=['create new','cn','cnw'],endCmd=['recipe','rcp']),
				'desc':"create a new recipe",
				'exec':self.create_new_rcp,
			},
			uuid1():{
				'cmds':generate_cmds(startcmd=['fix','fx'],endCmd=['tbl','table']),
				'desc':"reinstall table",
				'exec':self.fix_table,
			},
			uuid1():{
				'cmds':generate_cmds(startcmd=['rm','del','remove','delete'],endCmd=['recipe','rcp']),
				'desc':"delete a recipe(delete everything found by searchtext using recipe_uid as the final selection parameter)",
				'exec':self.rm_rcp,
			},
			uuid1():{
				'cmds':generate_cmds(startcmd=['rm','del','remove','delete'],endCmd=['ingredient','ingrdnt','component','cmpnt']),
				'desc':"delete a recipe ingredient/component(find a recipe, list its ingredients, select ingredients to delete, delete selected ingredients)",
				'exec':self.rm_ingredient,
			},
			uuid1():{
				'cmds':generate_cmds(startcmd=['ls','list','lst'],endCmd=['rcp','recipe']),
				'desc':"list recipe names",
				'exec':lambda self=self:self.ls_rcp_names(asSelector=False,whole=False,names=True),
			},
			uuid1():{
				'cmds':generate_cmds(startcmd=['ls','list','lst'],endCmd=['rcp ingrdnts','recipe ingredients']),
				'desc':"list recipe names",
				'exec':lambda self=self:self.ls_rcp_ingredients(),
			},
			uuid1():{
				'cmds':generate_cmds(startcmd=['ed','edt','edit'],endCmd=['rcp ingrdnts','recipe ingredients']),
				'desc':"edit recipe ingredients",
				'exec':lambda self=self:self.edit_rcp_ingredients(),
			},
			uuid1():{
				'cmds':generate_cmds(startcmd=['ed','edt','edit'],endCmd=['rcp','recipe']),
				'desc':"edit recipe names and instructions",
				'exec':lambda self=self:self.edit_rcp(),
			},
			uuid1():{
				'cmds':generate_cmds(startcmd=['ttl','total',],endCmd=['rcp','recipe']),
				'desc':"total nutritional facts",
				'exec':lambda self=self:self.total_rcp(),
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
