import boozelib
from . import *

class AlcoholConsumptionRecords(BASE,Template):
    __tablename__='AlcoholConsumptionRecords'
    acr_id=Column(Integer,primary_key=True)
    bac=Column(Float,default=0)
    #for data related to tester used to get bac
    tester_id=Column(Integer)
    drinks_consumed=Column(Integer)
    volume_consumed_ml=Column(Float)
    average_abv=Column(Float)
    notes=Column(String,default='')
    #seconds until sober provided by tester
    time_until_sober_by_tester=Column(Float)
    #seconds from dob
    dtob=Column(DateTime)
    weight_kg=Column(Float)
    height_cm=Column(Float)
    dtoe=Column(DateTime)
    when_did_you_start_drinking=Column(DateTime)
    
    def __init__(self,**kwargs):
        self.doe=datetime.now()
        for k in kwargs:
            fields=[str(i.name) for i in self.__table__.columns]
            if k in fields:
                setattr(self,k,kwargs[k])
                
class BACTester(BASE,Template):
    __tablename__='BACTester'
    tester_id=Column(Integer,primary_key=True)
    name=Column(String)
    doe=Column(DateTime)
    accuracy=Column(Float)
    brand=Column(String)
    serial_no=Column(String)
    sensor_type=Column(String)
    source=Column(String,default='where was this bought')
    weight_grams=Column(Float)
    power_source=Column(String)
    notes=Column(String)
    instructions=Column(Text)
    
    def __init__(self,**kwargs):
        self.doe=datetime.now()
        for k in kwargs:
            fields=[str(i.name) for i in self.__table__.columns]
            if k in fields:
                setattr(self,k,kwargs[k])   

BACTester.metadata.create_all(ENGINE)
AlcoholConsumptionRecords.metadata.create_all(ENGINE)

class AlcoholConsumption:
    def EditTester(self):
        while True:
            search=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"ACC/{Fore.light_steel_blue}Edit/New Tester{Fore.orange_red_1}Anything in a Text Field",helpText="what are you looking for?",data="string")
            if search in [None,]:
                if self.next_barcode():
                    continue
                else:
                    return
            selected=[]
            with Session(ENGINE) as session:
                q=[getattr(BACTester,i.name).icontains(search) for i in BACTester.__table__.columns if str(i.type).lower() in ["string","varchar","text"]]
                if search.lower() in ['all','*']:
                    results=session.query(BACTester).all()
                else:
                    results=session.query(BACTester).filter(or_(*q)).all()
                ct=len(results)
                if ct > 0:
                    htext=[]
                    for num,i in enumerate(results):
                        msg=f'''{num}/{num+1} of {ct} - {i}'''
                        htext.append(msg)
                    htext='\n'.join(htext)
                    print(htext)
                    editWhich=Prompt.__init2__(None,func=FormBuilderMkText,ptext="(Enter Creates New) Edit which indexes?",helpText=f"{htext}\ncomma separated list of indexes",data="list")
                    if editWhich in [None,]:
                        return
                    elif editWhich in ['d',]:
                        new=BACTester()
                        selected.append(new)
                    else:
                        try:
                            for i in editWhich:
                                try:
                                    index=int(i)
                                    selected.append(results[index])
                                except Exception as ee:
                                    print(ee)
                        except Exception as e:
                            print(e)
                else:
                    new=BACTester()
                    session.add(new)
                    session.commit()
                    session.refresh(new)
                    selected.append(new)
                ctSelected=len(selected)
                for num,select in enumerate(selected):
                    msg=f'BACTester {num}/{num+1} of {ctSelected} - {select}'
                    print(msg)
                    del_skip=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Del<rm>/Skip<s>/Continue<Enter>",helpText="Del<rm>/Skip<s>/Continue<Enter>",data="string")
                    if del_skip in [None,]:
                        if self.next_barcode():
                            continue
                        else:
                            return
                    elif del_skip.lower() in ['s','skip']:
                        continue
                    elif del_skip.lower() in ['rm','delete','del']:
                        session.delete(select)
                        session.commit()
                        continue
                    else:
                        pass

                    entry_default=select
                    data={str(i.name):{'type':str(i.type),'default':getattr(entry_default,str(i.name))} for i in BACTester.__table__.columns} 
                    fd=FormBuilder(data=data)
                    if fd in [None,]:
                        if self.next_barcode():
                            continue
                        else:
                            return
                    for i in fd:
                        setattr(select,i,fd.get(i))
                        session.commit()
                    session.commit()
                    session.refresh(select)
                    msg=f'BACTester {num}/{num+1} of {ctSelected} - {select}'
                    print(msg)

    def listTester(self):
        while True:
            search=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"ACC/{Fore.light_steel_blue} List Tester{Fore.orange_red_1}Anything in a Text Field",helpText="what are you looking for?",data="string")
            if search in [None,]:
                if self.next_barcode():
                    continue
                else:
                    return
            selected=[]
            with Session(ENGINE) as session:
                q=[getattr(BACTester,i.name).icontains(search) for i in BACTester.__table__.columns if str(i.type).lower() in ["string","varchar","text"]]
                if search.lower() in ['all','*']:
                    results=session.query(BACTester).all()
                else:
                    results=session.query(BACTester).filter(or_(*q)).all()
                ct=len(results)
                if ct == 0:
                    print("Nothing to display!")
                    return
                for num, i in enumerate(results):
                    msg=f'''{num}/{num+1} of {ct} -{i}'''
                    print(msg)

    def listACR(self):
        while True:
            search=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"ACC/{Fore.light_steel_blue}List ACR{Fore.orange_red_1} Anything in a Text Field",helpText="what are you looking for?",data="string")
            if search in [None,]:
                if self.next_barcode():
                    continue
                else:
                    return
            selected=[]
            with Session(ENGINE) as session:
                q=[getattr(AlcoholConsumptionRecords,i.name).icontains(search) for i in AlcoholConsumptionRecords.__table__.columns if str(i.type).lower() in ["string","varchar","text"]]
                if search.lower() in ['all','*']:
                    results=session.query(AlcoholConsumptionRecords).all()
                else:
                    results=session.query(AlcoholConsumptionRecords).filter(or_(*q)).all()
                ct=len(results)
                if ct == 0:
                    print("Nothing to display!")
                    return
                for num, i in enumerate(results):
                    msg=f'''{num}/{num+1} of {ct} -{i}'''
                    print(msg)

    def EditACR(self):
        with Session(ENGINE) as session:
            while True:
                search=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"ACC/{Fore.light_steel_blue}Edit/New Tester{Fore.orange_red_1}Anything in a Text Field",helpText="what are you looking for?",data="string")
                if search in [None,]:
                    if self.next_barcode():
                        continue
                    else:
                        return
            
            
                selected=[]
                q=[getattr(AlcoholConsumptionRecords,i.name).icontains(search) for i in AlcoholConsumptionRecords.__table__.columns if str(i.type).lower() in ["string","varchar","text"]]
                if search.lower() in ['all','*']:
                    results=session.query(AlcoholConsumptionRecords).all()
                else:
                    results=session.query(AlcoholConsumptionRecords).filter(or_(*q)).all()
                ct=len(results)
                if ct > 0:
                    htext=[]
                    for num,i in enumerate(results):
                        msg=f'''{num}/{num+1} of {ct} - {i}'''
                        htext.append(msg)
                    htext='\n'.join(htext)
                    print(htext)
                    editWhich=Prompt.__init2__(None,func=FormBuilderMkText,ptext="(Enter Creates New) Edit which indexes?",helpText=f"{htext}\ncomma separated list of indexes",data="list")
                    if editWhich in [None,]:
                        return
                    elif editWhich in ['d',]:
                        new=AlcoholConsumptionRecords()
                        session.add(new)
                        session.commit()
                        session.refresh(new)
                        selected.append(new)
                    else:
                        try:
                            for i in editWhich:
                                try:
                                    index=int(i)
                                    selected.append(results[index])
                                except Exception as ee:
                                    print(ee)
                        except Exception as e:
                            print(e)
                else:
                    new=AlcoholConsumptionRecords()
                    session.add(new)
                    session.commit()
                    session.refresh(new)
                    selected.append(new)
                ctSelected=len(selected)
                for num,select in enumerate(selected):
                    msg=f'AlcoholConsumptionRecords {num}/{num+1} of {ctSelected} - {select}'
                    print(msg)
                    del_skip=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Del<rm>/Skip<s>/Continue<Enter>",helpText="Del<rm>/Skip<s>/Continue<Enter>",data="string")
                    if del_skip in [None,]:
                        if self.next_barcode():
                            continue
                        else:
                            return
                    elif del_skip.lower() in ['s','skip']:
                        continue
                    elif del_skip.lower() in ['rm','delete','del']:
                        session.delete(select)
                        session.commit()
                        continue
                    else:
                        pass
                    print(msg)
                    entry_default=session.query(AlcoholConsumptionRecords).filter(AlcoholConsumptionRecords.acr_id==select.acr_id).first()
                    if entry_default:
                        data={str(i.name):{'type':str(i.type),'default':getattr(entry_default,str(i.name))} for i in AlcoholConsumptionRecords.__table__.columns} 
                        fd=FormBuilder(data=data)
                        if fd in [None,]:
                            if self.next_barcode():
                                continue
                            else:
                                return
                        for i in fd:
                            setattr(entry_default,i,fd.get(i))
                            session.commit()
                        session.commit()
                        session.refresh(entry_default)
                        msg=f'AlcoholConsumptionRecords {num}/{num+1} of {ctSelected} - {entry_default}'
                        print(msg)


    def alcohol_consumption_help(self,print_only=True):
        msg=f''''''
        for i in self.options:
            msg+=f"\n{self.options[i]['cmds']} - {self.options[i]['desc']}"
        if not print_only:
            return msg
        print(msg)

    def repair_tester_table(self):
        BACTester.__table__.drop(ENGINE)
        BACTester.metadata.create_all(ENGINE)

    def repair_acr_table(self):
        AlcoholConsumptionRecords.__table__.drop(ENGINE)
        AlcoholConsumptionRecords.metadata.create_all(ENGINE)

    def bac_usa(self):
        weight_pounds=Prompt.__init2__(None,func=FormBuilderMkText,ptext="How much is your weight in pounds?",helpText="pounds",data="float")
        if weight_pounds in [None,'d']:
            return
        height_inches=Prompt.__init2__(None,func=FormBuilderMkText,ptext="How tall are you in inches?",helpText="inches",data="integer")
        if height_inches in [None,'d']:
            return
        cm_ht=pint.UnitRegistry().convert(height_inches,"inches","centimeters")
        kg_wt=pint.UnitRegistry().convert(weight_pounds,"pounds","kilograms")
        #True for female

        sex=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Male[False] or Female[True]",helpText="DONT TYPE MALE or FEMALE, you will be FEMALE. true values are female",data="boolean")
        if sex in [None,]:
            return
        elif sex in ['d',]:
            sex=False
        #mL
        volume=Prompt.__init2__(None,func=FormBuilderMkText,ptext="How Much Volume in mL?",helpText="milliters",data="float")
        if volume in [None,]:
            return
        #% of total valume alcohol
        #percent=(((0.09*568)+(0.095*568))/volume)*100
        percent=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What is the % ABV?",helpText="% abv",data="float")
        if percent in [None,]:
            return
        age=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What is date of birth?",helpText="date",data="datetime")
        if age in ['d',None]:
            return
        age=pint.UnitRegistry().convert((age-datetime.now()).total_seconds(),"seconds","years")
        value=boozelib.get_blood_alcohol_content(age=age,weight=kg_wt,height=cm_ht,sex=sex,volume=volume,percent=percent)
        
        deg=0
        minutes=0
        while deg <= value:
            deg=boozelib.get_blood_alcohol_degradation(age=age,weight=kg_wt,height=cm_ht,sex=sex,minutes=minutes)
            minutes+=1
            print(deg,minutes,value)
        msg=f'''
BAC:{value}
Volume:{volume}
% ABC:{percent}
SEX:{sex}
WEIGHT(KG):{kg_wt}
HEIGHT(CM):{cm_ht}
Time To BAC(0) in Minutes: {timedelta(seconds=minutes*60)}
        '''
        print(msg)

    def next_barcode(self):
        with Session(ENGINE) as session:
            next_barcode=session.query(SystemPreference).filter(SystemPreference.name=="next_barcode").first()
            
            state=False
            
            if next_barcode:
                    try:
                        state=json.loads(next_barcode.value_4_Json2DictString).get("next_barcode")
                    except Exception as e:
                        print(e)
                        next_barcode.value_4_Json2DictString=json.dumps({'next_barcode':False})
                        session.commit()
                        session.refresh(next_barcode)
                        state=json.loads(next_barcode.value_4_Json2DictString).get("next_barcode")
            else:
                next_barcode=db.SystemPreference(name="next_barcode",value_4_Json2DictString=json.dumps({'next_barcode':False}))
                session.add(next_barcode)
                session.commit()
                session.refresh(next_barcode)
                state=json.loads(next_barcode.value_4_Json2DictString).get("next_barcode")
            f=deepcopy(state)
            print(f,"NEXT BARCODE")
            next_barcode.value_4_Json2DictString=json.dumps({'next_barcode':False})
            session.commit()
            return f


    def __init__(self):
        self.options={
            'help':{
                'cmds':['alcohol consumption help','ach'],
                'exec':self.alcohol_consumption_help,
                'desc':"helpful info for this tool"
                },
            'bac usa':{
                'cmds':['bac usa','blood alcohol content estimate usa'],
                'exec':self.bac_usa,
                'desc':'blood alcohol content estimate usa',
            },
            'repair acr':{
                'cmds':['repair_acr_table','r acr t','racrt'],
                'exec':self.repair_acr_table,
                'desc':"drop and create new acr table"
            },
            'repair tester':{
                'cmds':['repair tester table','rtt','r t t','r tt'],
                'exec':self.repair_tester_table,
                'desc':"drop and create new tester table"
            },
            'edit tester':{
                'cmds':['edit tester table','et','nt'],
                'exec':self.EditTester,
                'desc':"create/edit/delete tester"
            },
            'edit acr':{
                'cmds':['edit acr table','eacr',],
                'exec':self.EditACR,
                'desc':"create/edit/delete Alcohol Consumption Records"
            },
            'list acr':{
                'cmds':['list acr table','lacr',],
                'exec':self.listACR,
                'desc':"list Alcohol Consumption Records/search"
            },
            'list tester':{
                'cmds':['list tester table','lt',],
                'exec':self.listTester,
                'desc':"list Tester Data"
            },
            }
        while True:
            command=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f'{Fore.grey_70}[{Fore.light_steel_blue}AlcoholConsumption{Fore.grey_70}] {Fore.light_yellow}Menu[help/??/?]',helpText=self.alcohol_consumption_help(print_only=False),data="string")
            print(command)
            if command in [None,]:
                break
            elif command in ['','d']:
                self.alcohol_consumption_help(print_only=True)
            for option in self.options:
                if self.options[option]['exec'] != None and (command.lower() in self.options[option]['cmds'] or command in self.options[option]['cmds']):
                    self.options[option]['exec']()
                elif self.options[option]['exec'] == None and (command.lower() in self.options[option]['cmds'] or command in self.options[option]['cmds']):
                    return
