import resource,pint,barcode,json,inspect,string,chardet,holidays,sqlalchemy,re,os,sys,random
from colored import Fore,Style,Back
import radboy.DB.db as db
import radboy.DayLog as DL
import radboy.TasksMode as TM
import radboy.Comm as CM
import radboy.TouchStampC as TSC
from radboy.Unified.bareCA import *
from radboy import VERSION
import radboy.possibleCode as pc
from radboy.DB.config import *
from radboy.FB.FBMTXT import *
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base as dbase
from sqlalchemy.ext.automap import automap_base
from pathlib import Path
from datetime import datetime
from collections import namedtuple
from colored import Back,Fore,Style
import platform
from biip.upc import Upc
from datetime import datetime
from datetime import date as DATE
import lzma,base64
from Crypto.Cipher import AES
#from Cryptodome.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from decimal import Decimal
import biip

def getSuperTotal(results,location_fields,colormapped):
    with db.Session(db.ENGINE) as session:
        ROUNDTO=int(db.detectGetOrSet("lsbld ROUNDTO default",3,setValue=False,literal=True))
        master_total=0
        master_total_crv=0
        master_total_tax=0
        master_total_tax_crv=0
        for num,i in enumerate(results):
            total=0
            crv=0
            tax=0
            tax_crv=0
            i.Tax=round(i.Tax,ROUNDTO)
            i.CRV=round(i.CRV,ROUNDTO)
            i.Price=round(i.Price,ROUNDTO)
            session.commit()
            for n2,f in enumerate(location_fields):
                try:
                    if getattr(i,f) > 0:
                        total+=getattr(i,f)
                except Exception as e:
                    print(e)
            
            master_total+=total*round(i.Price,ROUNDTO)

            crv+=(round(i.CRV,ROUNDTO)*total)
            tax+=(round(i.Tax,ROUNDTO)*total)
            if tax == 0 and crv > 0:
                tax_crv=(round(i.CRV,ROUNDTO)*total)
            else:
                tax_crv+=((round(i.Tax,ROUNDTO)*total)+(round(i.CRV,ROUNDTO)*total))
            master_total_tax+=tax
            master_total_crv+=crv
            master_total_tax_crv+=tax_crv
            tax_crv=round(tax_crv,ROUNDTO)

        master_total=round(master_total,ROUNDTO)
        master_total_crv=round(master_total_crv,ROUNDTO)
        master_total_tax=round(master_total_tax,ROUNDTO)
        master_total_tax_crv=round(master_total_tax_crv,ROUNDTO)
        return {'final total':round(master_total_tax_crv+master_total,ROUNDTO),'master_total_tax_crv':master_total_tax_crv,'master_total_tax':master_total_tax,'master_total_crv':master_total_crv,'sub_total':master_total}


class Obfuscate:
    def mkBytes(self,text):
        if text.encode() in b''.rjust(16):
            print(f"{Fore.orange_red_1}Password Must not be empty!{Style.reset}")
            return None
        return text.encode().rjust(16)

    def encrypt(self):
        text=Prompt.__init2__(None,func=FormBuilderMkText,ptext="what do you wish to obfuscate?",helpText="what textual data",data="string")
        print("Encoded Data:",text)
        if text in [None,]:
            return
        print("Password:",self.password)
        text=pad(text.encode(),16)
        cipher = AES.new(self.password,AES.MODE_ECB)
        self.encoded = base64.b64encode(cipher.encrypt(text))
        self.lzmad=lzma.compress(self.encoded)
        self.b64d=base64.b64encode(self.lzmad)
        with open(self.FILE,"wb") as out:
            out.write(self.b64d)
        print("Finalized:",self.b64d)
        print("Saved to:",self.FILE)

    def decrypt(self):
        try:
            if self.FILE:
                if not Path(self.FILE).exists():
                    print(self.FILE,f"{Fore.light_red}Does not exist!{Style.reset}")
                    return           
            with open(self.FILE,"rb") as i:
                self.b64d=i.read()
                self.lzmad=lzma.decompress(base64.b64decode(self.b64d))
                self.encoded=self.lzmad
            cipher = AES.new(self.password,AES.MODE_ECB)
            self.decoded = unpad(cipher.decrypt(base64.b64decode(self.encoded)),16).decode("utf-8")
            print(f"'{self.decoded}'")
        except Exception as e:
            print(e)

    def __init__(self):
        self.FILE=db.detectGetOrSet("OBFUSCATED MSG FILE",value="MSG.txt",setValue=False,literal=True)
        while True:
            self.password=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Password",helpText="Protect your data",data="string")
            if self.password in [None,]:
                return
            self.password=self.mkBytes(self.password)
            if self.password in [None,]:
                continue
            else:
                break

        while True:
            helpText=f'''
e,encrypt - make msg on INPUT and store in {self.FILE}
de,decrypt - decrypt msg from {self.FILE}
            '''
            doWhat=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Obfuscate Menu",helpText=helpText,data="str")
            if doWhat in [None,]:
                return
            elif doWhat in ['d',]:
                print(helpText)
            elif doWhat.lower() in ['e','encrypt']:
                self.encrypt()
            elif doWhat.lower() in ['de','decrypt']:
                self.decrypt()
            else:
                print(helpText)
        
HOLI=holidays.USA(years=datetime.now().year)
extra_dates=[
{datetime(datetime.now().year,4,1):'Easter Sunday'},
]
for i in extra_dates:
    HOLI.append(i)

def next_holiday(self=None,today=None):
    holidates=sorted(HOLI.items())
    if today == None:
        today=DATE(datetime.today().year,datetime.today().month,datetime.today().day)
    
    for date,name in holidates:
        if date > today:
            return date,name,datetime(date.year,date.month,date.day)-datetime.today()
    next_year=today.year+1
    holidates=sorted(holidays.USA(years=next_year).items())
    for date,name in holidates:
        if date > today:
            return date,name,datetime(date.year,date.month,date.day)-datetime.now()

zholidate=next_holiday()
xholidate=f'{Fore.green_yellow}|{Fore.medium_violet_red}'.join([f'{i}' for i in zholidate])
msg_holidate=f'{Style.underline}{Fore.light_steel_blue}Next Holiday is:{Fore.medium_violet_red}{xholidate}{Style.reset}'

#need to make a unique store Storage model

def protocolors():
    screen={i:getattr(Back,i) for i in Back._COLORS}
    screen2={i:getattr(Fore,i) for i in Fore._COLORS}
    screen3={i:getattr(Style,i) for i in ["bold","underline","italic","dim","strikeout","blink"]}
    for i in screen:
        for ii in screen2:
            for iii in screen3:
                try:
                    print(f'{screen3[iii]}{screen[i]}{screen2[ii]}Style.{iii}|Back.{i}|Fore.{ii}{Style.reset}')
                except Exception as e:
                    print(e)
                    print(screen3)
                n=input("Next?[q/b/<Enter>]")
                if n.lower() in ['q','quit']:
                    exit("User Quit")
                elif n.lower() in ['b','back']:
                    return
                else:
                    continue

def useInputAsCode(cmd,display_only=False):
    if not display_only:
        strippedCode=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Is this a stripped upca from a shelf tag [{cmd}]?:",helpText="did this come with a shelf tag whose digits did not start with '0'?",data="boolean")
        if strippedCode in [None,]:
            return
        elif strippedCode == True:
            if (11-len(cmd)) >= 0:
                cmd=f"{'0'*(11-len(cmd))}{cmd}"
                try:
                    cmd=str(UPCA(cmd))
                except Exception as e:
                    print(e)
            else:
                print("code is too long to be a stripped upca")
        else:
            pass
    parsed=biip.parse(cmd)
    if parsed is None:
        return
    attrs=['gtin','upc',]
    codes={}
    if parsed.upc is not None:
        try:
            codes['upc -> gtin12']=parsed.upc.as_gtin_12()
        except Exception as e:
            print(e)
        try:   
            codes['upc -> gtin13']=parsed.upc.as_gtin_13()
        except Exception as e:
            print(e)
        try:   
            codes['upc -> gtin14']=parsed.upc.as_gtin_14()
        except Exception as e:
            print(e)
        try:   
            codes['upc -> upce']=parsed.upc.as_upc_e()
        except Exception as e:
            print(e)
        try:   
            codes['upc -> upca']=parsed.upc.as_upc_a()
        except Exception as e:
            print(e)
    if parsed.gtin is not None:
        try:
            codes['gtin -> gtin8']=parsed.gtin.as_gtin_8()
        except Exception as e:
            print(e)
        try:
            codes['gtin -> gtin12']=parsed.gtin.as_gtin_12()
        except Exception as e:
            print(e)
        try:
            codes['gtin -> gtin13']=parsed.gtin.as_gtin_13()
        except Exception as e:
            print(e)
        try:
            codes['gtin -> gtin14']=parsed.gtin.as_gtin_14()
        except Exception as e:
            print(e)
    codes['as is']=cmd
    #select code
    helpText=[f'{Fore.grey_70}--Input Code Analysis From Biip (added 05.01.25[Month/Day/Year])--{Style.reset}']
    ct=len(codes)
    keys=[]
    for num,i in enumerate(codes):
        msg=f"{Fore.cyan}{num}{Fore.yellow}/{num+1} of {Fore.light_magenta}{ct}[{Fore.light_red}{cmd}{Fore.light_magenta}] -> {Fore.light_green}{i}('{db.Entry.cfmt(None,codes[i])}')"
        helpText.append(msg)
        keys.append(i)
    helpText='\n'.join(helpText)
    
    if display_only:
        return helpText

    while True:
        print(helpText)
        try:
            k=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Which code's index to use",helpText=helpText,data="integer")
            if k in [None,]:
                return cmd
            elif k in ['d',]:
                return cmd
            code=str(codes[keys[k]])
            return code
        except Exception as e:
            print(e)

class MAP:
    def __init__(self):
        #max number of aisle, this includes wall side aisle
        self.amx=4
        #min number of aisle
        self.amn=0
        #max shadow boxes to generate names for this incudes wall side aisle
        self.max_sb=6
        print(self.generate_names())

    def generate_names(self):
        address=[]
        for i in range(self.amn,self.amx):
            address.append(f"Aisle {i}")
        for side in ['Front','Rear']:
            for i in range(self.amn,self.amx):
                address.append(f"Aisle {i} {side} : End Cap")
            for m in ['Right','Left']:
                for i in range(self.amn,self.amx):
                    address.append(f"Aisle {i} {side} : Mid-End {m}")
            for sb in range(self.amn,self.max_sb):
                address.append(f"Aisle {i} {side} : Shadow Box {sb}")
        if len(address) > 0:
            for num,i in enumerate(address):
                print(num,"->",i)
            while True:
                which=input("return which: ")
                if which == '':
                    return address[0]
                elif which.lower() in ['q','quit']:
                    exit("User Quit")
                elif which.lower() in ['b','back']:
                    return
                try:
                    ids=[i for i in range(len(address))]
                    if int(which) in ids:
                        return address[int(which)]
                    else:
                        continue
                except Exception as e:
                    print(e)
                    return address[0]
        return address


def mkb(text,self):
    try:
        if text.lower() in ['','y','yes','true','t','1']:
            return True
        elif text.lower() in ['n','no','false','f','0']:
            return False
        elif text.lower() in ['p',]:
            return text.lower()
        else:
            return bool(eval(text))
    except Exception as e:
        print(e)
        return False

KNOWN_DEVICES=[
'Moto G Stylus 5G (2023)',
'Moto G Stylus 5G (2024)',
'Samsung Galaxy A32',
]
KNOWN_SCANNERS=[
'Eyoyo EY-039HID',
'EY-038L',
'EY-022P',
'EY-027L',
'HoneyWell Voyager 1602UG',
]
def detectGetOrSet(name,value,setValue=False,literal=False):
        value=str(value)
        with Session(db.ENGINE) as session:
            q=session.query(db.SystemPreference).filter(db.SystemPreference.name==name).first()
            ivalue=None
            if q:
                try:
                    if setValue:
                        if not literal:
                            q.value_4_Json2DictString=json.dumps({name:eval(value)})
                        else:
                            q.value_4_Json2DictString=json.dumps({name:value})
                        session.commit()
                        session.refresh(q)
                    ivalue=json.loads(q.value_4_Json2DictString)[name]
                except Exception as e:
                    if not literal:
                        q.value_4_Json2DictString=json.dumps({name:eval(value)})
                    else:
                        q.value_4_Json2DictString=json.dumps({name:value})
                    session.commit()
                    session.refresh(q)
                    ivalue=json.loads(q.value_4_Json2DictString)[name]
            else:
                if not literal:
                    q=db.SystemPreference(name=name,value_4_Json2DictString=json.dumps({name:eval(value)}))
                else:
                    q=db.SystemPreference(name=name,value_4_Json2DictString=json.dumps({name:value}))
                session.add(q)
                session.commit()
                session.refresh(q)
                ivalue=json.loads(q.value_4_Json2DictString)[name]
            return ivalue


def global_search_for_text():
    '''search for text in all tables where possible'''
    with Session(db.ENGINE) as session:
        stext=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search Text:",helpText="what are you looking for",data="string")
        BSE=automap_base()
        BSE.prepare(autoload_with=db.ENGINE)
        classes={}
        for c in BSE.classes:
            classes[c.__class__]=c
            includes=["string","string+","varchar","text"]
            includes2=[str,]
            fields=[i.name for i in c.__table__.columns if str(i.type).lower() in includes and not getattr(i,"primary_key")]
            q=[]
            for f in fields:
                q.append(getattr(c,f).icontains(stext))
            query=session.query(c).filter(or_(*q))
            results=query.all()
            ct=len(results)
            text=[]
            gmsg=[]
            xnum=0
            for num,i in enumerate(results):
                mtp=''
                subfields=[z.name for z in i.__table__.columns if type(getattr(i,z.name)) in includes2 and stext in getattr(i,z.name) and str(z.type).lower() in includes]
                for zsub in subfields:
                    msg=f"{Fore.cyan}{xnum}/{Fore.light_sea_green}{xnum+1} from {Fore.light_magenta} {i.__class__.__name__}.{zsub} -> {getattr(i,zsub).replace(stext,f"{Fore.orange_red_1}{Back.grey_15}{stext}{Back.black}{Fore.light_magenta}")}"
                    gmsg.append(msg)
                    text.append(getattr(i,zsub))
                    xnum+=1
                    print(msg)
            if len(gmsg) > 0:
                gmsg='\n'.join(gmsg)
                return_text=Prompt.__init2__(None,FormBuilderMkText,ptext="Use Text by index?",helpText=gmsg,data="integer")
                if return_text in [None,'d']:
                    continue
                else:
                    return text[return_text]
        return ''



class Prompt(object):
    def QuitMenu(parent):
        def protect():
            bypass_time_protection=detectGetOrSet("bypass_time_protection",False,setValue=False)
            if bypass_time_protection:
                cleared_times=detectGetOrSet("cleared_times",1,setValue=True)
                new_date=datetime.now()
                x_day=new_date.day
                x_month=new_date.month
                x_year=new_date.year
                new_cleared_date=detectGetOrSet("cleared_date",f"{x_month}/{x_day}/{x_year}",setValue=True,literal=True)
                print(f"{Fore.light_yellow}WARNING!!! {Fore.light_red}--->>>> {Fore.light_steel_blue}Time Protection is disabled!{Style.reset}")
                return
            x_today=datetime.now()
            x_day=x_today.day
            x_month=x_today.month
            x_year=x_today.year
            bypass_clear_time_clear_protection=detectGetOrSet("bypass_clear_time_clear_protection",False,setValue=False,literal=False)
            cleared_date=datetime.strptime(detectGetOrSet("cleared_date",f"{x_month}/{x_day}/{x_year}",setValue=False,literal=True),"%m/%d/%Y")
            cleared_times=detectGetOrSet("cleared_times",0,setValue=False)
            #cleared_date=datetime(2025,2,27,0,23,0)
            print("-"*10)
            dur=datetime.now()-cleared_date
            print(dur)
            if not bypass_clear_time_clear_protection:
                clred=datetime(cleared_date.year,cleared_date.month,cleared_date.day)
                tdt=datetime(x_year,x_month,x_day)
                print(tdt,clred,clred!=tdt)
                if clred != tdt:
                    new_date=datetime.now()
                    new_date=datetime(new_date.year,new_date.month,new_date.day)
                    x_day=new_date.day
                    x_month=new_date.month
                    x_year=new_date.year
                    new_cleared_date=detectGetOrSet("cleared_date",f"{x_month}/{x_day}/{x_year}",setValue=True,literal=True)
                    cleared_times=detectGetOrSet("cleared_times",0,setValue=True)
                elif clred == tdt:
                    bu=detectGetOrSet("daily_backups_count",1,setValue=False,literal=False)
                    cleared_times=detectGetOrSet("cleared_times",0,setValue=False)
                    if cleared_times >= bu:
                        print(f"Too Many backups! only {bu} is permitted!")
                        today=datetime.now()
                        tomorrow=datetime(today.year,today.month,today.day)
                        waiting=tomorrow-today
                        print(f"{Fore.grey_70}cleared at {Fore.green_3a}{cleared_date}{Fore.grey_70}for a duration of {Fore.green_3a}{dur}{Fore.light_blue} :{Fore.light_cyan} clear protection is enabled and you have to wait ({Fore.light_steel_blue}to alter use the following cmd set {Fore.cyan}`sysset`;`se`;$INDEX_FOR==bypass_clear_time_clear_protection;`true` or `false`{Fore.light_cyan}) {Fore.light_cyan}{waiting}{Fore.orange_red_1} or @ {tomorrow} to clear data to zero to {Fore.light_yellow}prevent {Fore.light_red}duplicate logs!{Style.reset}")
                        exit()
                    else:
                        new_date=datetime.now()
                        new_date=datetime(new_date.year,new_date.month,new_date.day)
                        x_day=new_date.day
                        x_month=new_date.month
                        x_year=new_date.year
                        new_cleared_date=detectGetOrSet("cleared_date",f"{x_month}/{x_day}/{x_year}",setValue=True,literal=True)
                        cleared_times=detectGetOrSet("cleared_times",cleared_times+1,setValue=True)
                else:
                    
                    today=datetime.now()
                    tomorrow=datetime(today.year,today.month,today.day)+timedelta(seconds=24*60*60)
                    waiting=tomorrow-today

                    print(f"{Fore.grey_70}cleared at {Fore.green_3a}{cleared_date}{Fore.grey_70}for a duration of {Fore.green_3a}{dur}{Fore.light_blue} :{Fore.light_cyan} clear protection is enabled and you have to wait ({Fore.light_steel_blue}to alter use the following cmd set {Fore.cyan}`sysset`;`se`;$INDEX_FOR==bypass_clear_time_clear_protection;`true` or `false`{Fore.light_cyan}) {Fore.light_cyan}{waiting}{Fore.orange_red_1} or @ {tomorrow} to clear data to zero to {Fore.light_yellow}prevent {Fore.light_red}duplicate logs!{Style.reset}")
                    exit()
        
        def protect_unassigned_():
            protect_unassigned=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Protect Entry's with {Fore.light_magenta}Code{Fore.light_yellow}=='{Fore.light_red}UNASSIGNED_TO_NEW_ITEM{Fore.light_yellow}'",helpText="a boolean yes or no",data="boolean")
            if protect_unassigned in [None,]:
                return
            elif protect_unassigned in ['d',]:
                protect_unassigned=True
                detectGetOrSet("protect_unassigned",protect_unassigned,setValue=True)
            else:
                detectGetOrSet("protect_unassigned",protect_unassigned,setValue=True)

        def quit_backup(parent):
            protect()
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE)
            parent.cleanup_system(parent)

        def quit_backup_clear(parent):
            protect()
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE)
            protect_unassigned=detectGetOrSet("protect_unassigned",True,setValue=False)
            bare_ca(None,protect_unassigned=protect_unassigned)
            parent.cleanup_system(parent)

        def tag_quit_backup_clear(parent):
            protect()
            protect_unassigned=detectGetOrSet("protect_unassigned",True,setValue=False)
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE,addTag=True)
            bare_ca(None,protect_unassigned=protect_unassigned)
            parent.cleanup_system(parent)

        def quit_backup_clear_inlist(parent):
            protect()
            protect_unassigned=detectGetOrSet("protect_unassigned",True,setValue=False)
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE)
            bare_ca(None,inList=True,protect_unassigned=protect_unassigned)
            parent.cleanup_system(parent)

        def tag_quit_backup_clear_inlist(parent):
            protect()
            protect_unassigned=detectGetOrSet("protect_unassigned",True,setValue=False)
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE,addTag=True)
            bare_ca(None,inList=True,protect_unassigned=protect_unassigned)
            parent.cleanup_system(parent)

        def backup_clear(parent):
            protect()
            protect_unassigned=detectGetOrSet("protect_unassigned",True,setValue=False)
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE)
            bare_ca(None,protect_unassigned=protect_unassigned)

        def backup_clear_inlist(parent):
            protect()
            protect_unassigned=detectGetOrSet("protect_unassigned",True,setValue=False)
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE)
            bare_ca(None,inList=True,protect_unassigned=protect_unassigned)

        def tag_backup_clear(parent):
            protect()
            protect_unassigned=detectGetOrSet("protect_unassigned",True,setValue=False)
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE,addTag=True)
            bare_ca(None,protect_unassigned=protect_unassigned)

        def tag_backup_clear_inlist(parent):
            protect()
            protect_unassigned=detectGetOrSet("protect_unassigned",True,setValue=False)
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE,addTag=True)
            bare_ca(None,inList=True,protect_unassigned=protect_unassigned)

        def main(parent):
            if parent != None:  
                #parent must be Prompt
                options={
                'isProtectUnassignedOn':{
                'cmds':['ipuao','is protect unassigned on'],
                'exec':lambda:print(f'Is Enabled: {Fore.light_red}{detectGetOrSet("protect_unassigned",True,setValue=False)}{Style.reset}'),
                'desc':"print the status of protect unassigned for this menu session!",

                },
                'protect_unassigned':{
                    'cmds':['pua','protect_unassigned','p u a','protect unassigned'],
                    'exec':lambda:protect_unassigned_(),
                    'desc':'temporarily change default protect_unassigned settings: default == True'
                },
                'quit':{
                    'cmds':['e','jq','just quit','j quit','j q','exit'],
                    'exec':lambda parent=parent:parent.cleanup_system(parent),
                    'desc':"just quit"
                    },
                'quit backup':{
                    'cmds':['qb','quit backup',],
                    'exec':lambda parent=parent:quit_backup(parent),
                    'desc':"quit backup"
                    },
                'quit backup clear':{
                    'cmds':['qbc','quit backup clear'],
                    'exec':lambda parent=parent:quit_backup_clear(parent),
                    'desc':"quit backup clear"
                    },
                'quit backup clear inlist':{
                    'cmds':['qbci','quit backup clear inlist'],
                    'exec':lambda parent=parent:quit_backup_clear_inlist(parent),
                    'desc':"quit backup clear inlist"
                    },
                'tag quit backup clear':{
                    'cmds':['tqbc','tag quit backup clear'],
                    'exec':lambda parent=parent:tag_quit_backup_clear(parent),
                    'desc':"tag daylog entries quit backup clear current list"
                    },
                'tag quit backup clear inlist':{
                    'cmds':['tqbci','tag quit backup clear inlist'],
                    'exec':lambda parent=parent:tag_quit_backup_clear_inlist(parent),
                    'desc':"tag daylog entries quit backup clear current set inList=True"
                    },
                'backup clear':{
                    'cmds':['bc','backup clear'],
                    'exec':lambda parent=parent:backup_clear(parent),
                    'desc':"backup clear inlist=False"
                    },
                'backup clear inlist':{
                    'cmds':['bci','backup clear inlist'],
                    'exec':lambda parent=parent:backup_clear_inlist(parent),
                    'desc':"backup clear inlist=True"
                    },
                'tag backup clear':{
                    'cmds':['tbc','tag backup clear'],
                    'exec':lambda parent=parent:tag_backup_clear(parent),
                    'desc':"tag daylog entries backup clear current list InList=False"
                    },
                'tag backup clear inlist':{
                    'cmds':['tbci','tag backup clear inlist'],
                    'exec':lambda parent=parent:tag_backup_clear_inlist(parent),
                    'desc':"tag daylog entries quit backup clear current set inList=True"
                    },

                }
                htext=[]
                for i in options:
                    line=f"{Fore.light_salmon_1}{options[i]['cmds']} {Fore.light_sea_green}- {options[i]['desc']}"
                    htext.append(line)
                htext='\n'.join(htext)
                htext+=f"{Style.reset}"
                htext=f"{Back.black}{htext}"
                while True:
                    cmd=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f'{Fore.grey_70}[{Fore.light_steel_blue}Quit{Fore.grey_70}] {Fore.light_yellow}Menu',helpText=htext,data="string")
                    if cmd in [None,]:
                        break
                    elif cmd in ['','d']:
                        print(htext)
                    for option in options:
                        if options[option]['exec'] != None and (cmd.lower() in options[option]['cmds'] or cmd in options[option]['cmds']):
                            options[option]['exec']()
                        elif options[option]['exec'] == None and (cmd.lower() in options[option]['cmds'] or cmd in options[option]['cmds']):
                            return
        main(parent)
    '''
            #for use with header
            fieldname='ALL_INFO'
            mode='LU'
            h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
    '''
    header='{Fore.grey_70}[{Fore.light_steel_blue}{mode}{Fore.medium_violet_red}@{Fore.light_green}{fieldname}{Fore.grey_70}]{Style.reset}{Fore.light_yellow} '
    state=True
    status=None
    def mkfield_list(self,fields):
        ct=len(fields)
        htext=''
        x=[]
        for num,i in enumerate(fields):
            msg=f"{Fore.cyan}{num}/{Fore.light_steel_blue}{num+1} of {Fore.light_red}{ct} -> '{i}'"
            htext+=msg+"\n"
            print(msg)
        which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Which index(es[comma separated]): ",helpText="comma separated indexes/numbers",data="list")
        if which in ['d',None]:
            return
        try:
            for i in which:
                try:
                    i=int(i)
                    x.append(fields[i])
                except Exception as ee:
                    print(ee)
        except Exception as e:
            print(e)
        return x

    def cleanup_system(self):
        try:
            print("Cleanup Started!")
            s=namedtuple(field_names=['ageLimit',],typename="self")
            s.ageLimit=db.AGELIMIT

            db.ClipBoordEditor.autoClean(s)

            def deleteOutDated(RID):
                with Session(db.ENGINE) as session:
                    q=session.query(db.RandomString).filter(db.RandomString.RID==RID).first()
                    print(f"Deleting {q}")
                    session.delete(q)
                    session.commit()
                    session.flush()

            def checkForOutDated():
                try:
                    ageLimit=ageLimit=float(pint.UnitRegistry().convert(2,"years","seconds"))
                    with Session(db.ENGINE) as session:
                        results=session.query(db.RandomString).all()
                        ct=len(results)
                        print(f"{Fore.light_green}RandomString len({Fore.light_salmon_3a}History{Fore.light_green}){Fore.medium_violet_red}={Fore.green_yellow}{ct}{Style.reset}")
                        for num,i in enumerate(results):
                            if i:
                                if i.AgeLimit != ageLimit:
                                    i.AgeLimit= ageLimit
                                    session.commit()
                                    session.flush()
                                    session.refresh(i)
                                if (datetime.now()-i.CDateTime).total_seconds() >= i.AgeLimit:
                                    print("need to delete expired! -> {num+1}/{ct} -> {i}")
                                    deleteOutDated(i.RID)
                except sqlalchemy.exc.OperationalError as e:
                    print(e)
                    print("Table Needs fixing... doing it now!")
                    reset()
            
            def reset():
                db.RandomStringPreferences.__table__.drop(ENGINE)
                db.RandomStringPreferences.metadata.create_all(ENGINE)

                db.RandomString.__table__.drop(ENGINE)
                db.RandomString.metadata.create_all(ENGINE)
                print(f"{Fore.orange_red_1}A restart is required!{Style.reset}")
                exit("User Quit For Reboot!")
            checkForOutDated()
        except Exception as e:
            print(e)
        lastTime=db.detectGetOrSet("PromptLastDTasFloat",datetime.now().timestamp(),setValue=True)
        exit('User Quit')
    bld_file="./BLD.txt"
    def __init__(self,func,ptext='do what',helpText='',data={},noHistory=False):
        while True:
            cmd=input(f'{Fore.light_yellow}{ptext}{Style.reset}:{Fore.light_green} ')
            db.logInput(cmd)
            print(Style.reset,end='')
            
            if cmd.lower() in ['q','quit']:
                Prompt.cleanup_system(None)
            elif cmd.lower() in ['b','back']:
                self.status=False
                DayLogger(engine=ENGINE).addToday()
                return
            elif cmd.lower() in ['?','h','help']:
                print(helpText)
                extra=f'''
{Fore.light_yellow}{'.'*os.get_terminal_size().columns}{Style.reset}
{Fore.light_green}neu{Fore.light_steel_blue} - create a new entry menu{Style.reset}
{Fore.light_green}seu{Fore.light_steel_blue} - search entry menu{Style.reset}
                '''
                print(extra)
            else:
                #print(func)
                func(cmd,data)
                break

    def passwordfile(self):
        of=Path("GeneratedString.txt")
        if of.exists():
            age=datetime.now()-datetime.fromtimestamp(of.stat().st_ctime)
            days=float(age.total_seconds()/60/60/24)
            if days > 15:
                print(f"{Fore.light_yellow}Time is up, removeing old string file! {Fore.light_red}{of}{Style.reset}")
                of.unlink()
            else:
                print(f"{Fore.light_yellow}{of} {Fore.light_steel_blue}is {round(days,2)} {Fore.light_red}Days old!{Fore.light_steel_blue} you have {Fore.light_red}{15-round(days,2)} days{Fore.light_steel_blue} left to back it up!{Style.reset}")
                try:
                    print(f"{Fore.medium_violet_red}len(RandomString)={Fore.deep_pink_1a}{len(of.open().read())}\n{Fore.light_magenta}RandomString={Fore.dark_goldenrod}{Fore.orange_red_1}{of.open().read()}{Style.reset}")
                except Exception as e:
                    print(e)
                    print(f"{Fore.light_red}Could not read {of}{Style.reset}!")
        else:
            print(f"{Fore.orange_red_1}{of}{Fore.light_steel_blue} does not exist!{Style.reset}")

    def shortenToLen(text,length=os.get_terminal_size().columns-10):
        tmp=''
        for num,i in enumerate(text):
            if num%8==0 and num > 0:
                tmp+="\n"
            tmp+=i
        return tmp

    def resrc(self):
        try:
            rss=resource.getrusage(resource.RUSAGE_THREAD).ru_maxrss
        except Exception as e:
            print(e)
            rss=0
        try:
            page_size=resource.getpagesize()
        except Exception as e:
            page_size=0
        try:
            megabytes=pint.UnitRegistry().convert(rss*page_size,"bytes","megabytes")
        except Exception as e:
            print(e)
            megabytes=0
        out=f'''{Fore.orange_red_1}|MaxRSSThread({rss})*{Fore.dark_goldenrod}PageSize({page_size})={Fore.light_green}{round(megabytes,1)}MB'''
        return out
            

    def __init2__(self,func,ptext='do what',helpText='',data={},noHistory=False):
        lastTime=db.detectGetOrSet("PromptLastDTasFloat",datetime.now().timestamp())
        buffer=[]
        while True:
            color1=Style.bold+Fore.medium_violet_red
            color2=Fore.sea_green_2
            color3=Fore.pale_violet_red_1
            color4=color1
            split_len=int(os.get_terminal_size().columns/2)
            whereAmI=[str(Path.cwd())[i:i+split_len] for i in range(0, len(str(Path.cwd())), split_len)]
            helpText2=f'''
{Fore.light_salmon_3a}DT:{Fore.light_salmon_1}{datetime.now()}{Style.reset}
{Fore.orchid}PATH:{Fore.dark_sea_green_5a}{'#'.join(whereAmI)}{Style.reset}
{Fore.light_salmon_1}System Version: {Back.grey_70}{Style.bold}{Fore.red}{VERSION}{Style.reset}'''.replace('#','\n')
            
            default_list=''
            with db.Session(db.ENGINE) as session:
                    results=session.query(db.SystemPreference).filter(db.SystemPreference.name=="DefaultLists").all()
                    ct=len(results)
                    n=None
                    if ct <= 0:
                        pass
                        #print("no default tags")
                    else:
                        for num,r in enumerate(results):
                            try:
                                if r.default:
                                    default_list=','.join(json.loads(r.value_4_Json2DictString).get("DefaultLists"))
                                    break
                            except Exception as e:
                                print(e)

            #{Back.dark_orange_3b}
            now=datetime.now()
            nowFloat=now.timestamp()
            timeInshellStart=datetime.fromtimestamp(db.detectGetOrSet("InShellStart",nowFloat))
            InShellElapsed=datetime.now()-timeInshellStart
            lastCmdDT=None
            with db.Session(db.ENGINE) as session:
                lastCMD=session.query(db.PH).order_by(db.PH.dtoe.desc()).limit(2).all()                
                if len(lastCMD) >= 2:
                    lastCmdDT=lastCMD[1].dtoe
            if lastCmdDT != None:
                duration=now-lastCmdDT
            else:
                duration=None
            def lineTotal():
                total=0
                if not Path("STDOUT.TXT").exists():
                    with Path("STDOUT.TXT").open("w") as log:
                        log.write("")

                with open(Path("STDOUT.TXT"),"r") as log:
                    total=len(log.readlines())
                return total
            
            isit=now in HOLI
            holiname=HOLI.get(now.strftime("%m/%d/%Y"))

            if not holiname:
                holiname=f"""{Fore.orange_4b}Not a Holiday {Style.reset}"""
            holidate=f'{msg_holidate}\n{Fore.light_magenta}Holiday: {Fore.dark_goldenrod}{isit} | {Fore.light_sea_green}{holiname}{Style.reset}'
            m=f"{holidate}|{Fore.light_blue}DUR="+str(datetime.now()-datetime.fromtimestamp(lastTime)).split(".")[0]
            cmd=input(f'''{Fore.light_sea_green+((os.get_terminal_size().columns)-len(m))*'*'}
{Back.dark_red_1}{Fore.light_yellow}{ptext}{Style.reset}
{Fore.light_steel_blue+os.get_terminal_size().columns*'*'}
{m}{Fore.black}{Back.grey_70} P_CMDS SncLstCmd:{str(duration).split(".")[0]} {Style.reset}|{Fore.black}{Back.grey_50} TmInShl:{str(InShellElapsed).split(".")[0]}|DT:{now.ctime()}| {Fore.dark_blue}{Style.bold}{Style.underline}Week {datetime.now().strftime("%W")} {Style.reset}|{Fore.light_magenta}#RPLC#={Fore.tan}rplc {Fore.light_magenta}#RPLC#{Fore.tan} frm {Fore.light_red}CB{Fore.orange_3}.{Fore.light_green}default={Fore.light_yellow}True{Fore.light_steel_blue} or by {Fore.light_red}CB{Fore.orange_3}.{Fore.light_green}doe={Fore.light_yellow}Newest{Style.reset}|{Fore.light_salmon_1}c2c=calc2cmd={Fore.sky_blue_2}clctr rslt to inpt{Style.reset}|b={color2}back|{Fore.light_red}h={color3}help{color4}|{Fore.light_red}h+={color3}help+{color4}|{Fore.light_magenta}i={color3}info|{Fore.light_green}{Fore.light_steel_blue}CMD#c2cb[{Fore.light_red}e{Fore.light_steel_blue}]{Fore.light_green}{Fore.light_red}|{Fore.orange_3}c2cb[{Fore.light_red}e{Fore.orange_3}]#CMD{Fore.light_green} - copy CMD to cb and set default | Note: optional [{Fore.light_red}e{Fore.light_green}] executes after copy{Style.reset} {Fore.light_steel_blue}NTE: cmd ends/start-swith [{Fore.light_red}#clr|clr#{Fore.light_green}{Fore.light_steel_blue}] clrs crnt ln 4 a rtry{Style.reset} {Fore.orange_red_1}|c{Fore.light_steel_blue}=calc|{Fore.spring_green_3a}cb={Fore.light_blue}clipboard{Style.reset}|{Fore.light_salmon_1}cdp={Fore.green_yellow}paste cb dflt {Fore.green}|q={Fore.green_yellow}Quit Menu (qm)
{Fore.light_red+os.get_terminal_size().columns*'.'}
{Fore.rgb(55,191,78)}HFL:{Fore.rgb(55,130,191)}{lineTotal()}{Fore.light_red} ->{Fore.light_green}{Back.grey_15}''')
            db.logInput(cmd)
            print(f"{Fore.medium_violet_red}{os.get_terminal_size().columns*'.'}{Style.reset}",end='')
            
            def preProcess_RPLC(cmd):
                if '#RPLC#' in cmd:
                    with db.Session(db.ENGINE) as session:
                        dflt=session.query(db.ClipBoord).filter(db.ClipBoord.defaultPaste==True).order_by(db.ClipBoord.doe.desc()).first()
                        if dflt:
                            print(f"""{Fore.orange_red_1}using #RPLC#='{Fore.light_blue}{dflt.cbValue}{Fore.orange_red_1}'
    in {Fore.light_yellow}'{cmd.replace('#RPLC#',dflt.cbValue)}'{Style.reset}""")
                            return cmd.replace('#RPLC#',dflt.cbValue)
                        else:
                            return cmd
                            print(f"{Fore.orange_red_1}nothing to use to replace {Fore.orange_4b}#RPLC#!{Style.reset}")
                else:
                    return cmd
            cmd=preProcess_RPLC(cmd)
            def shelfCodeDetected(code):
                try:
                    with db.Session(db.ENGINE) as session:
                        results=session.query(db.Entry).filter(db.Entry.Code==code).all()
                        ct=len(results)
                except Exception as e:
                    print(e)
                    ct=0
                return f"{Fore.light_red}[{Fore.light_green}{Style.bold}Shelf{Style.reset}{Fore.light_green} CD FND{Fore.light_red}] {Fore.orange_red_1}{Style.underline}{code}{Style.reset} {Fore.light_green}{ct}{Fore.light_steel_blue} Found!{Style.reset}"
            
            def shelfBarcodeDetected(code):
                try:
                    with db.Session(db.ENGINE) as session:
                        results=session.query(db.Entry).filter(db.Entry.Barcode==code).all()
                        ct=len(results)
                        #extra_data#
                        if len(code) in range(6,14):
                            pc.run(db.ENGINE,CODE=code)
                except Exception as e:
                    print(e)
                    ct=0
                if ct > 0:
                    return f"{Fore.light_red}[{Fore.light_green}{Style.bold}Entry{Style.reset}{Fore.light_green} BCD FND{Fore.light_red}] {Fore.orange_red_1}{Style.underline}{code}{Style.reset} {Fore.light_green}{ct}{Fore.light_steel_blue} Found!{Style.reset}"
                else:
                    return ''
            def shelfPCCodeDetected(code):
                try:
                    with db.Session(db.ENGINE) as session:
                        results=session.query(db.PairCollection).filter(db.PairCollection.Code==code).all()
                        ct=len(results)
                except Exception as e:
                    print(e)
                    ct=0
                return f"{Fore.light_red}[{Fore.light_green}{Style.bold}Shelf{Style.reset}{Fore.light_green} CD FND in PC{Fore.light_red}] {Fore.orange_red_1}{Style.underline}{code}{Style.reset} {Fore.light_green}{ct}{Fore.light_steel_blue} Found!{Style.reset}"
            
            def shelfPCBarcodeDetected(code):
                try:
                    with db.Session(db.ENGINE) as session:
                        results=session.query(db.PairCollection).filter(db.PairCollection.Barcode==code).all()
                        ct=len(results)
                except Exception as e:
                    print(e)
                    ct=0
                if ct > 0:
                    return f"{Fore.light_red}[{Fore.light_green}{Style.bold}PC{Style.reset}{Fore.light_green} BCD FND{Fore.light_red}] {Fore.orange_red_1}{Style.underline}{code}{Style.reset} {Fore.light_green}{ct}{Fore.light_steel_blue} Found!{Style.reset}"
                else:
                    return ''



            def detectShelfCode(cmd):
                if cmd.startswith('*') and cmd.endswith('*') and len(cmd) - 2 == 8:
                    pattern=r"\*\d*\*"
                    shelfPattern=re.findall(pattern,cmd)
                    if len(shelfPattern) > 0:
                        #extra for shelf tag code
                        scMsg=f'{shelfCodeDetected(cmd[1:-1])}:{shelfPCCodeDetected(cmd[1:-1])}'
                        print(scMsg)
                        return cmd[1:-1]
                    else:
                        return cmd
                else:
                    return cmd
            bcdMsg=f'{shelfPCBarcodeDetected(cmd)}:{shelfBarcodeDetected(cmd)}'
            print(bcdMsg)
            
            def GetAsciiOnly(cmd):
                hws='\x1bOP\x1bOP'
                #hws='OPOP'
                tmp=cmd
                stripped=''
                if cmd.startswith(hws):
                   tmp=cmd[len(hws):]

                removed=[]
                for i in tmp:
                    if i in string.printable:
                        stripped+=i
                    else:
                        try:
                            print(ord(i),i)
                            #replace i with string representing emogi
                        except Exception as e:
                            pass
                        
                        removed.append(i)
                
                
                #if stripped.startswith("OPOP"):
                #    stripped=stripped[len("OPOP"):]
                ex=f"stripped({[hws.encode(),]})\n"
                if not cmd.startswith(hws):
                    ex=''
                ex1=f"stripped('{removed}')\n"
                if len(removed) <= 0:
                    ex1=''
                try:
                    msg=f'''{'.'*10}\n{Fore.grey_50}{Style.bold}Input Diagnostics
    Input Data({Fore.light_green}{cmd.encode()}{Fore.grey_50}){Style.reset}{Fore.light_salmon_1}
    {ex1}{ex}{Fore.light_blue}finalCmd('{stripped}')\n{'.'*10}
    cmd_len={len(cmd)}{Style.reset}'''
                except Exception as e:
                    print(e)
                    try:
                        detector = chardet.universaldetector.UniversalDetector()
                        detector.feed(cmd)
                        detector.close()
                        encoding=detector.result['encoding']
                        msg=f'''{'.'*10}\n{Fore.grey_50}{Style.bold}Input Diagnostics
        Input Data({Fore.light_green}{bytes(cmd,encoding)}{Fore.grey_50}){Style.reset}{Fore.light_salmon_1}
        {ex1}{ex}{Fore.light_blue}finalCmd('{stripped}')\n{'.'*10}
        cmd_len={len(cmd)}{Style.reset}'''
                    except Exception as e:
                        msg=f'''{'.'*10}\n{Fore.grey_50}{Style.bold}Input Diagnostics
        Input Data({Style.underline}{Style.bold}{Back.white}#UNDISPLAYABLE INPUT - {removed}#{Style.reset}{Fore.light_green}{Fore.grey_50}){Style.reset}{Fore.light_salmon_1}
        {ex1}{ex}{Fore.light_blue}finalCmd('{stripped}')\n{'.'*10}
        cmd_len={len(cmd)}{Style.reset}'''
                print(msg)
                return stripped
            #QR Codes with honeywell voyager 1602ug have an issue this filters it
            def GetAsciiOnly2(cmd):
                hws='\x1b[B'
                tmp=cmd
                stripped=''
                if cmd.endswith(hws):
                   tmp=cmd[:-1*len(hws)]
                   return tmp
                return cmd

            def detectGetOrSet(name,length):
                with db.Session(db.ENGINE) as session:
                    q=session.query(db.SystemPreference).filter(db.SystemPreference.name==name).first()
                    value=None
                    if q:
                        try:
                            value=json.loads(q.value_4_Json2DictString)[name]
                        except Exception as e:
                            q.value_4_Json2DictString=json.dumps({name:length})
                            session.commit()
                            session.refresh(q)
                            value=json.loads(q.value_4_Json2DictString)[name]
                    else:
                        q=db.SystemPreference(name=name,value_4_Json2DictString=json.dumps({name:length}))
                        session.add(q)
                        session.commit()
                        session.refresh(q)
                        value=json.loads(q.value_4_Json2DictString)[name]
                    return value

            cmd=GetAsciiOnly2(cmd)
            cmd=GetAsciiOnly(cmd)
            scanout=Path(detectGetOrSet('CMD_TO_FILE',str(Path('./SCANNER.TXT'))))

            ml_delim=str(detectGetOrSet('ML_DELIM',str(Path('#ml#'))))
            if cmd.startswith(ml_delim) and not cmd.endswith(ml_delim):
                msg=f'''
{Fore.light_steel_blue}
Generate the Barcodes for using Code128 as the Code Type
    {Fore.light_green}MNUSAV - saves honeywell 1602ug settings,{Fore.light_magenta}MNUABT - discards honeywell 1602ug settings,{Fore.light_green}RESET_ - reset scanner,{Fore.light_magenta}SUFBK2 - add Suffix,{Fore.light_green}SUFCA2 - Clear All Suffixes,{Fore.light_magenta}SUFCL2 - Clear One Suffix,{Fore.light_green}PREBK2 - Add Prefix,{Fore.light_magenta}PRECA2 - Clear all Prefixes,{Fore.light_green}PRECL2 - Clear One Prefix{Style.reset}
    {Fore.light_green}Use a Hex editor to convert alpha-numeric values to hex and use the below codes
    Scan the code sequence for 9,9 to set all prefixes and suffixes to
{Fore.light_steel_blue}
    {Fore.grey_70}K0K - 0,{Fore.cyan}K1K - 1,{Fore.grey_70}K3K - 3,{Fore.cyan}K4K - 4,{Fore.grey_70}K5K - 5,{Fore.cyan}K6K - 6,{Fore.grey_70}K7K - 7,{Fore.cyan}K8K - 8,{Fore.grey_70}K9K - 9,{Fore.cyan}KAK - A,{Fore.grey_70}KBK - B,{Fore.cyan}KCK - C,{Fore.grey_70}KDK - D,{Fore.cyan}KEK - E,{Fore.grey_70}KFK - F{Style.reset}
    {Fore.light_red}{Style.bold}You WILL need the scanners programming chart until further notice
and the honeywell set prefix/suffix is {ml_delim}
{Fore.light_yellow}The Sequences needed to be scanned are
-------------
Prefix {ml_delim}
-------------
    PRECA2
    PREBK2
    9,9
    2,3
    6,8
    7,7
    2,3
    MNUSAV
--------------
Suffix {ml_delim}\\n
--------------
    SUFCA2
    SUFBK2
    9,9
    2,3
    6,8
    7,7
    2,3
    0,D
    MNUSAV
{Style.reset}
'''
                print(msg)
                print(f"{Fore.orange_red_1}An Incomplete Scan Occurred, Please Finish with end of cmd followed immediately by {Fore.magenta}{ml_delim}{Style.reset}")
                buffer.append(cmd)
                continue
            elif cmd.startswith(ml_delim) and cmd.endswith(ml_delim):
                if len(buffer) > 0:
                    buffer.append(cmd)
                    #cmd=''.join(buffer).replace(ml_delim,'')
                    cmd='\n'.join(buffer)[len(ml_delim):-len(ml_delim)]
                else:
                    #cmd=cmd.replace(ml_delim,'')
                    cmd=cmd[len(ml_delim):-len(ml_delim)]
                    with scanout.open("w+") as out:
                        out.write(cmd)
            elif not cmd.startswith(ml_delim) and cmd.endswith(ml_delim):
                buffer.append(cmd)
                cmd='\n'.join(buffer)[len(ml_delim):-len(ml_delim)]
                with scanout.open("w+") as out:
                    out.write(cmd)
                msg=f'''
{Fore.light_steel_blue}
Generate the Barcodes for using Code128 as the Code Type
    {Fore.light_green}MNUSAV - saves honeywell 1602ug settings,{Fore.light_magenta}MNUABT - discards honeywell 1602ug settings,{Fore.light_green}RESET_ - reset scanner,{Fore.light_magenta}SUFBK2 - add Suffix,{Fore.light_green}SUFCA2 - Clear All Suffixes,{Fore.light_magenta}SUFCL2 - Clear One Suffix,{Fore.light_green}PREBK2 - Add Prefix,{Fore.light_magenta}PRECA2 - Clear all Prefixes,{Fore.light_green}PRECL2 - Clear One Prefix{Style.reset}
    {Fore.light_green}Use a Hex editor to convert alpha-numeric values to hex and use the below codes
    Scan the code sequence for 9,9 to set all prefixes and suffixes to
{Fore.light_steel_blue}
    {Fore.grey_70}K0K - 0,{Fore.cyan}K1K - 1,{Fore.grey_70}K3K - 3,{Fore.cyan}K4K - 4,{Fore.grey_70}K5K - 5,{Fore.cyan}K6K - 6,{Fore.grey_70}K7K - 7,{Fore.cyan}K8K - 8,{Fore.grey_70}K9K - 9,{Fore.cyan}KAK - A,{Fore.grey_70}KBK - B,{Fore.cyan}KCK - C,{Fore.grey_70}KDK - D,{Fore.cyan}KEK - E,{Fore.grey_70}KFK - F{Style.reset}
    {Fore.light_red}{Style.bold}You WILL need the scanners programming chart until further notice
and the honeywell set prefix/suffix is {ml_delim}
{Fore.light_yellow}The Sequences needed to be scanned are
-------------
Prefix {ml_delim}
-------------
    PRECA2
    PREBK2
    9,9
    2,3
    6,8
    7,7
    2,3
    MNUSAV
--------------
Suffix {ml_delim}\\n
--------------
    SUFCA2
    SUFBK2
    9,9
    2,3
    6,8
    7,7
    2,3
    0,D
    MNUSAV
{Style.reset}
'''
                print(msg)
                nl='\n'
                debuffer=f'{nl}'.join(buffer)
                print(f"{Fore.orange_red_1}An Incomplete Scan Occurred, '{Fore.light_green}{cmd}{Fore.light_yellow}' was finalized with {Fore.magenta}{ml_delim}{Fore.sky_blue_2}, as '{debuffer}'{Style.reset}")
                
                buffer=[]
            elif not cmd.startswith(ml_delim) and not cmd.endswith(ml_delim) and len(buffer) > 0:
                msg=f'''
{Fore.light_steel_blue}
Generate the Barcodes for using Code128 as the Code Type
    {Fore.light_green}MNUSAV - saves honeywell 1602ug settings,{Fore.light_magenta}MNUABT - discards honeywell 1602ug settings,{Fore.light_green}RESET_ - reset scanner,{Fore.light_magenta}SUFBK2 - add Suffix,{Fore.light_green}SUFCA2 - Clear All Suffixes,{Fore.light_magenta}SUFCL2 - Clear One Suffix,{Fore.light_green}PREBK2 - Add Prefix,{Fore.light_magenta}PRECA2 - Clear all Prefixes,{Fore.light_green}PRECL2 - Clear One Prefix{Style.reset}
    {Fore.light_green}Use a Hex editor to convert alpha-numeric values to hex and use the below codes
    Scan the code sequence for 9,9 to set all prefixes and suffixes to
{Fore.light_steel_blue}
    {Fore.grey_70}K0K - 0,{Fore.cyan}K1K - 1,{Fore.grey_70}K3K - 3,{Fore.cyan}K4K - 4,{Fore.grey_70}K5K - 5,{Fore.cyan}K6K - 6,{Fore.grey_70}K7K - 7,{Fore.cyan}K8K - 8,{Fore.grey_70}K9K - 9,{Fore.cyan}KAK - A,{Fore.grey_70}KBK - B,{Fore.cyan}KCK - C,{Fore.grey_70}KDK - D,{Fore.cyan}KEK - E,{Fore.grey_70}KFK - F{Style.reset}
    {Fore.light_red}{Style.bold}You WILL need the scanners programming chart until further notice
and the honeywell set prefix/suffix is {ml_delim}
{Fore.light_yellow}The Sequences needed to be scanned are
-------------
Prefix {ml_delim}
-------------
    PRECA2
    PREBK2
    9,9
    2,3
    6,8
    7,7
    2,3
    MNUSAV
--------------
Suffix {ml_delim}\\n
--------------
    SUFCA2
    SUFBK2
    9,9
    2,3
    6,8
    7,7
    2,3
    0,D
    MNUSAV
{Style.reset}
'''
                print(msg)
                print(f"""{Fore.orange_red_1}An Incomplete Scan Occurred;
                    type the remainder of the command to add it to the buffer,
                    Please Finish with end of cmd followed immediately by {Fore.magenta}{ml_delim}{Style.reset}.
                    CMD's are not final until ended with {Fore.magenta}{ml_delim}{Style.reset}""")
                buffer.append(cmd)
                print(buffer)
                continue



            #multiline end#

            hw_delim=str(detectGetOrSet('HW_DELIM',str(Path('#hw#'))))
            if cmd.startswith(hw_delim) and not cmd.endswith(hw_delim):
                msg=f'''
{Fore.light_steel_blue}
Generate the Barcodes for using Code128 as the Code Type
    {Fore.light_green}MNUSAV - saves honeywell 1602ug settings,{Fore.light_magenta}MNUABT - discards honeywell 1602ug settings,{Fore.light_green}RESET_ - reset scanner,{Fore.light_magenta}SUFBK2 - add Suffix,{Fore.light_green}SUFCA2 - Clear All Suffixes,{Fore.light_magenta}SUFCL2 - Clear One Suffix,{Fore.light_green}PREBK2 - Add Prefix,{Fore.light_magenta}PRECA2 - Clear all Prefixes,{Fore.light_green}PRECL2 - Clear One Prefix{Style.reset}
    {Fore.light_green}Use a Hex editor to convert alpha-numeric values to hex and use the below codes
    Scan the code sequence for 9,9 to set all prefixes and suffixes to
{Fore.light_steel_blue}
    {Fore.grey_70}K0K - 0,{Fore.cyan}K1K - 1,{Fore.grey_70}K3K - 3,{Fore.cyan}K4K - 4,{Fore.grey_70}K5K - 5,{Fore.cyan}K6K - 6,{Fore.grey_70}K7K - 7,{Fore.cyan}K8K - 8,{Fore.grey_70}K9K - 9,{Fore.cyan}KAK - A,{Fore.grey_70}KBK - B,{Fore.cyan}KCK - C,{Fore.grey_70}KDK - D,{Fore.cyan}KEK - E,{Fore.grey_70}KFK - F{Style.reset}
    {Fore.light_red}{Style.bold}You WILL need the scanners programming chart until further notice
and the honeywell set prefix/suffix is {hw_delim}
{Fore.light_yellow}The Sequences needed to be scanned are
-------------
Prefix {hw_delim}
-------------
    PRECA2
    PREBK2
    9,9
    2,3
    6,8
    7,7
    2,3
    MNUSAV
--------------
Suffix {hw_delim}\\n
--------------
    SUFCA2
    SUFBK2
    9,9
    2,3
    6,8
    7,7
    2,3
    0,D
    MNUSAV
{Style.reset}
'''
                print(msg)
                print(f"{Fore.orange_red_1}An Incomplete Scan Occurred, Please Finish with end of cmd followed immediately by {Fore.magenta}{hw_delim}{Style.reset}")
                buffer.append(cmd)
                continue
            elif cmd.startswith(hw_delim) and cmd.endswith(hw_delim):
                if len(buffer) > 0:
                    buffer.append(cmd)
                    #cmd=''.join(buffer).replace(hw_delim,'')
                    cmd=''.join(buffer)[len(hw_delim):-len(hw_delim)]
                else:
                    #cmd=cmd.replace(hw_delim,'')
                    cmd=cmd[len(hw_delim):-len(hw_delim)]
                    with scanout.open("w+") as out:
                        out.write(cmd)
            elif not cmd.startswith(hw_delim) and cmd.endswith(hw_delim):
                buffer.append(cmd)
                cmd=''.join(buffer)[len(hw_delim):-len(hw_delim)]
                with scanout.open("w+") as out:
                    out.write(cmd)
                msg=f'''
{Fore.light_steel_blue}
Generate the Barcodes for using Code128 as the Code Type
    {Fore.light_green}MNUSAV - saves honeywell 1602ug settings,{Fore.light_magenta}MNUABT - discards honeywell 1602ug settings,{Fore.light_green}RESET_ - reset scanner,{Fore.light_magenta}SUFBK2 - add Suffix,{Fore.light_green}SUFCA2 - Clear All Suffixes,{Fore.light_magenta}SUFCL2 - Clear One Suffix,{Fore.light_green}PREBK2 - Add Prefix,{Fore.light_magenta}PRECA2 - Clear all Prefixes,{Fore.light_green}PRECL2 - Clear One Prefix{Style.reset}
    {Fore.light_green}Use a Hex editor to convert alpha-numeric values to hex and use the below codes
    Scan the code sequence for 9,9 to set all prefixes and suffixes to
{Fore.light_steel_blue}
    {Fore.grey_70}K0K - 0,{Fore.cyan}K1K - 1,{Fore.grey_70}K3K - 3,{Fore.cyan}K4K - 4,{Fore.grey_70}K5K - 5,{Fore.cyan}K6K - 6,{Fore.grey_70}K7K - 7,{Fore.cyan}K8K - 8,{Fore.grey_70}K9K - 9,{Fore.cyan}KAK - A,{Fore.grey_70}KBK - B,{Fore.cyan}KCK - C,{Fore.grey_70}KDK - D,{Fore.cyan}KEK - E,{Fore.grey_70}KFK - F{Style.reset}
    {Fore.light_red}{Style.bold}You WILL need the scanners programming chart until further notice
and the honeywell set prefix/suffix is {hw_delim}
{Fore.light_yellow}The Sequences needed to be scanned are
-------------
Prefix {hw_delim}
-------------
    PRECA2
    PREBK2
    9,9
    2,3
    6,8
    7,7
    2,3
    MNUSAV
--------------
Suffix {hw_delim}\\n
--------------
    SUFCA2
    SUFBK2
    9,9
    2,3
    6,8
    7,7
    2,3
    0,D
    MNUSAV
{Style.reset}
'''
                print(msg)
                print(f"{Fore.orange_red_1}An Incomplete Scan Occurred, '{Fore.light_green}{cmd}{Fore.light_yellow}' was finalized with {Fore.magenta}{hw_delim}{Fore.sky_blue_2}, as '{''.join(buffer)}'{Style.reset}")
                
                buffer=[]
            elif not cmd.startswith(hw_delim) and not cmd.endswith(hw_delim) and len(buffer) > 0:
                msg=f'''
{Fore.light_steel_blue}
Generate the Barcodes for using Code128 as the Code Type
    {Fore.light_green}MNUSAV - saves honeywell 1602ug settings,{Fore.light_magenta}MNUABT - discards honeywell 1602ug settings,{Fore.light_green}RESET_ - reset scanner,{Fore.light_magenta}SUFBK2 - add Suffix,{Fore.light_green}SUFCA2 - Clear All Suffixes,{Fore.light_magenta}SUFCL2 - Clear One Suffix,{Fore.light_green}PREBK2 - Add Prefix,{Fore.light_magenta}PRECA2 - Clear all Prefixes,{Fore.light_green}PRECL2 - Clear One Prefix{Style.reset}
    {Fore.light_green}Use a Hex editor to convert alpha-numeric values to hex and use the below codes
    Scan the code sequence for 9,9 to set all prefixes and suffixes to
{Fore.light_steel_blue}
    {Fore.grey_70}K0K - 0,{Fore.cyan}K1K - 1,{Fore.grey_70}K3K - 3,{Fore.cyan}K4K - 4,{Fore.grey_70}K5K - 5,{Fore.cyan}K6K - 6,{Fore.grey_70}K7K - 7,{Fore.cyan}K8K - 8,{Fore.grey_70}K9K - 9,{Fore.cyan}KAK - A,{Fore.grey_70}KBK - B,{Fore.cyan}KCK - C,{Fore.grey_70}KDK - D,{Fore.cyan}KEK - E,{Fore.grey_70}KFK - F{Style.reset}
    {Fore.light_red}{Style.bold}You WILL need the scanners programming chart until further notice
and the honeywell set prefix/suffix is {hw_delim}
{Fore.light_yellow}The Sequences needed to be scanned are
-------------
Prefix {hw_delim}
-------------
    PRECA2
    PREBK2
    9,9
    2,3
    6,8
    7,7
    2,3
    MNUSAV
--------------
Suffix {hw_delim}\\n
--------------
    SUFCA2
    SUFBK2
    9,9
    2,3
    6,8
    7,7
    2,3
    0,D
    MNUSAV
{Style.reset}
'''
                print(msg)
                print(f"""{Fore.orange_red_1}An Incomplete Scan Occurred;
                    type the remainder of the command to add it to the buffer,
                    Please Finish with end of cmd followed immediately by {Fore.magenta}{hw_delim}{Style.reset}.
                    CMD's are not final until ended with {Fore.magenta}{hw_delim}{Style.reset}""")
                buffer.append(cmd)
                print(buffer)
                continue
            cmd=detectShelfCode(cmd)

            #cmd=GetAsciiOnly2(cmd)

            #cmd=GetAsciiOnly(cmd)

            def Mbool(text,data):
                try:
                    for i in ['n','no','false','f']:
                        if i in text.lower():
                            return False
                    for i in ['y','yes','true','t']:
                        if i in text.lower():
                            return True
                    return None
                except Exception as e:
                    return

            #PRESET_EAN13_LEN=13
            PRESET_EAN13_LEN=detectGetOrSet(name='PRESET_EAN13_LEN',length=13)
            if PRESET_EAN13_LEN != None and len(cmd) == PRESET_EAN13_LEN:
                try:
                    EAN13=barcode.EAN13(cmd)
                    use=Prompt.__init2__(None,func=Mbool,ptext=f"{Back.dark_red_1}{Fore.white}A EAN13({cmd}) Code was Entered, use it?{Style.reset}",helpText="yes or no",data="boolean")
                    if use in [True,None]:
                        pass
                    elif use in [False,]:
                        continue
                except Exception as e:
                    msg=f'''
{Fore.dark_red_1}{Style.bold}{str(e)}{Style.reset}
{Fore.yellow}{repr(e)}{Style.reset}
{Fore.light_green}Processing Will Continue...{Style.reset}
'''
                    print(msg)
            #this will be stored in system preferences as well as an gui be made to change it
            #PRESET_UPC_LEN=12
            #PRESET_UPC_LEN=None
            PRESET_UPC_LEN=detectGetOrSet(name='PRESET_UPC_LEN',length=12)
            if PRESET_UPC_LEN != None and len(cmd) == PRESET_UPC_LEN:
                try:
                    UPCA=barcode.UPCA(cmd)
                    use=Prompt.__init2__(None,func=Mbool,ptext=f"{Back.dark_red_1}{Fore.white}len({len(cmd)})-> A UPCA({cmd}) Code was Entered, use it?{Style.reset}",helpText="[y/Y]es(will ensure full UPCA-digit), or [n/N]o(will re-prompt), or [b]/back to use current text",data="boolean_basic")
                    if use in [True,None]:
                        pass
                    elif use in [False,]:
                        continue
                except Exception as e:
                    msg=f'''
{Fore.dark_red_1}{Style.bold}{str(e)}{Style.reset}
{Fore.yellow}{repr(e)}{Style.reset}
{Fore.light_green}Processing Will Continue...{Style.reset}
'''
                    print(msg)

            PRESET_UPCA11_LEN=detectGetOrSet(name='PRESET_UPCA11_LEN',length=11)   
            if PRESET_UPCA11_LEN != None and len(cmd) == PRESET_UPCA11_LEN:
                try:
                    UPCA11=str(barcode.UPCA(cmd))
                    use=Prompt.__init2__(None,func=Mbool,ptext=f"{Back.dark_red_1}{Fore.white}len({len(cmd)})-> A UPCA({cmd}) Code was Entered, use it?{Style.reset}",helpText="[y/Y]es(will ensure full UPCA-digit), or [n/N]o(will re-prompt), or [b]/back to use current text",data="boolean_basic")
                    print(f"USED:{use}")
                    if use in [True,]:
                        cmd=UPCA11
                    elif use in [None,]:
                        pass
                    elif use in [False,]:
                        continue
                except Exception as e:
                    msg=f'''
{Fore.dark_red_1}{Style.bold}{str(e)}{Style.reset}
{Fore.yellow}{repr(e)}{Style.reset}
{Fore.light_green}Processing Will Continue...{Style.reset}
'''
                    print(msg)
            #PRESET_CODE_LEN=8
            #PRESET_CODE_LEN=None
            PRESET_CODE_LEN=detectGetOrSet(name='PRESET_CODE_LEN',length=8)
            if PRESET_CODE_LEN != None and len(cmd) == PRESET_CODE_LEN:
                try:
                    Code39=barcode.Code39(cmd,add_checksum=False)
                    use=Prompt.__init2__(None,func=Mbool,ptext=f"{Back.dark_red_1}{Fore.white}A Possible Code39({cmd}) Code was Entered, use it?{Style.reset}",helpText="[y/Y]es(will ensure full UPCA-digit), or [n/N]o(will re-prompt), or [b]/back to use current text",data="boolean_basic")
                    if use in [True,None]:
                        final_use=True
                        pass
                    elif use in [False,]:
                        continue
                except Exception as e:
                    msg=f'''
    {Fore.dark_red_1}{Style.bold}{str(e)}{Style.reset}
    {Fore.yellow}{repr(e)}{Style.reset}
    {Fore.light_green}Processing Will Continue...{Style.reset}
    '''
                    print(msg)

            postFilterMsg=f"""{Style.underline}{Fore.light_yellow}Post_Filtering_Final_Cmd('{Style.bold}{Style.res_underline}{Fore.white}{db.Entry.cfmt(None,cmd)}{Style.bold}{Fore.grey_50}{Style.underline}{Style.res_bold}{Fore.light_yellow}'){Style.res_underline}|len({len(cmd)}){Style.reset}
{Fore.grey_70}**{Fore.orange_red_1}Exclude '{db.DEFAULT_SEPARATOR_CHAR}' from {db.Entry.cfmt(None,'text')} for original input({db.Entry.rebar(None,cmd,skip_sep=True)})!{Style.reset}
{Fore.grey_85}{os.get_terminal_size().columns*'.'}{Style.reset}"""
            print(postFilterMsg)
            #this is purely for debugging
            #more will come later
            ph_age=detectGetOrSet('PH_AGE',60*60*24*7)
            ph_limit=detectGetOrSet('PH_MAXLINES',10000)
            #ph_age=5
            if not noHistory:
                db.saveHistory(cmd,ph_age,executed=func,data=data)
            if cmd.endswith("#clr") or cmd.startswith('clr#'):
                print(f"{Fore.light_magenta}Sometimes we need to {Fore.sky_blue_2}re-think our '{Fore.light_red}{cmd}{Fore.sky_blue_2}'!{Style.reset}")
                continue
            elif cmd.lower() in ["ph","prompt history",]:
                ph=db.HistoryUi()
                if ph.cmd != None:
                    cmd=ph.cmd
                else:
                    continue
            elif cmd.lower() in ["aisle map",]:
                settings=namedtuple('self',['amx','amn','max_sb'])
                settings.amx=15
                settings.amn=0
                settings.max_sb=5
                ad=MAP.generate_names(settings)
                return func(ad,data)
            elif cmd.endswith("#c2cb"):
                with db.Session(db.ENGINE) as session:
                    ncb_text=cmd.split('#c2cb')[0]
                    cb=db.ClipBoord(cbValue=ncb_text,doe=datetime.now(),ageLimit=db.ClipBoordEditor.ageLimit,defaultPaste=True)
                    results=session.query(db.ClipBoord).filter(db.ClipBoord.defaultPaste==True).all()
                    ct=len(results)
                    if ct > 0:
                        for num,r in enumerate(results):
                            r.defaultPaste=False
                            if num % 100:
                                session.commit()
                        session.commit()
                    session.add(cb)
                    session.commit()
                    continue
            elif cmd.lower() == 'colors':
                protocolors()    
            elif cmd.lower() == 'obf msg':
                Obfuscate()
            elif cmd.startswith("c2cb#"):
                with db.Session(db.ENGINE) as session:
                    ncb_text=cmd.split('c2cb#')[-1]
                    cb=db.ClipBoord(cbValue=ncb_text,doe=datetime.now(),ageLimit=db.ClipBoordEditor.ageLimit,defaultPaste=True)
                    results=session.query(db.ClipBoord).filter(db.ClipBoord.defaultPaste==True).all()
                    ct=len(results)
                    if ct > 0:
                        for num,r in enumerate(results):
                            r.defaultPaste=False
                            if num % 100:
                                session.commit()
                        session.commit()
                    session.add(cb)
                    session.commit()
                    continue
            if cmd.endswith("#c2cbe"):
                with db.Session(db.ENGINE) as session:
                    ncb_text=cmd.split('#c2cbe')[0]
                    cb=db.ClipBoord(cbValue=ncb_text,doe=datetime.now(),ageLimit=db.ClipBoordEditor.ageLimit,defaultPaste=True)
                    results=session.query(db.ClipBoord).filter(db.ClipBoord.defaultPaste==True).all()
                    ct=len(results)
                    if ct > 0:
                        for num,r in enumerate(results):
                            r.defaultPaste=False
                            if num % 100:
                                session.commit()
                        session.commit()
                    session.add(cb)
                    session.commit()
                    return func(ncb_text,data)
            elif cmd.startswith("c2cbe#"):
                with db.Session(db.ENGINE) as session:
                    ncb_text=cmd.split('c2cbe#')[-1]
                    cb=db.ClipBoord(cbValue=ncb_text,doe=datetime.now(),ageLimit=db.ClipBoordEditor.ageLimit,defaultPaste=True)
                    results=session.query(db.ClipBoord).filter(db.ClipBoord.defaultPaste==True).all()
                    ct=len(results)
                    if ct > 0:
                        for num,r in enumerate(results):
                            r.defaultPaste=False
                            if num % 100:
                                session.commit()
                        session.commit()
                    session.add(cb)
                    session.commit()
                    return func(ncb_text,data)
            elif cmd.lower() in ['rob','readline on boot','readline_on_boot']:
                with db.Session(db.ENGINE) as session:
                    READLINE_PREFERECE=session.query(db.SystemPreference).filter(db.SystemPreference.name=='readline').order_by(db.SystemPreference.dtoe.desc()).all()
                    ct=len(READLINE_PREFERECE)
                    if ct <= 0:
                        try:
                            import readline
                            sp=SystemPreference(name="readline",value_4_Json2DictString=json.dumps({"readline":True}))
                            session.add(sp)
                            session.commit()
                        except Exception as e:
                            print("Could not import Readline, you might not have it installed!")
                    else:
                        try:
                            f=None
                            for num,i in enumerate(READLINE_PREFERECE):
                                if i.default == True:
                                    f=num
                                    break
                            if f == None:
                                f=0
                            cfg=READLINE_PREFERECE[f].value_4_Json2DictString
                            if cfg =='':
                                READLINE_PREFERECE[f].value_4_Json2DictString=json.dumps({"readline":True})
                                import readline
                                session.commit()
                                session.refresh(READLINE_PREFERECE[f])
                            else:
                                try:
                                    x=json.loads(READLINE_PREFERECE[f].value_4_Json2DictString)
                                    if x.get("readline") in [True,False,None]:
                                        try:
                                            if x.get("readline") == False:
                                               READLINE_PREFERECE[f].value_4_Json2DictString=json.dumps({"readline":True})
                                               session.commit()
                                               exit("Reboot is required!") 
                                            elif x.get("readline") == True:
                                                READLINE_PREFERECE[f].value_4_Json2DictString=json.dumps({"readline":False})
                                                session.commit()
                                                exit("Reboot is required!")
                                            else:
                                                READLINE_PREFERECE[f].value_4_Json2DictString=json.dumps({"readline":True})
                                                session.commit()
                                                exit("Reboot is required!")
                                            print(e)
                                        except Exception as e:
                                            print(e)
                                    else:
                                        print("readline is off")
                                except Exception as e:
                                    try:
                                        import readline
                                        print(e)
                                    except Exception as e:
                                        print(e)
                        except Exception as e:
                            print(e)
            elif cmd.lower() in ['uniq-rcpt-id','uniq rcpt id','unique_reciept_id','urid','unique reciept id','unique-reciept-id']:
                try:
                    urid=TM.Tasks.TasksMode(parent=self,engine=db.ENGINE,init_only=True).unique_reciept_id()
                    send=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Return the {Back.black}Code({db.Entry.cfmt(None,urid)}):",helpText="send the code as input",data="boolean")
                    if send in [None,]:
                        continue
                    elif send == True:
                        return func(urid,data)
                    else:
                        print(urid)
                        continue
                except Exception as e:
                    print(e)

            elif cmd.lower() in ['ic2oc','input code to output code']:
                c=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Code to Convert For Use:",helpText="a code that may be used elsewhere in a different format",data="str")
                if c in [None,'d']:
                    continue
                else:
                    try:
                        codeZ=str(useInputAsCode(c))
                        send=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Return the {Back.black}Code({db.Entry.cfmt(None,codeZ)}):",helpText="send the code as input",data="boolean")
                        if send in [None,]:
                            continue
                        elif send == True:
                            return func(codeZ,data)
                        else:
                            print(c)
                            continue
                    except Exception as e:
                        print(e)
            elif cmd.lower() in ['c2c','calc2cmd']:
                t=TM.Tasks.TasksMode.evaluateFormula(None,fieldname="Prompt",oneShot=True)
                return func(str(t),data)
            elif cmd.lower() in ['esu',]:
                TM.Tasks.TasksMode.Lookup()
            elif cmd.lower() in ['daylogu','dlu']:
                TM.Tasks.TasksMode(parent=self,engine=db.ENGINE,init_only=True).product_history()
            elif cmd.lower() in ['neu',]:
                TM.Tasks.TasksMode(parent=self,engine=db.ENGINE,init_only=True).NewEntryMenu()
            elif cmd.lower() in ['exp',]:
                TM.Tasks.TasksMode(parent=self,engine=db.ENGINE,init_only=True).Expiration_()
            elif cmd.lower() in ['mlu',]:
                TM.Tasks.TasksMode(parent=self,engine=db.ENGINE,init_only=True).MasterLookup()
            elif cmd.lower() in ['comm']:
                CM.RxTx.RxTx()
            elif cmd.lower() in ['tsu','j','journal','jrnl']:
                TSC.TouchStampC.TouchStampC(parent=self,engine=db.ENGINE)
            elif cmd.lower() in ['tvu','tag data']:
                pc.run(engine=db.ENGINE)
            elif cmd.lower() in ['c','calc']:
                #if len(inspect.stack(0)) <= 6:
                TM.Tasks.TasksMode.evaluateFormula(None,fieldname="Prompt")
                continue
                #else:
                #print(f"{Fore.light_green}Since {Fore.light_yellow}You{Fore.light_green} are already using the {Fore.light_red}Calculator{Fore.light_green}, I am refusing to recurse{Fore.light_steel_blue}(){Fore.light_green}!")
            elif cmd.lower() in ['q','qm','q?','quit menu','quit al la carte']:
                Prompt.QuitMenu(Prompt)
            elif cmd.lower() in ['cb','clipboard']:
                ed=db.ClipBoordEditor(self)
                continue
            elif cmd.lower() in ['#b',]:
                with db.Session(db.ENGINE) as session:
                    next_barcode=session.query(db.SystemPreference).filter(db.SystemPreference.name=='next_barcode').all()
                    ct=len(next_barcode)
                    if ct > 0:
                        if next_barcode[0]:
                            setattr(next_barcode[0],'value_4_Json2DictString',str(json.dumps({'next_barcode':True})))
                            session.commit()
                            session.refresh(next_barcode[0])
                    else:
                        next_barcode=db.SystemPreference(name="next_barcode",value_4_Json2DictString=json.dumps({'next_barcode':True}))
                        session.add(next_barcode)
                        session.commit()
                        session.refresh(next_barcode)
                lastTime=db.detectGetOrSet("PromptLastDTasFloat",datetime.now().timestamp(),setValue=True)
                return
            elif cmd.lower() in ['cse','clear selected entry']:
                code=Prompt.__init2__(None,func=FormBuilderMkText,ptext="what do you wish to clear?",helpText="barcode|code|name",data="string")
                if code in [None,]:
                    continue
                with Session(db.ENGINE) as session:
                    query=session.query(db.Entry).filter(db.Entry.InList==True,or_(db.Entry.Code.icontains(code),db.Entry.Barcode.icontains(code),db.Entry.Name.icontains(code)))
                    results=query.all()
                    ct=len(results)
                    if ct < 1:
                        print("No Results to Clear!")
                        continue
                    helpText=[]
                    for num,i in enumerate(results):
                        msg=f"{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct} -> {Fore.orange_red_1}{i.seeShort()}{Style.reset}"
                        helpText.append(msg)
                    helpText='\n'.join(helpText)
                    print(helpText)
                    selected=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Which index(es):",helpText=helpText,data="list")
                    try:
                        if selected in [None,'d',[]]:
                            continue
                        for i in selected:
                            try:
                                index=int(i)
                                obj=results[index]
                                update={
                                    'InList':False,
                                    'ListQty':0,
                                    'Shelf':0,
                                    'Note':'',
                                    'BackRoom':0,
                                    'Distress':0,
                                    'Display_1':0,
                                    'Display_2':0,
                                    'Display_3':0,
                                    'Display_4':0,
                                    'Display_5':0,
                                    'Display_6':0,
                                    'Stock_Total':0,
                                    'CaseID_BR':'',
                                    'CaseID_LD':'',
                                    'CaseID_6W':'',
                                    'SBX_WTR_DSPLY':0,
                                    'SBX_CHP_DSPLY':0,
                                    'SBX_WTR_KLR':0,
                                    'FLRL_CHP_DSPLY':0,
                                    'FLRL_WTR_DSPLY':0,
                                    'WD_DSPLY':0,
                                    'CHKSTND_SPLY':0,
                                    }
                                for i in update:
                                    setattr(obj,i,update[i])
                                session.commit()
                            except Exception as ee:
                                print(ee)
                    except Exception as e:
                        print(e)
            elif cmd.lower() in ['cslf','clear selected location field']:
                with db.Session(db.ENGINE) as session:
                    cta=len(db.LOCATION_FIELDS)
                    helpText=[]
                    for num,i in enumerate(db.LOCATION_FIELDS):
                        msg=f"{Fore.light_steel_blue}{num}/{Fore.slate_blue_1}{num+1}{Fore.orange_red_1} of {cta} ->{Fore.light_green}{i}{Style.reset}"
                        helpText.append(msg)
                    helpText="\n".join(helpText)
                    while True:
                        try:
                            print(helpText)
                            selected=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What Location Fields do you wish to clear only(a list if fine)?",helpText=helpText,data="list")
                            if selected in [None,'d']:
                                return
                            else:
                                upd8={}
                                for i in selected:
                                    try:
                                        index=int(i)
                                        upd8[db.LOCATION_FIELDS[index]]=0
                                    except Exception as ee:
                                        print(ee)
                                session.query(db.Entry).update(upd8)
                                session.commit()
                                break
                        except Exception as e:
                            print(e)
            elif cmd.lower() in ['mksl','make shopping list','p-slq','prompt slq','set list qty','slqp','slq-p']:
                TM.Tasks.TasksMode(parent=self,engine=db.ENGINE,init_only=True).setFieldInList("ListQty",load=True,only_select_qty=True)
            elif cmd.lower() in ['pc','prec calc',]:
                resultant=TM.Tasks.TasksMode(parent=self,engine=db.ENGINE,init_only=True).prec_calc()
                return func(resultant,data)
            elif cmd.lower() in ['b','back']:
                lastTime=db.detectGetOrSet("PromptLastDTasFloat",datetime.now().timestamp(),setValue=True)
                return
            elif cmd.lower() in ['h','help']:
                print(helpText)
                extra=f'''{Fore.orange_red_1}Dimension Fields {Fore.light_steel_blue}are fields that tell how much space the product is going to take up using the the product itself as the unit of measure
    {Fore.orange_red_1}Location Fields{Fore.light_steel_blue} are fields where the item resides at, will reside at, is coming from etc...
    {Fore.orange_red_1}Count Fields{Fore.light_steel_blue} are fields that define max values that relate to how much goes to the shelf,comes via the Load, how much comes in a Pallet, or Case{Style.reset}

 {Fore.orange_red_1}{Style.underline}Prompt Level CMDS(Access from anywhere But {Fore.light_red}Root){Style.reset}
 {Fore.light_yellow}Don't Use {Fore.grey_70}**{Style.reset}
 {Fore.grey_70}**{Fore.light_green}sft{Fore.light_red}u{Fore.light_steel_blue} - search for text across whole DB and return it as input{Style.reset}
 {Fore.grey_70}**{Fore.light_green}ne{Fore.light_red}u{Fore.light_steel_blue} - create a new entry menu{Style.reset}
 {Fore.grey_70}**{Fore.light_green}bld{Fore.light_red}ls{Fore.light_steel_blue} - list all items with InList==True and has a location value above {Fore.light_red}0{Style.reset}
 {Fore.grey_70}**{Fore.light_green}s{Fore.light_red}bld{Fore.light_steel_blue} - search with barcode in all items with InList==True and has a location value above {Fore.light_red}0{Style.reset}
 {Fore.grey_70}**{Fore.light_green}"bldlse","builde","buildlse","build list export ","bld ls exp",'elsbld','export list build','exp ls bld','ebld'{Fore.light_steel_blue} - same as versions without export, but dumps list to {Path(Prompt.bld_file).absolute()}{Style.reset}
 {Fore.grey_70}**{Fore.light_green}'esbld','export search build','export_search_build','exp scan build','exp_scan_bld'{Fore.light_steel_blue} - same as versions without export, but dumps list to {Path(Prompt.bld_file).absolute()}{Style.reset}
 {Fore.orange_red_1}**{Fore.grey_50}Add a {Fore.light_magenta}-{Fore.grey_50} to the end of each cmd to include negatives, but ignore '0' and 'None' if spaces are included then put a space before the last -, elsewise put a it immediately behind the cmd to to enable this feature{Style.reset}
 {Fore.grey_70}**{Fore.light_green}es{Fore.light_red}u{Fore.light_steel_blue} - search entry menu{Style.reset}
 {Fore.grey_70}**{Fore.light_green}tv{Fore.light_red}u{Fore.light_steel_blue} - show tag data info{Style.reset}
 {Fore.grey_70}**{Fore.light_green}dl{Fore.light_red}u{Fore.light_green},daylog{Fore.light_red}u{Fore.light_steel_blue} - Entry History System{Style.reset}
 {Fore.grey_70}**{Fore.light_green}mlu{Fore.light_steel_blue} - master lookup search for something in {SEARCH_TABLES}{Style.reset}
 {Fore.grey_70}**{Fore.light_green}exp{Fore.light_steel_blue} - product expiration menu{Style.reset}
 {Fore.grey_70}**{Fore.light_green}comm{Fore.light_steel_blue} - send an email message with gmail{Style.reset}
 {Fore.grey_70}**{Fore.light_sea_green}'crbc',"checked random barcode"{Fore.light_yellow}- generate a random, but non-local-system existant barcode for input{Style.reset}
 {Fore.grey_70}**{Fore.light_sea_green}'bcd-gen','bcd-img'{Fore.light_yellow}- generate a custom barcode img from input data possible output is selected from {barcode.PROVIDED_BARCODES}{Style.reset}
 {Fore.grey_70}**{Fore.light_sea_green}'qr-gen','qr-img'{Fore.light_yellow}- generate a custom barcode img from input data possible output is selected{Style.reset}
 {Fore.grey_70}**{Fore.light_red}u{Fore.light_steel_blue} is for {Fore.light_red}Universally{Fore.light_steel_blue} accessible where this menu is{Style.reset}
 {Fore.grey_70}**{Style.bold}{Fore.spring_green_3a}ts{Fore.light_red}u{Fore.spring_green_3a},j,journal,jrnl{Style.reset} -{Fore.light_steel_blue} Access TouchScan Journal from this prompt{Style.reset}
 {Fore.grey_70}**{Fore.light_red}The Current CMD type/scanned is written to {Fore.light_yellow}{scanout}{Fore.light_red}, so if you are stuck without traditional keyboard output, you can still utilize the Text file as a ClipBoard{Style.reset}
 {Fore.grey_70}**{Fore.light_steel_blue}obf msg {Fore.spring_green_3a}encrypted msgs via {db.detectGetOrSet("OBFUSCATED MSG FILE",value="MSG.txt",setValue=False,literal=True)} and Prompt Input{Style.reset}
 {Fore.grey_70}**{Fore.light_salmon_1}Start a line with {Fore.cyan}#ml#{Fore.light_salmon_1} followed by text, where {Fore.light_red}<ENTER>/<RETURN>{Fore.light_salmon_1} will allow for additional lines of input until you end the multi-line input with {Fore.cyan}#ml#{Style.reset}
 {Fore.light_sea_green}Code=="UNASSIGNED_TO_NEW_ITEM" --> {Fore.light_steel_blue} `neu;set field;#select indexes for Code,Name,Price,CaseCount from prompt; type "UNASSIGNED_TO_NEW_ITEM" and hit <ENTER>/<RETURN>;#follow the prompts to fill the Entry Data for those Fields`{Style.reset}
 {Fore.grey_70}**{Fore.light_green}'upcify','format upc','fupc'{Fore.light_steel_blue} Format input text to look '{db.Entry.rebar(None,"TESTTEXTUPCA")}{Style.reset}'
 {Fore.grey_70}**{Fore.light_green}'codify','format code','fcode'{Fore.light_steel_blue} Format input text to look '{db.Entry.cfmt(None,"TESTTEXT")}{Style.reset}'
 {Fore.grey_70}**{Fore.light_green}'upcify str','upcify.str','upcify-str','format upc str','fupcs'{Fore.light_steel_blue} Format input text to look and use formatted text as input-text'{db.Entry.rebar(None,"TESTTEXTUPCA")}{Style.reset}'
 {Fore.grey_70}**{Fore.light_green}'codify str','codify.str','codify-str','format code str','fcodes'{Fore.light_steel_blue} Format input text to look and use formatted text as input-text'{db.Entry.cfmt(None,"TESTTEXT")}{Style.reset}'
 {Fore.grey_70}**{Fore.light_green}'quick price','qprc','price'{Fore.light_steel_blue} Calculate price information using user provided data for an arbitrary product who Data is not in the Entry table{Style.reset}
 {Fore.grey_70}**{Fore.light_green}'mksl','make shopping list','p-slq','prompt slq','set list qty','slqp','slq-p'{Fore.light_steel_blue} make a list using {Fore.green_3a}slq{Fore.light_steel_blue} from {Fore.orange_red_1}Tasks.{Fore.light_red}TasksMode{Style.reset}
 {Fore.grey_70}**{Fore.light_green}'ic2oc','input code to output code'{Fore.light_steel_blue} Convert an input code to its neighboring format for view or input use{Style.reset}
 {Fore.grey_70}**{Fore.light_green}'uniq-rcpt-id','uniq rcpt id','unique_reciept_id','urid','unique reciept id','unique-reciept-id'{Fore.light_steel_blue} Generate Relavent Receipt Id to be searchable in DayLogger{Style.reset}
 {Fore.grey_70}**{Fore.light_green}'cslf','clear selected location field'{Fore.light_steel_blue} set Entry's with selected field's to Zero, but do not do change InList==False{Style.reset}
 {Fore.grey_70}**{Fore.light_green}'cse','clear selected entry'{Fore.light_steel_blue} clear selected entry{Style.reset}
{Fore.grey_70}**{Fore.light_green}'fmbh','formbuilder help','form helptext'{Fore.light_steel_blue} print formbuilder helptext{Style.reset}
'''
                print(extra)
                continue
            elif cmd.lower() in ['known','known devices','known dev','knwn dev']:
                disp=KNOWN_DEVICES
                disp.append('')
                disp=list(reversed(disp))
                dText='\n\t- '.join(disp)

                kscan_disp=KNOWN_SCANNERS
                kscan_disp.append('')
                kscan_disp=list(reversed(kscan_disp))
                kscan='\n\t- '.join(kscan_disp)
                try:
                    hline='.'*os.get_terminal_size().columns
                except Exception as e:
                    hline=20
                msg=f"""
{Fore.medium_purple_3b}Known Cellar Devices that can use this Software{Style.reset}
{Fore.medium_purple_3b}{hline}{Style.reset}
{Fore.medium_violet_red}{dText}{Style.reset}

{Fore.light_yellow}The Recommended Scanners, currently
(as this code was writtern around them) are:
{Fore.dark_goldenrod}{kscan}{Style.reset}
{Style.bold}{Fore.light_green}Scanner Notes{Style.reset}
{hline}
{Fore.light_magenta}If You can add a suffix/prefix to 
your scanners output, use {Fore.cyan}{hw_delim}{Fore.light_magenta} as the prefix 
and suffix, to allow for additional code error correction, 
where the scanner might insert a newline right before the
checksum{Style.reset}

{Fore.dark_sea_green_5a}if you encapsulate your commands 
with '{Fore.cyan}{hw_delim}{Fore.dark_sea_green_5a}', like '{Fore.cyan}{hw_delim}{Fore.dark_sea_green_5a}ls Shelf{Fore.cyan}{hw_delim}{Fore.dark_sea_green_5a}' 
you can spread your command over several returns/newlines, 
which will result in a cmd of 'ls Shelf'{Style.reset}
                """
                print(msg)
            elif cmd in ['upcify','format upc','fupc']:
                def mkT(text,data):
                    return text
                code=Prompt.__init2__(None,func=mkT,ptext="Text/Data: ",helpText=f"Format input text to look '{db.Entry.rebar(None,'TESTTEXTUPCA')}'",data='')
                if code in [None,]:
                    end=True
                    break
                elif code in ['d',]:
                    continue
                resultant=db.Entry.rebar(None,code)
                print(resultant)
            elif cmd in ['codify','format code','fcode']:
                def mkT(text,data):
                    return text
                code=Prompt.__init2__(None,func=mkT,ptext="Text/Data: ",helpText=f"Format input text to look '{db.Entry.cfmt(None,'TESTTEXT')}'",data='')
                if code in [None,]:
                    end=True
                    break
                elif code in ['d',]:
                    continue
                resultant=db.Entry.cfmt(None,code)
                print(resultant)
            elif cmd in ['upcify str','upcify.str','upcify-str','format upc str','fupcs']:
                def mkT(text,data):
                    return text
                code=Prompt.__init2__(None,func=mkT,ptext="Text/Data: ",helpText=f"Format input text to look '{db.Entry.rebar(None,'TESTTEXTUPCA')}'",data='')
                if code in [None,]:
                    end=True
                    break
                elif code in ['d',]:
                    continue
                resultant=db.Entry.rebar(None,code)
                print(resultant)
                return func(resultant,data)
            elif cmd.lower() in ['fmbh','formbuilder help','form helptext']:
                FormBuilderHelpText()
                continue
            elif cmd in ['codify str','codify.str','codify-str','format code str','fcodes']:
                def mkT(text,data):
                    return text
                code=Prompt.__init2__(None,func=mkT,ptext="Text/Data: ",helpText=f"Format input text to look '{db.Entry.cfmt(None,'TESTTEXT')}'",data='')
                if code in [None,]:
                    end=True
                    break
                elif code in ['d',]:
                    continue
                resultant=db.Entry.cfmt(None,code)
                print(resultant)
                return func(resultant,data)
            elif cmd.lower() in ['bcd-gen','bcd-img']:
                TM.Tasks.TasksMode(parent=self,engine=db.ENGINE,init_only=True).bcd_img()
            elif cmd.lower() in ['qr-gen','qr-img']:
                TM.Tasks.TasksMode(parent=self,engine=db.ENGINE,init_only=True).qr_img()
            elif cmd.lower() in ['crbc',"checked random barcode"]:
                with db.Session(db.ENGINE) as session:
                    while True:
                        try:
                            code=''.join([str(random.randint(0,9)) for i in ' '*11])
                            UPCAcode=barcode.UPCA(code)
                            check=session.query(db.Entry).filter(or_(db.Entry.Barcode==str(UPCAcode),db.Entry.Barcode.icontains(str(UPCAcode)))).first()
                            if check != None:
                                continue
                            print(UPCAcode)
                            return func(str(UPCAcode),data)
                        except Exception as e:
                            print(e)
            elif cmd.lower() in ['h+','help+']:
                print(f'''{Fore.grey_50}If a Number in a formula is like '1*12345678*1', use '1*12345678.0*1' to get around regex for '*' values; {Fore.grey_70}{Style.bold}If An Issue Arises!{Style.reset}
                {Fore.grey_50}This is due to the {Fore.light_green}Start/{Fore.light_red}Stop{Fore.grey_50} Characters for Code39 ({Fore.grey_70}*{Fore.grey_50}) being filtered with {Fore.light_yellow}Regex
{Fore.light_magenta}rob=turn readline on/off at start
{Fore.light_steel_blue}if 'b' returns to previous menu, try '#b' to return to barcode input, in ListMode@$LOCATION_FIELD, 'e' does the same{Style.reset}''')
                continue
            elif cmd.lower() in ['i','info']:
                msg_fmbtxt=f"""Prompt's where FormBuilderMkText is used keywords like 
today = today
tomorrow = today+24h
yesterday = today-24h
next month = today+30d
next year = today+365d
next week = today+7d
last week = today-7d
last year = today-365d
last month = today-30d
"""
                print(msg_fmbtxt)
                l=Path("Holidays.txt")
                if not l.exists():
                    l=Path(__file__).parent.parent/Path("Holidays.txt")
                print(l)
                with open(l,"r") as msgr:
                    for num,line in enumerate(msgr.readlines()):
                        if num % 2 == 0:
                            color=Fore.light_yellow
                        else:
                            color=Fore.sea_green_2

                        msg=f"""{Fore.magenta}Line {Fore.cyan}{num}/{Fore.light_steel_blue}{num+1} - {color}{line}{Style.reset}"""
                        print(msg)
                print(f"{Fore.orange_red_1}You can override the default Holidays.txt by placing a file called 'Holidays.txt' in your current pwd{Style.reset}")
                print(f"{Fore.light_cyan}Running on Android:{Fore.slate_blue_1}{db.onAndroid()}{Style.reset}")
                print(f"{Fore.light_cyan}Running on {Fore.slate_blue_1}{platform.system()} {Fore.light_cyan}Rel:{Fore.orange_red_1}{platform.release()}{Style.reset}")
                print(helpText2)
                Prompt.passwordfile(None,)
                print(Prompt.resrc(Prompt))
                sales_tax_msg=f'''
{Fore.light_green}{Style.underline}Tax Formulas{Style.reset}
{Fore.light_blue}Price is what is stated on the reciept or shelf tag without {Fore.light_red}Tax{Fore.cyan} and CRV applied.{Style.reset}
{Fore.cyan}CRV is for beverages, where under 24 Fluid Ounces, the CRV is {Fore.light_cyan}$0.05{Fore.cyan} and above 24 Fluid ounces is {Fore.light_cyan}$0.10,{Fore.light_steel_blue}if multiple bottles are in a single purchased case, then the CRV is applied to each contained within the sold/purchased case{Style.reset}
{Fore.cyan}CRV={Fore.light_cyan}({Fore.light_green}CRV_4_SIZE*{Fore.green_yellow}QTY_OF_cONTAINERS_IN_CASE{Fore.light_cyan}){Style.reset}
{Fore.light_red}Total=(({Fore.cyan}CRV+{Fore.light_blue}Price)*{Fore.light_magenta}(Sales Tax Rate(0.0925)))+{Fore.light_blue}Price{Style.reset}
{Fore.light_red}Tax=(({Fore.cyan}CRV+{Fore.light_blue}Price)*{Fore.light_magenta}(Sales Tax Rate(0.0925))){Style.reset}
                '''
                print(sales_tax_msg)
                continue
            elif cmd.lower() in ['sftu','search for text universal',]:
                result=global_search_for_text()
                return func(result,data)
            elif cmd.lower() in ["bldls","build","buildls","build list","bld ls",'lsbld','list build','ls bld','bld']:
                with db.Session(db.ENGINE) as session:
                    results_query=session.query(db.Entry).filter(db.Entry.InList==True)
                    location_fields=["Shelf","BackRoom","Display_1","Display_2","Display_3","Display_4","Display_5","Display_6","ListQty","SBX_WTR_DSPLY","SBX_CHP_DSPLY","SBX_WTR_KLR","FLRL_CHP_DSPLY","FLRL_WTR_DSPLY","WD_DSPLY","CHKSTND_SPLY","Distress"]
                    z=Prompt.mkfield_list(None,location_fields)
                    if z in [[],None]:
                        z=location_fields
                    location_fields=z
                    tmp=[]
                    for f in location_fields:
                        tmp.append(or_(getattr(db.Entry,f)>=0.0001))
                    results_query=results_query.filter(or_(*tmp))
                    results=results_query.all()
                    ct=len(results)
                    if ct < 1:
                        print(f"{Fore.light_steel_blue}Nothing in {Fore.slate_blue_1}Bld{Fore.light_red}LS!{Style.reset}")
                        continue
                    ROUNDTO=int(db.detectGetOrSet("lsbld ROUNDTO default",3,setValue=False,literal=True))
                    master_total=0
                    master_total_crv=0
                    master_total_tax=0
                    master_total_tax_crv=0

                    for num,i in enumerate(results):
                        msg=f'{"*"*os.get_terminal_size().columns}\n{Fore.light_green}{num}{Fore.light_magenta}/{Fore.orange_3}{num+1} of {Fore.light_red}{ct}[{Fore.dark_slate_gray_1}EID{Fore.orange_3}]{Fore.dark_violet_1b}{i.EntryId}{Style.reset} |-| {Fore.light_yellow}{i.Name}|{Fore.light_salmon_1}[{Fore.light_red}BCD]{i.rebar()}{Fore.medium_violet_red}|[{Fore.light_red}CD{Fore.medium_violet_red}]{i.cfmt(i.Code)} {Style.reset}|-| '
                        colormapped=[
                        Fore.deep_sky_blue_4c,
                        Fore.spring_green_4,
                        Fore.turquoise_4,
                        Fore.dark_cyan,
                        Fore.deep_sky_blue_2,
                        Fore.spring_green_2a,
                        Fore.medium_spring_green,
                        Fore.steel_blue,
                        Fore.cadet_blue_1,
                        Fore.aquamarine_3,
                        Fore.purple_1a,
                        Fore.medium_purple_3a,
                        Fore.slate_blue_1,
                        Fore.light_slate_grey,
                        Fore.dark_olive_green_3a,
                        Fore.deep_pink_4c,
                        Fore.orange_3,
                        ]
                        total=0
                        crv=0
                        tax=0
                        tax_crv=0
                        i.Tax=round(i.Tax,ROUNDTO)
                        i.CRV=round(i.CRV,ROUNDTO)
                        i.Price=round(i.Price,ROUNDTO)
                        session.commit()
                        for n2,f in enumerate(location_fields):
                            try:
                                if getattr(i,f) > 0:
                                    total+=getattr(i,f)
                            except Exception as e:
                                print(e)
                        for n2,f in enumerate(location_fields):
                            if getattr(i,f) > 0:
                                msg2=f'{colormapped[n2]}{f} = {round(getattr(i,f),ROUNDTO)}{Style.reset}'
                                if n2 < len(location_fields):
                                    msg2+=","
                                msg+=msg2
                        master_total+=total*round(i.Price,ROUNDTO)

                        crv+=(round(i.CRV,ROUNDTO)*total)
                        tax+=(round(i.Tax,ROUNDTO)*total)
                        if tax == 0 and crv > 0:
                            tax_crv=(round(i.CRV,ROUNDTO)*total)
                        else:
                            tax_crv+=((round(i.Tax,ROUNDTO)*total)+(round(i.CRV,ROUNDTO)*total))
                        master_total_tax+=tax
                        master_total_crv+=crv
                        master_total_tax_crv+=tax_crv
                        tax_crv=round(tax_crv,ROUNDTO)
                        try:
                            super_total=(round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)/getSuperTotal(results,location_fields,colormapped)['final total'],ROUNDTO))*100
                        except Exception as e:
                            p1=round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO))
                            p2=getSuperTotal(results,location_fields,colormapped)['final total']
                            print(e)
                            print(p1,"p1")
                            print(p2,"p2")
                            super_total=0

                        msg+=f"""{Fore.light_magenta} |-|{Fore.light_green} Total = {Fore.light_sea_green}{round(total,ROUNDTO)}
{Fore.light_magenta}Price({i.Price}){Fore.medium_violet_red}*{Fore.light_slate_blue}Total({round(total,ROUNDTO)}):{round(i.Price*total,ROUNDTO)}
{Fore.grey_70}+CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TotalCRV({crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+crv,ROUNDTO)})
{Fore.grey_70}+Tax({i.Tax}) w/o CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxNoCRVTotal({tax})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax,ROUNDTO)})
{Fore.grey_70}+Tax({i.Tax}) w/ CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxCRVTotal({tax_crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)})
{Fore.medium_violet_red}PercentOfTotal({round(super_total,ROUNDTO)}) of Total({getSuperTotal(results,location_fields,colormapped)['final total']})
{'*'*os.get_terminal_size().columns}{Style.reset}"""
                        print(msg)
                    master_total=round(master_total,ROUNDTO)
                    master_total_crv=round(master_total_crv,ROUNDTO)
                    master_total_tax=round(master_total_tax,ROUNDTO)
                    master_total_tax_crv=round(master_total_tax_crv,ROUNDTO)
                    msg=f"""{Fore.light_green}Total Product Value:{Fore.slate_blue_1}{round(master_total,ROUNDTO)}
{Fore.light_green}Total Product Value w/CRV({master_total_crv}):{Fore.slate_blue_1}{round(master_total_crv+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/o CRV({master_total_tax}):{Fore.slate_blue_1}{round(master_total_tax+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/ CRV({master_total_tax_crv}):{Fore.slate_blue_1}{round(master_total_tax_crv+master_total,ROUNDTO)}
                    {Style.reset}"""
                    print(msg)
            elif cmd.lower() in ['quick price','qprc','price']:
                t=TM.Tasks.TasksMode.pricing(None)
                if t is not None:
                    return func(str(t),data)
            elif cmd.lower() in ["bldlse","builde","buildlse","build list export ","bld ls exp",'elsbld','export list build','exp ls bld','ebld']:
                msg=''
                db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file,clear_only=True)
                with db.Session(db.ENGINE) as session:
                    results_query=session.query(db.Entry).filter(db.Entry.InList==True)
                    location_fields=["Shelf","BackRoom","Display_1","Display_2","Display_3","Display_4","Display_5","Display_6","ListQty","SBX_WTR_DSPLY","SBX_CHP_DSPLY","SBX_WTR_KLR","FLRL_CHP_DSPLY","FLRL_WTR_DSPLY","WD_DSPLY","CHKSTND_SPLY","Distress"]
                    z=Prompt.mkfield_list(None,location_fields)
                    if z in [[],None]:
                        z=location_fields
                    location_fields=z
                    tmp=[]
                    for f in location_fields:
                        tmp.append(or_(getattr(db.Entry,f)>=0.0001))
                    results_query=results_query.filter(or_(*tmp))
                    results=results_query.all()
                    ct=len(results)
                    if ct < 1:
                        msg=f"{Fore.light_steel_blue}Nothing in {Fore.slate_blue_1}Bld{Fore.light_red}LS!{Style.reset}"
                        db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file)
                        print(msg)
                        continue
                    #start
                    ROUNDTO=int(db.detectGetOrSet("lsbld ROUNDTO default",3,setValue=False,literal=True))
                    master_total=0
                    master_total_crv=0
                    master_total_tax=0
                    master_total_tax_crv=0

                    for num,i in enumerate(results):
                        msg=f'{"*"*os.get_terminal_size().columns}\n{Fore.light_green}{num}{Fore.light_magenta}/{Fore.orange_3}{num+1} of {Fore.light_red}{ct}[{Fore.dark_slate_gray_1}EID{Fore.orange_3}]{Fore.dark_violet_1b}{i.EntryId}{Style.reset} |-| {Fore.light_yellow}{i.Name}|{Fore.light_salmon_1}[{Fore.light_red}BCD]{i.rebar()}{Fore.medium_violet_red}|[{Fore.light_red}CD{Fore.medium_violet_red}]{i.cfmt(i.Code)} {Style.reset}|-| '
                        colormapped=[
                        Fore.deep_sky_blue_4c,
                        Fore.spring_green_4,
                        Fore.turquoise_4,
                        Fore.dark_cyan,
                        Fore.deep_sky_blue_2,
                        Fore.spring_green_2a,
                        Fore.medium_spring_green,
                        Fore.steel_blue,
                        Fore.cadet_blue_1,
                        Fore.aquamarine_3,
                        Fore.purple_1a,
                        Fore.medium_purple_3a,
                        Fore.slate_blue_1,
                        Fore.light_slate_grey,
                        Fore.dark_olive_green_3a,
                        Fore.deep_pink_4c,
                        Fore.orange_3,
                        ]
                        total=0
                        crv=0
                        tax=0
                        tax_crv=0
                        i.Tax=round(i.Tax,ROUNDTO)
                        i.CRV=round(i.CRV,ROUNDTO)
                        i.Price=round(i.Price,ROUNDTO)
                        session.commit()
                        for n2,f in enumerate(location_fields):
                            try:
                                if getattr(i,f) > 0:
                                    total+=getattr(i,f)
                            except Exception as e:
                                print(e)
                        for n2,f in enumerate(location_fields):
                            if getattr(i,f) > 0:
                                msg2=f'{colormapped[n2]}{f} = {round(getattr(i,f),ROUNDTO)}{Style.reset}'
                                if n2 < len(location_fields):
                                    msg2+=","
                                msg+=msg2
                        master_total+=total*round(i.Price,ROUNDTO)

                        crv+=(round(i.CRV,ROUNDTO)*total)
                        tax+=(round(i.Tax,ROUNDTO)*total)
                        if tax == 0 and crv > 0:
                            tax_crv=(round(i.CRV,ROUNDTO)*total)
                        else:
                            tax_crv+=((round(i.Tax,ROUNDTO)*total)+(round(i.CRV,ROUNDTO)*total))
                        master_total_tax+=tax
                        master_total_crv+=crv
                        master_total_tax_crv+=tax_crv
                        tax_crv=round(tax_crv,ROUNDTO)
                        try:
                            super_total=(round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)/getSuperTotal(results,location_fields,colormapped)['final total'],ROUNDTO))*100
                        except Exception as e:
                            p1=round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO))
                            p2=getSuperTotal(results,location_fields,colormapped)['final total']
                            print(e)
                            print(p1,"p1")
                            print(p2,"p2")
                            super_total=0
                        msg+=f"""{Fore.light_magenta} |-|{Fore.light_green} Total = {Fore.light_sea_green}{round(total,ROUNDTO)}
{Fore.light_magenta}Price({i.Price}){Fore.medium_violet_red}*{Fore.light_slate_blue}Total({round(total,ROUNDTO)}):{round(i.Price*total,ROUNDTO)}
{Fore.grey_70}+CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TotalCRV({crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(total*i.Price,ROUNDTO)+crv})
{Fore.grey_70}+Tax({i.Tax}) w/o CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxNoCRVTotal({tax})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax,ROUNDTO)})
{Fore.grey_70}+Tax({i.Tax}) w/ CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxCRVTotal({tax_crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)})
{Fore.medium_violet_red}PercentOfTotal({round(super_total,ROUNDTO)}) of Total({getSuperTotal(results,location_fields,colormapped)['final total']})
{'*'*os.get_terminal_size().columns}{Style.reset}"""
                        db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file)
                        print(msg)
                    master_total=round(master_total,ROUNDTO)
                    master_total_crv=round(master_total_crv,ROUNDTO)
                    master_total_tax=round(master_total_tax,ROUNDTO)
                    master_total_tax_crv=round(master_total_tax_crv,ROUNDTO)
                    msg=f"""{Fore.light_green}Total Product Value:{Fore.slate_blue_1}{round(master_total,ROUNDTO)}
{Fore.light_green}Total Product Value w/CRV({master_total_crv}):{Fore.slate_blue_1}{round(master_total_crv+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/o CRV({master_total_tax}):{Fore.slate_blue_1}{round(master_total_tax+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/ CRV({master_total_tax_crv}):{Fore.slate_blue_1}{round(master_total_tax_crv+master_total,ROUNDTO)}
                    {Style.reset}"""
                    db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file)
                    print(msg)
            elif cmd.lower() in ['sbld','search build','search_build','scan build','scan_bld']:
                end=False
                while not end:
                    with db.Session(db.ENGINE) as session:
                        def mkT(text,data):
                            return text
                        code=Prompt.__init2__(None,func=mkT,ptext="Code|Barcode|Name: ",helpText="find by code,barcode,name",data='')
                        if code in [None,]:
                            end=True
                            break
                        elif code in ['d',]:
                            continue
                            
                        results_query=session.query(db.Entry).filter(db.Entry.InList==True)
                        results_query=results_query.filter(
                            db.or_(
                                db.Entry.Code==code,
                                db.Entry.Barcode==code,
                                db.Entry.Barcode.icontains(code),
                                db.Entry.Code.icontains(code),
                                db.Entry.Name.icontains(code)
                                )
                            )
                        location_fields=["Shelf","BackRoom","Display_1","Display_2","Display_3","Display_4","Display_5","Display_6","ListQty","SBX_WTR_DSPLY","SBX_CHP_DSPLY","SBX_WTR_KLR","FLRL_CHP_DSPLY","FLRL_WTR_DSPLY","WD_DSPLY","CHKSTND_SPLY","Distress"]
                        z=Prompt.mkfield_list(None,location_fields)
                        if z in [[],None]:
                            z=location_fields
                        location_fields=z
                        tmp=[]
                        for f in location_fields:
                            tmp.append(or_(getattr(db.Entry,f)>=0.0001))
                        results_query=results_query.filter(or_(*tmp))
                        results=results_query.all()
                        ct=len(results)
                        if ct < 1:
                            print(f"{Fore.light_steel_blue}Nothing in {Fore.slate_blue_1}Bld{Fore.light_red}LS!{Style.reset}")
                            continue
                    
                    ROUNDTO=int(db.detectGetOrSet("lsbld ROUNDTO default",3,set_value=False,literal=True))
                    #ROUNDTO=int(db.detectGetOrSet("lsbld ROUNDTO default",3,setValue=False,literal=True))
                    master_total=0
                    master_total_crv=0
                    master_total_tax=0
                    master_total_tax_crv=0

                    for num,i in enumerate(results):
                        msg=f'{"*"*os.get_terminal_size().columns}\n{Fore.light_green}{num}{Fore.light_magenta}/{Fore.orange_3}{num+1} of {Fore.light_red}{ct}[{Fore.dark_slate_gray_1}EID{Fore.orange_3}]{Fore.dark_violet_1b}{i.EntryId}{Style.reset} |-| {Fore.light_yellow}{i.Name}|{Fore.light_salmon_1}[{Fore.light_red}BCD]{i.rebar()}{Fore.medium_violet_red}|[{Fore.light_red}CD{Fore.medium_violet_red}]{i.cfmt(i.Code)} {Style.reset}|-| '
                        colormapped=[
                        Fore.deep_sky_blue_4c,
                        Fore.spring_green_4,
                        Fore.turquoise_4,
                        Fore.dark_cyan,
                        Fore.deep_sky_blue_2,
                        Fore.spring_green_2a,
                        Fore.medium_spring_green,
                        Fore.steel_blue,
                        Fore.cadet_blue_1,
                        Fore.aquamarine_3,
                        Fore.purple_1a,
                        Fore.medium_purple_3a,
                        Fore.slate_blue_1,
                        Fore.light_slate_grey,
                        Fore.dark_olive_green_3a,
                        Fore.deep_pink_4c,
                        Fore.orange_3,
                        ]
                        total=0
                        crv=0
                        tax=0
                        tax_crv=0
                        i.Tax=round(i.Tax,ROUNDTO)
                        i.CRV=round(i.CRV,ROUNDTO)
                        i.Price=round(i.Price,ROUNDTO)
                        session.commit()
                        for n2,f in enumerate(location_fields):
                            try:
                                if getattr(i,f) > 0:
                                    total+=getattr(i,f)
                            except Exception as e:
                                print(e)
                        for n2,f in enumerate(location_fields):
                            if getattr(i,f) > 0:
                                msg2=f'{colormapped[n2]}{f} = {round(getattr(i,f),ROUNDTO)}{Style.reset}'
                                if n2 < len(location_fields):
                                    msg2+=","
                                msg+=msg2
                        master_total+=total*round(i.Price,ROUNDTO)

                        crv+=(round(i.CRV,ROUNDTO)*total)
                        tax+=(round(i.Tax,ROUNDTO)*total)
                        if tax == 0 and crv > 0:
                            tax_crv=(round(i.CRV,ROUNDTO)*total)
                        else:
                            tax_crv+=((round(i.Tax,ROUNDTO)*total)+(round(i.CRV,ROUNDTO)*total))
                        master_total_tax+=tax
                        master_total_crv+=crv
                        master_total_tax_crv+=tax_crv
                        tax_crv=round(tax_crv,ROUNDTO)
                        try:
                            super_total=(round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)/getSuperTotal(results,location_fields,colormapped)['final total'],ROUNDTO))*100
                        except Exception as e:
                            p1=round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO))
                            p2=getSuperTotal(results,location_fields,colormapped)['final total']
                            print(e)
                            print(p1,"p1")
                            print(p2,"p2")
                            super_total=0
                        msg+=f"""{Fore.light_magenta} |-|{Fore.light_green} Total = {Fore.light_sea_green}{round(total,ROUNDTO)}
{Fore.light_magenta}Price({i.Price}){Fore.medium_violet_red}*{Fore.light_slate_blue}Total({round(total,ROUNDTO)}):{round(i.Price*total,ROUNDTO)}
{Fore.grey_70}+CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TotalCRV({crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(total*i.Price,ROUNDTO)+crv})
{Fore.grey_70}+Tax({i.Tax}) w/o CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxNoCRVTotal({tax})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax,ROUNDTO)})
{Fore.grey_70}+Tax({i.Tax}) w/ CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxCRVTotal({tax_crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)})
{'*'*os.get_terminal_size().columns}{Style.reset}"""
                        print(msg)
                    master_total=round(master_total,ROUNDTO)
                    master_total_crv=round(master_total_crv,ROUNDTO)
                    master_total_tax=round(master_total_tax,ROUNDTO)
                    master_total_tax_crv=round(master_total_tax_crv,ROUNDTO)
                    msg=f"""{Fore.light_green}Total Product Value:{Fore.slate_blue_1}{round(master_total,ROUNDTO)}
{Fore.light_green}Total Product Value w/CRV({master_total_crv}):{Fore.slate_blue_1}{round(master_total_crv+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/o CRV({master_total_tax}):{Fore.slate_blue_1}{round(master_total_tax+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/ CRV({master_total_tax_crv}):{Fore.slate_blue_1}{round(master_total_tax_crv+master_total,ROUNDTO)}
{Fore.medium_violet_red}PercentOfTotal({round(super_total,ROUNDTO)}) of Total({getSuperTotal(results,location_fields,colormapped)['final total']})
                    {Style.reset}"""
                    print(msg)
            elif cmd.lower() in ['esbld','export search build','export_search_build','exp scan build','exp_scan_bld']:
                end=False
                msg=''
                db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file,clear_only=True)
                while not end:
                    with db.Session(db.ENGINE) as session:
                        def mkT(text,data):
                            return text
                        code=Prompt.__init2__(None,func=mkT,ptext="Code|Barcode|Name: ",helpText="find by code,barcode,name",data='')
                        if code in [None,]:
                            end=True
                            break
                        elif code in ['d',]:
                            continue
                            
                        results_query=session.query(db.Entry).filter(db.Entry.InList==True)
                        results_query=results_query.filter(
                            db.or_(
                                db.Entry.Code==code,
                                db.Entry.Barcode==code,
                                db.Entry.Barcode.icontains(code),
                                db.Entry.Code.icontains(code),
                                db.Entry.Name.icontains(code)
                                )
                            )
                        location_fields=["Shelf","BackRoom","Display_1","Display_2","Display_3","Display_4","Display_5","Display_6","ListQty","SBX_WTR_DSPLY","SBX_CHP_DSPLY","SBX_WTR_KLR","FLRL_CHP_DSPLY","FLRL_WTR_DSPLY","WD_DSPLY","CHKSTND_SPLY","Distress"]
                        z=Prompt.mkfield_list(None,location_fields)
                        if z in [[],None]:
                            z=location_fields
                        location_fields=z
                        tmp=[]
                        for f in location_fields:
                            tmp.append(or_(getattr(db.Entry,f)>=0.0001))
                        results_query=results_query.filter(or_(*tmp))
                        results=results_query.all()
                        ct=len(results)
                        if ct < 1:
                            msg=f"{Fore.light_steel_blue}Nothing in {Fore.slate_blue_1}Bld{Fore.light_red}LS!{Style.reset}"
                            db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file)
                            print(msg)
                            continue
                    
                    #start
                    ROUNDTO=int(db.detectGetOrSet("lsbld ROUNDTO default",3,setValue=False,literal=True))
                    master_total=0
                    master_total_crv=0
                    master_total_tax=0
                    master_total_tax_crv=0

                    for num,i in enumerate(results):
                        msg=f'{"*"*os.get_terminal_size().columns}\n{Fore.light_green}{num}{Fore.light_magenta}/{Fore.orange_3}{num+1} of {Fore.light_red}{ct}[{Fore.dark_slate_gray_1}EID{Fore.orange_3}]{Fore.dark_violet_1b}{i.EntryId}{Style.reset} |-| {Fore.light_yellow}{i.Name}|{Fore.light_salmon_1}[{Fore.light_red}BCD]{i.rebar()}{Fore.medium_violet_red}|[{Fore.light_red}CD{Fore.medium_violet_red}]{i.cfmt(i.Code)} {Style.reset}|-| '
                        colormapped=[
                        Fore.deep_sky_blue_4c,
                        Fore.spring_green_4,
                        Fore.turquoise_4,
                        Fore.dark_cyan,
                        Fore.deep_sky_blue_2,
                        Fore.spring_green_2a,
                        Fore.medium_spring_green,
                        Fore.steel_blue,
                        Fore.cadet_blue_1,
                        Fore.aquamarine_3,
                        Fore.purple_1a,
                        Fore.medium_purple_3a,
                        Fore.slate_blue_1,
                        Fore.light_slate_grey,
                        Fore.dark_olive_green_3a,
                        Fore.deep_pink_4c,
                        Fore.orange_3,
                        ]
                        total=0
                        crv=0
                        tax=0
                        tax_crv=0
                        i.Tax=round(i.Tax,ROUNDTO)
                        i.CRV=round(i.CRV,ROUNDTO)
                        i.Price=round(i.Price,ROUNDTO)
                        session.commit()
                        for n2,f in enumerate(location_fields):
                            try:
                                if getattr(i,f) > 0:
                                    total+=getattr(i,f)
                            except Exception as e:
                                print(e)
                        for n2,f in enumerate(location_fields):
                            if getattr(i,f) > 0:
                                msg2=f'{colormapped[n2]}{f} = {round(getattr(i,f),ROUNDTO)}{Style.reset}'
                                if n2 < len(location_fields):
                                    msg2+=","
                                msg+=msg2
                        master_total+=total*round(i.Price,ROUNDTO)

                        crv+=(round(i.CRV,ROUNDTO)*total)
                        tax+=(round(i.Tax,ROUNDTO)*total)
                        if tax == 0 and crv > 0:
                            tax_crv=(round(i.CRV,ROUNDTO)*total)
                        else:
                            tax_crv+=((round(i.Tax,ROUNDTO)*total)+(round(i.CRV,ROUNDTO)*total))
                        master_total_tax+=tax
                        master_total_crv+=crv
                        master_total_tax_crv+=tax_crv
                        tax_crv=round(tax_crv,ROUNDTO)
                        try:
                            super_total=(round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)/getSuperTotal(results,location_fields,colormapped)['final total'],ROUNDTO))*100
                        except Exception as e:
                            p1=round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO))
                            p2=getSuperTotal(results,location_fields,colormapped)['final total']
                            print(e)
                            print(p1,"p1")
                            print(p2,"p2")
                            super_total=0
                        msg+=f"""{Fore.light_magenta} |-|{Fore.light_green} Total = {Fore.light_sea_green}{round(total,ROUNDTO)}
{Fore.light_magenta}Price({i.Price}){Fore.medium_violet_red}*{Fore.light_slate_blue}Total({round(total,ROUNDTO)}):{round(i.Price*total,ROUNDTO)}
{Fore.grey_70}+CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TotalCRV({crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(total*i.Price,ROUNDTO)+crv})
{Fore.grey_70}+Tax({i.Tax}) w/o CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxNoCRVTotal({tax})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax,ROUNDTO)})
{Fore.grey_70}+Tax({i.Tax}) w/ CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxCRVTotal({tax_crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)})
{Fore.medium_violet_red}PercentOfTotal({round(super_total,ROUNDTO)}) of Total({getSuperTotal(results,location_fields,colormapped)['final total']})
{'*'*os.get_terminal_size().columns}{Style.reset}"""
                        db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file)
                        print(msg)
                    master_total=round(master_total,ROUNDTO)
                    master_total_crv=round(master_total_crv,ROUNDTO)
                    master_total_tax=round(master_total_tax,ROUNDTO)
                    master_total_tax_crv=round(master_total_tax_crv,ROUNDTO)
                    msg=f"""{Fore.light_green}Total Product Value:{Fore.slate_blue_1}{round(master_total,ROUNDTO)}
{Fore.light_green}Total Product Value w/CRV({master_total_crv}):{Fore.slate_blue_1}{round(master_total_crv+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/o CRV({master_total_tax}):{Fore.slate_blue_1}{round(master_total_tax+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/ CRV({master_total_tax_crv}):{Fore.slate_blue_1}{round(master_total_tax_crv+master_total,ROUNDTO)}
                    {Style.reset}"""
                    db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file)
                    print(msg)
            elif cmd.lower() in ["bldls-","build-","buildls-","build list -","bld ls -",'lsbld-','list build -','ls bld -','bld-']:
                with db.Session(db.ENGINE) as session:
                    results_query=session.query(db.Entry).filter(db.Entry.InList==True)
                    location_fields=["Shelf","BackRoom","Display_1","Display_2","Display_3","Display_4","Display_5","Display_6","ListQty","SBX_WTR_DSPLY","SBX_CHP_DSPLY","SBX_WTR_KLR","FLRL_CHP_DSPLY","FLRL_WTR_DSPLY","WD_DSPLY","CHKSTND_SPLY","Distress"]
                    z=Prompt.mkfield_list(None,location_fields)
                    if z in [[],None]:
                        z=location_fields
                    location_fields=z
                    tmp=[]
                    for f in location_fields:
                        tmp.append(or_(getattr(db.Entry,f)!=0,getattr(db.Entry,f)!=None))
                    results_query=results_query.filter(or_(*tmp))
                    results=results_query.all()
                    ct=len(results)
                    if ct < 1:
                        print(f"{Fore.light_steel_blue}Nothing in {Fore.slate_blue_1}Bld{Fore.light_red}LS!{Style.reset}")
                        continue
                    ROUNDTO=int(db.detectGetOrSet("lsbld ROUNDTO default",3,setValue=False,literal=True))
                    master_total=0
                    master_total_crv=0
                    master_total_tax=0
                    master_total_tax_crv=0

                    for num,i in enumerate(results):
                        msg=f'{"*"*os.get_terminal_size().columns}\n{Fore.light_green}{num}{Fore.light_magenta}/{Fore.orange_3}{num+1} of {Fore.light_red}{ct}[{Fore.dark_slate_gray_1}EID{Fore.orange_3}]{Fore.dark_violet_1b}{i.EntryId}{Style.reset} |-| {Fore.light_yellow}{i.Name}|{Fore.light_salmon_1}[{Fore.light_red}BCD]{i.rebar()}{Fore.medium_violet_red}|[{Fore.light_red}CD{Fore.medium_violet_red}]{i.cfmt(i.Code)} {Style.reset}|-| '
                        colormapped=[
                        Fore.deep_sky_blue_4c,
                        Fore.spring_green_4,
                        Fore.turquoise_4,
                        Fore.dark_cyan,
                        Fore.deep_sky_blue_2,
                        Fore.spring_green_2a,
                        Fore.medium_spring_green,
                        Fore.steel_blue,
                        Fore.cadet_blue_1,
                        Fore.aquamarine_3,
                        Fore.purple_1a,
                        Fore.medium_purple_3a,
                        Fore.slate_blue_1,
                        Fore.light_slate_grey,
                        Fore.dark_olive_green_3a,
                        Fore.deep_pink_4c,
                        Fore.orange_3,
                        ]
                        total=0
                        crv=0
                        tax=0
                        tax_crv=0
                        for n2,f in enumerate(location_fields):
                            try:
                                if getattr(i,f) != 0:
                                    total+=getattr(i,f)
                            except Exception as e:
                                print(e)
                        for n2,f in enumerate(location_fields):
                            if getattr(i,f) != 0:
                                msg2=f'{colormapped[n2]}{f} = {round(getattr(i,f),3)}{Style.reset}'
                                if n2 < len(location_fields):
                                    msg2+=","
                                msg+=msg2
                        master_total+=total*round(i.Price,ROUNDTO)

                        crv+=(round(i.CRV,ROUNDTO)*total)
                        tax+=(round(i.Tax,ROUNDTO)*total)
                        if tax == 0 and crv > 0:
                            tax_crv=(round(i.CRV,ROUNDTO)*total)
                        else:
                            tax_crv+=((round(i.Tax,ROUNDTO)*total)+(round(i.CRV,ROUNDTO)*total))
                        master_total_tax+=tax
                        master_total_crv+=crv
                        master_total_tax_crv+=tax_crv
                        tax_crv=round(tax_crv,ROUNDTO)
                        try:
                            super_total=(round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)/getSuperTotal(results,location_fields,colormapped)['final total'],ROUNDTO))*100
                        except Exception as e:
                            p1=round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO))
                            p2=getSuperTotal(results,location_fields,colormapped)['final total']
                            print(e)
                            print(p1,"p1")
                            print(p2,"p2")
                            super_total=0

                        msg+=f"""{Fore.light_magenta} |-|{Fore.light_green} Total = {Fore.light_sea_green}{round(total,ROUNDTO)}
{Fore.light_magenta}Price({i.Price}){Fore.medium_violet_red}*{Fore.light_slate_blue}Total({round(total,ROUNDTO)}):{round(i.Price*total,ROUNDTO)}
{Fore.grey_70}+CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TotalCRV({crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(total*i.Price,ROUNDTO)+crv})
{Fore.grey_70}+Tax({i.Tax}) w/o CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxNoCRVTotal({tax})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax,ROUNDTO)})
{Fore.grey_70}+Tax({i.Tax}) w/ CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxCRVTotal({tax_crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)})
{Fore.medium_violet_red}PercentOfTotal({round(super_total,ROUNDTO)}) of Total({getSuperTotal(results,location_fields,colormapped)['final total']})
{'*'*os.get_terminal_size().columns}{Style.reset}"""
                        print(msg)
                    master_total=round(master_total,ROUNDTO)
                    master_total_crv=round(master_total_crv,ROUNDTO)
                    master_total_tax=round(master_total_tax,ROUNDTO)
                    master_total_tax_crv=round(master_total_tax_crv,ROUNDTO)
                    msg=f"""{Fore.light_green}Total Product Value:{Fore.slate_blue_1}{round(master_total,ROUNDTO)}
{Fore.light_green}Total Product Value w/CRV({master_total_crv}):{Fore.slate_blue_1}{round(master_total_crv+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/o CRV({master_total_tax}):{Fore.slate_blue_1}{round(master_total_tax+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/ CRV({master_total_tax_crv}):{Fore.slate_blue_1}{round(master_total_tax_crv+master_total,ROUNDTO)}
                    {Style.reset}"""
                    print(msg)
            elif cmd.lower() in ["bldlse-","builde-","buildlse-","build list export -","bld ls exp -",'elsbld-','export list build -','exp ls bld -','ebld-']:
                msg=''
                db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file,clear_only=True)
                with db.Session(db.ENGINE) as session:
                    results_query=session.query(db.Entry).filter(db.Entry.InList==True)
                    location_fields=["Shelf","BackRoom","Display_1","Display_2","Display_3","Display_4","Display_5","Display_6","ListQty","SBX_WTR_DSPLY","SBX_CHP_DSPLY","SBX_WTR_KLR","FLRL_CHP_DSPLY","FLRL_WTR_DSPLY","WD_DSPLY","CHKSTND_SPLY","Distress"]
                    z=Prompt.mkfield_list(None,location_fields)
                    if z in [[],None]:
                        z=location_fields
                    location_fields=z
                    tmp=[]
                    for f in location_fields:
                        tmp.append(or_(getattr(db.Entry,f)!=0,getattr(db.Entry,f)!=None))
                    results_query=results_query.filter(or_(*tmp))
                    results=results_query.all()
                    ct=len(results)
                    if ct < 1:
                        msg=f"{Fore.light_steel_blue}Nothing in {Fore.slate_blue_1}Bld{Fore.light_red}LS!{Style.reset}"
                        db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file)
                        print(msg)
                        continue
                    ROUNDTO=int(db.detectGetOrSet("lsbld ROUNDTO default",3,setValue=False,literal=True))
                    master_total=0
                    master_total_crv=0
                    master_total_tax=0
                    master_total_tax_crv=0

                    for num,i in enumerate(results):
                        msg=f'{"*"*os.get_terminal_size().columns}\n{Fore.light_green}{num}{Fore.light_magenta}/{Fore.orange_3}{num+1} of {Fore.light_red}{ct}[{Fore.dark_slate_gray_1}EID{Fore.orange_3}]{Fore.dark_violet_1b}{i.EntryId}{Style.reset} |-| {Fore.light_yellow}{i.Name}|{Fore.light_salmon_1}[{Fore.light_red}BCD]{i.rebar()}{Fore.medium_violet_red}|[{Fore.light_red}CD{Fore.medium_violet_red}]{i.cfmt(i.Code)} {Style.reset}|-| '
                        colormapped=[
                        Fore.deep_sky_blue_4c,
                        Fore.spring_green_4,
                        Fore.turquoise_4,
                        Fore.dark_cyan,
                        Fore.deep_sky_blue_2,
                        Fore.spring_green_2a,
                        Fore.medium_spring_green,
                        Fore.steel_blue,
                        Fore.cadet_blue_1,
                        Fore.aquamarine_3,
                        Fore.purple_1a,
                        Fore.medium_purple_3a,
                        Fore.slate_blue_1,
                        Fore.light_slate_grey,
                        Fore.dark_olive_green_3a,
                        Fore.deep_pink_4c,
                        Fore.orange_3,
                        ]
                        total=0
                        crv=0
                        tax=0
                        tax_crv=0
                        for n2,f in enumerate(location_fields):
                            try:
                                if getattr(i,f) != 0:
                                    total+=getattr(i,f)
                            except Exception as e:
                                print(e)
                        for n2,f in enumerate(location_fields):
                            if getattr(i,f) != 0:
                                msg2=f'{colormapped[n2]}{f} = {round(getattr(i,f),ROUNDTO)}{Style.reset}'
                                if n2 < len(location_fields):
                                    msg2+=","
                                msg+=msg2
                        master_total+=total*round(i.Price,ROUNDTO)

                        crv+=(round(i.CRV,ROUNDTO)*total)
                        tax+=(round(i.Tax,ROUNDTO)*total)
                        if tax == 0 and crv > 0:
                            tax_crv=(round(i.CRV,ROUNDTO)*total)
                        else:
                            tax_crv+=((round(i.Tax,ROUNDTO)*total)+(round(i.CRV,ROUNDTO)*total))
                        master_total_tax+=tax
                        master_total_crv+=crv
                        master_total_tax_crv+=tax_crv
                        tax_crv=round(tax_crv,ROUNDTO)
                        try:
                            super_total=(round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)/getSuperTotal(results,location_fields,colormapped)['final total'],ROUNDTO))*100
                        except Exception as e:
                            p1=round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO))
                            p2=getSuperTotal(results,location_fields,colormapped)['final total']
                            print(e)
                            print(p1,"p1")
                            print(p2,"p2")
                            super_total=0

                        msg+=f"""{Fore.light_magenta} |-|{Fore.light_green} Total = {Fore.light_sea_green}{round(total,ROUNDTO)}
{Fore.light_magenta}Price({i.Price}){Fore.medium_violet_red}*{Fore.light_slate_blue}Total({round(total,ROUNDTO)}):{round(i.Price*total,ROUNDTO)}
{Fore.grey_70}+CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TotalCRV({crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(total*i.Price,ROUNDTO)+crv})
{Fore.grey_70}+Tax({i.Tax}) w/o CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxNoCRVTotal({tax})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax,ROUNDTO)})
{Fore.grey_70}+Tax({i.Tax}) w/ CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxCRVTotal({tax_crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)})
{Fore.medium_violet_red}PercentOfTotal({round(super_total,ROUNDTO)}) of Total({getSuperTotal(results,location_fields,colormapped)['final total']})
{'*'*os.get_terminal_size().columns}{Style.reset}"""
                        print(msg)
                        db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file)

                    master_total=round(master_total,ROUNDTO)
                    master_total_crv=round(master_total_crv,ROUNDTO)
                    master_total_tax=round(master_total_tax,ROUNDTO)
                    master_total_tax_crv=round(master_total_tax_crv,ROUNDTO)
                    msg=f"""{Fore.light_green}Total Product Value:{Fore.slate_blue_1}{round(master_total,ROUNDTO)}
{Fore.light_green}Total Product Value w/CRV({master_total_crv}):{Fore.slate_blue_1}{round(master_total_crv+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/o CRV({master_total_tax}):{Fore.slate_blue_1}{round(master_total_tax+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/ CRV({master_total_tax_crv}):{Fore.slate_blue_1}{round(master_total_tax_crv+master_total,ROUNDTO)}
                    {Style.reset}"""
                    print(msg)
                    db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file)
            elif cmd.lower() in ['sbld-','search build -','search_build-','scan build-','scan_bld-']:
                end=False
                while not end:
                    with db.Session(db.ENGINE) as session:
                        def mkT(text,data):
                            return text
                        code=Prompt.__init2__(None,func=mkT,ptext="Code|Barcode|Name: ",helpText="find by code,barcode,name",data='')
                        if code in [None,]:
                            end=True
                            break
                        elif code in ['d',]:
                            continue
                            
                        results_query=session.query(db.Entry).filter(db.Entry.InList==True)
                        results_query=results_query.filter(
                            db.or_(
                                db.Entry.Code==code,
                                db.Entry.Barcode==code,
                                db.Entry.Barcode.icontains(code),
                                db.Entry.Code.icontains(code),
                                db.Entry.Name.icontains(code)
                                )
                            )
                        location_fields=["Shelf","BackRoom","Display_1","Display_2","Display_3","Display_4","Display_5","Display_6","ListQty","SBX_WTR_DSPLY","SBX_CHP_DSPLY","SBX_WTR_KLR","FLRL_CHP_DSPLY","FLRL_WTR_DSPLY","WD_DSPLY","CHKSTND_SPLY","Distress"]
                        z=Prompt.mkfield_list(None,location_fields)
                        if z in [[],None]:
                            z=location_fields
                        location_fields=z
                        tmp=[]
                        for f in location_fields:
                            tmp.append(or_(getattr(db.Entry,f)!=0,getattr(db.Entry,f)!=None))
                        results_query=results_query.filter(or_(*tmp))
                        results=results_query.all()
                        ct=len(results)
                        if ct < 1:
                            print(f"{Fore.light_steel_blue}Nothing in {Fore.slate_blue_1}Bld{Fore.light_red}LS!{Style.reset}")
                            continue
                    ROUNDTO=int(db.detectGetOrSet("lsbld ROUNDTO default",3,setValue=False,literal=True))
                    master_total=0
                    master_total_crv=0
                    master_total_tax=0
                    master_total_tax_crv=0

                    for num,i in enumerate(results):
                        msg=f'{"*"*os.get_terminal_size().columns}\n{Fore.light_green}{num}{Fore.light_magenta}/{Fore.orange_3}{num+1} of {Fore.light_red}{ct}[{Fore.dark_slate_gray_1}EID{Fore.orange_3}]{Fore.dark_violet_1b}{i.EntryId}{Style.reset} |-| {Fore.light_yellow}{i.Name}|{Fore.light_salmon_1}[{Fore.light_red}BCD]{i.rebar()}{Fore.medium_violet_red}|[{Fore.light_red}CD{Fore.medium_violet_red}]{i.cfmt(i.Code)} {Style.reset}|-| '
                        colormapped=[
                        Fore.deep_sky_blue_4c,
                        Fore.spring_green_4,
                        Fore.turquoise_4,
                        Fore.dark_cyan,
                        Fore.deep_sky_blue_2,
                        Fore.spring_green_2a,
                        Fore.medium_spring_green,
                        Fore.steel_blue,
                        Fore.cadet_blue_1,
                        Fore.aquamarine_3,
                        Fore.purple_1a,
                        Fore.medium_purple_3a,
                        Fore.slate_blue_1,
                        Fore.light_slate_grey,
                        Fore.dark_olive_green_3a,
                        Fore.deep_pink_4c,
                        Fore.orange_3,
                        ]
                        total=0
                        crv=0
                        tax=0
                        tax_crv=0
                        for n2,f in enumerate(location_fields):
                            try:
                                if getattr(i,f) != 0:
                                    total+=getattr(i,f)
                            except Exception as e:
                                print(e)
                        for n2,f in enumerate(location_fields):
                            if getattr(i,f) != 0:
                                msg2=f'{colormapped[n2]}{f} = {round(getattr(i,f),ROUNDTO)}{Style.reset}'
                                if n2 < len(location_fields):
                                    msg2+=","
                                msg+=msg2
                        master_total+=total*round(i.Price,3)

                        crv+=(round(i.CRV,ROUNDTO)*total)
                        tax+=(round(i.Tax,ROUNDTO)*total)
                        if tax == 0 and crv > 0:
                            tax_crv=(round(i.CRV,ROUNDTO)*total)
                        else:
                            tax_crv+=((round(i.Tax,ROUNDTO)*total)+(round(i.CRV,ROUNDTO)*total))
                        master_total_tax+=tax
                        master_total_crv+=crv
                        master_total_tax_crv+=tax_crv
                        tax_crv=round(tax_crv,ROUNDTO)
                        try:
                            super_total=(round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)/getSuperTotal(results,location_fields,colormapped)['final total'],ROUNDTO))*100
                        except Exception as e:
                            p1=round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO))
                            p2=getSuperTotal(results,location_fields,colormapped)['final total']
                            print(e)
                            print(p1,"p1")
                            print(p2,"p2")
                            super_total=0

                        msg+=f"""{Fore.light_magenta} |-|{Fore.light_green} Total = {Fore.light_sea_green}{round(total,ROUNDTO)}
{Fore.light_magenta}Price({i.Price}){Fore.medium_violet_red}*{Fore.light_slate_blue}Total({round(total,ROUNDTO)}):{round(i.Price*total,ROUNDTO)}
{Fore.grey_70}+CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TotalCRV({crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(total*i.Price,ROUNDTO)+crv})
{Fore.grey_70}+Tax({i.Tax}) w/o CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxNoCRVTotal({tax})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax,ROUNDTO)})
{Fore.grey_70}+Tax({i.Tax}) w/ CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxCRVTotal({tax_crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)})
{Fore.medium_violet_red}PercentOfTotal({round(super_total,ROUNDTO)}) of Total({getSuperTotal(results,location_fields,colormapped)['final total']})
{'*'*os.get_terminal_size().columns}{Style.reset}"""
                        print(msg)
                    master_total=round(master_total,ROUNDTO)
                    master_total_crv=round(master_total_crv,ROUNDTO)
                    master_total_tax=round(master_total_tax,ROUNDTO)
                    master_total_tax_crv=round(master_total_tax_crv,ROUNDTO)
                    msg=f"""{Fore.light_green}Total Product Value:{Fore.slate_blue_1}{round(master_total,ROUNDTO)}
{Fore.light_green}Total Product Value w/CRV({master_total_crv}):{Fore.slate_blue_1}{round(master_total_crv+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/o CRV({master_total_tax}):{Fore.slate_blue_1}{round(master_total_tax+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/ CRV({master_total_tax_crv}):{Fore.slate_blue_1}{round(master_total_tax_crv+master_total,ROUNDTO)}
                    {Style.reset}"""
                    print(msg)
            elif cmd.lower() in ['esbld-','export search build -','export_search_build-','exp scan build-','exp_scan_bld-']:
                end=False
                msg=''
                db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file,clear_only=True)
                while not end:
                    with db.Session(db.ENGINE) as session:
                        def mkT(text,data):
                            return text
                        code=Prompt.__init2__(None,func=mkT,ptext="Code|Barcode|Name: ",helpText="find by code,barcode,name",data='')
                        if code in [None,]:
                            end=True
                            break
                        elif code in ['d',]:
                            continue
                            
                        results_query=session.query(db.Entry).filter(db.Entry.InList==True)
                        results_query=results_query.filter(
                            db.or_(
                                db.Entry.Code==code,
                                db.Entry.Barcode==code,
                                db.Entry.Barcode.icontains(code),
                                db.Entry.Code.icontains(code),
                                db.Entry.Name.icontains(code)
                                )
                            )
                        location_fields=["Shelf","BackRoom","Display_1","Display_2","Display_3","Display_4","Display_5","Display_6","ListQty","SBX_WTR_DSPLY","SBX_CHP_DSPLY","SBX_WTR_KLR","FLRL_CHP_DSPLY","FLRL_WTR_DSPLY","WD_DSPLY","CHKSTND_SPLY","Distress"]
                        z=Prompt.mkfield_list(None,location_fields)
                        if z in [[],None]:
                            z=location_fields
                        location_fields=z
                        tmp=[]
                        for f in location_fields:
                            tmp.append(or_(getattr(db.Entry,f)!=0,getattr(db.Entry,f)!=None))
                        results_query=results_query.filter(or_(*tmp))
                        results=results_query.all()
                        ct=len(results)
                        if ct < 1:
                            msg=f"{Fore.light_steel_blue}Nothing in {Fore.slate_blue_1}Bld{Fore.light_red}LS!{Style.reset}"
                            db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file)
                            print(msg)
                            continue
                    ROUNDTO=int(db.detectGetOrSet("lsbld ROUNDTO default",3,setValue=False,literal=True))
                    master_total=0
                    master_total_crv=0
                    master_total_tax=0
                    master_total_tax_crv=0

                    for num,i in enumerate(results):
                        msg=f'{"*"*os.get_terminal_size().columns}\n{Fore.light_green}{num}{Fore.light_magenta}/{Fore.orange_3}{num+1} of {Fore.light_red}{ct}[{Fore.dark_slate_gray_1}EID{Fore.orange_3}]{Fore.dark_violet_1b}{i.EntryId}{Style.reset} |-| {Fore.light_yellow}{i.Name}|{Fore.light_salmon_1}[{Fore.light_red}BCD]{i.rebar()}{Fore.medium_violet_red}|[{Fore.light_red}CD{Fore.medium_violet_red}]{i.cfmt(i.Code)} {Style.reset}|-| '
                        colormapped=[
                        Fore.deep_sky_blue_4c,
                        Fore.spring_green_4,
                        Fore.turquoise_4,
                        Fore.dark_cyan,
                        Fore.deep_sky_blue_2,
                        Fore.spring_green_2a,
                        Fore.medium_spring_green,
                        Fore.steel_blue,
                        Fore.cadet_blue_1,
                        Fore.aquamarine_3,
                        Fore.purple_1a,
                        Fore.medium_purple_3a,
                        Fore.slate_blue_1,
                        Fore.light_slate_grey,
                        Fore.dark_olive_green_3a,
                        Fore.deep_pink_4c,
                        Fore.orange_3,
                        ]
                        total=0
                        crv=0
                        tax=0
                        tax_crv=0
                        for n2,f in enumerate(location_fields):
                            try:
                                if getattr(i,f) != 0:
                                    total+=getattr(i,f)
                            except Exception as e:
                                print(e)
                        for n2,f in enumerate(location_fields):
                            if getattr(i,f) != 0:
                                msg2=f'{colormapped[n2]}{f} = {round(getattr(i,f),ROUNDTO)}{Style.reset}'
                                if n2 < len(location_fields):
                                    msg2+=","
                                msg+=msg2
                        master_total+=total*round(i.Price,ROUNDTO)

                        crv+=(round(i.CRV,ROUNDTO)*total)
                        tax+=(round(i.Tax,ROUNDTO)*total)
                        if tax == 0 and crv > 0:
                            tax_crv=(round(i.CRV,ROUNDTO)*total)
                        else:
                            tax_crv+=((round(i.Tax,ROUNDTO)*total)+(round(i.CRV,ROUNDTO)*total))
                        master_total_tax+=tax
                        master_total_crv+=crv
                        master_total_tax_crv+=tax_crv
                        tax_crv=round(tax_crv,ROUNDTO)
                        try:
                            super_total=(round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)/getSuperTotal(results,location_fields,colormapped)['final total'],ROUNDTO))*100
                        except Exception as e:
                            p1=round(round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO))
                            p2=getSuperTotal(results,location_fields,colormapped)['final total']
                            print(e)
                            print(p1,"p1")
                            print(p2,"p2")
                            super_total=0
                        msg+=f"""{Fore.light_magenta} |-|{Fore.light_green} Total = {Fore.light_sea_green}{round(total,ROUNDTO)}
{Fore.light_magenta}Price({i.Price}){Fore.medium_violet_red}*{Fore.light_slate_blue}Total({round(total,ROUNDTO)}):{round(i.Price*total,ROUNDTO)}
{Fore.grey_70}+CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TotalCRV({crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(total*i.Price,ROUNDTO)+crv})
{Fore.grey_70}+Tax({i.Tax}) w/o CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxNoCRVTotal({tax})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax,ROUNDTO)})
{Fore.grey_70}+Tax({i.Tax}) w/ CRV({i.CRV})*Total({round(total,ROUNDTO)}){Fore.slate_blue_1}\n=TaxCRVTotal({tax_crv})+TotalPrice({round(total*i.Price,ROUNDTO)})=NetPrice({round(round(total*i.Price,ROUNDTO)+tax_crv,ROUNDTO)})
{Fore.medium_violet_red}PercentOfTotal({round(super_total,ROUNDTO)}) of Total({getSuperTotal(results,location_fields,colormapped)['final total']})
{'*'*os.get_terminal_size().columns}{Style.reset}"""
                        print(msg)
                        db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file)
                    master_total=round(master_total,ROUNDTO)
                    master_total_crv=round(master_total_crv,ROUNDTO)
                    master_total_tax=round(master_total_tax,ROUNDTO)
                    master_total_tax_crv=round(master_total_tax_crv,ROUNDTO)
                    msg=f"""{Fore.light_green}Total Product Value:{Fore.slate_blue_1}{round(master_total,ROUNDTO)}
{Fore.light_green}Total Product Value w/CRV({master_total_crv}):{Fore.slate_blue_1}{round(master_total_crv+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/o CRV({master_total_tax}):{Fore.slate_blue_1}{round(master_total_tax+master_total,ROUNDTO)}
{Fore.light_green}Total Product Value Taxed w/ CRV({master_total_tax_crv}):{Fore.slate_blue_1}{round(master_total_tax_crv+master_total,ROUNDTO)}
                    {Style.reset}"""
                    print(msg)
                    db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file)
                #end#
            elif cmd.lower() in ['cdp','clipboard_default_paste','clipboard default paste']:
                with db.Session(db.ENGINE) as session:
                    dflt=session.query(db.ClipBoord).filter(db.ClipBoord.defaultPaste==True).order_by(db.ClipBoord.doe.desc()).first()
                    if dflt:
                        print(f"{Fore.orange_red_1}using '{Fore.light_blue}{dflt.cbValue}{Fore.orange_red_1}'{Style.reset}")
                        return func(dflt.cbValue,data)
                    else:
                        print(f"{Fore.orange_red_1}nothing to use!{Style.reset}")
            else:
                return func(cmd,data)   

    #since this will be used statically, no self is required 
    #example filter method
    def cmdfilter(text,data):
        print(text)

prefix_text=f'''{Fore.light_red}$code{Fore.light_blue} is the scanned text literal{Style.reset}
{Fore.light_magenta}{Style.underline}#code refers to:{Style.reset}
{Fore.grey_70}e.{Fore.light_red}$code{Fore.light_blue} == search EntryId{Style.reset}
{Fore.grey_70}B.{Fore.light_red}$code{Fore.light_blue} == search Barcode{Style.reset}
{Fore.grey_70}c.{Fore.light_red}$code{Fore.light_blue} == search Code{Style.reset}
{Fore.light_red}$code{Fore.light_blue} == search Code | Barcode{Style.reset}
'''
def prefix_filter(text,self):
    split=text.split(self.get('delim'))
    if len(split) == 2:
        prefix=split[0]
        code=split[-1]
        try:
            if prefix.lower() == 'c':
                return self.get('c_do')(code)
            elif prefix == 'B':
                return self.get('b_do')(code)
            elif prefix.lower() == 'e':
                return self.get('e_do')(code)
        except Exception as e:
            print(e)
    else:
        return self.get('do')(text)






if __name__ == "__main__":  
    Prompt(func=Prompt.cmdfilter,ptext='code|barcode',helpText='test help!',data={})
        

    