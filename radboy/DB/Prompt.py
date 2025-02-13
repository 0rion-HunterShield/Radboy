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

from datetime import datetime
from datetime import date as DATE
import lzma,base64
from Crypto.Cipher import AES
#from Cryptodome.Cipher import AES
from Crypto.Util.Padding import pad, unpad

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
        

def next_holiday(self=None,today=None):
    if today == None:
        today=DATE(datetime.today().year,datetime.today().month,datetime.today().day)
    holidates=sorted(holidays.USA(years=today.year).items())
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


class Prompt(object):
    def QuitMenu(parent):
        def quit_backup(parent):
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE)
            parent.cleanup_system(parent)

        def quit_backup_clear(parent):
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE)
            bare_ca(None)
            parent.cleanup_system(parent)

        def tag_quit_backup_clear(parent):
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE,addTag=True)
            bare_ca(None)
            parent.cleanup_system(parent)

        def quit_backup_clear_inlist(parent):
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE)
            bare_ca(None,inList=True)
            parent.cleanup_system(parent)

        def tag_quit_backup_clear_inlist(parent):
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE,addTag=True)
            bare_ca(None,inList=True)
            parent.cleanup_system(parent)

        def backup_clear(parent):
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE)
            bare_ca(None)

        def backup_clear_inlist(parent):
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE)
            bare_ca(None,inList=True)

        def tag_backup_clear(parent):
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE,addTag=True)
            bare_ca(None)

        def tag_backup_clear_inlist(parent):
            DL.DayLogger.DayLogger.addTodayP(db.ENGINE,addTag=True)
            bare_ca(None,inList=True)

        def main(parent):
            if parent != None:  
                #parent must be Prompt
                options={
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
            holi=holidays.USA()
            isit=now in holi
            holiname=holi.get(now.strftime("%m/%d/%Y"))

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

            postFilterMsg=f"{Style.underline}{Back.deep_sky_blue_4a}{Fore.light_yellow}Post_Filtering_Final_Cmd('{Style.bold}{Style.res_underline}{Back.spring_green_4}{Fore.white}{cmd}{Style.dim}{Back.deep_sky_blue_4a}{Fore.white}{Style.underline}{Style.res_bold}{Back.deep_sky_blue_4a}{Fore.light_yellow}'){Style.res_underline}|len({Style.res_dim}{len(cmd)}{Style.dim}){Style.reset}"
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
            elif cmd.lower() in ['b','back']:
                lastTime=db.detectGetOrSet("PromptLastDTasFloat",datetime.now().timestamp(),setValue=True)
                return
            elif cmd.lower() in ['h','help']:
                print(helpText)
                extra=f'''{Fore.orange_red_1}Dimension Fields {Fore.light_steel_blue}are fields that tell how much space the product is going to take up using the the product itself as the unit of measure
    {Fore.orange_red_1}Location Fields{Fore.light_steel_blue} are fields where the item resides at, will reside at, is coming from etc...
    {Fore.orange_red_1}Count Fields{Fore.light_steel_blue} are fields that define max values that relate to how much goes to the shelf,comes via the Load, how much comes in a Pallet, or Case{Style.reset}

{Fore.orange_red_1}{Style.underline}Access from anywhere But {Fore.light_red}Root{Style.reset}
{Fore.light_yellow}Don't Use {Fore.grey_70}**{Style.reset}
 {Fore.grey_70}**{Fore.light_green}ne{Fore.light_red}u{Fore.light_steel_blue} - create a new entry menu{Style.reset}
 {Fore.grey_70}**{Fore.light_green}bld{Fore.light_red}ls{Fore.light_steel_blue} - list all items with InList==True and has a location value above {Fore.light_red}0{Style.reset}
 {Fore.grey_70}**{Fore.light_green}s{Fore.light_red}bld{Fore.light_steel_blue} - search with barcode in all items with InList==True and has a location value above {Fore.light_red}0{Style.reset}
 {Fore.grey_70}**{Fore.light_green}"bldlse","builde","buildlse","build list export ","bld ls exp",'elsbld','export list build','exp ls bld','ebld'{Fore.light_steel_blue} - same as versions without export, but dumps list to {Path(Prompt.bld_file).absolute()}{Style.reset}
 {Fore.grey_70}**{Fore.light_green}'esbld','export search build','export_search_build','exp scan build','exp_scan_bld'{Fore.light_steel_blue} - same as versions without export, but dumps list to {Path(Prompt.bld_file).absolute()}{Style.reset}
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
                print(f"{Fore.light_cyan}Running on Android:{Fore.slate_blue_1}{db.onAndroid()}{Style.reset}")
                print(f"{Fore.light_cyan}Running on {Fore.slate_blue_1}{platform.system()} {Fore.light_cyan}Rel:{Fore.orange_red_1}{platform.release()}{Style.reset}")
                print(helpText2)
                Prompt.passwordfile(None,)
                print(Prompt.resrc(Prompt))
                continue
            elif cmd.lower() in ["bldls","build","buildls","build list","bld ls",'lsbld','list build','ls bld','bld']:
                with db.Session(db.ENGINE) as session:
                    results_query=session.query(db.Entry).filter(db.Entry.InList==True)
                    location_fields=["Shelf","BackRoom","Display_1","Display_2","Display_3","Display_4","Display_5","Display_6","ListQty","SBX_WTR_DSPLY","SBX_CHP_DSPLY","SBX_WTR_KLR","FLRL_CHP_DSPLY","FLRL_WTR_DSPLY","WD_DSPLY","CHKSTND_SPLY","Distress"]
                    tmp=[]
                    for f in location_fields:
                        tmp.append(or_(getattr(db.Entry,f)>=1))
                    results_query=results_query.filter(or_(*tmp))
                    results=results_query.all()
                    ct=len(results)
                    if ct < 1:
                        print(f"{Fore.light_steel_blue}Nothing in {Fore.slate_blue_1}Bld{Fore.light_red}LS!{Style.reset}")
                        continue
                    for num,i in enumerate(results):
                        msg=f'{Fore.light_green}{num}{Fore.light_magenta}/{Fore.orange_3}{num+1} of {Fore.light_red}{ct}[{Fore.dark_slate_gray_1}EID{Fore.orange_3}]{Fore.dark_violet_1b}{i.EntryId}{Style.reset} |-| {Fore.light_yellow}{i.Name}|{Fore.light_salmon_1}[{Fore.light_red}BCD{Fore.light_salmon_1}]{i.Barcode}{Fore.medium_violet_red}|[{Fore.light_red}CD{Fore.medium_violet_red}]{i.Code} {Style.reset}|-| '
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
                        for n2,f in enumerate(location_fields):
                            try:
                                if getattr(i,f) > 0:
                                    total+=getattr(i,f)
                            except Exception as e:
                                print(e)
                        for n2,f in enumerate(location_fields):
                            if getattr(i,f) > 0:
                                msg2=f'{colormapped[n2]}{f} = {getattr(i,f)}{Style.reset}'
                                if n2 < len(location_fields):
                                    msg2+=","
                                msg+=msg2
                        msg+=f"{Fore.light_magenta} |-|{Fore.light_green} Total = {Fore.light_sea_green}{total}{Style.reset}"
                        print(msg)
            elif cmd.lower() in ["bldlse","builde","buildlse","build list export ","bld ls exp",'elsbld','export list build','exp ls bld','ebld']:
                msg=''
                db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file,clear_only=True)
                with db.Session(db.ENGINE) as session:
                    results_query=session.query(db.Entry).filter(db.Entry.InList==True)
                    location_fields=["Shelf","BackRoom","Display_1","Display_2","Display_3","Display_4","Display_5","Display_6","ListQty","SBX_WTR_DSPLY","SBX_CHP_DSPLY","SBX_WTR_KLR","FLRL_CHP_DSPLY","FLRL_WTR_DSPLY","WD_DSPLY","CHKSTND_SPLY","Distress"]
                    tmp=[]
                    for f in location_fields:
                        tmp.append(or_(getattr(db.Entry,f)>=1))
                    results_query=results_query.filter(or_(*tmp))
                    results=results_query.all()
                    ct=len(results)
                    if ct < 1:
                        msg=f"{Fore.light_steel_blue}Nothing in {Fore.slate_blue_1}Bld{Fore.light_red}LS!{Style.reset}"
                        db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file)
                        print(msg)
                        continue
                    for num,i in enumerate(results):
                        msg=f'{Fore.light_green}{num}{Fore.light_magenta}/{Fore.orange_3}{num+1} of {Fore.light_red}{ct}[{Fore.dark_slate_gray_1}EID{Fore.orange_3}]{Fore.dark_violet_1b}{i.EntryId}{Style.reset} |-| {Fore.light_yellow}{i.Name}|{Fore.light_salmon_1}[{Fore.light_red}BCD{Fore.light_salmon_1}]{i.Barcode}{Fore.medium_violet_red}|[{Fore.light_red}CD{Fore.medium_violet_red}]{i.Code} {Style.reset}|-| '
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
                        for n2,f in enumerate(location_fields):
                            try:
                                if getattr(i,f) > 0:
                                    total+=getattr(i,f)
                            except Exception as e:
                                print(e)
                        for n2,f in enumerate(location_fields):
                            if getattr(i,f) > 0:
                                msg2=f'{colormapped[n2]}{f} = {getattr(i,f)}{Style.reset}'
                                if n2 < len(location_fields):
                                    msg2+=","
                                msg+=msg2
                        msg+=f"{Fore.light_magenta} |-|{Fore.light_green} Total = {Fore.light_sea_green}{total}{Style.reset}"
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
                        tmp=[]
                        for f in location_fields:
                            tmp.append(or_(getattr(db.Entry,f)>=1))
                        results_query=results_query.filter(or_(*tmp))
                        results=results_query.all()
                        ct=len(results)
                        if ct < 1:
                            print(f"{Fore.light_steel_blue}Nothing in {Fore.slate_blue_1}Bld{Fore.light_red}LS!{Style.reset}")
                            continue
                        for num,i in enumerate(results):
                            msg=f'{Fore.light_green}{num}{Fore.light_magenta}/{Fore.orange_3}{num+1} of {Fore.light_red}{ct}[{Fore.dark_slate_gray_1}EID{Fore.orange_3}]{Fore.dark_violet_1b}{i.EntryId}{Style.reset} |-| {Fore.light_yellow}{i.Name}|{Fore.light_salmon_1}[{Fore.light_red}BCD{Fore.light_salmon_1}]{i.Barcode}{Fore.medium_violet_red}|[{Fore.light_red}CD{Fore.medium_violet_red}]{i.Code} {Style.reset}|-| '
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
                            for n2,f in enumerate(location_fields):
                                try:
                                    if getattr(i,f) > 0:
                                        total+=getattr(i,f)
                                except Exception as e:
                                    print(e)
                            for n2,f in enumerate(location_fields):
                                if getattr(i,f) > 0:
                                    msg2=f'{colormapped[n2]}{f} = {getattr(i,f)}{Style.reset}'
                                    if n2 < len(location_fields):
                                        msg2+=","
                                    msg+=msg2
                            msg+=f"{Fore.light_magenta} |-|{Fore.light_green} Total = {Fore.light_sea_green}{total}{Style.reset}"
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
                        tmp=[]
                        for f in location_fields:
                            tmp.append(or_(getattr(db.Entry,f)>=1))
                        results_query=results_query.filter(or_(*tmp))
                        results=results_query.all()
                        ct=len(results)
                        if ct < 1:
                            msg=f"{Fore.light_steel_blue}Nothing in {Fore.slate_blue_1}Bld{Fore.light_red}LS!{Style.reset}"
                            db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file)
                            print(msg)
                            continue
                        for num,i in enumerate(results):
                            msg=f'{Fore.light_green}{num}{Fore.light_magenta}/{Fore.orange_3}{num+1} of {Fore.light_red}{ct}[{Fore.dark_slate_gray_1}EID{Fore.orange_3}]{Fore.dark_violet_1b}{i.EntryId}{Style.reset} |-| {Fore.light_yellow}{i.Name}|{Fore.light_salmon_1}[{Fore.light_red}BCD{Fore.light_salmon_1}]{i.Barcode}{Fore.medium_violet_red}|[{Fore.light_red}CD{Fore.medium_violet_red}]{i.Code} {Style.reset}|-| '
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
                            for n2,f in enumerate(location_fields):
                                try:
                                    if getattr(i,f) > 0:
                                        total+=getattr(i,f)
                                except Exception as e:
                                    print(e)
                            for n2,f in enumerate(location_fields):
                                if getattr(i,f) > 0:
                                    msg2=f'{colormapped[n2]}{f} = {getattr(i,f)}{Style.reset}'
                                    if n2 < len(location_fields):
                                        msg2+=","
                                    msg+=msg2
                            msg+=f"{Fore.light_magenta} |-|{Fore.light_green} Total = {Fore.light_sea_green}{total}{Style.reset}"
                            print(msg)
                            db.logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=Prompt.bld_file)
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
        

    