#Collector2.py
from radboy.DB.db import *
from radboy.DB.Prompt import *

import radboy.Unified.Unified as unified


class Collector2:
    def __init__(self,engine,parent):
        self.parent=parent
        self.engine=engine



        self.cmds={
        'quit':{
            'cmds':['q','quit'],
            'exec':lambda :exit("user quit"),
            'desc':'quit program!'
        },
        'back':{
            'cmds':['b','back'],
            'exec':None,
            'desc':'go back a menu if any'
        },
        'collect':{
            'cmds':['collect','1'],
            'exec':self.collect,
            'desc':'collect code pairs',
        },
        'collect+':{
            'cmds':['collect+','1+'],
            'exec':self.collect_plus,
            'desc':'collect code pairs, but do add new code if already in Entry table by Barcode',
        },
        'collect_barcode':{
            'cmds':['collect_barcode','1b'],
            'exec':self.collect_barcode,
            'desc':'collect code pairs',
        },
         'collect_barcode+':{
            'cmds':['collect_barcode','1b+'],
            'exec':self.collect_barcode_plus,
            'desc':'collect code pairs, but do add new code if already in Entry table by Barcode',
        },
        'collect_barcode_w_nu_code':{
            'cmds':['collect_barcode_w_nu_code','1bnuc'],
            'exec':self.collect_barcode_w_nu_code,
            'desc':'collect code pairs with item code, but do not check item code uniqueness [all item code duplicates!]',
        },
         'collect_barcode_w_nu_code_plus':{
            'cmds':['collect_barcode_w_nu_code+','1bnuc+'],
            'exec':self.collect_barcode_w_nu_code_plus,
            'desc':'collect code pairs with item code, but do not check item code uniqueness [all item code duplicates!], check entry db for barcodes dont add if found',
        },
        'collect_barcode_wo_nu_code':{
            'cmds':['collect_barcode_w_nu_code','1bnoc'],
            'exec':self.collect_barcode_wo_nu_code,
            'desc':'collect code pairs without item code!]',
        },
        'collect_barcode_wo_nu_code_plus':{
            'cmds':['collect_barcode_w_nu_code+','1bnoc+'],
            'exec':self.collect_barcode_wo_nu_code_plus,
            'desc':'collect code pairs without item code, but do not add if found in Entry table!]',
        },
        'export':{
            'cmds':['export','2'],
            'exec':self.export,
            'desc':'export code pairs',
        },
        'edit':{
            'cmds':['edit','3'],
            'exec':self.edit,
            'desc':'edit code pairs',
        },
        'list':{
            'cmds':['list','4'],
            'exec':self.list,
            'desc':'list code pairs',
        },
        'save':{
            'cmds':['save_cp','5'],
            'exec':self.saveAll,
            'desc':'save code pairs to img',
        },
         'save_csv':{
            'cmds':['save_pc_csv','pc-5-csv'],
            'exec':self.saveAllCSV,
            'desc':'save code pairs to csv',
        },
        'clear':{
            'cmds':['clear_all_cp','6'],
            'exec':self.clearAll,
            'desc':'clear all code pairs',
        },
        'remove':{
            'cmds':['remove_pc','7'],
            'exec':self.removePC,
            'desc':'remove code pair',
        },
        'removeBy':{
            'cmds':['rmby','8'],
            'exec':self.removeBy,
            'desc':'remove code pair by field==value',
        },
        'barName':{
            'cmds':['1bn','9'],
            'exec':self.BarNameCollector,
            'desc':'Collect Barcode and Name, Code="No_CODE"',
        },
        'barName+':{
            'cmds':['1bn+','9+'],
            'exec':self.BarNameCollector_plus,
            'desc':'Collect Barcode and Name, Code="No_CODE", but do not add if already in Entry table',
        },
        'collect_barcode_code_name':{
            'cmds':['1bcn','10'],
            'exec':self.collect_barcode_code_name,
            'desc':'Collect Barcode,Code,Name',
        },
        'collect_barcode_code_name+':{
            'cmds':['1bcn+','10+'],
            'exec':self.collect_barcode_code_name_plus,
            'desc':'Collect Barcode,Code,Name; Do not add if already in Entry table',
        },
        '?PC?':{
            'cmds':['help',],
            'exec':self.helpSMG,
            'desc':"show help!"
        },
        '?unified':{
            'cmds':['?unified',],
            'exec':self.helpSMG2,
            'desc':"unified cmds!"
        }
        }
        while True:
            #cmd=input("do what[help]? :")
            def mkText(text,self):
                    if text in ['',]:
                        return None
                    else:
                        return text
            fieldname='Menu'
            mode='Collect'
            h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
            cmd=Prompt.__init2__(None,func=mkText,ptext=f"{h}Do What[h|help]",helpText=self.help2(),data=self)
            if cmd in [None,]:
                break
            for c in self.cmds:
                if self.cmds[c]['exec']!=None and cmd.lower() in self.cmds[c]['cmds'] or cmd.split(",")[0].lower() in self.cmds[c]['cmds']:
                    if cmd.split(',')[0].lower() in ['edit','3'] or cmd.lower() in ["edit",'3']:
                        if len(cmd.split(",")) == 2:
                            self.edit(cmd.split(",")[1])
                        elif len(cmd.split(",")) == 3:
                            self.edit(cmd.split(",")[1],cmd.split(",")[2])
                        elif len(cmd.split(",")) == 4:
                            self.edit(cmd.split(",")[1],cmd.split(",")[2],cmd.split(",")[3])
                        else:
                            print("""
#edit,$PCId - prompt for value and entry
#edit,$PCId,field - prompt for value
#edit,$PCId,field,value - set field=$field,value=$value no prompt
                        """)
                    elif cmd.split(',')[0].lower() in ['list','4'] or cmd.lower() in ["list",'4']:
                        if len(cmd.split(",")) == 2:
                            self.list(cmd.split(",")[1])
                        else:
                            print("""
#list,$PCId - print PC
#list,all - list all PC
                        """)

                    elif cmd.split(',')[0].lower() in ['remove_pc','7'] or cmd.lower() == ["remove_pc",'7']:
                        if len(cmd.split(",")) == 2:
                            self.removePC(cmd.split(",")[1])
                        elif len(cmd.split(",")) == 3:
                            self.removePC(cmd.split(",")[1],onlyID=bool(cmd.split(",")[2]))
                        else:
                            print("""
#remove_pc,$PCId - remove codePair by ID
#remove_pc,$PCId,onlyId - remove codepair by id only if True , if set to false will go by code|barcode|id and will delete all if all exist DANGEROUS!!!
#remove_cp, - show this
                        """)
                    else:
                        if self.cmds[c]['exec'] == None:
                            return
                        self.cmds[c]['exec']()
                    break
                elif self.cmds[c]['exec']==None and cmd.lower() in self.cmds[c]['cmds']:
                    return
                elif self.parent != None and self.parent.Unified(cmd):
                    print("ran an external command!")
                    break
    def checkEntryForBarcode(self,barcode):
        try:
            with Session(self.engine) as session:
                results=session.query(Entry).filter(Entry.Barcode==barcode).all()
                ct=len(results)
                if ct != 0:
                    print(f"{Fore.light_magenta}{'-*-'*2} Entry Found {'-*-'*2}{Style.reset}")
                for num,i in enumerate(results):
                    msg=f"""{Fore.yellow}{num}/{Style.reset}{Fore.light_red}{ct}{Style.reset} {Fore.magenta}{Style.bold}FOUND{Style.reset} -> {i}"""
                    print(msg)
                if ct != 0:
                    print(f"{Fore.light_magenta}{'-*-'*2} Entry Found {'-*-'*2}{Style.reset}")
                if ct == 0:
                    return False
                elif ct != 0:
                    return True
        except Exception as e:
            print(e)

    def saveAllCSV(self):
        with Session(self.engine) as session:
            query=session.query(PairCollection)
            df = pd.read_sql(query.statement, query.session.bind)
            def mkT(text,self):
                if text in ['','.','..']:
                    return "db.csv"
                return text
            while True:
                try:
                    efilename=Prompt.__init2__(None,func=mkT,ptext="Save where",helpText="save the data to where?",data=self)

                    if isinstance(efilename,str):
                        df=df[['Barcode','Code','Name']]
                        df.to_csv(efilename,sep=';')
                        print(f"{Fore.dark_goldenrod}{df}{Style.reset}")
                        msg=f"{Fore.cyan}{Style.bold}Saved to '{Fore.light_yellow}{Style.underline}{Path(efilename).absolute()}{Style.reset}{Fore.cyan}'!{Style.reset}"
                        print(msg)
                    break
                except Exception as e:
                    print(e)


    def edit(self,ID,field=None,value=None):
        try:
            if field and value:
                with Session(self.engine) as session:
                    result=session.query(PairCollection).filter(PairCollection.PairCollectionId==ID).first()
                    if result:
                        setattr(result,field,value)
                        session.commit()
                        session.flush()
                        session.refresh(result)
                        print(result)
                    else:
                        print(f"{Fore.red}{Back.white}{'*'*20}{Style.reset}\n{Fore.dark_goldenrod}No Result!{Style.reset}\n{Fore.red}{Back.white}{'*'*20}{Style.reset}")
            if field and not value:
                with Session(self.engine) as session:
                    result=session.query(PairCollection).filter(PairCollection.PairCollectionId==ID).first()
                    if result:
                        value=input(f"{Fore.red}{field}{Style.reset} : ")
                        setattr(result,field,value)
                        session.commit()
                        session.flush()
                        session.refresh(result)
                        print(result)
                    else:
                        print(f"{Fore.red}{Back.white}{'*'*20}{Style.reset}\n{Fore.dark_goldenrod}No Result!{Style.reset}\n{Fore.red}{Back.white}{'*'*20}{Style.reset}")
            if not field and not value:
                with Session(self.engine) as session:
                    result=session.query(PairCollection).filter(PairCollection.PairCollectionId==ID).first()
                    if result:
                        field=input(f"{','.join([i.name for i in PairCollection.__table__.columns])}\n{Fore.yellow}Field{Style.reset}: ")
                        value=input(f"{Fore.red}{field}OLD:{Style.reset}({getattr(result,field)}) : ")
                        setattr(result,field,value)
                        session.commit()
                        session.flush()
                        session.refresh(result)
                        print(result)
                    else:
                        print(f"{Fore.red}{Back.white}{'*'*20}{Style.reset}\n{Fore.dark_goldenrod}No Result!{Style.reset}\n{Fore.red}{Back.white}{'*'*20}{Style.reset}")
        except Exception as e:
            print(e)

    def saveAll(self):
         with Session(self.engine) as session:
                    result=session.query(PairCollection).all()
                    try:
                        for num, r in enumerate(result):
                            print(f"""{Fore.red}{num}{Style.reset} -> {r}""")
                            r.saveItemData(num=num)
                    except Exception as e:
                        print(f"""{Fore.red}0{Style.reset} -> {result}""")
    def clearAll(self):
         with Session(self.engine) as session:
            result=session.query(PairCollection).delete()
            session.commit()
            session.flush()
            print(result)

    def removeBy(self,):
        while True:
            try:
            
                def mkBool(text,data):
                    if text.lower() in ['y','yes','true','1',]:
                        return True
                    elif text.lower() in ['n','no','false','0']:
                        return False
                    else:
                        return None

                def mkT(text,self):
                    return text

                all_=Prompt.__init2__(None,func=mkBool,ptext="Delete All Results?",helpText="if yes, all results will be deleted!",data=self)
                if all_ == None:
                    return
                field=Prompt.__init2__(None,func=mkT,ptext="FieldName?",helpText=",".join([i.name for i in PairCollection.__table__.columns]),data=self)
                if field == None:
                    return
                while True:
                    value=Prompt.__init2__(None,func=mkT,ptext="Value?",helpText="exact value to delete by",data=self)
                    if value == None:
                        return

                    with Session(self.engine) as session:
                        query=session.query(PairCollection).filter(getattr(PairCollection,field)==value)
                        results=[]
                        if all_:
                            results=[i for i in query.all()]
                        else:
                            results.append(query.first())
                        ct=len(results)
                        for num,r in enumerate(results):
                            if r:
                                print(f"{Fore.light_green}{num}/{Fore.light_red}{ct-1} - {Fore.cyan}deleting -> {r}")
                                session.delete(r)
                                if num%10==0:
                                    session.commit()
                                session.commit()
                    another=Prompt.__init2__(None,func=mkBool,ptext="Another?",helpText="if yes, ask for another $code to delete!",data=self)
                    if another == False:
                        break
                    elif another == None:
                        return
                return
            except Exception as e:
                print(e)

    def list(self,ID=None):
        try:
            if ID == None:
                ID=input("{Fore.green_yellow}ID{Style.reset}|{Fore.cyan}Code{Style.reset}|{Fore.rgb(254,20,36)}Barcode to remove:{Style.reset} ")
            if ID.lower() not in ["all",'a','al','*']:
                with Session(self.engine) as session:
                    result=session.query(PairCollection).filter(or_(PairCollection.PairCollectionId==int(ID),PairCollection.Barcode==ID,PairCollection.Code==ID)).all()
                    try:
                        for num, r in result:
                            print(f"""{Fore.red}{num}{Style.reset} -> {r}""")
                    except Exception as e:
                        print(f"""{Fore.red}0{Style.reset} -> {result}""")
            else:
                with Session(self.engine) as session:
                    result=session.query(PairCollection).all()
                    try:
                        for num, r in enumerate(result):
                            print(f"""{Fore.red}{num}{Style.reset} -> {r}""")
                    except Exception as e:
                        print(f"""{Fore.red}0{Style.reset} -> {result}""")
        except Exception as e:
            print(e)

    def removePC(self,ID=None,onlyID=True):
        try:
            if ID == None:
                ID=input("{Fore.green_yellow}ID{Style.reset}|{Fore.cyan}Code{Style.reset}|{Fore.rgb(254,20,36)}Barcode to remove:{Style.reset} ")
            if ID.lower() != "":
                if not onlyID:
                    with Session(self.engine) as session:
                        result=session.query(PairCollection).filter(or_(PairCollection.PairCollectionId==int(ID),PairCollection.Barcode==ID,PairCollection.Code==ID)).delete()
                        print(result)
                        session.commit()
                        session.flush()
                else:
                    with Session(self.engine) as session:
                        result=session.query(PairCollection).filter(PairCollection.PairCollectionId==int(ID)).delete()
                        print(result)
                        session.commit()
                        session.flush()
        except Exception as e:
            print(e)

    def helpSMG2(self):
        self.parent.Unified('?')

    def help2(self):
        tmp=[]
        for num,k in enumerate(self.cmds):
            if num%2==0:
                color=Fore.green
                color2=Fore.cyan
            else:
                color=Fore.light_magenta
                color2=Fore.light_red
            tmp.append(f"{color}{self.cmds[k]['cmds']}{Style.reset} - {color2}{self.cmds[k]['desc']}{Style.reset}")
        return '\n'.join(tmp)

    def helpSMG(self):
        for num,k in enumerate(self.cmds):
            if num%2==0:
                color=Fore.green
                color2=Fore.cyan
            else:
                color=Fore.light_magenta
                color2=Fore.light_red
            print(f"{color}{self.cmds[k]['cmds']}{Style.reset} - {color2}{self.cmds[k]['desc']}{Style.reset}")

    def export(self):
        with Session(self.engine) as session:
            result=session.query(PairCollection).all()
            for num,i in enumerate(result):
                i.saveItemData(num=num)
                print(i)
            if len(result) < 1:
                print(f"{Fore.red}{Back.white}{'*'*20}{Style.reset}\n{Fore.dark_goldenrod}No Items in List!{Style.reset}\n{Fore.red}{Back.white}{'*'*20}{Style.reset}")
            else:
                print(f"{Fore.green}{Back.white}{'*'*20}{Style.reset}\n{Fore.dark_goldenrod}List Contains {len(result)} PairCollection()'s\n{Style.reset}{Fore.green}{Back.white}{'*'*20}{Style.reset}")


    def collect(self):
        while True:
            try:
                print(Style.reset)
                def mkText(text,self):
                    if text in ['',]:
                        return None
                    else:
                        return text
                fieldnameH='1'
                modeH='Collect'
                h=f'{Prompt.header.format(Fore=Fore,mode=modeH,fieldname=fieldnameH,Style=Style)}'
                barcode=Prompt.__init2__(None,func=mkText,ptext=f"{h}Barcode[h|help]",helpText=self.help2(),data=self)
                if barcode in [None,]:
                    return
                
                code=Prompt.__init2__(None,func=mkText,ptext=f"{h}Shelf Code/Code[h|help]",helpText=self.help2(),data=self)
                if code in [None,]:
                    return
                
                if barcode in ['','n/a'] and code not in ['','n/a']:
                    barcode=code
                elif barcode not in ['','n/a'] and code in ['','n/a']:
                    pass
                elif barcode not in ['','n/a'] and code not in ['','n/a']:
                    pass
                else:
                    raise Exception(f"1 Not Enough Values!{barcode}|BCD CD|{code}")


                if code in ['','n/a'] and barcode not in ['','n/a']:
                    code=barcode
                elif code not in ['','n/a'] and barcode not in ['','n/a']:
                    pass
                else:
                    raise Exception(f"2 Not Enough Values! {barcode}|BCD CD|{code}")

                print(Style.reset)
                with Session(self.engine) as session:
                    query=session.query(PairCollection).filter(or_(PairCollection.Barcode==barcode,PairCollection.Code==code))
                    result=query.first()
                    if not result:
                        pcd=PairCollection(Barcode=barcode,Code=code)
                        session.add(pcd)
                        session.commit()
                        session.flush()
                        session.refresh(pcd)
                        print(f"{Back.green}{'*'*10}{Style.reset}\n{pcd}\n{Back.green}{'*'*10}{Style.reset}")

                    else:
                        print(f"{Back.red}{'*'*10}{Style.reset}\n{result}\n{Back.red}{'*'*10}{Style.reset}")
                print(Style.reset)
            except Exception as e:
                print(e)
    def collect_plus(self):
        while True:
            try:
                print(Style.reset)
                def mkText(text,self):
                    if text in ['',]:
                        return None
                    else:
                        return text
                fieldnameH='1+'
                modeH='Collect'
                h=f'{Prompt.header.format(Fore=Fore,mode=modeH,fieldname=fieldnameH,Style=Style)}'
                barcode=Prompt.__init2__(None,func=mkText,ptext=f"{h}Barcode[h|help]",helpText=self.help2(),data=self)
                if barcode in [None,]:
                    return
                
                code=Prompt.__init2__(None,func=mkText,ptext=f"{h}Shelf Code/Code[h|help]",helpText=self.help2(),data=self)
                if code in [None,]:
                    return
                
                if barcode in ['','n/a'] and code not in ['','n/a']:
                    barcode=code
                elif barcode not in ['','n/a'] and code in ['','n/a']:
                    pass
                elif barcode not in ['','n/a'] and code not in ['','n/a']:
                    pass
                else:
                    raise Exception(f"1 Not Enough Values!{barcode}|BCD CD|{code}")


                if code in ['','n/a'] and barcode not in ['','n/a']:
                    code=barcode
                elif code not in ['','n/a'] and barcode not in ['','n/a']:
                    pass
                else:
                    raise Exception(f"2 Not Enough Values! {barcode}|BCD CD|{code}")
                t=self.checkEntryForBarcode(barcode=barcode)
                if t:
                    continue
                print(Style.reset)
                with Session(self.engine) as session:
                    query=session.query(PairCollection).filter(or_(PairCollection.Barcode==barcode,PairCollection.Code==code))
                    result=query.first()
                    if not result:
                        pcd=PairCollection(Barcode=barcode,Code=code)
                        session.add(pcd)
                        session.commit()
                        session.flush()
                        session.refresh(pcd)
                        print(f"{Back.green}{'*'*10}{Style.reset}\n{pcd}\n{Back.green}{'*'*10}{Style.reset}")

                    else:
                        print(f"{Back.red}{'*'*10}{Style.reset}\n{result}\n{Back.red}{'*'*10}{Style.reset}")
                print(Style.reset)
            except Exception as e:
                print(e)

    def collect_barcode(self):
        while True:
            try:
                print(Style.reset)

                def mkText(text,self):
                    if text in ['',]:
                        return None
                    else:
                        return text
                fieldnameH='1b'
                modeH='Collect'
                h=f'{Prompt.header.format(Fore=Fore,mode=modeH,fieldname=fieldnameH,Style=Style)}'
                barcode=Prompt.__init2__(None,func=mkText,ptext=f"{h}Barcode[h|help]",helpText=self.help2(),data=self)
                if barcode in [None,]:
                    return
                
                print(Style.reset)
                with Session(self.engine) as session:
                    query=session.query(PairCollection).filter(PairCollection.Barcode==barcode)
                    result=query.first()
                    if not result:
                        pcd=PairCollection(Barcode=barcode,Code='',Name=f"New Item Created From Scan @ {datetime.now().ctime()}")
                        session.add(pcd)
                        session.commit()
                        session.flush()
                        session.refresh(pcd)
                        print(f"{Back.green}{'*'*10}{Style.reset}\n{pcd}\n{Back.green}{'*'*10}{Style.reset}")

                    else:
                        print(f"{Back.red}{'*'*10}{Style.reset}\n{result}\n{Back.red}{'*'*10}{Style.reset}")
                print(Style.reset)
            except Exception as e:
                print(e)
    
    def collect_barcode_plus(self):
        while True:
            try:
                print(Style.reset)
                def mkText(text,self):
                    if text in ['',]:
                        return None
                    else:
                        return text
                fieldnameH='1b+'
                modeH='Collect'
                h=f'{Prompt.header.format(Fore=Fore,mode=modeH,fieldname=fieldnameH,Style=Style)}'
                barcode=Prompt.__init2__(None,func=mkText,ptext=f"{h}Barcode[h|help]",helpText=self.help2(),data=self)
                if barcode in [None,]:
                    return

                t=self.checkEntryForBarcode(barcode=barcode)
                if t:
                    continue
                print(Style.reset)
                with Session(self.engine) as session:
                    query=session.query(PairCollection).filter(PairCollection.Barcode==barcode)
                    result=query.first()
                    if not result:
                        pcd=PairCollection(Barcode=barcode,Code='',Name=f"New Item Created From Scan @ {datetime.now().ctime()}")
                        session.add(pcd)
                        session.commit()
                        session.flush()
                        session.refresh(pcd)
                        print(f"{Back.green}{'*'*10}{Style.reset}\n{pcd}\n{Back.green}{'*'*10}{Style.reset}")

                    else:
                        print(f"{Back.red}{'*'*10}{Style.reset}\n{result}\n{Back.red}{'*'*10}{Style.reset}")
                print(Style.reset)
            except Exception as e:
                print(e)

    def collect_barcode_wo_nu_code(self):
        while True:
            try:                
                def mkText(text,self):
                    if text in ['',]:
                        return None
                    else:
                        return text

                fieldnameH='1bnoc'
                modeH='Collect'
                h=f'{Prompt.header.format(Fore=Fore,mode=modeH,fieldname=fieldnameH,Style=Style)}'
                barcode=Prompt.__init2__(None,func=mkText,ptext=f"{h}Barcode to Store in PairCollections[h|help]",helpText=self.help2(),data=self)
                if barcode in [None,]:
                    return
                
                with Session(self.engine) as session:
                    query=session.query(PairCollection).filter(PairCollection.Barcode==barcode)
                    result=query.first()
                    if not result:
                        pcd=PairCollection(Barcode=barcode,Code="No_CODE",Name=f"New Item Created From Scan @ {datetime.now().ctime()}")
                        session.add(pcd)
                        session.commit()
                        session.flush()
                        session.refresh(pcd)
                        print(f"{Back.green}{'*'*10}{Style.reset}\n{pcd}\n{Back.green}{'*'*10}{Style.reset}")

                    else:
                        print(f"{Back.red}{'*'*10}{Style.reset}\n{result}\n{Back.red}{'*'*10}{Style.reset}")
                print(Style.reset)
            except Exception as e:
                print(e)
    def collect_barcode_wo_nu_code_plus(self):
        while True:
            try:                
                def mkText(text,self):
                    if text in ['',]:
                        return None
                    else:
                        return text
                        
                fieldnameH='1bnoc+'
                modeH='Collect'
                h=f'{Prompt.header.format(Fore=Fore,mode=modeH,fieldname=fieldnameH,Style=Style)}'
                barcode=Prompt.__init2__(None,func=mkText,ptext=f"{h}Barcode to Store in PairCollections[h|help]",helpText=self.help2(),data=self)
                if barcode in [None,]:
                    return

                t=self.checkEntryForBarcode(barcode=barcode)
                if t:
                    continue
                with Session(self.engine) as session:
                    query=session.query(PairCollection).filter(PairCollection.Barcode==barcode)
                    result=query.first()
                    if not result:
                        pcd=PairCollection(Barcode=barcode,Code="No_CODE",Name=f"New Item Created From Scan @ {datetime.now().ctime()}")
                        session.add(pcd)
                        session.commit()
                        session.flush()
                        session.refresh(pcd)
                        print(f"{Back.green}{'*'*10}{Style.reset}\n{pcd}\n{Back.green}{'*'*10}{Style.reset}")

                    else:
                        print(f"{Back.red}{'*'*10}{Style.reset}\n{result}\n{Back.red}{'*'*10}{Style.reset}")
                print(Style.reset)
            except Exception as e:
                print(e)

    def collect_barcode_w_nu_code(self):
        while True:
            try:
                print(Style.reset)
                def mkText(text,self):
                    if text in ['',]:
                        return None
                    else:
                        return text
                fieldnameH='1bnuc'
                modeH='Collect'
                h=f'{Prompt.header.format(Fore=Fore,mode=modeH,fieldname=fieldnameH,Style=Style)}'
                barcode=Prompt.__init2__(None,func=mkText,ptext=f"{h}Barcode to Store in PairCollections[h|help]",helpText=self.help2(),data=self)
                if barcode in [None,]:
                    return
                
                code=Prompt.__init2__(None,func=mkText,ptext=f"{h}Shelf Tag Code/ItemCode/Code/CIC[h|help]",helpText=self.help2(),data=self)
                if code in [None,]:
                    return
               
                with Session(self.engine) as session:
                    query=session.query(PairCollection).filter(PairCollection.Barcode==barcode)
                    result=query.first()
                    if not result:
                        pcd=PairCollection(Barcode=barcode,Code=code,Name=f"New Item Created From Scan @ {datetime.now().ctime()}")
                        session.add(pcd)
                        session.commit()
                        session.flush()
                        session.refresh(pcd)
                        print(f"{Back.green}{'*'*10}{Style.reset}\n{pcd}\n{Back.green}{'*'*10}{Style.reset}")

                    else:
                        print(f"{Back.red}{'*'*10}{Style.reset}\n{result}\n{Back.red}{'*'*10}{Style.reset}")
                print(Style.reset)
            except Exception as e:
                print(e)

    def collect_barcode_w_nu_code_plus(self):
        while True:
            try:
                print(Style.reset)
                def mkText(text,self):
                    if text in ['',]:
                        return None
                    else:
                        return text
                fieldnameH='1bnuc+'
                modeH='Collect'
                h=f'{Prompt.header.format(Fore=Fore,mode=modeH,fieldname=fieldnameH,Style=Style)}'
                barcode=Prompt.__init2__(None,func=mkText,ptext=f"{h}Barcode to Store in PairCollections[h|help]",helpText=self.help2(),data=self)
                if barcode in [None,]:
                    return
                
                code=Prompt.__init2__(None,func=mkText,ptext=f"{h}Shelf Tag Code/ItemCode/Code/CIC[h|help]",helpText=self.help2(),data=self)
                if code in [None,]:
                    return

                t=self.checkEntryForBarcode(barcode=barcode)
                if t:
                    continue
               
                with Session(self.engine) as session:
                    query=session.query(PairCollection).filter(PairCollection.Barcode==barcode)
                    result=query.first()
                    if not result:
                        pcd=PairCollection(Barcode=barcode,Code=code,Name=f"New Item Created From Scan @ {datetime.now().ctime()}")
                        session.add(pcd)
                        session.commit()
                        session.flush()
                        session.refresh(pcd)
                        print(f"{Back.green}{'*'*10}{Style.reset}\n{pcd}\n{Back.green}{'*'*10}{Style.reset}")

                    else:
                        print(f"{Back.red}{'*'*10}{Style.reset}\n{result}\n{Back.red}{'*'*10}{Style.reset}")
                print(Style.reset)
            except Exception as e:
                print(e)

    def collect_barcode_code_name(self):
        while True:
            try:
                print(Style.reset)
                def mkText(text,self):
                    if text in ['',]:
                        return None
                    else:
                        return text
                fieldnameH='1bcn'
                modeH='Collect'
                h=f'{Prompt.header.format(Fore=Fore,mode=modeH,fieldname=fieldnameH,Style=Style)}'
                barcode=Prompt.__init2__(None,func=mkText,ptext=f"{h}Barcode to Store in PairCollections[h|help]",helpText=self.help2(),data=self)
                if barcode in [None,]:
                    return
                
                code=Prompt.__init2__(None,func=mkText,ptext=f"{h}Shelf Tag Code/ItemCode/Code/CIC[h|help]",helpText=self.help2(),data=self)
                if code in [None,]:
                    return

                name=Prompt.__init2__(None,func=mkText,ptext=f"{h}Product Name[h|help]",helpText="Name of Product",data=self)
                if name in [None,]:
                    return
                               
                with Session(self.engine) as session:
                    query=session.query(PairCollection).filter(PairCollection.Barcode==barcode)
                    result=query.first()
                    if not result:
                        pcd=PairCollection(Barcode=barcode,Code=code,Name=name)
                        session.add(pcd)
                        session.commit()
                        session.flush()
                        session.refresh(pcd)
                        print(f"{Back.green}{'*'*10}{Style.reset}\n{pcd}\n{Back.green}{'*'*10}{Style.reset}")

                    else:
                        print(f"{Back.red}{'*'*10}{Style.reset}\n{result}\n{Back.red}{'*'*10}{Style.reset}")
                print(Style.reset)
            except Exception as e:
                print(e)
    def collect_barcode_code_name_plus(self):
        while True:
            try:
                print(Style.reset)
                def mkText(text,self):
                    if text in ['',]:
                        return None
                    else:
                        return text
                fieldnameH='1bcn+'
                modeH='Collect'
                h=f'{Prompt.header.format(Fore=Fore,mode=modeH,fieldname=fieldnameH,Style=Style)}'
                barcode=Prompt.__init2__(None,func=mkText,ptext=f"{h}Barcode to Store in PairCollections[h|help]",helpText=self.help2(),data=self)
                if barcode in [None,]:
                    return
                #because you have to move slow using this one, the check here will allow you to speed past unnecessary entries
                t=self.checkEntryForBarcode(barcode=barcode)
                if t:
                    continue

                code=Prompt.__init2__(None,func=mkText,ptext=f"{h}Shelf Tag Code/ItemCode/Code/CIC[h|help]",helpText=self.help2(),data=self)
                if code in [None,]:
                    return

                name=Prompt.__init2__(None,func=mkText,ptext=f"{h}Product Name[h|help]",helpText="Name of Product",data=self)
                if name in [None,]:
                    return
               
                with Session(self.engine) as session:
                    query=session.query(PairCollection).filter(PairCollection.Barcode==barcode)
                    result=query.first()
                    if not result:
                        pcd=PairCollection(Barcode=barcode,Code=code,Name=name)
                        session.add(pcd)
                        session.commit()
                        session.flush()
                        session.refresh(pcd)
                        print(f"{Back.green}{'*'*10}{Style.reset}\n{pcd}\n{Back.green}{'*'*10}{Style.reset}")

                    else:
                        print(f"{Back.red}{'*'*10}{Style.reset}\n{result}\n{Back.red}{'*'*10}{Style.reset}")
                print(Style.reset)
            except Exception as e:
                print(e)


    def BarNameCollector(self):
            while True:
                try:
                    fieldnameH='1bn'
                    modeH='Collect'
                    h=f'{Prompt.header.format(Fore=Fore,mode=modeH,fieldname=fieldnameH,Style=Style)}'
                    print(Style.reset)
                    def mkT(text,self):
                        return text
                    barcode=Prompt.__init2__(None,func=mkT,ptext=f"{h}Barcode",helpText="Barcode to Store in PairCollections",data=self)
                    if barcode == None:
                        return


                    def mkT(text,self):
                        return text
                    name=Prompt.__init2__(None,func=mkT,ptext=f"{h}{Style.bold}{Fore.dark_goldenrod}Product Name:",helpText="Name of Product",data=self)
                    if name == None:
                        return
                   
                    with Session(self.engine) as session:
                        query=session.query(PairCollection).filter(PairCollection.Barcode==barcode)
                        result=query.first()
                        if not result:
                            pcd=PairCollection(Barcode=barcode,Code="No_CODE",Name=name)
                            session.add(pcd)
                            session.commit()
                            session.flush()
                            session.refresh(pcd)
                            print(f"{Back.green}{'*'*10}{Style.reset}\n{pcd}\n{Back.green}{'*'*10}{Style.reset}")

                        else:
                            print(f"{Back.red}{'*'*10}{Style.reset}\n{result}\n{Back.red}{'*'*10}{Style.reset}")
                    print(Style.reset)
                except Exception as e:
                    print(e)
    def BarNameCollector_plus(self):
            while True:
                try:
                    fieldnameH='1bn+'
                    modeH='Collect'
                    h=f'{Prompt.header.format(Fore=Fore,mode=modeH,fieldname=fieldnameH,Style=Style)}'
                    print(Style.reset)
                    def mkT(text,self):
                        return text
                    barcode=Prompt.__init2__(None,func=mkT,ptext=f"{h}Barcode",helpText="Barcode to Store in PairCollections",data=self)
                    if barcode == None:
                        return

                    t=self.checkEntryForBarcode(barcode=barcode)
                    if t:
                        continue

                    def mkT(text,self):
                        return text
                    name=Prompt.__init2__(None,func=mkT,ptext=f"{h}{Style.bold}{Fore.dark_goldenrod}Product Name:",helpText="Name of Product",data=self)
                    if name == None:
                        return
                   
                    with Session(self.engine) as session:
                        query=session.query(PairCollection).filter(PairCollection.Barcode==barcode)
                        result=query.first()
                        if not result:
                            pcd=PairCollection(Barcode=barcode,Code="No_CODE",Name=name)
                            session.add(pcd)
                            session.commit()
                            session.flush()
                            session.refresh(pcd)
                            print(f"{Back.green}{'*'*10}{Style.reset}\n{pcd}\n{Back.green}{'*'*10}{Style.reset}")

                        else:
                            print(f"{Back.red}{'*'*10}{Style.reset}\n{result}\n{Back.red}{'*'*10}{Style.reset}")
                    print(Style.reset)
                except Exception as e:
                    print(e)