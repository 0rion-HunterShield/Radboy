from . import *

class StopWatch(BASE,Template):
    __tablename__='StopWatch'
    swid=Column(Integer,primary_key=True)
    start=Column(DateTime)
    end=Column(DateTime)
    lap=Column(String,default='[]')
    default=Column(Boolean,default=False)
    name=Column(String,default='name')
    
    def __init__(self,**kwargs):
        for k in kwargs:
            fields=[str(i.name) for i in self.__table__.columns]
            if k in fields:
                setattr(self,k,kwargs[k])
try:                
 StopWatch.metadata.create_all(ENGINE)
except Exception as e:
    print(e)

class StopWatchUi:
    def sw_help(self,print_only=True):
        msg=f''''''
        for i in self.options:
            msg+=f"\n{self.options[i]['cmds']} - {self.options[i]['desc']}"
        if not print_only:
            return msg
        print(msg)

    def title(self):
        try:
            with Session(ENGINE) as session:
                check=session.query(StopWatch).filter(StopWatch.swid==1).first()
                name=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Name/Desc",helpText="desscribe the duration",data="string")
                if name in [None,]:
                    return
                elif name in ['d',]:
                    name=''
                if not check:
                    sw=StopWatch(start=None,end=None,default=True,name=name,swid=1)
                    session.add(sw)
                    session.commit()
                    session.refresh(sw)
                    print(sw)
                else:
                    check.name=name
                    session.commit()
                    session.refresh(check)
                    print(check)
        except Exception as e:
            print(e)

    def s1(self):
        try:
            with Session(ENGINE) as session:
                check=session.query(StopWatch).filter(StopWatch.swid==1).first()
               
                if not check:
                    name=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Name/Desc",helpText="desscribe the duration",data="string")
                    if name in [None,]:
                        return
                    elif name in ['d',]:
                        name=''
                    sw=StopWatch(start=datetime.now(),end=None,default=True,name=name,swid=1)
                    session.add(sw)
                    session.commit()
                    session.refresh(sw)
                    print(sw)
                else:
                    check.start=datetime.now()
                    session.commit()
                    session.refresh(check)
                    print(check)
        except Exception as e:
            print(e)

    def l1(self):
        try:
            with Session(ENGINE) as session:
                check=session.query(StopWatch).filter(StopWatch.swid==1).first()
                if not check:
                    name=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Name/Desc",helpText="desscribe the duration",data="string")
                    if name in [None,]:
                        return
                    elif name in ['d',]:
                        name=''
                    sw=StopWatch(start=datetime.now(),end=None,default=True,name=name,swid=1)
                    session.add(sw)
                    session.commit()
                    session.refresh(sw)
                    sw.lap=json.loads(sw.lap)
                    sw.lap.append(string(datetime.now()-sw.start))
                    sw.lap=json.dumps(sw.lap)
                    print(sw)
                else:
                    if check.start == None:
                        check.start=datetime.now()
                        session.commit()
                        session.refresh(check)
                    try:
                        check.lap=json.loads(check.lap)
                    except Exception as e:
                        check.lap=json.loads('[]')
                    check.lap.append(str(datetime.now()-check.start))
                    check.lap=json.dumps(check.lap)
                    session.commit()
                    session.refresh(check)
                    print(check)
        except Exception as e:
            print(e)

    def e1(self):
        try:
            with Session(ENGINE) as session:
                check=session.query(StopWatch).filter(StopWatch.swid==1).first()
                if not check:
                    name=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Name/Desc",helpText="desscribe the duration",data="string")
                    if name in [None,]:
                        return
                    elif name in ['d',]:
                        name=''
                    sw=StopWatch(start=datetime.now(),end=datetime.now(),default=True,name=name,swid=1)
                    session.add(sw)
                    session.commit()
                    session.refresh(sw)
                    print(sw)
                else:
                    check.end=datetime.now()
                    session.commit()
                    session.refresh(check)
                    print(check)
                    print(check.end-check.start)
        except Exception as e:
            print(e)

    def v1(self):
        try:
            with Session(ENGINE) as session:
                check=session.query(StopWatch).filter(StopWatch.swid==1).first()
                if not check:
                    name=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Name/Desc",helpText="desscribe the duration",data="string")
                    if name in [None,]:
                        return
                    elif name in ['d',]:
                        name=''
                    sw=StopWatch(start=datetime.now(),end=datetime.now(),default=True,name=name,swid=1)
                    session.add(sw)
                    session.commit()
                    session.refresh(sw)
                    print(sw)
                else:
                    print(check)
                    if not check.end:
                        print(datetime.now()-check.start)
                    else:
                        print(check.end-check.start)
        except Exception as e:
            print(e)

    def c1(self):
        try:
            with Session(ENGINE) as session:
                check=session.query(StopWatch).filter(StopWatch.swid==1).first()
                if not check:
                    sw=StopWatch(start=None,end=None,default=None,name=None,swid=1)
                    session.add(sw)
                    session.commit()
                    session.refresh(sw)
                    print(sw)
                else:
                    for i in StopWatch.__table__.columns:
                        if i.name not in ['default','swid']:
                            setattr(check,i.name,None)
                        else:
                            if i == 'default':
                                setattr(check,'default',False)
                    session.commit()
                    session.refresh(check)
                    print(check)
        except Exception as e:
            print(e)

    def __init__(self):
        self.options={
            'help':{
                'cmds':['stopwatch help','sw help'],
                'exec':self.sw_help,
                'desc':"helpful info for this tool"
                },
            'title':{
                'cmds':['title_1','t_1','name_1'],
                'exec':self.title,
                'desc':'describe this run for swid==1',
            },
            's1':{
                'cmds':['start 1','s_1','s1','start_1'],
                'exec':self.s1,
                'desc':'start this run for swid==1',
            },
            'l1':{
                'cmds':['lap 1','l_1','l1','lap_1'],
                'exec':self.l1,
                'desc':'add a lap for this run for swid==1',
            },
            'e1':{
                'cmds':['end 1','e_1','e1','end_1'],
                'exec':self.e1,
                'desc':'end this run for swid==1',
            },
            'v1':{
                'cmds':['view 1','v_1','v1','view_1'],
                'exec':self.v1,
                'desc':'see duration for swid==1',
            },
            'c1':{
                'cmds':['clear 1','c_1','c1','clear_1'],
                'exec':self.c1,
                'desc':'clear swid==1',
            },
            }
        while True:
            command=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f'{Fore.grey_70}[{Fore.light_steel_blue}StopWatchUi{Fore.grey_70}] {Fore.light_yellow}Menu[help/??/?]',helpText=self.sw_help(print_only=False),data="string")
            print(command)
            if command in [None,]:
                break
            elif command in ['','d']:
                self.sw_help(print_only=True)
            for option in self.options:
                if self.options[option]['exec'] != None and (command.lower() in self.options[option]['cmds'] or command in self.options[option]['cmds']):
                    self.options[option]['exec']()
                elif self.options[option]['exec'] == None and (command.lower() in self.options[option]['cmds'] or command in self.options[option]['cmds']):
                    return

    #t - title/name of run
    #s - punch start (datetime)
    #l - lap (json list of lap datetime's)
    #e - punch end (datetime)