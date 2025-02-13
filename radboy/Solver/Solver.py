from .__init__ import *
class SolverFormulasStore(BASE,Template):
    __tablename__="SolverFormulasStore"
    SFSiD=Column(Integer,primary_key=True)
    Script=Column(LargeBinary,default=b'')
    Description=Column(String,default="Tell Me What this Script DOES")
    Notes=Column(String,default="Addition Notes About this Script")
    DTOE=Column(DateTime,default=datetime.now())
    LastUsed=Column(DateTime,default=None)
    HTEXT=Column(String,default="Tell Me How to use this in the KISS principle (KEEP IT SIMPLE, STUPID[Don't be Bitch about either, yall treated me like I was a Crazy-Ass Mother-Fucker, now its your turn to eat God-Damned Shit Fresh of the Plate of I Fucking Told you so, asshole, and you know why that is? Because...])")

    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))

SolverFormulasStore.metadata.create_all(ENGINE)

class solverUi:
    def searchAndRun(self):
        with Session(ENGINE) as session:
            search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What script are you looking for?",helpText="search for the cmd to execute, use a % to symbolize anything so 'gross%income' would match 'gross income' and 'gross1income'",data="string")
            if search in [None,'d']:
                print("Nothing was selected!")
                return
            scripts=session.query(SolverFormulasStore).filter(or_(SolverFormulasStore.Notes.icontains(search),SolverFormulasStore.Description.icontains(search),SolverFormulasStore.HTEXT.icontains(search))).group_by(SolverFormulasStore.Script).order_by(SolverFormulasStore.LastUsed).all()
            ct=len(scripts)
            if ct == 0:
                print("No Scripts available to use!")
                return
            else:
                for num,i in enumerate(scripts):
                    color_desc=f"{Fore.light_red}"
                    color_note=f"{Fore.light_yellow}"
                    color_htext=f"{Fore.grey_50}"
                    if (num%2) == 0:
                        color_desc=f"{Fore.light_green}"
                        color_note=f"{Fore.cyan}"
                        color_htext=f"{Fore.grey_70}" 
                    msg=f'{Fore.light_magenta}{num}/{Fore.green_yellow}{num+1} of {Fore.orange_red_1}{ct} | {color_desc}{i.Description} | {color_htext}{i.HTEXT}{color_note}{i.Notes}{Style.reset}'
                    print(msg)
                which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="index(es) to remove",helpText="remove which indexes?",data="list")
                if which in [None,'d']:
                    return
                for i in which:
                    try:
                        exec(scripts[int(i)].Script)
                        scripts[int(i)].LastUsed=datetime.now()
                        session.commit()
                    except Exception as e:
                        print(e)

    def reviewStorage(self):
        with Session(ENGINE) as session:
            scripts=session.query(SolverFormulasStore).group_by(SolverFormulasStore.Script).order_by(SolverFormulasStore.LastUsed).all()
            ct=len(scripts)
            if ct == 0:
                print("No Scripts available to use!")
                return
            else:
                for num,i in enumerate(scripts):
                    color_desc=f"{Fore.light_red}"
                    color_note=f"{Fore.light_yellow}"
                    color_htext=f"{Fore.grey_50}"
                    if (num%2) == 0:
                        color_desc=f"{Fore.light_green}"
                        color_note=f"{Fore.cyan}"
                        color_htext=f"{Fore.grey_70}" 
                    msg=f'{Fore.light_magenta}{num}/{Fore.green_yellow}{num+1} of {Fore.orange_red_1}{ct} | {color_desc}{i.Description} | {color_htext}{i.HTEXT}{color_note}{i.Notes}{Style.reset}'
                    print(msg)
                which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="index(es) to remove",helpText="remove which indexes?",data="list")
                if which in [None,'d']:
                    return
                for ii in which:
                    try:
                        ii=int(ii)
                        msg=f'''
{Fore.light_steel_blue}{scripts[ii].Description} - {Fore.light_magenta}{scripts[ii].HTEXT} - {Fore.orange_red_1}{scripts[ii].Notes} | {Fore.light_red}BOF |{Style.reset}
{Style.bold}{Fore.spring_green_3b}#SCRIPT#{Style.reset}
{Fore.light_steel_blue}{scripts[ii].Description} - {Fore.light_magenta}{scripts[ii].HTEXT} - {Fore.orange_red_1}{scripts[ii].Notes} | {Fore.light_red}EOF |{Style.reset}
                        '''.encode()
                        msg=msg.replace(b'#SCRIPT#',scripts[ii].Script)
                        try:
                            print(msg.decode("ascii"))
                        except Exception as e:
                            print(e)
                            print(msg)
                    except Exception as e:
                        print(e)

    def saveStorage(self):
        with Session(ENGINE) as session:
            scripts=session.query(SolverFormulasStore).group_by(SolverFormulasStore.Script).order_by(SolverFormulasStore.LastUsed).all()
            ct=len(scripts)
            if ct == 0:
                print("No Scripts available to use!")
                return
            else:
                for num,i in enumerate(scripts):
                    color_desc=f"{Fore.light_red}"
                    color_note=f"{Fore.light_yellow}"
                    color_htext=f"{Fore.grey_50}"
                    if (num%2) == 0:
                        color_desc=f"{Fore.light_green}"
                        color_note=f"{Fore.cyan}"
                        color_htext=f"{Fore.grey_70}" 
                    msg=f'{Fore.light_magenta}{num}/{Fore.green_yellow}{num+1} of {Fore.orange_red_1}{ct} | {color_desc}{i.Description} | {color_htext}{i.HTEXT}{color_note}{i.Notes}{Style.reset}'
                    print(msg)
                which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="index(es) to remove",helpText="remove which indexes?",data="list")
                if which in [None,'d']:
                    return
                for ii in which:
                    try:
                        ii=int(ii)
                        msg=f'''
{Fore.light_steel_blue}{scripts[ii].Description} - {Fore.light_magenta}{scripts[ii].HTEXT} - {Fore.orange_red_1}{scripts[ii].Notes} | {Fore.light_red}BOF |{Style.reset}
{Style.bold}{Fore.spring_green_3b}#SCRIPT#{Style.reset}
{Fore.light_steel_blue}{scripts[ii].Description} - {Fore.light_magenta}{scripts[ii].HTEXT} - {Fore.orange_red_1}{scripts[ii].Notes} | {Fore.light_red}EOF |{Style.reset}
                        '''.encode()
                        msg=msg.replace(b'#SCRIPT#',scripts[ii].Script)
                        name=scripts[ii].Description
                        for char in string.whitespace:
                            name=name.replace(char,"_")
                        name=name.replace("*","_asterisk_")
                        name=name.replace("%","_percent_")
                        name=name.replace("#","_pound_")
                        name=name.replace(":","_colon_")
                        name=name.replace("?","_question_mark_")
                        name=name.replace("{","_Left_curly_bracket_")
                        name=name.replace("&","_Right_curly_bracket_")
                        name=name.replace("\\","_backslash_")
                        name=name.replace("/","_forwardslash_")
                        name=name.replace("<","_Left_angle_bracket_")
                        name=name.replace(">","_Right_angle_bracket_")

                        name=name+".py"
                        with open(name,"wb") as out:
                            htext=scripts[ii].HTEXT.split("\n")
                            htext=[ f'#HTEXT| {i}' for i in htext]
                            htext='\n'.join(htext)+"\n"
                            out.write(htext.encode())

                            Notes=scripts[ii].Notes.split("\n")
                            Notes=[ f'#Notes| {i}' for i in Notes]
                            Notes='\n'.join(Notes)+"\n"
                            out.write(Notes.encode())

                            out.write(scripts[ii].Script)

                        try:
                            print(msg.decode("ascii"))
                        except Exception as e:
                            print(e)
                            print(msg)
                        print(f"{Fore.orange_red_1}Saved to {Fore.light_red}{Path(name)}{Style.reset}")
                    except Exception as e:
                        print(e)

    def runId(self):
        with Session(ENGINE) as session:
            scripts=session.query(SolverFormulasStore).group_by(SolverFormulasStore.Script).order_by(SolverFormulasStore.LastUsed).all()
            ct=len(scripts)
            if ct == 0:
                print("No Scripts available to use!")
                return
            else:
                for num,i in enumerate(scripts):
                    color_desc=f"{Fore.light_red}"
                    color_note=f"{Fore.light_yellow}"
                    color_htext=f"{Fore.grey_50}"
                    if (num%2) == 0:
                        color_desc=f"{Fore.light_green}"
                        color_note=f"{Fore.cyan}"
                        color_htext=f"{Fore.grey_70}" 
                    msg=f'{Fore.light_magenta}{num}/{Fore.green_yellow}{num+1} of {Fore.orange_red_1}{ct} | {color_desc}{i.Description} | {color_htext}{i.HTEXT}{color_note}{i.Notes}{Style.reset}'
                    print(msg)
                which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="index(es) to remove",helpText="remove which indexes?",data="list")
                if which in [None,'d']:
                    return
                for i in which:
                    try:
                        exec(scripts[int(i)].Script)
                        scripts[int(i)].LastUsed=datetime.now()
                        session.commit()
                    except Exception as e:
                        print(e)

    def rmId(self):
       with Session(ENGINE) as session:
            scripts=session.query(SolverFormulasStore).group_by(SolverFormulasStore.Script).order_by(SolverFormulasStore.LastUsed).all()
            ct=len(scripts)
            if ct == 0:
                print("No Scripts available to use!")
                return
            else:
                for num,i in enumerate(scripts):
                    color_desc=f"{Fore.light_red}"
                    color_note=f"{Fore.light_yellow}"
                    color_htext=f"{Fore.grey_50}"
                    if (num%2) == 0:
                        color_desc=f"{Fore.light_green}"
                        color_note=f"{Fore.cyan}"
                        color_htext=f"{Fore.grey_70}" 
                    msg=f'{Fore.light_magenta}{num}/{Fore.green_yellow}{num+1} of {Fore.orange_red_1}{ct} | {color_desc}{i.Description} | {color_htext}{i.HTEXT}{color_note}{i.Notes}{Style.reset}'
                    print(msg)
                which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="index(es) to remove",helpText="remove which indexes?",data="list")
                if which in [None,'d']:
                    return
                for i in which:
                    try:
                        session.delete(scripts[int(i)])
                        session.commit()
                    except Exception as e:
                        print(e)

    def showStore(self):
        with Session(ENGINE) as session:
            scripts=session.query(SolverFormulasStore).group_by(SolverFormulasStore.Script).order_by(SolverFormulasStore.LastUsed).all()
            ct=len(scripts)
            if ct == 0:
                print("No Scripts available to use!")
                return
            else:
                for num,i in enumerate(scripts):
                    color_desc=f"{Fore.light_red}"
                    color_note=f"{Fore.light_yellow}"
                    color_htext=f"{Fore.grey_50}"
                    if (num%2) == 0:
                        color_desc=f"{Fore.light_green}"
                        color_note=f"{Fore.cyan}"
                        color_htext=f"{Fore.grey_70}" 
                    msg=f'{Fore.light_magenta}{num}/{Fore.green_yellow}{num+1} of {Fore.orange_red_1}{ct} | {color_desc}{i.Description} | {color_htext}{i.HTEXT}{color_note}{i.Notes}{Style.reset}'
                    print(msg)

    def test_file_no_save(self,save=False):
        script=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Filename or FilePath/Filename?",helpText="A filename",data="Path")
        print(script)
        if script in [None,'d']:
            return
        else:
            buffer=b''
            if script.exists():
                print(script,script.exists())
                with script.open("rb") as sc:
                    while True:
                        d=sc.read(1024)
                        if not d:
                            break
                        buffer+=d
                try:
                    exec(buffer)
                    if save:
                        with Session(ENGINE) as session:
                            check=session.query(SolverFormulasStore).filter(SolverFormulasStore.Script==buffer).first()
                            if not check:
                                helpText=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f" {script} | helpText: ",helpText="helpful info",data="String")
                                if helpText in [None]:
                                    return
                                elif helpText in ['d',]:
                                    helpText=''

                                description=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f" {script} | description: ",helpText="helpful info",data="String")
                                if description in [None]:
                                    return
                                elif description in ['d',]:
                                    description=''

                                Notes=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f" {script} | Notes: ",helpText="helpful info",data="String")
                                if Notes in [None]:
                                    return
                                elif Notes in ['d',]:
                                    Notes=''

                                store=SolverFormulasStore(Script=buffer,Description=description,Notes=Notes,HTEXT=helpText,LastUsed=datetime.now())

                                session.add(store)
                                session.commit()
                                session.refresh(store)
                                print(store)
                            else:
                                print(check)


                except Exception as e:
                    print(e)

    def showGlobals(self):
        script='''
glbls=globals()
for i in glbls:
    try:
        print(f"{Fore.light_red}{i}{Fore.cyan}{type(glbls.get(i))}{Fore.light_yellow}{glbls.get(i)}{Style.reset}")
    except Exception as e:
        print(f"{Fore.light_red}{i}{Fore.cyan}{type(glbls.get(i))}{Fore.light_yellow}{e}{Fore.green_yellow}{repr(e)}{str(e)}{Style.reset}")
        '''
        exec(script)

    def __init__(self):
        cmds={
        'test file':{
            'cmds':['test file','run as is','run only','tfo','tf'],
            'desc':"test a file written, but dont save it to store",
            'exec':self.test_file_no_save
            },
            'run file':{
            'cmds':['run and save','ras'],
            'desc':"test a file written, and if successful save to store",
            'exec':lambda self=self:self.test_file_no_save(save=True)
            },
            'show store':{
            'cmds':['show store','show all','sa',],
            'desc':"show stored script contents",
            'exec':lambda self=self:self.showStore()
            },
            'rmid':{
            'cmds':['rm from all','rmfa',],
            'desc':"show stored script contents",
            'exec':lambda self=self:self.rmId()
            },
            'runid':{
            'cmds':['run from all','runfa',],
            'desc':"show stored script contents",
            'exec':lambda self=self:self.runId()
            },
            'srunid':{
            'cmds':['search and run','srun','run'],
            'desc':"show stored script contents",
            'exec':lambda self=self:self.searchAndRun()
            },
            'show globals':{
            'cmds':['show globals','shoglbl',],
            'desc':"show globals that can be used within exec() script",
            'exec':lambda self=self:self.showGlobals()
            },
            'review store':{
            'cmds':['review store','rs','view code','vc'],
            'desc':"select and view code in storage",
            'exec':lambda self=self:self.reviewStorage()
            },
            'save store':{
            'cmds':['save store','ss','save code','sc'],
            'desc':"select and view code in storage",
            'exec':lambda self=self:self.saveStorage()
            }
        }
        helpText=[]
        for i in cmds:
            helpText.append(f"{','.join(cmds[i]['cmds'])} - {cmds[i]['desc']}")
        helpText='\n'.join(helpText)
        while True:
            cmd=Prompt.__init2__(None,func=FormBuilderMkText,ptext="[solver Root] Do what",helpText=helpText,data="string")
            if cmd in [None,]:
                return
            elif cmd.lower() in ['d',]:
                print(helpText)
            else:
                for k in cmds:
                    if cmd.lower() in [i.lower() for i in cmds[k]['cmds']]:
                        cmds[k]['exec']()