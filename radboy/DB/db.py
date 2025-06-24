import math
import sqlalchemy,json
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base as dbase
from sqlalchemy.ext.automap import automap_base
from datetime import datetime,timedelta,date,time
from colored import Fore,Style,Back
from datetime import datetime,timedelta
from pathlib import Path
import pandas as pd
import tarfile,zipfile
import base64
import pint
import qrcode
import barcode
from barcode import UPCA,EAN13,Code39
from qrcode import QRCode
from barcode.writer import ImageWriter
import csv,string,random
import shutil,upcean
import radboy.possibleCode as pc
from radboy.DB.renderText2Png import *
from radboy.DB.Prompt import *
from radboy.DB.DatePicker import *
from radboy.FB.FBMTXT import *
import geocoder
import forecast_weather as fw
import requests
import holidays
import platform
from uuid import uuid1
import sys

class switch_bootable:
    '''Template Cmd
str(uuid1()):{
    'cmds':[],
    'exec':None,
    'desc':""
    },

    '''
    def quick_parse(self,text,helptext='',no_dir_name=False):
        if text.lower() in ['',]:
            if no_dir_name:
                return ''
            else:
                text=f"BOOTABLE {datetime.now().strftime('%m-%d-%Y')}"
            return text
        elif text.lower() in ['q','quit']:
            exit("User quit!")
        elif text.lower() in ['b','back']:
            return None
        elif text.lower() in ['?','h','help']:
            print(helptext)
            return False
        else:
            return text

    def quick_parse_int(self,text,helptext=''):
        if text.lower() in ['',]:
            return None
        elif text.lower() in ['q','quit',]:
            exit("User quit!")
        elif text.lower() in ['b','back']:
            return None
        elif text.lower() in ['?','h','help']:
            print(helptext)
            return False
        else:
            try:
                val=int(text)
                return val
            except Exception as e:
                return None

    def mkBootBlank(self):
        try:
            while True:
                bootdirname=self.quick_parse(input("Bootable Directory Name:"))
                if bootdirname is None:
                    return
                elif bootdirname is False:
                    continue
                else:
                    break
            bt=self.boot_dirs/Path(bootdirname)
            if not bt.exists():
                bt.mkdir(parents=True)
            with open(bt/Path("__bootable__.py"),"wb") as bootfile:
                bootfile.write(b'')
        except Exception as e:
            print(e,repr(e),str(e))


    def cmdSystem(self):
        cmds={
        str(uuid1()):{
        'cmds':["mkblnkbt","mk_blnk_bt","make blank bootdir","mk blnk bt"],
        'exec':self.mkBootBlank,
        'desc':"make a new bootable instance directory that is completely blank"
        },
        str(uuid1()):{
            'cmds':['list boot','lsbt','lsboot','ls boot'],
            'exec':self.lsboot,
            'desc':"list boot dirs"
        }, 
        str(uuid1()):{
            'cmds':['boot','','bt'],
            'exec':self.legacy_start,
            'desc':"start the system by selecting instance"
            },     
        }
        cmdhtext=[]
        ct=len(cmds)
        for num,i in enumerate(cmds):
            msg=self.static_colorize(f"{Fore.light_green}{cmds[i]['cmds']} - {Fore.green_yellow}{cmds[i]['desc']}",num,ct)
            cmdhtext.append(msg)
        cmdhtext='\n'.join(cmdhtext)

        while True:
            doWhat=self.quick_parse(input("Boot CMDS:"),helptext=cmdhtext,no_dir_name=True)
            if doWhat is None:
                exit("User Quit!")
            elif doWhat is False:
                continue
            for cmd in cmds:
                if doWhat.lower() in [str(i) for i in cmds[cmd]['cmds']]:
                    if callable(cmds[cmd]['exec']):
                        ready=cmds[cmd]['exec']()
                        print(ready)
                        if ready is True:
                            return
                        break
                    else:
                        print(f"cmd({cmds[cmd]['cmds']}) is not callable()")

    def static_colorize(self,m,n,c):
        msg=f'{Fore.cyan}{n}/{Fore.light_yellow}{n+1}{Fore.light_red} of {c} {Fore.dark_goldenrod}{m}{Style.reset}'
        return msg

    def __init__(self):
        self.boot_dirs=Path("RadBoy_Boot_Directory")
        self.cmdSystem()


        #self.legacy_start()

    def lsboot(self):
        boot_dirs=self.boot_dirs
        if not boot_dirs.exists():
            boot_dirs.mkdir()
        bootable_dirs=[]
        bootable_dirs.append(str(Path(".").absolute()))
        for root,dirs,files in boot_dirs.walk(top_down=True):
            for d in dirs:
                dsub=root/d
                if dsub not in bootable_dirs:
                    bootcfg=dsub/Path("__bootable__.py")
                    if bootcfg.exists():
                        bootable_dirs.append(dsub)

        htext=[]
        ct=len(bootable_dirs)
        for num,i in enumerate(bootable_dirs):
            msg=f"{Fore.light_green}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct} -> {Fore.dark_goldenrod}{i}{Style.reset}"
            htext.append(msg)
        htext='\n'.join(htext)
        print(htext)
        return bootable_dirs

    def legacy_start(self):
        boot_dirs=self.boot_dirs
        if not boot_dirs.exists():
            boot_dirs.mkdir()

        while True:
            try:
                bootable_dirs=[]
                bootable_dirs.append(str(Path(".").absolute()))
                for root,dirs,files in boot_dirs.walk(top_down=True):
                    for d in dirs:
                        dsub=root/d
                        if dsub not in bootable_dirs:
                            bootcfg=dsub/Path("__bootable__.py")
                            if bootcfg.exists():
                                bootable_dirs.append(dsub)

                htext=[]
                ct=len(bootable_dirs)
                for num,i in enumerate(bootable_dirs):
                    msg=f"{Fore.light_green}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct} -> {Fore.dark_goldenrod}{i}{Style.reset}"
                    htext.append(msg)
                htext='\n'.join(htext)
                if ct > 0:
                    print(htext)
                    which=input("Please type an integer index for selection: ")
                    if which.lower() in ['d','']:
                        return True
                    elif which.lower() in ['b',]:
                        break
                    elif which.lower() in ['q','quit']:
                        exit("User chose to quit!")
                    try:
                        which=int(which)
                        os.chdir(bootable_dirs[which])
                        return True
                    except Exception as e:
                        print(e)
                else:
                    print("No Bootable Directories found!")
                    return True
            except Exception as e:
                print(e)
switch_bootable()

def onAndroid()->bool:
    '''returns True if on Android

    else, return False
    '''
    if hasattr(sys,"getandroidapilevel"):
        return True
    else:
        return False


'''Class Entry is the main product table.'''
AGELIMIT=7*24*60*60
def roundup(number):
    return math.ceil(number*100)/100

filename="codesAndBarcodes.db"
DEVMOD=False
if DEVMOD:
    if Path(filename).exists():
        Path(filename).unlink()
dbfile="sqlite:///"+str(filename)
img_dir=Path("Images")
if not img_dir.exists():
    img_dir.mkdir()
print(dbfile)
#import sqlite3
#z=sqlite3.connect(filename)
#print(z)
ENGINE=create_engine(dbfile)
BASE=dbase()
#BASE.prepare(autoload_with=ENGINE)
img_dir=Path("Images")
def reInit(f=None,dbf=None):
    filename="codesAndBarcodes.db"
    dbfile="sqlite:///"+str(filename)
    if f:
        filename=f
    if dbf:
        dbfile=dbf
    if Path(filename).exists():
        Path(filename).unlink()
    ENGINE=create_engine(dbfile)
    Entry.metadata.create_all(ENGINE)
    DayLog.metadata.create_all(ENGINE)
    try:
        img_dir=Path("Images")
        if not img_dir.exists():
            img_dir.mkdir()
        else:
            shutil.rmtree(img_dir)
            img_dir.mkdir()
    except Exception as e:
        print(e)

    exit(f"A {Style.bold}{Style.underline}{Fore.yellow}Factory Reset{Style.reset} was performed. A {Style.bold}{Style.underline}{Fore.yellow}Restart{Style.reset} is {Style.bold}{Style.underline}{Fore.yellow}Required{Style.reset}.")

LOCATION_FIELDS=[
        'Shelf',
        'BackRoom',
        'Display_1',
        'Display_2',
        'Display_3',
        'Display_4',
        'Display_5',
        'Display_6',
        'SBX_WTR_DSPLY',
        'SBX_CHP_DSPLY',
        'SBX_WTR_KLR',
        'FLRL_CHP_DSPLY',
        'FLRL_WTR_DSPLY',
        'WD_DSPLY',
        'CHKSTND_SPLY',
        'Distress',
        'ListQty'
        ]

def strip_colors(colored_text):
    text=colored_text
    colors=[getattr(Fore,i) for i in Fore._COLORS]
    colors2=[getattr(Fore,i) for i in Back._COLORS]
    styles3=[getattr(Style,i) for i in Style._STYLES]
    #text=''.join([i for i in text if i in string.printable])
    escape_codes=[]
    escape_codes.extend(colors)
    escape_codes.extend(colors2)
    escape_codes.extend(styles3)
    for i in escape_codes:
        text=text.replace(i,'')
    return text

class tagList:
    """Add or Remove Tags from Entry class."""
    def remTag(self,session,entry,tag):
        try:
            old=list(json.loads(entry.Tags))
            if tag not in old:
                return
            tmp=[]
            for t in old:
                if t != tag:
                    tmp.append(t)
            entry.Tags=json.dumps(tmp)
        except Exception as e:
            print(e)
            print(f"{Fore.cyan}Correcting with {[]}{Style.reset}")
            entry.Tags=json.dumps([])
        session.commit()
        session.flush()
        session.refresh(entry)

    def addTag(self,session,entry,tag):
        try:
            old=list(json.loads(entry.Tags))
            if tag not in old:
                old.append(tag)
            entry.Tags=json.dumps(old)
        except Exception as e:
            print(e)
            print(f"{Fore.cyan}Correcting with {[tag,]}...{Style.reset}")
            entry.Tags=json.dumps([tag,])
        session.commit()
        session.flush()
        session.refresh(entry)

    def __init__(self,engine,state=True,tag='ReverseInventory',removeTag=["have/has",]):
        t="System"
        if tag == None:
            t="Personal"
            while True:
                try:
                    def mkT(text,self):
                        return text
                    stated='Add to'
                    if not state:
                        stated="Remove from"
                    tag=Prompt.__init2__(None,func=mkT,ptext="Tag",helpText=f"Personal Tag to {stated} Enties.Tag where Entry.InList==True")
                    if tag in [None,]:
                        return
                    break
                except Exception as e:
                    print(e)
        with Session(engine) as session:
            results=session.query(Entry).filter(Entry.InList==True).all()
            ct=len(results)
            for num,r in enumerate(results):
                if num%2==0:
                    color_Alt=Fore.green_yellow
                    color_Alt2=Fore.dark_goldenrod
                else:
                    color_Alt=Fore.medium_violet_red
                    color_Alt2=Fore.pale_violet_red_1

                msg=f'{color_Alt}{num+1}/{color_Alt2}{ct}{Style.reset} - {r.seeShort()}'
                print(msg)
                if state == True:
                    self.addTag(session,r,f'#{tag}@{t}')
                    if t != 'Personal':
                        for ta in removeTag:
                            self.remTag(session,r,f'#{ta}@{t}')
                elif state == False:
                    self.remTag(session,r,f'#{tag}@{t}')

def copySrc(self,entry):
    """Copy src image to Entry.Image."""
    while True:
        try:
            def mkPath(text,self):
                try:
                    p=Path(text)
                    if p.exists() and p.is_file():
                        return Path(p)
                    else:
                        if p.exists() and not p.is_file():
                            raise Exception(f"Not a File '{text}'")
                        elif not p.exists():
                            raise Exception(f"Does not Exist '{text}'!")
                        else:
                            raise Exception(text)
                except Exception as e:
                    print(e)
            fromPath=Prompt.__init2__(None,func=mkPath,ptext=f"From where",helpText="what image do you want to copy to Entry.Image?",data=self)
            if fromPath in [None,]:
                return
            ifilePath=fromPath
            ofilePath=Path(img_dir)/Path(f"{entry.EntryId}{ifilePath.suffix}")
            value=str(ofilePath.absolute())
            entry.Image=value


            with ifilePath.open("rb") as ifile,ofilePath.open("wb") as ofile:
                while True:
                    d=ifile.read(1024*1024)
                    if not d:
                        break
                    ofile.write(d)
            print(f"{Fore.light_green}{str(ifilePath.absolute())}{Fore.light_yellow} -> {Fore.light_red}{str(ofilePath.absolute())}{Style.reset}")
            break
        except Exception as e:
            print(e)

def removeImage(image_dir,img_name):
    """Remove Image using Path(image_dir)/Path(img_name)."""
    try:
        if img_name != '':
            im=Path(image_dir)/Path(img_name)
            if im.exists():
                im.unlink()
                print(f"{im} removed from FS!")
    except Exception as e:
        print(e)

def importImage(image_dir,src_path,nname=None,ow=False):
    try:
        if not Path(image_dir).exists():
            Path(image_dir).mkdir()
        if not nname:
            dest=Path(image_dir)/Path(Path(src_path).name)
        else:
            dest=Path(image_dir)/Path(nname)
        if not ow and dest.exists():
            raise Exception(f'exists {dest}')
        if not Path(src_path).exists():
            raise Exception (f'src {src_path} does not exist!')
        size=Path(src_path). stat().st_size
        with dest.open('wb') as out, Path(src_path).open('rb') as ifile:
            while True:
                d=ifile.read(1024*1024)
                print(f'writing {len(d)} - {ifile.tell()}/{size}')
                if not d:
                    break
                out.write(d)
        return str(dest)
    except Exception as e:
        print(e)
        return ''

def save_results(query):
    while True:
        save_results=input(f"Save Results {Fore.cyan}y{Style.reset}|{Fore.yellow}N{Style.reset}] : ")
        if save_results.lower() in ['n','no']:
            return
        elif save_results.lower() in ['y','yes']:
            df = pd.read_sql(query.statement, query.session.bind,dtype=str)
            while True:
                saveTo=input("save to: ")
                print(f"Saving to '{Path(saveTo)}'!")
                if Path(saveTo).parent.exists():
                    df.to_csv(saveTo,index=False)
                    return
                print(Path(saveTo))
        else:
            print("Invalid Entry!")

class PairCollection(BASE):
    '''A Basic Class for collecting Barcodes where Barcode,Code, and Name are stored.'''
    __tablename__="PairCollection"
    Barcode=Column(String)
    Code=Column(String)
    PairCollectionId=Column(Integer,primary_key=True)
    Name=Column(String)

    def __init__(self,Barcode,Code,Name='',PairCollectionId=None):
        if PairCollectionId:
            self.PairCollectionId=PairCollectionId
        self.Name=Name
        self.Barcode=Barcode
        self.Code=Code

    def __repr__(self):
        msg=f'''PairCollection(
            Barcode='{self.cfmt(self.Barcode)}',
            Code='{self.cfmt(self.Code)}',
            Name='{self.Name}',
            PairCollectionId={self.PairCollectionId},
        )'''
        return msg

    def __str__(self):
        msg=f'''PairCollection(
            {Fore.green}Barcode='{self.Barcode}',{Style.reset}
            {Fore.green_yellow}Code='{self.Code}',{Style.reset}
            {Fore.dark_goldenrod}Name='{self.Name}',{Style.reset}
            {Fore.yellow}PairCollectionId={self.PairCollectionId},{Style.reset}
        )'''
        return msg
    LCL=Path("LCL_IMG")
    LCL_ANDROID=Path("/storage/emulated/0/DCIM/Screenshots")

    def save_code(self):
        filename=Path(f"{self.PairCollectionId}_code.png")
        if self.LCL_ANDROID.exists():
            filename=str(self.LCL_ANDROID/filename)
        else:
            filename=str(self.LCL/filename)
        print(filename)
        try:
            codes=[Code39,QRCode]
            for code in codes:
                try:
                    if code == QRCode:
                        qrcode.make(self.Code).save(filename)
                        break
                    else:
                        code(self.Code,add_checksum=False,writer=ImageWriter()).write(filename)
                        break
                    pass
                except Exception as e:
                    print(e)


            return filename
        except Exception as e:
            print(e)
        return False

    def save_barcode(self):
        filename=Path(f"{self.PairCollectionId}_barcode.png")
        if self.LCL_ANDROID.exists():
            filename=str(self.LCL_ANDROID/filename)
        else:
            filename=str(self.LCL/filename)
        print(filename)
        try:
            codes=[UPCA,EAN13,QRCode]
            for code in codes:
                try:
                    if code == QRCode:
                        qrcode.make(self.Barcode).save(filename)
                        break
                    else:
                        if len(self.Barcode) <= 8 and code == UPCA:
                            upca=upcean.convert.convert_barcode_from_upce_to_upca(self.Barcode)
                            if upca != False:
                                code(upca,writer=ImageWriter()).write(filename)
                            else:
                                continue
                        elif len(self.Barcode) > 12:
                            if code == EAN13:
                                code(self.Barcode,writer=ImageWriter()).write(filename)
                            else:
                                continue
                        else:
                            code(self.Barcode,writer=ImageWriter()).write(filename)
                        break
                except Exception as e:
                    print(e)
            return filename


        except Exception as e:
            print(e)
        return False

    def saveItemData(self,num=None):
        if self.LCL_ANDROID.exists():
            self.LCL=self.LCL_ANDROID
        text=[]
        for column in self.__table__.columns:
            text.append('='.join([column.name,str(self.__dict__[column.name])]))
        data='\n'.join(text)
        #LCL=Path("LCL_IMG")
        if not self.LCL.exists():
            self.LCL.mkdir()
        fname=str(self.LCL/Path(str(self.PairCollectionId)))
        n=self.save_barcode()
        c=self.save_code()
        print(n,c)
        renderImageFromText(fname,data,barcode_file=n,code_file=c)

    def listdisplay(self,num=None):
        name=self.Name
        ma=32
        n=self.split_by_len(name,ma)
        #print(n)
        new=[]
        for i in n:
            if n.index(i) > 0:
                new.append(i)
            else:
                new.append(i)
        name='\n'.join(new)
        name="\n"+name
        if num == None:
            num=''
        msg=f'''{Fore.magenta}{Fore.dark_goldenrod}{num}->({Style.reset} NAME={Fore.cyan}{name}{Style.reset} | UPC={Fore.green}{self.Barcode}{Style.reset} | CODE={Fore.yellow}{self.cfmt(self.Code)}{Style.reset} |{self.PairCollectionId}{Style.reset}{Fore.magenta} )-<{Fore.dark_goldenrod}{num}{Style.reset}'''
        print(msg)
    def split_by_len(self,string, length):
        result = []
        for i in range(0, len(string), length):
            result.append(string[i:i + length])
        return result

class NOCREATION(Exception):
    pass

class EntryExtras:
    '''Add options to EntryClass through inheritance.'''
    def __add__(self,val):
        return self.Price+val
    def __sub__(self,val):
        return self.Price-val
    def __truediv__(self,val):
        return self.Price/val
    def __mul__(self,val):
        return self.Price*val
    def __pow__(self,val):
        return self.Price**val
    def __floordiv__(self,val):
        return self.Price//val
    def __mod__(self,val):
        return self.Price%val

    def __radd__(self,val):
        return self.Price+val

    def __rsub__(self,val):
        return self.Price-val

    def __rtruediv__(self,val):
        return self.Price/val

    def __rmul__(self,val):
        return self.Price*val

    def __rpow__(self,val):
        return self.Price**val

    def __rfloordiv__(self,val):
        return self.Price//val

    def __rmod__(self,val):
        return self.Price%val

    def __iadd__(self,val):
        self.Price+=val
        return self
    def __isub__(self,val):
        self.Price-=val
        return self
    def __itruediv__(self,val):
        self.Price/=val
        return self
    def __imul__(self,val):
        self.Price*=val
        return self
    def __ipow__(self,val):
        self.Price**=val
        return self
    def __ifloordiv__(self,val):
        self.Price//=val
        return self
    def __imod__(self,val):
        self.Price%=val  
        return self

    def __pos__(self):
        return +self.Price
    def __neg__(self):
        return -self.Price

class Template:
    def colorize(self,m,n,c):
        msg=f'{Fore.cyan}{n}/{Fore.light_yellow}{n+1}{Fore.light_red} of {c} {Fore.dark_goldenrod}{m}{Style.reset}'
        return msg

    def cfmt(self,line,n=4):
        if not line:
            line='None'
        '''Colorize Format Code Data For terminal display for quick reading.'''
        x=[line[i:i+n] for i in range(0,len(line),n)]
        second=x[0][1:]
        first=x[0][0]
        #untouched last element of x
        lastblock=x[-1]
        for num,i in enumerate(x):
            if num % 2 == 0:
                x[num]=f"{Fore.cyan}{x[num]}{Style.reset}"
            else:
                x[num]=f"{Fore.light_steel_blue}{x[num]}{Style.reset}"
        cformat=f'{DEFAULT_SEPARATOR_CHAR}'.join(x)
        return cformat

    def init(self,**kwargs):
        __tablename__=kwargs.get("__tablename__")
        fields=[i.name for i in self.__table__.columns]
        for i in fields:
            if i in list(kwargs.keys()):
                setattr(self,i,kwargs.get(i))

    def __str__(self,vc=Fore.dark_blue+Style.bold,fc=Fore.light_green,cc=Fore.light_magenta,vg=Back.grey_50):
        m=[]
        now=datetime.now()
        microid=now.timestamp()
        nowStr=now.strftime(" -> Time:%I:%M:%S %p(12)/%H:%M:%S(24H)\nDate:%m/%d/%Y")+f" Timestamp:{microid}\n"
        m.append(f"{nowStr} -> {cc}{self.__tablename__}{Style.reset}(")
        fields=[i.name for i in self.__table__.columns]
        ft={i.name:str(i.type).lower() for i in self.__table__.columns}
        nsc={
        0:Fore.green_yellow
        }
        settting=0
        for num,i in enumerate(fields):
            if isinstance(getattr(self,i),time):

                m.append(f"{fc}{i}{nsc[settting]}[{ft[i]}]{fc}={vg}{Style.bold}{nsc[settting]}'{fc}{vc}{getattr(self,i).strftime(f"{Fore.deep_pink_4a}%I:%M %p(12H)/{Fore.dark_red_1}%H:%M(24H)")}{nsc[settting]}'{Style.reset}{Back.black}")
            elif isinstance(getattr(self,i),datetime):
                m.append(f"{fc}{i}{nsc[settting]}[{ft[i]}]{fc}={vg}{Style.bold}{nsc[settting]}'{fc}{vc}{getattr(self,i).strftime(f"{Fore.deep_sky_blue_4a}%m/%d/%Y @ {Fore.deep_pink_4a}%I:%M %p(12H) / {Fore.dark_red_1}%H:%M(24H)")}{nsc[settting]}'{Style.reset}{Back.black}")
            else:
                m.append(f"{fc}{i}{nsc[settting]}[{ft[i]}]{fc}={vg}{Style.bold}{nsc[settting]}'{fc}{vc}{getattr(self,i)}{nsc[settting]}'{Style.reset}{Back.black}")
        m.append(f") {Fore.dark_goldenrod}{nowStr.replace("\n","")}{Style.reset}")
        return '\n'.join(m)

    def __repr__(self,vc=Fore.dark_blue+Style.bold,fc=Fore.light_green,cc=Fore.light_magenta,vg=Back.grey_50):
        return self.str(self,vc,fc,cc,vg)


class EntryDataExtras(BASE,Template):
    '''Stores extra fields not in the Entry Class.
    
    will be used with esu searches
    extras will be added under the neu menu
    data is default stored as large binary, if a serializable format is found then use that but must be usable between python versions
    '''
    
    __tablename__="EntryDataExtras"
    field_name=Column(String)
    field_type=Column(String)
    field_value=Column(String)
    doe=Column(DateTime,default=datetime.now())
    EntryId=Column(Integer)
    ede_id=Column(Integer,primary_key=True)
    
    def __init__(self,*args,**kwargs):
        fields=[i.name for i in self.__table__.columns]
        for k in kwargs:
            if k in fields:
                if k in ('field_note','field_value','field_value','field_name'):
                    if k == 'field_name' and 'EntryId' in kwargs.keys():
                        with Session(ENGINE) as session:
                            check=session.query(self.__class__).filter(self.__class__.field_name==kwargs[k],self.__class__.EntryId==kwargs['EntryId']).first()
                            if isinstance(check,self.__class__):
                                if check.field_value == kwargs['field_value']:
                                    raise Exception(f"Value is duplicated for {k}={kwargs['field_value']}")
                                else:
                                    dateStr=datetime.now().strftime("[Updated on %m/%d/%Y at %H:%M:%S.]")
                                    kwargs[k]=f"{kwargs[k]} {dateStr}"
                    setattr(self,k,str(kwargs[k]))
                else:
                    setattr(self,k,kwargs[k])
            else:
                print(k,kwargs,fields,"not in fields")
                
EntryDataExtras.metadata.create_all(ENGINE)



class Entry(BASE,EntryExtras):
    def cfmt(self,line,n=4):
        if not line:
            line='None'
        '''Colorize Format Code Data For terminal display for quick reading.'''
        x=[line[i:i+n] for i in range(0,len(line),n)]
        second=x[0][1:]
        first=x[0][0]
        #untouched last element of x
        lastblock=x[-1]
        for num,i in enumerate(x):
            if num % 2 == 0:
                x[num]=f"{Fore.cyan}{x[num]}{Style.reset}"
            else:
                x[num]=f"{Fore.light_steel_blue}{x[num]}{Style.reset}"
        cformat=f'{DEFAULT_SEPARATOR_CHAR}'.join(x)
        return cformat
    '''Stores Product Entry Details.

    Code -> shelf tag code, cic, store code
    Barcode -> Barcode found on product packaging used for internal tracking
    Name -> what the product identified by barcode, or code, is called
    Price -> How much the product costs
    CRV -> crv tax value
    Tax -> taxes added onto product
    TaxNote -> extra info related to taxes
    Note -> temporary info related to product
    Description -> Describe the product
    Size -> how big is it?
    CaseCount -> CasePack; how much comes in a case ordered of product
    Shelf,Distress,BackRoom,Display_1,Display_2,
    Display_3,Display_4,Display_5,Display_6,SBX_WTR_DSPLY,
    SBX_CHP_DSPLY,SBX_WTR_KLR,FLRL_CHP_DSPLY,ListQty,
    FLRL_WTR_DSPLY,WD_DSPLY,CHKSTND_SPLY -> Qty fields
    InList -> is the product being used with a value in any of the above Location fields
    Location -> where is the product stored using Aisle/Shelf Module/Shelf Number
    ALT_Barcode -> alternate code that the entry might be under
    DUP_Barcode -> duplicate barcode
    CaseID_BR -> Backroom case id
    CaseID_LD -> Load case id
    CaseID_6W -> 6-wheeler case id
    Tags -> extra search terms to help id/group product stored
    Facings -> how many units wide a product is across total shelves product is stored
    UnitsHigh -> how many units high of product that can be stacked
    UnitsDeep -> how many units can fit in a straight line to the back of the shelf, unstacked
    LoadCount -> how many units come in on load
    PalletCount -> how many units come in on a pallet
    ShelfCount -> how many units can fit on the shelf
    '''
    __tablename__="Entry"
    Code=Column(String)
    Barcode=Column(String)
    Distress=Column(Integer,default=0)
    
    Name=Column(String)
    Price=Column(Float,default=0.0)
    CRV=Column(Float,default=0.0)
    Tax=Column(Float,default=0.0)
    TaxNote=Column(String,default=f'''
{Fore.light_green}What's taxable at a California grocery store?{Style.reset}
    {Fore.orange_red_1}Drinks:{Style.reset}
        {Fore.light_steel_blue}Alcoholic beverages{Style.reset}
        {Fore.light_steel_blue}Carbonated and effervescent water{Style.reset}
        {Fore.light_steel_blue}Carbonated soft drinks and mixes{Style.reset}
        {Fore.light_steel_blue}Kombucha tea (if the alcohol content is 0.5% or greater by volume){Style.reset}
    {Fore.orange_red_1}Entertainment:{Style.reset}
        {Fore.light_steel_blue}Books and publications{Style.reset}
        {Fore.light_steel_blue}Cameras and film{Style.reset}
        {Fore.light_steel_blue}Newspapers and periodicals{Style.reset}
    {Fore.orange_red_1}Medications, cosmetics, household items{Style.reset}
        {Fore.light_steel_blue}Cosmetics{Style.reset}
        {Fore.light_steel_blue}Dietary supplements{Style.reset}
        {Fore.light_steel_blue}Drug sundries, toys, hardware, and household goods{Style.reset}
        {Fore.light_steel_blue}Medicated gum (Nicorette, Aspergum){Style.reset}
        {Fore.light_steel_blue}Over-the-counter medicines, such as aspirin, cough syrups, cough drops, throat lozenges, and so forth{Style.reset}
        {Fore.light_steel_blue}Soaps or detergents{Style.reset}
    {Fore.orange_red_1}Food-related{Style.reset}
        {Fore.light_steel_blue}Ice{Style.reset}
        {Fore.light_steel_blue}Hot prepared food products{Style.reset}
        {Fore.light_steel_blue}Food sold for consumption on your premises (see Foodservice operations){Style.reset}
        {Fore.light_steel_blue}Pet food and supplies{Style.reset}
    {Fore.dark_goldenrod}Some items were more difficult to place in specific categories but included "Nursery stock," "Prepaid Mobile Telephony Services," "Sporting goods," "Clothing," and "Fixtures and equipment used in an activity requiring the holding of a seller's permit, if sold at retail."{Style.reset}
{Fore.light_green}What can't be taxed at a California grocery store?{Style.reset}
    {Fore.orange_red_1}Nutrition{Style.reset}
        {Fore.light_steel_blue}Baby formulas (including Isomil){Style.reset}
        {Fore.light_steel_blue}Edge Bars, Energy Bars, Power Bars{Style.reset}
        {Fore.light_steel_blue}Pedialyte{Style.reset}
        {Fore.light_steel_blue}Noncarbonated sports drinks ( Gatorade, Powerade, All-Sport){Style.reset}
    {Fore.orange_red_1}Food-related{Style.reset}
        {Fore.light_steel_blue}Cooking wine{Style.reset}
        {Fore.light_steel_blue}Food products{Style.reset}
        {Fore.light_steel_blue}Granola Bars{Style.reset}
    {Fore.orange_red_1}Drinks{Style.reset}
        {Fore.light_steel_blue}Kombucha tea (if less than 0.5 percent alcohol by volume and naturally effervescent){Style.reset}
        {Fore.light_steel_blue}Martinelli's Sparkling Cider{Style.reset}
        {Fore.light_steel_blue}Water — bottled noncarbonated, noneffervescent drinking water{Style.reset}
    {Fore.dark_goldenrod}According to the California Department of Tax and Fee Administration, taxes also don't generally apply to food products that people eat or nutritional drinks that are milk and juice-based and promote themselves as having additional nutrients.
For hot food, one of the notable exceptions is "Hot Baked Goods," like pretzels or croissants that are sold to go.{Style.reset}
''')
    Note=Column(String,default='')
    Description=Column(String,default='')
    Size=Column(String,default='Units/Eaches')
    
    CaseCount=Column(Integer,default=1)

    Shelf=Column(Integer,default=0)
    BackRoom=Column(Integer,default=0)
    Display_1=Column(Integer,default=0)
    Display_2=Column(Integer,default=0)
    Display_3=Column(Integer,default=0)
    Display_4=Column(Integer,default=0)
    Display_5=Column(Integer,default=0)
    Display_6=Column(Integer,default=0)
    InList=Column(Boolean,default=True)
    Stock_Total=Column(Integer,default=0)
    Location=Column(String,default='///')
    userUpdated=Column(Boolean,default=False)
    ListQty=Column(Float,default=0)
    upce2upca=Column(String,default='')
    Image=Column(String,default=' ')
    EntryId=Column(Integer,primary_key=True)
    Timestamp=Column(Float,default=datetime.now().timestamp())

    ALT_Barcode=Column(String,default='')
    DUP_Barcode=Column(String,default='')
    CaseID_BR=Column(String,default='')
    CaseID_LD=Column(String,default='')
    CaseID_6W=Column(String,default='')
    Tags=Column(String,default='[]')
    Facings=Column(Integer,default=1)
    UnitsHigh=Column(Integer,default=1)
    UnitsDeep=Column(Integer,default=1)
    SBX_WTR_DSPLY=Column(Integer,default=0)
    SBX_CHP_DSPLY=Column(Integer,default=0)
    SBX_WTR_KLR=Column(Integer,default=0)
    FLRL_CHP_DSPLY=Column(Integer,default=0)
    FLRL_WTR_DSPLY=Column(Integer,default=0)
    WD_DSPLY=Column(Integer,default=0)
    CHKSTND_SPLY=Column(Integer,default=0)

    #How Much Typically Comes in Load
    LoadCount=Column(Integer,default=0)
    #If product comes in pallets at a time, fill with how much comes
    PalletCount=Column(Integer,default=0)
    #how much can be held on the shelf at the time
    ShelfCount=Column(Integer,default=0)
    #LoadCount=1,PalletCount=1,ShelfCount=1

    def csv_headers(self):
        headers=[]
        for i in self.__table__.columns:
            headers.append(i.name)
        headers.append("DateFromTimeStamp")
        return headers

    def csv_values(self):
        values=[]
        for i in self.__table__.columns:
            value=self.__dict__.get(i.name)
            if isinstance(value,str):
                value=value.replace("\n","$NEWLINECHAR$").replace("\t","$TABCHAR$").replace(",","$COMMA$")
            values.append(value)
        values.append(datetime.fromtimestamp(self.Timestamp).ctime())
        print(f"""use: 
{Fore.light_blue}$NEWLINECHAR$ for {Fore.light_yellow}\\n{Style.reset} is for line ending
{Fore.light_blue}$TABCHAR$ for {Fore.light_yellow}\\t{Style.reset}
{Fore.light_blue}$COMMA$ for {Fore.light_yellow},{Style.reset} as {Fore.light_yellow},{Style.reset} is csv delimiter
                    """)
        return values
    def synthetic_field_str(self):
        f=string.ascii_uppercase+string.digits
        part=[]
        for num in range(4):
            part.append(f[random.randint(0,len(f)-1)])
        part.append("-")
        for num in range(4):
            part.append(f[random.randint(0,len(f)-1)])
        return ''.join(part)

    def copySrc(self):
        if self.Image in ['',None]:
            try:
                while True:
                    try:
                        def mkPath(text,self):
                                if text.lower() == '':
                                    return
                                p=Path(text)
                                if p.exists() and p.is_file():
                                    return Path(p)
                                else:
                                    if p.exists() and not p.is_file():
                                        raise Exception(f"Not a File '{text}'")
                                    elif not p.exists():
                                        raise Exception(f"Does not Exist '{text}'!")
                                    else:
                                        raise Exception(text)
                        fromPath=Prompt.__init2__(None,func=mkPath,ptext=f"Image From where",helpText="what image do you want to copy to Entry.Image? @This pt. The Entry Is Made Any attempt to stop has already failed!",data=self)
                        if fromPath in [None,]:
                            return

                        ifilePath=fromPath
                        ofilePath=Path(img_dir)/Path(f"{self.EntryId}{ifilePath.suffix}")
                        value=str(ofilePath)
                        self.Image=value
                        

                        with ifilePath.open("rb") as ifile,ofilePath.open("wb") as ofile:
                            while True:
                                d=ifile.read(1024*1024)
                                if not d:
                                    break
                                ofile.write(d)
                        print(f"{Fore.light_green}{str(ifilePath.absolute())}{Fore.light_yellow} -> {Fore.light_red}{str(ofilePath.absolute())}{Style.reset}")
                        break
                    except Exception as e:
                        print(e)
                    
                        
            except Exception as e:
                print(e)

    def fromDefaults(self):
        '''Set Defaults for Entry.'''
        excludes=['Barcode','Code','Name','EntryId','Timestamp']
        for c in [s.name for s in self.__table__.columns if s.name not in excludes]:
            setattr(self,c,None)

    def fromDictionary(self,**kwargs):
        '''Set fields from Dictionary at kwargs'''
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))

    def __init__(self,Barcode,Code,upce2upca='',Name='',InList=True,Price=0.0,Note='',Size='',CaseCount=1,Shelf=0,BackRoom=0,Display_1=0,Display_2=0,Display_3=0,Display_4=0,Display_5=0,Display_6=0,Stock_Total=0,Timestamp=datetime.now().timestamp(),EntryId=None,Location='///',ListQty=0.0,Image='',CHKSTND_SPLY=0,WD_DSPLY=0,FLRL_CHP_DSPLY=0,FLRL_WTR_DSPLY=0,SBX_WTR_KLR=0,SBX_CHP_DSPLY=0,SBX_WTR_DSPLY=0,Facings=0,Tags='',CaseID_6W='',CaseID_BR='',CaseID_LD='',ALT_Barcode='',DUP_Barcode='',CRV=0.0,Tax=0.0,TaxNote='',userUpdated=False,LoadCount=1,PalletCount=1,ShelfCount=1,Description='',Distress=0,UnitsDeep=1,UnitsHigh=1):
        if EntryId:
            self.EntryId=EntryId
        self.CRV=CRV
        self.userUpdated=userUpdated
        self.Tax=Tax
        self.Description=Description
        self.TaxNote=TaxNote
        self.Barcode=Barcode
        self.Code=Code
        self.Name=Name
        self.Price=Price
        self.Note=Note
        self.Size=Size
        self.Shelf=Shelf
        self.CaseCount=CaseCount
        self.BackRoom=BackRoom
        self.Display_1=Display_1
        self.Display_2=Display_2
        self.Display_3=Display_3
        self.Display_4=Display_4
        self.Display_5=Display_5
        self.Display_6=Display_6
        self.Stock_Total=Stock_Total
        self.Location=Location
        self.Timestamp=Timestamp
        self.InList=InList
        self.ListQty=ListQty
        self.upce2upca=upce2upca
        self.Image=Image
        self.Tags=Tags
        self.Facings=Facings
        self.Distress=Distress
        self.ALT_Barcode=ALT_Barcode
        if InList == '':
            InList=True
        self.UnitsHigh=UnitsHigh
        self.UnitsDeep=UnitsDeep
        if isinstance(userUpdated,str):
            try:
                self.InList=eval(InList)
            except Exception as e:
                self.InList=True

        if userUpdated == '':
            self.userUpdated=False
        if isinstance(userUpdated,str):
            try:
                self.userUpdated=eval(userUpdated)
            except Exception as e:
                self.userUpdated=False
        try:
            #print(f'{Style.bold+Style.underline+Fore.orange_red_1}X{Style.reset}')
            if len(self.Barcode) == 8:

                if self.ALT_Barcode == '':
                    #print(f'{Fore.light_yellow}X{Style.reset}')
                    self.ALT_Barcode=upcean.convert.convert_barcode_from_upce_to_upca(upc=self.Barcode)
                    if not isinstance(self.ALT_Barcode,str):
                        print(f"{Fore.light_yellow}ALT_Barcode=={self.ALT_Barcode}{Style.reset}")
                        self.ALT_Barcode=''
        except Exception as e:
            print(repr(e),str(e),e)
        
        self.DUP_Barcode=DUP_Barcode
        self.CaseID_BR=CaseID_BR
        self.CaseID_LD=CaseID_LD
        self.CaseID_6W=CaseID_6W
        self.SBX_WTR_DSPLY=SBX_WTR_DSPLY
        self.SBX_CHP_DSPLY=SBX_CHP_DSPLY
        self.SBX_WTR_KLR=SBX_WTR_KLR
        self.FLRL_CHP_DSPLY=FLRL_CHP_DSPLY
        self.FLRL_WTR_DSPLY=FLRL_WTR_DSPLY
        self.WD_DSPLY=WD_DSPLY
        self.CHKSTND_SPLY=CHKSTND_SPLY
        self.ShelfCount=ShelfCount
        self.PalletCount=PalletCount
        self.LoadCount=LoadCount
        #CHKSTND_SPLY=0,WD_DSPLY=0,FLRL_CHP_DSPLY=0,FLRL_WTR_DSPLY=0,SBX_WTR_KLR=0,SBX_CHP_DSPLY=0,SBX_WTR_DSPLY=0,Facings=0,Tags='',CaseID_6W='',CaseID_BR='',CaseID_LD='',ALT_Barcode='',DUP_Barcode=''

        '''
        ALT_Barcode=Column(String)
        DUP_Barcode=Column(String)
        CaseID_BR=Column(String)
        CaseID_LD=Column(String)
        CaseID_6W=Column(String)
        Tags=Column(String)
        Facings=Column(Integger)
        SBX_WTR_DSPLY=Column(Integer)
        SBX_CHP_DSPLY=Column(Integer)
        SBX_WTR_KLR=Column(Integer)
        FLRL_CHP_DSPLY=Column(Integer)
        FLRL_WTR_DSPLY=Column(Integer)
        WD_DSPLY=WD_DSPLY=Column(Integer)
        CHKSTND_SPLY=CHKSTND_SPLY=Column(Integer)
        '''


        #proposed fields
        #[done]smle,s|search|? - calls a prompt to search for InList==True with CODE|BARCODE instead of direct search waits for b for back, q for quit, for next CODE|BARCODE
        #optional fields
        #self.alt_barcode
        #self.duplicate_code
        #self.case_id_backroom - in case specific case is needed to be logged
        #csidbm,$EntryId,generate - create a synthetic id for case and save item to and save qrcode png of $case_id
        #csidbm,$EntryId,$case_id - set case id for item
        #csidbm,$EntryId - display item case id
        #csidbm,s|search,$case_id - display items associated with $case_id
        #csidbm,$EntryId,clr_csid - set $case_id to ''
        #the above applies to the below self.case_id_load as well
        #self.case_id_load - in case specific is found in load wanted in data

        #self.Tags
        #cmd syntax
        #tag,$EntryID,+|-|=,$tag_text
        #tag,s|search,$tag_text -> search for items with tag txt (multiple tags separated with a bar '|'')
        #tag,$EntryId|$code|$barcode -> display tags for item with $entryId, $code (returns multiple values), $barcode (returns multiple values)
        #- removes tag from field with tags
        #+ adds a tag to field with tags
        #= set field to $tag_text
        #self.Tags is a string separated by json string containing a list of tags
        #json.dumps(['a','b','c'])
        #json.loads('["a", "b", "c"]')

        #self.Facings
        #additional inventory fields
        #self.checkstandsupplies
        #self.sbx_dsply
        #self.flrl_dsply
        #self.wd_dsply

        try:
            if not self.LCL_ANDROID.exists():
                self.LCL_ANDROID.mkdir(parents=True)
        except Exception as e:
            print(e,"android directory!")
        if self.Price is None:
            self.Price=0
        if self.Tax is None:
            self.Tax=0
        if self.CRV is None:
            self.CRV=0
    LCL=Path("LCL_IMG")
    LCL_ANDROID=Path("/storage/emulated/0/DCIM/Screenshots")

    def save_code(self):
        filename=Path(f"{self.EntryId}_code.png")
        if self.LCL_ANDROID.exists():
            filename=str(self.LCL_ANDROID/filename)
        else:
            filename=str(self.LCL/filename)
        print(filename)
        try:
            codes=[Code39,QRCode]
            for code in codes:
                try:
                    if code == QRCode:
                        qrcode.make(self.Barcode).save(filename)
                        break
                    else:
                        code(self.Code,add_checksum=False,writer=ImageWriter()).write(filename)
                        break
                    pass
                except Exception as e:
                    print(e)


            return filename
        except Exception as e:
            print(e)
        return False

    def save_field(self,fieldname=None):
        def mkT(text,self):
            return text
        if not fieldname:
            fieldname=Prompt.__init2__(self,func=mkT,ptext="Fieldname: ",helpText="Export FieldData to Encoded Img "+','.join([i.name for i in self.__table__.columns]),data=self)
        filename=Path(f"{self.EntryId}_{fieldname}.png")
        if self.LCL_ANDROID.exists():
            filename=str(self.LCL_ANDROID/filename)
        else:
            filename=str(self.LCL/filename)
        print(filename)
        try:
            codes=[QRCode,]
            for code in codes:
                try:
                    filename_qr=Path(f"{self.EntryId}_{fieldname}_qr.png")
                    if self.LCL_ANDROID.exists():
                        filename_qr=str(self.LCL_ANDROID/filename_qr)
                    else:
                        filename_qr=str(self.LCL/filename_qr)
                    qrf=qrcode.make(str(getattr(self,fieldname))).save(filename_qr)
                    

                    if self.LCL_ANDROID.exists():
                        self.LCL=self.LCL_ANDROID
                   
                    #LCL=Path("LCL_IMG")
                    if not self.LCL.exists():
                        self.LCL.mkdir()
                    fname=str(self.LCL/Path(str(self.EntryId)+f"_{fieldname}"))
                    n=self.save_barcode()
                    c=self.save_code()
                    text=[]
                    for column in self.__table__.columns:
                        text.append('='.join([column.name,str(self.__dict__[column.name])]))
                    data='\n'.join(text)
                    renderImageFromText(fname,data,barcode_file=n,code_file=c,img_file=filename_qr)
                    Path(filename_qr).unlink()
                except Exception as e:
                    print(e)


            return filename
        except Exception as e:
            print(e)
        return False

    def save_barcode(self):
        filename=Path(f"{self.EntryId}_barcode.png")
        if self.LCL_ANDROID.exists():
            filename=str(self.LCL_ANDROID/filename)
        else:
            filename=str(self.LCL/filename)
        print(filename)
        try:
            codes=[UPCA,EAN13,QRCode]
            for code in codes:
                try:
                    if code == QRCode:
                        qrcode.make(self.Barcode).save(filename)
                        break
                    else:
                        if len(self.Barcode) <= 8 and code == UPCA:
                            upca=upcean.convert.convert_barcode_from_upce_to_upca(self.Barcode)
                            if upca != False:
                                code(upca,writer=ImageWriter()).write(filename)
                            else:
                                continue
                        elif len(self.Barcode) > 12:
                            if code == EAN13:
                                code(self.Barcode,writer=ImageWriter()).write(filename)
                            else:
                                continue
                        else:
                            code(self.Barcode,writer=ImageWriter()).write(filename)
                        break
                except Exception as e:
                    print(e)
            return filename


        except Exception as e:
            print(e)
        return False

    def saveItemData(self,num=None):
        if self.LCL_ANDROID.exists():
            self.LCL=self.LCL_ANDROID
        text=[]
        for column in self.__table__.columns:
            text.append('='.join([column.name,str(self.__dict__[column.name])]))
        data='\n'.join(text)
        #LCL=Path("LCL_IMG")
        if not self.LCL.exists():
            self.LCL.mkdir()
        fname=str(self.LCL/Path(str(self.EntryId)))
        n=self.save_barcode()
        c=self.save_code()
        renderImageFromText(fname,data,barcode_file=n,img_file=self.Image,code_file=c)

    def listdisplay(self,num=None):
        name=self.Name
        ma=32
        n=self.split_by_len(name,ma)
        #print(n)
        new=[]
        for i in n:
            if n.index(i) > 0:
                new.append(i)
            else:
                new.append(i)
        name='\n'.join(new)
        name="\n"+name
        if num == None:
            num=''
        msg=f'''{Fore.magenta}{Fore.dark_goldenrod}{num}->({Style.reset} NAME={Fore.cyan}{name}{Style.reset} | UPC={Fore.green}{self.Barcode}{Style.reset} | SHELF={Fore.yellow}{self.cfmt(self.Code)}{Style.reset} | QTY={Fore.violet}{self.ListQty}{Style.reset} | EID={Fore.sky_blue_2}{self.EntryId}{Style.reset}{Fore.magenta} )-<{Fore.dark_goldenrod}{num}{Style.reset}'''
        print(msg)
    def split_by_len(self,string, length):
        result = []
        for i in range(0, len(string), length):
            result.append(string[i:i + length])
        return result

    def saveListExtended(self,num):
        if self.LCL_ANDROID.exists():
            self.LCL=self.LCL_ANDROID
        total=self.Display_1+self.Display_2+self.Display_3+self.Display_4+self.Display_5+self.Display_6+self.Shelf+self.BackRoom
        total+=self.WD_DSPLY+self.SBX_WTR_KLR+self.SBX_CHP_DSPLY+self.SBX_WTR_DSPLY+self.FLRL_CHP_DSPLY+self.FLRL_WTR_DSPLY+self.CHKSTND_SPLY
        name=self.Name
        ma=32
        if len(name) > ma:
            n=self.split_by_len(name,ma)
            #print(n)
            new=[]
            for i in n:
                if n.index(i) > 0:
                    new.append(str(' '*7)+i)
                else:
                    new.append(i)
            name='\n'.join(new)
        if num == None:
            num=''
        msg=f"""
============={num}============
Barcode = {self.rebar()}
Code/Shelf/Label = {self.cfmt(self.Code)}
Name = {name}
Desc = {self.Description}
Shelf = {self.Shelf}
BackRoom/Wall = {self.BackRoom}
Display_1 = {self.Display_1}
Display_2 = {self.Display_2}
Display_3 = {self.Display_3}
Display_4 = {self.Display_4}
Display_5 = {self.Display_5}
Display_6 = {self.Display_6}
SBX_WTR_DSPLY={self.SBX_WTR_DSPLY}
SBX_CHP_DSPLY={self.SBX_CHP_DSPLY}
SBX_WTR_KLR={self.SBX_WTR_KLR}
FLRL_CHP_DSPLY={self.FLRL_CHP_DSPLY}
FLRL_WTR_DSPLY={self.FLRL_WTR_DSPLY}
WD_DSPLY={self.WD_DSPLY}
CHKSTND_SPLY={self.CHKSTND_SPLY}
Distress={self.Distress} #not added to total
Total = {total}
Total(w/o BR+) - Backroom = {(total-self.BackRoom)-self.BackRoom}
-------------{num}-------------
"""
        
        if not self.LCL.exists():
            self.LCL.mkdir()
        fname=str(self.LCL/Path(str(self.EntryId)))
        renderImageFromText(fname,msg)
        '''
ALT_Barcode={self.ALT_Barcode}
DUP_Barcode={self.DUP_Barcode}
CaseID_BR={self.CaseID_BR}
CaseID_LD={self.CaseID_LD}
CaseID_6W={self.CaseID_6W}
Tags={self.Tags}
Facings={self.Facings}

        '''
    #if BackRoom is True, total includes Backroom*price
    #if Backroom is False, total is needed for the shelf minus whatever is brought from backroom*price
    def total_value(self,BackRoom=False,CaseMode=True):
        total=self.Display_1+self.Display_2+self.Display_3+self.Display_4+self.Display_5+self.Display_6+self.Shelf+self.BackRoom
        total+=self.SBX_WTR_DSPLY
        total+=self.SBX_CHP_DSPLY
        total+=self.SBX_WTR_KLR
        total+=self.FLRL_CHP_DSPLY
        total+=self.FLRL_WTR_DSPLY
        total+=self.WD_DSPLY
        total+=self.CHKSTND_SPLY
        if not self.Price:
            self.Price=0
        if not self.CaseCount:
            self.CaseCount=1

        if not BackRoom:
            total-=self.BackRoom-self.BackRoom
        if not CaseMode:
            return round(total*self.Price,2)
        else:
            if self.CaseCount in [None,0,-1]:
                self.CaseCount=1
            return round((total*self.CaseCount)*self.Price,2)

    def total_units(self,BackRoom=True):
        total=self.Display_1+self.Display_2+self.Display_3+self.Display_4+self.Display_5+self.Display_6+self.Shelf+self.BackRoom
        total+=self.SBX_WTR_DSPLY
        total+=self.SBX_CHP_DSPLY
        total+=self.SBX_WTR_KLR
        total+=self.FLRL_CHP_DSPLY
        total+=self.FLRL_WTR_DSPLY
        total+=self.WD_DSPLY
        total+=self.CHKSTND_SPLY
        if not BackRoom:
            total-=self.BackRoom
            total-=self.BackRoom
        #print(BackRoom)
        return total

    def listdisplay_extended(self,num):
        #print(self.csv_headers())
        #print(self.csv_values())
        total=self.Display_1+self.Display_2+self.Display_3+self.Display_4+self.Display_5+self.Display_6+self.Shelf+self.BackRoom
        total+=self.SBX_WTR_DSPLY
        total+=self.SBX_CHP_DSPLY
        total+=self.SBX_WTR_KLR
        total+=self.FLRL_CHP_DSPLY
        total+=self.FLRL_WTR_DSPLY
        total+=self.WD_DSPLY
        total+=self.CHKSTND_SPLY

        name=self.Name
        ma=32
        if len(name) > ma:
            n=self.split_by_len(name,ma)
            #print(n)
            new=[]
            for i in n:
                if n.index(i) > 0:
                    new.append(str(' '*7)+i)
                else:
                    new.append(i)
            name='\n'.join(new)
        if num == None:
            num=''
        total_value=self.total_value(CaseMode=False)
        total_value_case=self.total_value()
        msg=f"""

============={Fore.green}{num}{Style.reset}============
{Fore.light_magenta}UserUpdated={self.userUpdated}{Style.reset}
{Style.bold+Style.underline+Fore.orange_red_1}EntryId{Style.bold}={Fore.green_yellow}{self.EntryId}{Style.reset}
{Fore.blue}Barcode{Style.reset} = {Fore.aquamarine_3}{self.rebar()}{Style.reset}
{Fore.dark_goldenrod}Code/Shelf/Label{Style.reset} = {Fore.yellow}{self.cfmt(self.Code)}{Style.reset}
{Fore.green_yellow}Name{Style.reset} = {Fore.cyan}{name}{Style.reset}
{Fore.light_steel_blue}{Style.underline}Description{Style.reset} = {Fore.cyan}{self.Description}{Style.reset}
{Fore.violet}Shelf{Style.reset} = {Fore.magenta}{self.Shelf}{Style.reset}
{Fore.yellow_4b}BackRoom/Wall{Style.reset} = {Fore.orange_4b}{self.BackRoom}{Style.reset}
{Fore.slate_blue_1}Display_1{Style.reset} = {Fore.medium_purple_3b}{self.Display_1}{Style.reset}
{Fore.medium_violet_red}Display_2{Style.reset} = {Fore.magenta_3a}{self.Display_2}{Style.reset}
{Fore.deep_pink_1a}Display_3 = {Style.reset}{Fore.purple_1a}{self.Display_3}{Style.reset}
{Fore.orange_red_1}Display_4 = {Style.reset}{Fore.plum_4}{self.Display_4}{Style.reset}
{Fore.light_salmon_1}Display_5 = {Style.reset}{Fore.pale_green_1a}{self.Display_5}{Style.reset}
{Fore.pink_1}Display_6 = {Style.reset}{Fore.gold_3a}{self.Display_6}{Style.reset}
{Fore.cyan}SBX_WTR_DSPLY{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_DSPLY}{Style.reset}
{Fore.cyan}SBX_CHP_DSPLY{Style.reset}={Fore.pale_green_1b}{self.SBX_CHP_DSPLY}{Style.reset}
{Fore.cyan}SBX_WTR_KLR{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_KLR}{Style.reset}
{Fore.violet}FLRL_CHP_DSPLY{Style.reset}={Fore.green_yellow}{self.FLRL_CHP_DSPLY}{Style.reset}
{Fore.violet}FLRL_WTR_DSPLY{Style.reset}={Fore.green_yellow}{self.FLRL_WTR_DSPLY}{Style.reset}
{Fore.grey_50}WD_DSPLY{Style.reset}={self.WD_DSPLY}{Style.reset}
{Fore.grey_50}CHKSTND_SPLY{Style.reset}={self.CHKSTND_SPLY}{Style.reset}
{Fore.pale_green_1b}{Style.underline}If Backroom is needed as part of total use value Below...{Style.reset}
{Fore.magenta}{Style.bold}1->{Style.reset}{Fore.spring_green_3a}Total{Style.reset} = {Fore.light_yellow}{total}{Style.reset}
{Fore.yellow_4b}{Style.underline}If Product was Pulled From BR to Fill Shelf, and needs to be 
deducted from Total as remainder is to be filled from LOAD{Style.reset}
{Fore.cyan}{Style.bold}2->{Style.reset}{Fore.hot_pink_2}Total(w/o BR+) - Backroom{Style.reset} = {Fore.light_yellow}{(total-self.BackRoom)-self.BackRoom}{Style.reset}
{Fore.medium_violet_red}Total Product Handled/To Be Handled Value: {Fore.spring_green_3a}{total_value}{Style.reset}
{Fore.medium_violet_red}Total Product Handled/To Be Handled Value*CaseCount: {Fore.spring_green_3a}{total_value_case}{Style.reset}
{Fore.orange_3}Distressed Product:{Fore.light_red}{self.Distress}{Style.reset}
-------------{Style.bold+Style.underline+Fore.orange_red_1}{num}{Style.reset}-------------
"""
        print(msg)
        return msg

    def imageExists(self):
        try:
            return Path(self.Image).exists() and Path(self.Image).is_file()
        except Exception as e:
            return False

    def cp_src_img_to_entry_img(self,src_img):
        try:
            path_src=Path(src_img)
            if path_src.exists() and path_src.is_file():
                img=Image.open(str(path_src))
                entryImg=Image.new(img.mode,size=img.size,color=(255,255,255))
                entryImg.paste(img.copy())
                name=f"Images/{self.EntryId}.png"
                entryImg.save(name)
                return name
        except Exception as e:
            return ''
    def seeShortRaw(self):
        #msg=f'''Short Data - Name({self.Name}) EID({self.EntryId}) [BCD/UPC[A/E]/EAN[8/13]/GTIN]({self.rebar()}):[SHELF/TAG/CIC/STR_CD]({self.cfmt(self.Code)})|CaseCount({self.CaseCount}|Price({self.Price})'''
        msg=strip_colors(self.seeShort())
        return msg

    def rebar(self,barcode=None,steps=4,skip_sep=False):
        try:
            if barcode == None:
                local_barcode=self.Barcode
            else:
                local_barcode=barcode

            if not isinstance(steps,int):
                steps=4
            rebar=[]
            steps=4
            r=range(0,len(local_barcode),steps)
            for num,i in enumerate(r):
                if num == len(r)-1:
                        chunk=local_barcode[i:i+steps]
                        primary=chunk[:-1]
                        lastChar=chunk[-1]
                        if (num % 2) == 0:
                            if skip_sep:
                                m=f"{Fore.light_steel_blue}{primary}{Fore.dark_goldenrod}{lastChar}{Style.reset}"
                            else:
                                m=f"{Fore.light_steel_blue}{primary}{Fore.dark_goldenrod}{DEFAULT_CHECKSUM_SEPARATOR_CHAR}{lastChar}{Style.reset}"
                        else:
                            if skip_sep:
                                m=f"{Fore.light_sea_green}{primary}{Fore.dark_goldenrod}{lastChar}{Style.reset}"
                            else:
                                m=f"{Fore.light_sea_green}{primary}{Fore.dark_goldenrod}{DEFAULT_CHECKSUM_SEPARATOR_CHAR}{lastChar}{Style.reset}"
                        rebar.append(m)
                elif (num % 2) == 0:
                    rebar.append(Fore.light_steel_blue+local_barcode[i:i+steps]+Style.reset)
                else:
                    rebar.append(Fore.light_sea_green+local_barcode[i:i+steps]+Style.reset)
            if skip_sep:
                return ''.join(rebar)

            rebar=f'{DEFAULT_SEPARATOR_CHAR}'.join(rebar)

            return rebar
        except Exception as e:
            print(e)
            print(str(e))
            print(repr(e))
            return self.Barcode

    def seeShort(self):
        rebar=self.rebar()
        ROUNDTO=int(detectGetOrSet("TotalSpent ROUNDTO default",3,setValue=False,literal=True))
        default_taxrate=float(detectGetOrSet("Tax Rate",0.0925,setValue=False,literal=True))
        price=round(self.Price,ROUNDTO)+round(self.CRV,ROUNDTO)
        
        formula=round(price+self.Tax,ROUNDTO)

        msg=f''' {Fore.slate_blue_1}{Style.underline}{'-'*5}{Style.reset}{Style.bold} Short Data {Style.reset}
{Fore.light_yellow}Name({Fore.pale_green_1b}{self.Name}{Fore.light_yellow}) {Fore.light_magenta}Price Per Unit({Fore.slate_blue_1}prc={self.Price}{Fore.light_magenta},crv={self.CRV},tax={self.Tax},ttl={formula}){Style.reset} {Fore.misty_rose_3}EID({Fore.pale_green_1b}{self.EntryId}{Fore.light_yellow}) {Fore.spring_green_3a}[BCD/UPC[A/E]/EAN[8/13]/GTIN](cd={Fore.light_magenta}{rebar},{Fore.chartreuse_1}no_sep={self.rebar(skip_sep=True)}{Fore.spring_green_3a}){Style.reset}{Fore.slate_blue_1} -{Fore.cyan}> {Fore.orange_red_1}[SHELF/TAG/CIC/STR_CD]({Fore.light_red}cd={self.cfmt(self.Code)}{Fore.orange_red_1}){Style.reset}'''
        return msg

    pinfo=f"{Back.green_3a}{Fore.red}**{Fore.white}{Style.bold}Product/Entry Info{Fore.red}- #REPLACE#**{Style.reset} "
    def __repr__(self):
        pinfo=self.pinfo
        total_value=self.total_value(CaseMode=False)
        total_value_case=self.total_value()
        types={i.name:str(i.type) for i in self.__table__.columns}
        m= f"""
        {pinfo.replace('#REPLACE#','Start')}
        {Style.bold}{Style.underline}{Fore.pale_green_1b}Entry{Style.reset}(
        {Fore.light_magenta}userUpdated:{Fore.grey_70}{types['userUpdated']}{Style.reset}={self.userUpdated}{Style.reset},
        {Fore.hot_pink_2}{Style.bold}{Style.underline}EntryId{Style.reset}:{Fore.grey_70}{types['EntryId']}{Style.reset}={self.EntryId}
        {Fore.violet}{Style.underline}Code{Style.reset}:{Fore.grey_70}{types['Code']}{Style.reset}='{self.cfmt(self.Code,n=4)}',
        {Fore.orange_3}{Style.bold}Barcode{Style.reset}:{Fore.grey_70}{types['Barcode']}{Style.reset}='{self.rebar()}',
        {Fore.orange_3}{Style.underline}UPCE from UPCA[if any]{Style.reset}:{Fore.grey_70}{types['upce2upca']}{Style.reset}='{self.upce2upca}',
        {Fore.green}{Style.bold}Price{Style.reset}{Fore.grey_70}:{types['Price']}{Style.reset}=${self.Price},
        {Fore.green}{Style.bold}CRV{Style.reset}{Fore.grey_70}:{types['CRV']}{Style.reset}=${self.CRV},
        {Fore.green}{Style.bold}Tax{Style.reset}{Fore.grey_70}:{types['Tax']}{Style.reset}=${self.Tax},
        {Fore.green}{Style.bold}TaxNote{Style.reset}:{Fore.grey_70}{types['TaxNote']}{Style.reset}='{self.TaxNote}',
        {Style.bold+Style.underline+Fore.orange_red_1}Name{Style.reset}:{Fore.grey_70}{types['Name']}{Style.reset}='{self.Name}',
        {Fore.light_steel_blue}{Style.underline}Description{Style.reset}:{Fore.grey_70}{types['Description']}{Style.reset}= '{Fore.cyan}{self.Description}{Style.reset}',
        {Fore.tan}Note{Style.reset}:{Fore.grey_70}{types['Note']}{Style.reset}='{self.Note}',
        {Fore.grey_50}ALT_Barcode{Style.reset}:{Fore.grey_70}{types['ALT_Barcode']}{Style.reset}={Fore.grey_70}{self.ALT_Barcode}{Style.reset}
        {Fore.grey_50}DUP_Barcode{Style.reset}:{Fore.grey_70}{types['DUP_Barcode']}{Style.reset}={Fore.grey_70}{self.DUP_Barcode}{Style.reset}
        {Fore.grey_50}CaseID_BR{Style.reset}:{Fore.grey_70}{types['CaseID_BR']}{Style.reset}={Fore.grey_70}{self.CaseID_BR}{Style.reset}
        {Fore.grey_50}CaseID_LD{Style.reset}:{Fore.grey_70}{types['CaseID_LD']}{Style.reset}={Fore.grey_70}{self.CaseID_LD}{Style.reset}
        {Fore.grey_50}CaseID_6W{Style.reset}:{Fore.grey_70}{types['CaseID_6W']}{Style.reset}={Fore.grey_70}{self.CaseID_6W}{Style.reset}
        {Fore.grey_50}Tags{Style.reset}:{Fore.grey_70}{types['Tags']}{Style.reset}={Fore.grey_70}{self.Tags}{Style.reset}

        {Fore.orange_red_1}{Style.bold}Dimension Fields{Style.reset}
        {Fore.grey_50}Facings{Style.reset}:{Fore.grey_70}{types['Facings']}{Style.reset}={Fore.grey_70}{self.Facings}{Style.reset}
        {Fore.grey_50}UnitsDeep{Style.reset}:{Fore.grey_70}{types['UnitsDeep']}{Style.reset}={Fore.grey_70}{self.UnitsDeep}{Style.reset}
        {Fore.grey_50}UnitsHigh{Style.reset}:{Fore.grey_70}{types['UnitsHigh']}{Style.reset}={Fore.grey_70}{self.UnitsHigh}{Style.reset}

        {Fore.pale_green_1b}Timestamp{Style.reset}:{Fore.grey_70}{types['Timestamp']}{Style.reset}='{datetime.fromtimestamp(self.Timestamp).strftime('%D@%H:%M:%S')}',

        {Fore.orange_red_1}{Style.bold}Location Fields{Style.reset}
        {Fore.deep_pink_3b}Shelf{Style.reset}:{Fore.grey_70}{types['Shelf']}{Style.reset}={self.Shelf},
        {Fore.light_steel_blue}BackRoom{Style.reset}:{Fore.grey_70}{types['BackRoom']}{Style.reset}={self.BackRoom},
        {Fore.cyan}Display_1{Style.reset}:{Fore.grey_70}{types['Display_1']}{Style.reset}={self.Display_1},
        {Fore.cyan}Display_2{Style.reset}:{Fore.grey_70}{types['Display_2']}{Style.reset}={self.Display_2},
        {Fore.cyan}Display_3{Style.reset}:{Fore.grey_70}{types['Display_3']}{Style.reset}={self.Display_3},
        {Fore.cyan}Display_4{Style.reset}:{Fore.grey_70}{types['Display_4']}{Style.reset}={self.Display_4},
        {Fore.cyan}Display_5{Style.reset}:{Fore.grey_70}{types['Display_5']}{Style.reset}={self.Display_5},
        {Fore.cyan}Display_6{Style.reset}:{Fore.grey_70}{types['Display_6']}{Style.reset}={self.Display_6},
        {Fore.cyan}SBX_WTR_DSPLY{Style.reset}:{Fore.grey_70}{types['SBX_WTR_DSPLY']}{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_DSPLY}{Style.reset}
        {Fore.cyan}SBX_CHP_DSPLY{Style.reset}:{Fore.grey_70}{types['SBX_CHP_DSPLY']}{Style.reset}={Fore.pale_green_1b}{self.SBX_CHP_DSPLY}{Style.reset}
        {Fore.cyan}SBX_WTR_KLR{Style.reset}{Fore.grey_70}:{types['SBX_WTR_KLR']}{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_KLR}{Style.reset}
        {Fore.violet}FLRL_CHP_DSPLY{Style.reset}:{Fore.grey_70}{types['FLRL_CHP_DSPLY']}{Style.reset}={Fore.green_yellow}{self.FLRL_CHP_DSPLY}{Style.reset}
        {Fore.violet}FLRL_WTR_DSPLY{Style.reset}:{Fore.grey_70}{types['FLRL_WTR_DSPLY']}{Style.reset}={Fore.green_yellow}{self.FLRL_WTR_DSPLY}{Style.reset}
        {Fore.grey_50}WD_DSPLY{Style.reset}:{Fore.grey_70}{types['WD_DSPLY']}{Style.reset}={self.WD_DSPLY}{Style.reset}
        {Fore.grey_50}CHKSTND_SPLY{Style.reset}:{Fore.grey_70}{types['CHKSTND_SPLY']}{Style.reset}={self.CHKSTND_SPLY}{Style.reset}
        {Fore.light_salmon_3a}Stock_Total{Style.reset}:{Fore.grey_70}{types['Stock_Total']}{Style.reset}={self.Stock_Total},
        {Fore.magenta_3c}InList{Style.reset}{Fore.grey_70}:{types['InList']}{Style.reset}={self.InList}
        {Fore.indian_red_1b}{Style.bold}{Style.underline}{Style.blink}ListQty{Style.reset}:{Fore.grey_70}{types['userUpdated']}{Style.reset}={self.ListQty}
        {Fore.misty_rose_3}Location{Style.reset}:{Fore.grey_70}{types['Location']}{Style.reset}={self.Location}
        {Fore.orange_3}Distress:{Fore.grey_70}{types['Distress']}{Style.reset}={Fore.light_red}{self.Distress},

        {Fore.orange_red_1}{Style.bold}Count Fields{Style.reset}
        {Fore.sky_blue_2}CaseCount{Style.reset}:{Fore.grey_70}{types['CaseCount']}{Style.reset}={self.CaseCount}
        {Fore.light_steel_blue}ShelfCount{Style.reset}:{Fore.grey_70}{types['ShelfCount']}{Style.reset}={self.ShelfCount},
        {Fore.light_steel_blue}PalletCount{Style.reset}:{Fore.grey_70}{types['PalletCount']}{Style.reset}={self.PalletCount},
        {Fore.light_steel_blue}LoadCount{Style.reset}:{Fore.grey_70}{types['LoadCount']}{Style.reset}={self.LoadCount},
        
        {Fore.sky_blue_2}Size{Style.reset}:{Fore.grey_70}{types['Size']}{Style.reset}={self.Size}
        {Fore.tan}Image[{Fore.dark_goldenrod}Exists:{Fore.deep_pink_3b}{self.imageExists()}{Style.reset}{Fore.tan}]{Style.reset}:{Fore.grey_70}{types['Image']}{Style.reset}={self.Image}
        {Fore.slate_blue_1}{Style.underline}{'-'*5}{Style.reset}{Style.bold} Short Data {Style.reset}{Fore.slate_blue_1}{Style.underline}{'-'*5}{Style.reset}
        {Fore.light_yellow}{self.Name} ({Fore.light_magenta}{self.Barcode}[{Fore.spring_green_3a}UPC{Style.reset}{Fore.light_magenta}]:{Fore.light_red}{self.cfmt(self.Code)}[{Fore.orange_red_1}SHELF/TAG/CIC]{Fore.light_red}){Style.reset}
        {Fore.medium_violet_red}Total Product Handled/To Be Handled Value: {Fore.spring_green_3a}{total_value}{Style.reset}
        {Fore.medium_violet_red}Total Product Handled/To Be Handled Value*CaseCount: {Fore.spring_green_3a}{total_value_case}{Style.reset}
        {Fore.orange_red_1}(Estimated/Inverted Shelf Qty) Shelf=ShelfCount - Qty {Fore.light_yellow}[{Fore.cyan}{self.ShelfCount}{Fore.light_yellow} -{Fore.cyan}{self.Shelf}{Fore.light_yellow}]={Fore.pale_green_1b}{self.ShelfCount-self.Shelf}{Style.reset}"""
        if self.imageExists():
            m+=f"""
        {Fore.green}Image {Fore.orange_3}{Style.bold}{Style.underline}ABSOLUTE{Style.reset}{Style.reset}={Path(self.Image).absolute()}"""
        mtext=''
        with Session(ENGINE) as session:
            extras=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==self.EntryId).all()
            ct=len(extras)
            mtext=[]
            for n,e in enumerate(extras):
                mtext.append(f"\t -{Fore.orange_red_1}{e.field_name}:{Fore.light_steel_blue}{e.field_type}={Fore.light_yellow}{e.field_value} {Fore.cyan}ede_id={e.ede_id} {Fore.light_magenta}doe={e.doe}{Style.reset}")
            mtext='\n'.join(mtext)
        m+=f"\n{mtext}"
        m+=f"""
        )
        {pinfo.replace('#REPLACE#','End')}
        """
        if self.Barcode and len(self.Barcode) >= 13:
            print(f"{Fore.hot_pink_1b}Detected Code is 13 digits long; please verify the 'EAN13 Stripped $var_x=$var_z' data first before using the UPC Codes!{Style.reset}")
        pc.PossibleCodes(scanned=self.Barcode)
        pc.PossibleCodesEAN13(scanned=self.Barcode)
        return m


    def before_entry_delete(self):
        image=Path(self.Image)
        if image.exists() and image.is_file():
            image.unlink()
        print(f"rmvd {image}")





Entry.metadata.create_all(ENGINE)
PairCollection.metadata.create_all(ENGINE)
tables={
    'Entry':Entry,
    'PairCollection':PairCollection,
}

class DayLog(BASE,EntryExtras):
    def cfmt(self,line,n=4):
        if not line:
            line='None'
        '''Colorize Format Code Data For terminal display for quick reading.'''
        x=[line[i:i+n] for i in range(0,len(line),n)]
        second=x[0][1:]
        first=x[0][0]
        #untouched last element of x
        lastblock=x[-1]
        for num,i in enumerate(x):
            if num % 2 == 0:
                x[num]=f"{Fore.cyan}{x[num]}{Style.reset}"
            else:
                x[num]=f"{Fore.light_steel_blue}{x[num]}{Style.reset}"
        cformat=f'{DEFAULT_SEPARATOR_CHAR}'.join(x)
        return cformat
    '''Stores Product Entry Details as History.

    Code -> shelf tag code, cic, store code
    Barcode -> Barcode found on product packaging used for internal tracking
    Name -> what the product identified by barcode, or code, is called
    Price -> How much the product costs
    CRV -> crv tax value
    Tax -> taxes added onto product
    TaxNote -> extra info related to taxes
    Note -> temporary info related to product
    Description -> Describe the product
    Size -> how big is it?
    CaseCount -> CasePack; how much comes in a case ordered of product
    Shelf,Distress,BackRoom,Display_1,Display_2,
    Display_3,Display_4,Display_5,Display_6,SBX_WTR_DSPLY,
    SBX_CHP_DSPLY,SBX_WTR_KLR,FLRL_CHP_DSPLY,ListQty,
    FLRL_WTR_DSPLY,WD_DSPLY,CHKSTND_SPLY -> Qty fields
    InList -> is the product being used with a value in any of the above Location fields
    Location -> where is the product stored using Aisle/Shelf Module/Shelf Number
    ALT_Barcode -> alternate code that the entry might be under
    DUP_Barcode -> duplicate barcode
    CaseID_BR -> Backroom case id
    CaseID_LD -> Load case id
    CaseID_6W -> 6-wheeler case id
    Tags -> extra search terms to help id/group product stored
    Facings -> how many units wide a product is across total shelves product is stored
    UnitsHigh -> how many units high of product that can be stacked
    UnitsDeep -> how many units can fit in a straight line to the back of the shelf, unstacked
    LoadCount -> how many units come in on load
    PalletCount -> how many units come in on a pallet
    ShelfCount -> how many units can fit on the shelf
    '''
    __tablename__="DayLog"
    DayLogId=Column(Integer,primary_key=True)
    DayLogDate=Column(Date)
    Code=Column(String)
    Barcode=Column(String)
    Distress=Column(Integer)
    #How Much Typically Comes in Load
    LoadCount=Column(Integer)
    #If product comes in pallets at a time, fill with how much comes
    PalletCount=Column(Integer)
    #how much can be held on the shelf at the time
    ShelfCount=Column(Integer)
    UnitsHigh=Column(Integer)
    UnitsDeep=Column(Integer)
    #not found in prompt requested by
    '''
    #name {Entryid}
    #name {Entryid} {new_value}
    
    #price {Entryid}
    #price {Entryid} {new_value}

    #note {Entryid}
    #note {Entryid} {new_value}
    
    #size {Entryid} 
    #size {Entryid} {new_value}
    '''
    Name=Column(String)
    Price=Column(Float)
    CRV=Column(Float)
    Tax=Column(Float)
    TaxNote=Column(String)

    Description=Column(String)
    Note=Column(String)
    Size=Column(String)
    
    CaseCount=Column(Integer)
    userUpdated=Column(Boolean)
    Shelf=Column(Integer)
    BackRoom=Column(Integer)
    Display_1=Column(Integer)
    Display_2=Column(Integer)
    Display_3=Column(Integer)
    Display_4=Column(Integer)
    Display_5=Column(Integer)
    Display_6=Column(Integer)
    InList=Column(Boolean)
    Stock_Total=Column(Integer)
    Location=Column(String)
    ListQty=Column(Float)
    upce2upca=Column(String)
    Image=Column(String)
    EntryId=Column(Integer)
    Timestamp=Column(Float)

    ALT_Barcode=Column(String)
    DUP_Barcode=Column(String)
    CaseID_BR=Column(String)
    CaseID_LD=Column(String)
    CaseID_6W=Column(String)
    Tags=Column(String)
    Facings=Column(Integer)
    SBX_WTR_DSPLY=Column(Integer)
    SBX_CHP_DSPLY=Column(Integer)
    SBX_WTR_KLR=Column(Integer)
    FLRL_CHP_DSPLY=Column(Integer)
    FLRL_WTR_DSPLY=Column(Integer)
    WD_DSPLY=WD_DSPLY=Column(Integer)
    CHKSTND_SPLY=CHKSTND_SPLY=Column(Integer)

    def csv_headers(self):
        headers=[]
        for i in self.__table__.columns:
            headers.append(i.name)
        headers.append("DateFromTimeStamp")
        return headers

    def csv_values(self):
        values=[]
        for i in self.__table__.columns:
            value=self.__dict__.get(i.name)
            values.append(value)
        values.append(datetime.fromtimestamp(self.Timestamp).ctime())
        return values
    def synthetic_field_str(self):
        f=string.ascii_uppercase+string.digits
        part=[]
        for num in range(4):
            part.append(f[random.randint(0,len(f)-1)])
        part.append("-")
        for num in range(4):
            part.append(f[random.randint(0,len(f)-1)])
        return ''.join(part)

    def seeShortRaw(self):
        #msg=f'''Short Data - Name({self.Name}) EID({self.EntryId}) [BCD/UPC[A/E]/EAN[8/13]/GTIN]({self.rebar()}):[SHELF/TAG/CIC/STR_CD]({self.cfmt(self.Code)})|CaseCount({self.CaseCount}|Price({self.Price})'''
        msg=strip_colors(self.seeShort())
        return msg

    def rebar(self,skip_sep=False):
        rebar=[]
        steps=4
        r=range(0,len(self.Barcode),steps)
        for num,i in enumerate(r):
            if num == len(r)-1:
                    chunk=self.Barcode[i:i+steps]
                    primary=chunk[:-1]
                    lastChar=chunk[-1]
                    if (num % 2) == 0:
                        if skip_sep:
                            m=f"{Fore.light_steel_blue}{primary}{Fore.dark_goldenrod}{lastChar}{Style.reset}"

                        else:
                            m=f"{Fore.light_steel_blue}{primary}{Fore.dark_goldenrod}{DEFAULT_CHECKSUM_SEPARATOR_CHAR}{lastChar}{Style.reset}"
                    else:
                        if skip_sep:
                            m=f"{Fore.light_sea_green}{primary}{Fore.dark_goldenrod}{lastChar}{Style.reset}"

                        else:
                            m=f"{Fore.light_sea_green}{primary}{Fore.dark_goldenrod}{DEFAULT_CHECKSUM_SEPARATOR_CHAR}{lastChar}{Style.reset}"
                    rebar.append(m)
            elif (num % 2) == 0:
                rebar.append(Fore.light_steel_blue+self.Barcode[i:i+steps]+Style.reset)
            else:
                rebar.append(Fore.light_sea_green+self.Barcode[i:i+steps]+Style.reset)
        if skip_sep:
            return ''.join(rebar)
        rebar=f'{DEFAULT_SEPARATOR_CHAR}'.join(rebar)
        
        return rebar

    def seeShort(self):
        rebar=self.rebar()
        ROUNDTO=int(detectGetOrSet("TotalSpent ROUNDTO default",3,setValue=False,literal=True))
        default_taxrate=float(detectGetOrSet("Tax Rate",0.0925,setValue=False,literal=True))
        price=round(self.Price,ROUNDTO)+round(self.CRV,ROUNDTO)
        
        formula=round(price+self.Tax,ROUNDTO)

        msg=f''' {Fore.slate_blue_1}{Style.underline}{'-'*5}{Style.reset}{Style.bold} Short Data {Style.reset}
{Fore.light_yellow}Name({Fore.pale_green_1b}{self.Name}{Fore.light_yellow}) {Fore.light_magenta}Price Per Unit({Fore.slate_blue_1}prc={self.Price}{Fore.light_magenta},crv={self.CRV},tax={self.Tax},ttl={formula}){Style.reset} {Fore.misty_rose_3}EID({Fore.pale_green_1b}{self.EntryId}{Fore.light_yellow}) {Fore.spring_green_3a}[BCD/UPC[A/E]/EAN[8/13]/GTIN](cd={Fore.light_magenta}{rebar},{Fore.chartreuse_1}no_sep={self.rebar(skip_sep=True)}{Fore.spring_green_3a}){Style.reset}{Fore.slate_blue_1} -{Fore.cyan}> {Fore.orange_red_1}[SHELF/TAG/CIC/STR_CD]({Fore.light_red}cd={self.cfmt(self.Code)}{Fore.orange_red_1}){Style.reset}'''
        return msg

    def __init__(self,Barcode,Code,upce2upca='',Name='',InList=False,Price=0.0,Note='',Size='',CaseCount=0,Shelf=0,BackRoom=0,Display_1=0,Display_2=0,Display_3=0,Display_4=0,Display_5=0,Display_6=0,Stock_Total=0,Timestamp=datetime.now().timestamp(),EntryId=None,Location='///',ListQty=0.0,Image='',CHKSTND_SPLY=0,WD_DSPLY=0,FLRL_CHP_DSPLY=0,FLRL_WTR_DSPLY=0,SBX_WTR_KLR=0,SBX_CHP_DSPLY=0,SBX_WTR_DSPLY=0,Facings=0,Tags='',CaseID_6W='',CaseID_BR='',CaseID_LD='',ALT_Barcode='',DUP_Barcode='',DayLogDate=datetime.now(),DayLogId=None,CRV=0.0,Tax=0.0,TaxNote='',userUpdated=False,LoadCount=1,PalletCount=1,ShelfCount=1,Description='',Distress=0,UnitsDeep=1,UnitsHigh=1):
        if EntryId:
            self.EntryId=EntryId
        self.userUpdated=userUpdated
        self.Distress=Distress
        self.UnitsHigh=UnitsHigh
        self.UnitsDeep=UnitsDeep
        self.CRV=CRV
        self.Tax=Tax
        self.TaxNote=TaxNote
        self.Description=Description
        self.Barcode=Barcode
        if self.Barcode == None:
            self.Barcode = ''
        self.Code=Code
        if self.Code == None:
            self.Code=''
        self.Name=Name
        if self.Name == None:
            self.Name=''
        self.Price=Price
        self.Note=Note
        self.Size=Size
        self.Shelf=Shelf
        self.CaseCount=CaseCount
        self.BackRoom=BackRoom
        self.Display_1=Display_1
        self.Display_2=Display_2
        self.Display_3=Display_3
        self.Display_4=Display_4
        self.Display_5=Display_5
        self.Display_6=Display_6
        self.Stock_Total=Stock_Total
        self.Location=Location
        self.Timestamp=Timestamp
        self.InList=InList
        self.ListQty=ListQty
        self.upce2upca=upce2upca
        self.Image=Image
        self.Tags=Tags
        self.Facings=Facings


        self.ALT_Barcode=ALT_Barcode
        if InList == '':
            InList=True

        if isinstance(userUpdated,str):
            try:
                self.InList=eval(InList)
            except Exception as e:
                self.InList=True

        if userUpdated == '':
            self.userUpdated=False
        if isinstance(userUpdated,str):
            try:
                self.userUpdated=eval(userUpdated)
            except Exception as e:
                self.userUpdated=False
        try:
            #print(f'{Style.bold+Style.underline+Fore.orange_red_1}X{Style.reset}')
            if len(self.Barcode) == 8:

                if self.ALT_Barcode == '':
                    #print(f'{Fore.light_yellow}X{Style.reset}')
                    self.ALT_Barcode=upcean.convert.convert_barcode_from_upce_to_upca(upc=self.Barcode)
                    if not isinstance(self.ALT_Barcode,str):
                        print(f"{Fore.light_yellow}ALT_Barcode=={self.ALT_Barcode}{Style.reset}")
                        self.ALT_Barcode=''
        except Exception as e:
            print(repr(e),str(e),e)
        
        self.DUP_Barcode=DUP_Barcode
        self.CaseID_BR=CaseID_BR
        self.CaseID_LD=CaseID_LD
        self.CaseID_6W=CaseID_6W
        self.SBX_WTR_DSPLY=SBX_WTR_DSPLY
        self.SBX_CHP_DSPLY=SBX_CHP_DSPLY
        self.SBX_WTR_KLR=SBX_WTR_KLR
        self.FLRL_CHP_DSPLY=FLRL_CHP_DSPLY
        self.FLRL_WTR_DSPLY=FLRL_WTR_DSPLY
        self.WD_DSPLY=WD_DSPLY
        self.CHKSTND_SPLY=CHKSTND_SPLY
        self.ShelfCount=ShelfCount
        self.PalletCount=PalletCount
        self.LoadCount=LoadCount

        if DayLogDate:
            self.DayLogDate=DayLogDate
        else:
            self.DayLogDate=datetime.now()
        if DayLogId:
            self.DayLogId=DayLogId
        #CHKSTND_SPLY=0,WD_DSPLY=0,FLRL_CHP_DSPLY=0,FLRL_WTR_DSPLY=0,SBX_WTR_KLR=0,SBX_CHP_DSPLY=0,SBX_WTR_DSPLY=0,Facings=0,Tags='',CaseID_6W='',CaseID_BR='',CaseID_LD='',ALT_Barcode='',DUP_Barcode=''

        '''
        ALT_Barcode=Column(String)
        DUP_Barcode=Column(String)
        CaseID_BR=Column(String)
        CaseID_LD=Column(String)
        CaseID_6W=Column(String)
        Tags=Column(String)
        Facings=Column(Integger)
        SBX_WTR_DSPLY=Column(Integer)
        SBX_CHP_DSPLY=Column(Integer)
        SBX_WTR_KLR=Column(Integer)
        FLRL_CHP_DSPLY=Column(Integer)
        FLRL_WTR_DSPLY=Column(Integer)
        WD_DSPLY=WD_DSPLY=Column(Integer)
        CHKSTND_SPLY=CHKSTND_SPLY=Column(Integer)
        '''


        #proposed fields
        #[done]smle,s|search|? - calls a prompt to search for InList==True with CODE|BARCODE instead of direct search waits for b for back, q for quit, for next CODE|BARCODE
        #optional fields
        #self.alt_barcode
        #self.duplicate_code
        #self.case_id_backroom - in case specific case is needed to be logged
        #csidbm,$EntryId,generate - create a synthetic id for case and save item to and save qrcode png of $case_id
        #csidbm,$EntryId,$case_id - set case id for item
        #csidbm,$EntryId - display item case id
        #csidbm,s|search,$case_id - display items associated with $case_id
        #csidbm,$EntryId,clr_csid - set $case_id to ''
        #the above applies to the below self.case_id_load as well
        #self.case_id_load - in case specific is found in load wanted in data

        #self.Tags
        #cmd syntax
        #tag,$EntryID,+|-|=,$tag_text
        #tag,s|search,$tag_text -> search for items with tag txt (multiple tags separated with a bar '|'')
        #tag,$EntryId|$code|$barcode -> display tags for item with $entryId, $code (returns multiple values), $barcode (returns multiple values)
        #- removes tag from field with tags
        #+ adds a tag to field with tags
        #= set field to $tag_text
        #self.Tags is a string separated by json string containing a list of tags
        #json.dumps(['a','b','c'])
        #json.loads('["a", "b", "c"]')

        #self.Facings
        #additional inventory fields
        #self.checkstandsupplies
        #self.sbx_dsply
        #self.flrl_dsply
        #self.wd_dsply

        try:
            if not self.LCL_ANDROID.exists():
                self.LCL_ANDROID.mkdir(parents=True)
        except Exception as e:
            print(e,"android directory!")
    LCL=Path("LCL_IMG")
    LCL_ANDROID=Path("/storage/emulated/0/DCIM/Screenshots")

    def save_code(self):
        filename=Path(f"{self.EntryId}_code.png")
        if self.LCL_ANDROID.exists():
            filename=str(self.LCL_ANDROID/filename)
        else:
            filename=str(self.LCL/filename)
        print(filename)
        try:
            codes=[Code39,QRCode]
            for code in codes:
                try:
                    if code == QRCode:
                        qrcode.make(self.Barcode).save(filename)
                        break
                    else:
                        code(self.Code,add_checksum=False,writer=ImageWriter()).write(filename)
                        break
                    pass
                except Exception as e:
                    print(e)


            return filename
        except Exception as e:
            print(e)
        return False

    def save_barcode(self):
        filename=Path(f"{self.EntryId}_barcode.png")
        if self.LCL_ANDROID.exists():
            filename=str(self.LCL_ANDROID/filename)
        else:
            filename=str(self.LCL/filename)
        print(filename)
        try:
            codes=[UPCA,EAN13,QRCode]
            for code in codes:
                try:
                    if code == QRCode:
                        qrcode.make(self.Barcode).save(filename)
                        break
                    else:
                        if len(self.Barcode) <= 8 and code == UPCA:
                            upca=upcean.convert.convert_barcode_from_upce_to_upca(self.Barcode)
                            if upca != False:
                                code(upca,writer=ImageWriter()).write(filename)
                            else:
                                continue
                        elif len(self.Barcode) > 12:
                            if code == EAN13:
                                code(self.Barcode,writer=ImageWriter()).write(filename)
                            else:
                                continue
                        else:
                            code(self.Barcode,writer=ImageWriter()).write(filename)
                        break
                except Exception as e:
                    print(e)
            return filename


        except Exception as e:
            print(e)
        return False

    def saveItemData(self,num=None):
        if self.LCL_ANDROID.exists():
            self.LCL=self.LCL_ANDROID
        text=[]
        for column in self.__table__.columns:
            text.append('='.join([column.name,str(self.__dict__[column.name])]))
        data='\n'.join(text)
        #LCL=Path("LCL_IMG")
        if not self.LCL.exists():
            self.LCL.mkdir()
        fname=str(self.LCL/Path(str(self.EntryId)))
        n=self.save_barcode()
        c=self.save_code()
        renderImageFromText(fname,data,barcode_file=n,img_file=self.Image,code_file=c)

    def listdisplay(self,num=None):
        name=self.Name
        ma=32
        n=self.split_by_len(name,ma)
        #print(n)
        new=[]
        for i in n:
            if n.index(i) > 0:
                new.append(i)
            else:
                new.append(i)
        name='\n'.join(new)
        name="\n"+name
        if num == None:
            num=''
        msg=f'''{Fore.magenta}{Fore.dark_goldenrod}{num}->({Style.reset} NAME={Fore.cyan}{name}{Style.reset} | UPC={Fore.green}{self.Barcode}{Style.reset} | SHELF={Fore.yellow}{self.cfmt(self.Code)}{Style.reset} | QTY={Fore.violet}{self.ListQty}{Style.reset} | EID={Fore.sky_blue_2}{self.EntryId}{Style.reset}{Fore.magenta} )-<{Fore.dark_goldenrod}{num}{Style.reset}'''
        print(msg)
    def split_by_len(self,string, length):
        result = []
        for i in range(0, len(string), length):
            result.append(string[i:i + length])
        return result

    def saveListExtended(self,num):
        if self.LCL_ANDROID.exists():
            self.LCL=self.LCL_ANDROID
        total=self.Display_1+self.Display_2+self.Display_3+self.Display_4+self.Display_5+self.Display_6+self.Shelf+self.BackRoom
        total+=self.WD_DSPLY+self.SBX_WTR_KLR+self.SBX_CHP_DSPLY+self.SBX_WTR_DSPLY+self.FLRL_CHP_DSPLY+self.FLRL_WTR_DSPLY+self.CHKSTND_SPLY
        name=self.Name
        ma=32
        if len(name) > ma:
            n=self.split_by_len(name,ma)
            #print(n)
            new=[]
            for i in n:
                if n.index(i) > 0:
                    new.append(str(' '*7)+i)
                else:
                    new.append(i)
            name='\n'.join(new)
        if num == None:
            num=''
        msg=f"""
============={num}============
DayLogId = {self.DayLogId}
DayLogDate = {self.DayLogDate}
Barcode = {self.Barcode}
Code/Shelf/Label = {self.cfmt(self.Code,n=4)}
Name = {name}
Desc = {self.Description}
Shelf = {self.Shelf}
BackRoom/Wall = {self.BackRoom}
Display_1 = {self.Display_1}
Display_2 = {self.Display_2}
Display_3 = {self.Display_3}
Display_4 = {self.Display_4}
Display_5 = {self.Display_5}
Display_6 = {self.Display_6}
SBX_WTR_DSPLY={self.SBX_WTR_DSPLY}
SBX_CHP_DSPLY={self.SBX_CHP_DSPLY}
SBX_WTR_KLR={self.SBX_WTR_KLR}
FLRL_CHP_DSPLY={self.FLRL_CHP_DSPLY}
FLRL_WTR_DSPLY={self.FLRL_WTR_DSPLY}
WD_DSPLY={self.WD_DSPLY}
CHKSTND_SPLY={self.CHKSTND_SPLY}
Total = {total}
Distressed={self.Distress} #not included in total
Total(w/o BR+) - Backroom = {(total-self.BackRoom)-self.BackRoom}
-------------{num}-------------
"""
        
        if not self.LCL.exists():
            self.LCL.mkdir()
        fname=str(self.LCL/Path(str(self.EntryId)))
        renderImageFromText(fname,msg)
        '''
ALT_Barcode={self.ALT_Barcode}
DUP_Barcode={self.DUP_Barcode}
CaseID_BR={self.CaseID_BR}
CaseID_LD={self.CaseID_LD}
CaseID_6W={self.CaseID_6W}
Tags={self.Tags}
Facings={self.Facings}

        '''

    def listdisplay_extended(self,num):
        #print(self.csv_headers())
        #print(self.csv_values())
        total=self.Display_1+self.Display_2+self.Display_3+self.Display_4+self.Display_5+self.Display_6+self.Shelf+self.BackRoom
        total+=self.SBX_WTR_DSPLY
        total+=self.SBX_CHP_DSPLY
        total+=self.SBX_WTR_KLR
        total+=self.FLRL_CHP_DSPLY
        total+=self.FLRL_WTR_DSPLY
        total+=self.WD_DSPLY
        total+=self.CHKSTND_SPLY

        name=self.Name
        ma=32
        if len(name) > ma:
            n=self.split_by_len(name,ma)
            #print(n)
            new=[]
            for i in n:
                if n.index(i) > 0:
                    new.append(str(' '*7)+i)
                else:
                    new.append(i)
            name='\n'.join(new)
        if num == None:
            num=''
        msg=f"""
============={Fore.green}{num}{Style.reset}============
{Fore.cyan}DayLogId = {self.DayLogId}{Style.reset}
{Fore.light_magenta}userUpdated = {self.userUpdated}{Style.reset}
{Fore.cyan}DayLogDate = {self.DayLogDate}{Style.reset}
{Style.bold+Style.underline+Fore.orange_red_1}EntryId{Style.bold}={Fore.green_yellow}{self.EntryId}{Style.reset}
{Fore.blue}Barcode{Style.reset} = {Fore.aquamarine_3}{self.Barcode}{Style.reset}
{Fore.dark_goldenrod}Code/Shelf/Label{Style.reset} = {Fore.yellow}{self.cfmt(self.Code)}{Style.reset}
{Fore.green_yellow}Name{Style.reset} = {Fore.cyan}{name}{Style.reset}
{Fore.light_steel_blue}{Style.underline}Description{Style.reset} = {Fore.cyan}{self.Description}{Style.reset}
{Fore.violet}Shelf{Style.reset} = {Fore.magenta}{self.Shelf}{Style.reset}
{Fore.yellow_4b}BackRoom/Wall{Style.reset} = {Fore.orange_4b}{self.BackRoom}{Style.reset}
{Fore.slate_blue_1}Display_1{Style.reset} = {Fore.medium_purple_3b}{self.Display_1}{Style.reset}
{Fore.medium_violet_red}Display_2{Style.reset} = {Fore.magenta_3a}{self.Display_2}{Style.reset}
{Fore.deep_pink_1a}Display_3 = {Style.reset}{Fore.purple_1a}{self.Display_3}{Style.reset}
{Fore.orange_red_1}Display_4 = {Style.reset}{Fore.plum_4}{self.Display_4}{Style.reset}
{Fore.light_salmon_1}Display_5 = {Style.reset}{Fore.pale_green_1a}{self.Display_5}{Style.reset}
{Fore.pink_1}Display_6 = {Style.reset}{Fore.gold_3a}{self.Display_6}{Style.reset}
{Fore.cyan}SBX_WTR_DSPLY{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_DSPLY}{Style.reset}
{Fore.cyan}SBX_CHP_DSPLY{Style.reset}={Fore.pale_green_1b}{self.SBX_CHP_DSPLY}{Style.reset}
{Fore.cyan}SBX_WTR_KLR{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_KLR}{Style.reset}
{Fore.violet}FLRL_CHP_DSPLY{Style.reset}={Fore.green_yellow}{self.FLRL_CHP_DSPLY}{Style.reset}
{Fore.violet}FLRL_WTR_DSPLY{Style.reset}={Fore.green_yellow}{self.FLRL_WTR_DSPLY}{Style.reset}
{Fore.grey_50}WD_DSPLY{Style.reset}={self.WD_DSPLY}{Style.reset}
{Fore.grey_50}CHKSTND_SPLY{Style.reset}={self.CHKSTND_SPLY}{Style.reset}
{Fore.orange_3}Distress{Fore.light_red}={self.Distress}{Style.reset}
{Fore.pale_green_1b}{Style.underline}If Backroom is needed as part of total use value Below...{Style.reset}
{Fore.magenta}{Style.bold}1->{Style.reset}{Fore.spring_green_3a}Total{Style.reset} = {Fore.light_yellow}{total}{Style.reset}
{Fore.yellow_4b}{Style.underline}If Product was Pulled From BR to Fill Shelf, and needs to be 
deducted from Total as remainder is to be filled from LOAD{Style.reset}
{Fore.cyan}{Style.bold}2->{Style.reset}{Fore.hot_pink_2}Total(w/o BR+) - Backroom{Style.reset} = {Fore.light_yellow}{(total-self.BackRoom)-self.BackRoom}{Style.reset}
-------------{Style.bold+Style.underline+Fore.orange_red_1}{num}{Style.reset}-------------
"""
        print(msg)
        return msg

    def imageExists(self):
        try:
            return Path(self.Image).exists() and Path(self.Image).is_file()
        except Exception as e:
            return False

    def cp_src_img_to_entry_img(self,src_img):
        try:
            path_src=Path(src_img)
            if path_src.exists() and path_src.is_file():
                img=Image.open(str(path_src))
                entryImg=Image.new(img.mode,size=img.size,color=(255,255,255))
                entryImg.paste(img.copy())
                name=f"Images/{self.EntryId}.png"
                entryImg.save(name)
                return name
        except Exception as e:
            return ''

    def __repr__(self):
        types={i.name:str(i.type) for i in self.__table__.columns}
        m= f"""
        {Style.bold}{Style.underline}{Fore.pale_green_1b}Daylog{Style.reset}(
        {Fore.cyan}DayLogId:{Fore.grey_70}{types['DayLogId']}{Style.reset}={self.DayLogId}{Style.reset},
        {Fore.cyan}DayLogDate:{Fore.grey_70}{types['DayLogDate']}{Style.reset}={self.DayLogDate}{Style.reset},
        {Fore.light_magenta}userUpdated:{Fore.grey_70}{types['userUpdated']}{Style.reset}={self.userUpdated}{Style.reset},
        {Fore.hot_pink_2}{Style.bold}{Style.underline}EntryId{Style.reset}:{Fore.grey_70}{types['EntryId']}{Style.reset}={self.EntryId}
        {Fore.violet}{Style.underline}Code{Style.reset}:{Fore.grey_70}{types['Code']}{Style.reset}='{self.cfmt(self.Code)}',
        {Fore.orange_3}{Style.bold}Barcode{Style.reset}:{Fore.grey_70}{types['Barcode']}{Style.reset}='{self.rebar()}',
        {Fore.orange_3}{Style.underline}UPCE from UPCA[if any]{Style.reset}:{Fore.grey_70}{types['upce2upca']}{Style.reset}='{self.upce2upca}',
        {Fore.green}{Style.bold}Price{Style.reset}{Fore.grey_70}:{types['Price']}{Style.reset}=${self.Price},
        {Fore.green}{Style.bold}CRV{Style.reset}{Fore.grey_70}:{types['CRV']}{Style.reset}=${self.CRV},
        {Fore.green}{Style.bold}Tax{Style.reset}{Fore.grey_70}:{types['Tax']}{Style.reset}=${self.Tax},
        {Fore.green}{Style.bold}TaxNote{Style.reset}:{Fore.grey_70}{types['TaxNote']}{Style.reset}='{self.TaxNote}',
        {Style.bold+Style.underline+Fore.orange_red_1}Name{Style.reset}:{Fore.grey_70}{types['Name']}{Style.reset}='{self.Name}',
        {Fore.light_steel_blue}{Style.underline}Description{Style.reset}:{Fore.grey_70}{types['Description']}{Style.reset}= '{Fore.cyan}{self.Description}{Style.reset}',
        {Fore.tan}Note{Style.reset}:{Fore.grey_70}{types['Note']}{Style.reset}='{self.Note}',
        {Fore.grey_50}ALT_Barcode{Style.reset}:{Fore.grey_70}{types['ALT_Barcode']}{Style.reset}={Fore.grey_70}{self.ALT_Barcode}{Style.reset}
        {Fore.grey_50}DUP_Barcode{Style.reset}:{Fore.grey_70}{types['DUP_Barcode']}{Style.reset}={Fore.grey_70}{self.DUP_Barcode}{Style.reset}
        {Fore.grey_50}CaseID_BR{Style.reset}:{Fore.grey_70}{types['CaseID_BR']}{Style.reset}={Fore.grey_70}{self.CaseID_BR}{Style.reset}
        {Fore.grey_50}CaseID_LD{Style.reset}:{Fore.grey_70}{types['CaseID_LD']}{Style.reset}={Fore.grey_70}{self.CaseID_LD}{Style.reset}
        {Fore.grey_50}CaseID_6W{Style.reset}:{Fore.grey_70}{types['CaseID_6W']}{Style.reset}={Fore.grey_70}{self.CaseID_6W}{Style.reset}
        {Fore.grey_50}Tags{Style.reset}:{Fore.grey_70}{types['Tags']}{Style.reset}={Fore.grey_70}{self.Tags}{Style.reset}

        {Fore.orange_red_1}{Style.bold}Dimension Fields{Style.reset}
        {Fore.grey_50}Facings{Style.reset}:{Fore.grey_70}{types['Facings']}{Style.reset}={Fore.grey_70}{self.Facings}{Style.reset}
        {Fore.grey_50}UnitsDeep{Style.reset}:{Fore.grey_70}{types['UnitsDeep']}{Style.reset}={Fore.grey_70}{self.UnitsDeep}{Style.reset}
        {Fore.grey_50}UnitsHigh{Style.reset}:{Fore.grey_70}{types['UnitsHigh']}{Style.reset}={Fore.grey_70}{self.UnitsHigh}{Style.reset}

        {Fore.pale_green_1b}Timestamp{Style.reset}:{Fore.grey_70}{types['Timestamp']}{Style.reset}='{datetime.fromtimestamp(self.Timestamp).strftime('%D@%H:%M:%S')}',

        {Fore.orange_red_1}{Style.bold}Location Fields{Style.reset}
        {Fore.deep_pink_3b}Shelf{Style.reset}:{Fore.grey_70}{types['Shelf']}{Style.reset}={self.Shelf},
        {Fore.light_steel_blue}BackRoom{Style.reset}:{Fore.grey_70}{types['BackRoom']}{Style.reset}={self.BackRoom},
        {Fore.cyan}Display_1{Style.reset}:{Fore.grey_70}{types['Display_1']}{Style.reset}={self.Display_1},
        {Fore.cyan}Display_2{Style.reset}:{Fore.grey_70}{types['Display_2']}{Style.reset}={self.Display_2},
        {Fore.cyan}Display_3{Style.reset}:{Fore.grey_70}{types['Display_3']}{Style.reset}={self.Display_3},
        {Fore.cyan}Display_4{Style.reset}:{Fore.grey_70}{types['Display_4']}{Style.reset}={self.Display_4},
        {Fore.cyan}Display_5{Style.reset}:{Fore.grey_70}{types['Display_5']}{Style.reset}={self.Display_5},
        {Fore.cyan}Display_6{Style.reset}:{Fore.grey_70}{types['Display_6']}{Style.reset}={self.Display_6},
        {Fore.cyan}SBX_WTR_DSPLY{Style.reset}:{Fore.grey_70}{types['SBX_WTR_DSPLY']}{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_DSPLY}{Style.reset}
        {Fore.cyan}SBX_CHP_DSPLY{Style.reset}:{Fore.grey_70}{types['SBX_CHP_DSPLY']}{Style.reset}={Fore.pale_green_1b}{self.SBX_CHP_DSPLY}{Style.reset}
        {Fore.cyan}SBX_WTR_KLR{Style.reset}{Fore.grey_70}:{types['SBX_WTR_KLR']}{Style.reset}={Fore.pale_green_1b}{self.SBX_WTR_KLR}{Style.reset}
        {Fore.violet}FLRL_CHP_DSPLY{Style.reset}:{Fore.grey_70}{types['FLRL_CHP_DSPLY']}{Style.reset}={Fore.green_yellow}{self.FLRL_CHP_DSPLY}{Style.reset}
        {Fore.violet}FLRL_WTR_DSPLY{Style.reset}:{Fore.grey_70}{types['FLRL_WTR_DSPLY']}{Style.reset}={Fore.green_yellow}{self.FLRL_WTR_DSPLY}{Style.reset}
        {Fore.grey_50}WD_DSPLY{Style.reset}:{Fore.grey_70}{types['WD_DSPLY']}{Style.reset}={self.WD_DSPLY}{Style.reset}
        {Fore.grey_50}CHKSTND_SPLY{Style.reset}:{Fore.grey_70}{types['CHKSTND_SPLY']}{Style.reset}={self.CHKSTND_SPLY}{Style.reset}
        {Fore.light_salmon_3a}Stock_Total{Style.reset}:{Fore.grey_70}{types['Stock_Total']}{Style.reset}={self.Stock_Total},
        {Fore.magenta_3c}InList{Style.reset}{Fore.grey_70}:{types['InList']}{Style.reset}={self.InList}
        {Fore.indian_red_1b}{Style.bold}{Style.underline}{Style.blink}ListQty{Style.reset}:{Fore.grey_70}{types['userUpdated']}{Style.reset}={self.ListQty}
        {Fore.misty_rose_3}Location{Style.reset}:{Fore.grey_70}{types['Location']}{Style.reset}={self.Location}
        {Fore.orange_3}Distress:{Fore.grey_70}{types['Distress']}{Style.reset}={Fore.light_red}{self.Distress},

        {Fore.orange_red_1}{Style.bold}Count Fields{Style.reset}
        {Fore.sky_blue_2}CaseCount{Style.reset}:{Fore.grey_70}{types['CaseCount']}{Style.reset}={self.CaseCount}
        {Fore.light_steel_blue}ShelfCount{Style.reset}:{Fore.grey_70}{types['ShelfCount']}{Style.reset}={self.ShelfCount},
        {Fore.light_steel_blue}PalletCount{Style.reset}:{Fore.grey_70}{types['PalletCount']}{Style.reset}={self.PalletCount},
        {Fore.light_steel_blue}LoadCount{Style.reset}:{Fore.grey_70}{types['LoadCount']}{Style.reset}={self.LoadCount},
        
        {Fore.sky_blue_2}Size{Style.reset}:{Fore.grey_70}{types['Size']}{Style.reset}={self.Size}
        {Fore.tan}Image[{Fore.dark_goldenrod}Exists:{Fore.deep_pink_3b}{self.imageExists()}{Style.reset}{Fore.tan}]{Style.reset}:{Fore.grey_70}{types['Image']}{Style.reset}={self.Image}
        {Fore.orange_red_1}(Estimated/Inverted Shelf Qty) Shelf=ShelfCount - Qty {Fore.light_yellow}[{Fore.cyan}{self.ShelfCount}{Fore.light_yellow} -{Fore.cyan}{self.Shelf}{Fore.light_yellow}]={Fore.pale_green_1b}{self.ShelfCount-self.Shelf}{Style.reset}"""
        if self.imageExists():
            m+=f"""
        {Fore.green}Image {Fore.orange_3}{Style.bold}{Style.underline}ABSOLUTE{Style.reset}{Style.reset}={Path(self.Image).absolute()}"""
        mtext=''
        with Session(ENGINE) as session:
            extras=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==self.EntryId).all()
            ct=len(extras)
            mtext=[]
            for n,e in enumerate(extras):
                mtext.append(f"\t -{Fore.orange_red_1}{e.field_name}:{Fore.light_steel_blue}{e.field_type}={Fore.light_yellow}{e.field_value} {Fore.cyan}ede_id={e.ede_id} {Fore.light_magenta}doe={e.doe}{Style.reset}")
            mtext='\n'.join(mtext)
        m+=f"\n{mtext}"
        m+="""
        )
        """
        if self.Barcode and len(self.Barcode) >= 13:
            print(f"{Fore.hot_pink_1b}Detected Code is 13 digits long; please verify the 'EAN13 Stripped $var_x=$var_z' data first before using the UPC Codes!{Style.reset}")
        pc.PossibleCodes(scanned=self.Barcode)
        pc.PossibleCodesEAN13(scanned=self.Barcode)
        return m

   
DayLog.metadata.create_all(ENGINE)



class TouchStamp(BASE):
    __tablename__="TouchStamp"
    EntryId=Column(Integer)
    TouchStampId=Column(Integer,primary_key=True)
    Timestamp=Column(DateTime)
    Note=Column(String)
    geojson=Column(String)


    def __init__(self,EntryId,Note,Timestamp=datetime.now(),TouchStampId=None):
        if TouchStampId:
            self.TouchStampId=TouchStampId
        self.EntryId=EntryId
        self.Note=Note
        self.Timestamp=Timestamp
        
        try:
            d=geocoder.ip("me")
            print(d,d.geojson)
            self.geojson=json.dumps(d.geojson)
        except Exception as e:
            print(e)
            self.geojson=''

    def __str__(self):
        entry=None
        try:
            with Session(ENGINE) as session:
                entry=session.query(Entry).filter(Entry.EntryId==self.EntryId).first()
                if entry:
                    msg=f"""
TouchStamp(
    {Style.bold+Style.underline+Fore.orange_red_1}TouchStampId{Style.reset}={Fore.yellow}{self.TouchStampId}{Style.reset}
    {Fore.dark_goldenrod}EntryId{Style.reset}={Fore.green}"{self.EntryId}"{Style.reset},
    {Fore.green}Note{Style.reset}={Fore.tan}"{self.Note}"{Style.reset},
    {Fore.yellow}Timestamp{Style.reset}={Fore.pale_green_1b}{self.Timestamp}{Style.reset},
    {Fore.violet}Timestamp_converted{Style.reset}={Fore.magenta_3a}"{self.Timestamp.ctime()}{Style.reset}",
    {Fore.grey_50}geojson{Style.reset}={Fore.green_yellow}"{self.geojson}",{Style.reset}

    {Fore.dark_goldenrod}EntryId{Style.reset} refers to:
    =====================================
                        {entry}
    =====================================
    )
    """
                    return msg
        except Exception as e:
            print(e)
        msg=f"""
                TouchStamp(
    {Style.bold+Style.underline+Fore.orange_red_1}TouchStampId{Style.reset}={Fore.yellow}{self.TouchStampId}{Style.reset}
    {Fore.dark_goldenrod}EntryId{Style.reset}={Fore.green}"{self.EntryId}"{Style.reset},
    {Fore.green}Note{Style.reset}={Fore.tan}"{self.Note}"{Style.reset},
    {Fore.yellow}Timestamp{Style.reset}={Fore.pale_green_1b}{self.Timestamp}{Style.reset},
    {Fore.violet}Timestamp_converted{Style.reset}={Fore.magenta_3a}"{self.Timestamp.ctime()}{Style.reset}",
    {Fore.grey_50}geojson{Style.reset}={Fore.green_yellow}"{self.geojson}",{Style.reset}

    {Fore.dark_goldenrod}EntryId{Style.reset} refers to:
    =====================================
                        {entry}
    =====================================
    )
    """
        return msg
TouchStamp.metadata.create_all(ENGINE)


class EntrySet:
    def mkText(self,text,data):
        return text
    def __init__(self,engine,parent):
        self.helpText=f'''
{Fore.orange_3}#code is:
    Code -    returns multiple results,prefixed by a
              'c.' searches by ; else uses first result
    EntryId - returns 1 entry,prefixed by a 'e.' 
              searches by ; else uses first result
    Barcode - returns multiple results,
              prefixed by a 'b.' searches by ; else uses first 
              result
{Style.reset}

{Fore.violet}fields|flds|list_fields{Style.reset} - {Fore.grey_70}list fields to edit{Style.reset}
{Fore.green_yellow}scan_set|ss|set{Style.reset} - {Fore.grey_70}scan a #code with prompt for field and value{Style.reset}
{Fore.green_yellow}scan_set|ss|set,$code{Style.reset} - {Fore.grey_70}get #code and set $field && $value from prompt{Style.reset}
{Fore.green_yellow}scan_set|ss|set,$field,#code{Style.reset} - {Fore.grey_70}prompt for $value of $field for #code{Style.reset}
{Fore.green_yellow}scan_set|ss|set,$field,$value,#code{Style.reset} - {Fore.grey_70}set $value of $field for #code no prompt{Style.reset}
{Fore.green_yellow}ssb{Style.reset} - {Fore.grey_70}set $value of $field for #code by prompt in batchmode{Style.reset}
{Fore.green}search|s|sch|find|lu|lookup{Style.reset} - {Fore.grey_70}find code by prompt and display #uses extensions listed at top{Style.reset}
{Fore.green}search|s|sch|find|lu|lookup,#code{Style.reset} - {Fore.grey_70}find #code and display #uses extensions listed at top{Style.reset}
{Fore.dark_goldenrod}remove|delete,#code{Style.reset} - {Fore.grey_70}remove an #code{Style.reset}
{Fore.dark_goldenrod}remove|delete{Style.reset} - {Fore.grey_70}remove an Entry{Style.reset}
{Fore.tan}help|?{Style.reset} - {Fore.grey_70}display help text by Prompted Id{Style.reset}
        '''
        self.engine=engine
        self.parent=parent
        self.valid_fields={i.name:i.type for i in Entry.__table__.columns}
        self.valid_field_names=tuple([i.name for i in Entry.__table__.columns])

        while True:
            try:
                #do=input(f"{Fore.green_yellow}Do What? :{Style.reset} ")
                fieldname='Menu'
                mode='ItemEdit'
                h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                do=Prompt.__init2__(None,func=self.mkText,ptext=f"{h}Do What?",helpText=self.helpText,data=None)
                if do in [None,]:
                    return
                elif do.lower() in ['?','help']:
                    self.helpTextPrint()
                elif do.lower() in ['ssb']:
                    self.ssb()
                else:
                    spl=do.split(",")
                    if spl[0].lower() in ['ss','scan_set','set']:
                        if spl[0].lower() in ['q','quit']:
                            exit("user quit!")
                        elif spl[0].lower() in ['b','back']:
                            return
                        else:
                            if len(spl) == 1:
                                self.scan_set(loop=True)
                            elif len(spl) == 2:
                                self.scan_set(code=spl[-1])
                            elif len(spl) == 3:
                                self.scan_set(code=spl[-1],field=spl[-2])
                            elif len(spl) == 4:
                                self.scan_set(code=spl[-1],field=spl[-3],value=spl[-2])
                            else:
                                self.helpTextPrint()
                    if spl[0].lower() in ['fields','flds','list_fields']:
                        self.list_fields()
                    elif spl[0].lower() in 'search|s|sch|find|lu|lookup'.split('|'):
                        if len(spl) == 1:
                            self.search()
                        elif len(spl) == 2:
                            self.search(code=spl[-1])
                    elif spl[0].lower() in 'remove|delete'.split('|'):
                        if len(spl) == 1:
                            self.delete()
                        elif len(spl) == 2:
                            self.delete(code=spl[-1])
            except Exception as e:
                print(e)

    def list_fields(self):
        for num,field in enumerate(Entry.__table__.columns):
            print(f"{Style.bold+Style.underline+Fore.orange_red_1}{num}{Style.reset} -> {Fore.magenta_3a}{field.name}{Style.reset}({Fore.violet}{field.type}{Style.reset})")


    def helpTextPrint(self):
        print(self.helpText)

    def search(self,code=None):
        if code == None:
            fieldname='Menu'
            mode='ItemEdit'
            h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
            code=Prompt.__init2__(None,func=self.mkText,ptext=f"{h}{Fore.cyan}Barcode{Style.reset}|{Fore.green_yellow}Code{Style.reset}|{Fore.yellow}EntryId",helpText=self.helpText,data=None)
            if code in [None,]:
                return
            #code=input(f"{Fore.cyan}Barcode{Style.reset}|{Fore.green_yellow}Code{Style.reset}|{Fore.yellow}EntryId{Style.reset}: ")
            #get item next
        with Session(self.engine) as session:
            ext=code.lower().split('.')[0]
            cd=code.lower().split('.')[-1]
            if cd.lower() in ['q','quit']:
                exit("user quit!")
            elif cd.lower() in ['back','b']:
                return
            elif cd.lower() in ['?','help']:
                self.helpTextPrint()
            #result=session.query()
            if ext in ['b']:
                try:
                    result=session.query(Entry).filter(or_(Entry.Barcode==cd,Entry.Barcode.icontains(cd))).all()
                    ct=len(result)
                    for num,r in enumerate(result):
                        print(f"{num}/{ct-1} -> {r}")
                    print(f"{Fore.green}{Style.bold}Total Results:{Style.reset} {Fore.cyan}{ct}{Style.reset}")
                except Exception as e:
                    raise e
            elif ext in ['c']:
                try:
                    result=session.query(Entry).filter(or_(Entry.Code==cd,Entry.Code.icontains(cd))).all()
                    ct=len(result)
                    for num,r in enumerate(result):
                        print(f"{num}/{ct-1} -> {r}")
                    print(f"{Fore.green}{Style.bold}Total Results:{Style.reset} {Fore.cyan}{ct}{Style.reset}")
                except Exception as e:
                    raise e
            elif ext in ['e']:
                #entry id
                try:
                    cdi=int(cd)
                    result=session.query(Entry)
                    result=result.filter(Entry.EntryId==cdi).first()
                    print(result)
                except Exception as e:
                    raise e
            else:
                result=session.query(Entry)
                try:
                    try:
                        cdi=int(eval(cd))
                    except Exception as e:
                        print(e)
                        cdi=int(cd)
                    result=session.query(Entry)
                    result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi))
                except Exception as e:
                    print(e)
                    result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd)))
                result=result.all()
                ct=len(result)
                for num,r in enumerate(result):
                    print(f"{num}/{ct-1} -> {r}")
                print(f"{Fore.green}{Style.bold}Total Results:{Style.reset} {Fore.cyan}{ct}{Style.reset}")

    def delete(self,code=None):
        if code == None:
            #code=input(f"{Fore.cyan}Barcode{Style.reset}|{Fore.green_yellow}Code{Style.reset}|{Fore.yellow}EntryId{Style.reset}: ")
            fieldname='Menu'
            mode='ItemEdit'
            h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
            code=Prompt.__init2__(None,func=self.mkText,ptext=f"{h}{Fore.cyan}Barcode{Style.reset}|{Fore.green_yellow}Code{Style.reset}|{Fore.yellow}EntryId",helpText=self.helpText,data=None)
            if code in [None,]:
                return
            #get item next
        with Session(self.engine) as session:
            ext=code.lower().split('.')[0]
            cd=code.lower().split('.')[-1]
            if cd.lower() in ['q','quit']:
                exit("user quit!")
            elif cd.lower() in ['back','b']:
                return
            elif cd.lower() in ['?','help']:
                self.helpTextPrint()
            #result=session.query()
            if ext in ['b']:
                try:
                    result=session.query(Entry).filter(or_(Entry.Barcode==cd,Entry.Barcode.icontains(cd))).all()
                    ct=len(result)
                    for num,r in enumerate(result):
                        print(f"{num}/{ct-1} -> {r}")

                    print(f"({Fore.green}{Style.bold}Total Results:{Style.reset} {Fore.cyan}{ct}{Style.reset}")
                    if ct > 1:
                        def mkSelection(text,data):
                            try:
                                if text in '':
                                    return 0
                                else:
                                    return int(text)
                            except Exception as e:
                               return
                        delete_which=Prompt.__init2__(None,func=mkSelection,ptext=f"{Fore.dark_goldenrod}Delete Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ",helpText='',data=self)
                        #edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ")
                        if delete_which in [None,]:
                            return
                        else:
                            dlt=session.delete(result[delete_which])
                            session.commit()
                    else:
                        print(f"{Fore.light_red}Nothing To Delete!{Style.reset}")
                except Exception as e:
                    raise e
            elif ext in ['c']:
                try:
                    result=session.query(Entry).filter(or_(Entry.Code==cd,Entry.Code.icontains(cd))).all()
                    ct=len(result)
                    for num,r in enumerate(result):
                        print(f"{num}/{ct-1} -> {r}")
                    print(f"({Fore.green}{Style.bold}Total Results:{Style.reset} {Fore.cyan}{ct}{Style.reset}")
                    if ct > 1:
                        def mkSelection(text,data):
                            try:
                                if text in '':
                                    return 0
                                else:
                                    return int(text)
                            except Exception as e:
                               return
                        delete_which=Prompt.__init2__(None,func=mkSelection,ptext=f"{Fore.dark_goldenrod}Delete Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ",helpText='',data=self)
                        #edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ")
                        if delete_which in [None,]:
                            return
                        else:
                            dlt=session.delete(result[delete_which])
                            session.commit()
                    else:
                        print(f"{Fore.light_red}Nothing To Delete!{Style.reset}")
                except Exception as e:
                    raise e
            elif ext in ['e']:
                #entry id
                try:
                    cdi=int(cd)
                    result=session.query(Entry)
                    result=result.filter(Entry.EntryId==cdi).first()
                    print(result)
                    session.delete(result)
                except Exception as e:
                    raise e
            else:
                result=session.query(Entry)
                try:
                    try:
                        cdi=int(eval(cd))
                    except Exception as e:
                        print(e)
                        cdi=into(cd)
                    result=session.query(Entry)
                    result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi))
                except Exception as e:
                    print(e)
                    result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd)))
                result=result.all()
                ct=len(result)
                for num,r in enumerate(result):
                    print(f"{num}/{ct-1} -> {r}")
                print(f"({Fore.green}{Style.bold}Total Results:{Style.reset} {Fore.cyan}{ct}{Style.reset}")
                if ct > 1:
                    def mkSelection(text,data):
                        try:
                            if text in '':
                                return 0
                            else:
                                return int(text)
                        except Exception as e:
                           return
                    delete_which=Prompt.__init2__(None,func=mkSelection,ptext=f"{Fore.dark_goldenrod}Delete Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ",helpText='',data=self)
                    #edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ")
                    if delete_which in [None,]:
                        return
                    else:
                        dlt=session.delete(result[delete_which])
                        session.commit()
                else:
                    print(f"{Fore.light_red}Nothing To Delete!{Style.reset}")

    def ssb(self):
        def mkT(text,self):
            return text
        new_value=Prompt.__init2__(None,func=mkT,ptext="New Value To Apply",helpText="value to apply to items scanned",data=self)
        def mkF(text,self):
            if text in self:
                return text
            else:
                raise Exception(f"try one of [{self}] instead of '{text}'!")
        fields=[i.name for i in Entry.__table__.columns]
        field=Prompt.__init2__(None,func=mkF,ptext="Field",helpText=f"Field to apply value to from [{fields}]",data=fields)
        if field in [None,]:
            return
        while True:
            code=Prompt.__init2__(None,func=mkT,ptext="Code|Barcode|EntryId",helpText="#code to apply data to")
            if code in [None,]:
                break
            self.scan_set(code=code,value=new_value,field=field)


    #loop only applies when code=None and field=None and value=None
    def scan_set(self,code=None,field=None,value=None,loop=False):
        #print(code,field,value)
        if code and field and value:
            print(code,field,value)
            if field not in self.valid_field_names:
                raise Exception(f"InvalidField '{field}:{self.valid_field_names}'")
            if field in ['Timestamp',]:
                raise Exception(f"Field not supported for changes yet!")


            with Session(self.engine) as session:
                ext=code.lower().split('.')[0]
                cd=code.lower().split('.')[-1]
                cd_orig=code.split('.')[-1]
                #result=session.query()
                if ext in ['b']:
                    try:
                        result=session.query(Entry).filter(or_(Entry.Barcode==cd,Entry.Barcode.icontains(cd),Entry.Barcode.icontains(cd_orig))).all()
                        ct=len(result)
                        for num,r in enumerate(result):
                            print(f"{num}/{ct-1} -> {r}")
                        def mkSelection(text,data):
                            try:
                                if text in '':
                                    return 0
                                else:
                                    return int(text)
                            except Exception as e:
                               return
                        edit_which=Prompt.__init2__(None,func=mkSelection,ptext=f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ",helpText='',data=self)
                        #edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ")
                        if edit_which in [None,]:
                            return
                        else:
                            self.setValuePrompt(field,result[edit_which],session,value=value)
                    except Exception as e:
                        raise e
                elif ext in ['c']:
                    try:
                        result=session.query(Entry).filter(or_(Entry.Code==cd,Entry.Code.icontains(cd)),Entry.Code.icontains(cd_orig)).all()
                        ct=len(result)
                        for num,r in enumerate(result):
                            print(f"{num}/{ct-1} -> {r}")
                        def mkSelection(text,data):
                            try:
                                if text in '':
                                    return 0
                                else:
                                    return int(text)
                            except Exception as e:
                               return
                        edit_which=Prompt.__init2__(None,func=mkSelection,ptext=f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ",helpText='',data=self)
                        #edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ")
                        if edit_which in [None,]:
                            return
                        else:
                            self.setValuePrompt(field,result[edit_which],session,value=value)
                    except Exception as e:
                        raise e
                elif ext in ['e']:
                    #entry id
                    try:
                        cdi=int(cd)
                        result=session.query(Entry)
                        result=result.filter(Entry.EntryId==cdi).first()
                        if result:
                            self.setValuePrompt(field,result,session,value=value)
                    except Exception as e:
                        raise e
                else:
                    result=session.query(Entry)
                    try:
                        try:
                            cdi=int(eval(cd))
                        except Exception as e:
                            print(e)
                            cdi=None
                        if cdi:
                            result=session.query(Entry)
                            result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi,Entry.Code==cd_orig,Entry.Barcode==cd_orig))
                        else:
                            result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.Code==cd_orig,Entry.Barcode==cd_orig))
                    except Exception as e:
                        print(e)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.Code==cd_orig,Entry.Barcode==cd_orig))
                    result=result.all()
                    ct=len(result)
                    for num,r in enumerate(result):
                        print(f"{num}/{ct-1} -> {r}")

                    def mkSelection(text,data):
                        try:
                            if text in '':
                                return 0
                            else:
                                return int(text)
                        except Exception as e:
                           return
                    edit_which=Prompt.__init2__(None,func=mkSelection,ptext=f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ",helpText='',data=self)
                    #edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ")
                    if edit_which in [None,]:
                        return
                    else:
                        self.setValuePrompt(field,result[edit_which],session,value=value)
        elif code and field and value == None:
            if field not in self.valid_field_names:
                raise Exception(f"InvalidField '{field}:{self.valid_field_names}'")
            if field in ['Timestamp',]:
                raise Exception(f"Field not supported for changes yet!")

            with Session(self.engine) as session:
                ext=code.lower().split('.')[0]
                cd=code.lower().split('.')[-1]
                cd_orig=code.split('.')[-1]
                #result=session.query()
                if ext in ['b']:
                    try:
                        result=session.query(Entry).filter(or_(Entry.Barcode==cd,Entry.Barcode.icontains(cd),Entry.Barcode.icontains(cd_orig))).all()
                        ct=len(result)
                        for num,r in enumerate(result):
                            print(f"{num}/{ct-1} -> {r}")
                        def mkSelection(text,data):
                            try:
                                if text in '':
                                    return 0
                                else:
                                    return int(text)
                            except Exception as e:
                               return
                        edit_which=Prompt.__init2__(None,func=mkSelection,ptext=f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ",helpText='',data=self)
                        #edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ")
                        if edit_which in [None,]:
                            return
                        else:
                            self.setValuePrompt(field,result[edit_which],session)
                    except Exception as e:
                        raise e
                elif ext in ['c']:
                    try:
                        result=session.query(Entry).filter(or_(Entry.Code==cd,Entry.Code.icontains(cd),Entry.Code.icontains(cd_orig))).all()
                        ct=len(result)
                        for num,r in enumerate(result):
                            print(f"{num}/{ct-1} -> {r}")
                        def mkSelection(text,data):
                            try:
                                if text in '':
                                    return 0
                                else:
                                    return int(text)
                            except Exception as e:
                               return
                        edit_which=Prompt.__init2__(None,func=mkSelection,ptext=f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ",helpText='',data=self)
                        #edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ")
                        if edit_which in [None,]:
                            return
                        else:
                            self.setValuePrompt(field,result[edit_which],session)
                    except Exception as e:
                        raise e
                elif ext in ['e']:
                    #entry id
                    try:
                        cdi=int(cd)
                        result=session.query(Entry)
                        result=result.filter(Entry.EntryId==cdi).first()
                        if result:
                            self.setValuePrompt(field,result,session)
                    except Exception as e:
                        raise e
                else:
                    result=session.query(Entry)
                    try:
                        try:
                            cdi=int(eval(cd))
                        except Exception as e:
                            print(e)
                            cdi=int(cd)
                        result=session.query(Entry)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi,Entry.Barcode==cd_orig,Entry.Code==cd_orig))
                    except Exception as e:
                        print(e)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.Barcode==cd_orig,Entry.Code==cd_orig))
                    result=result.all()
                    ct=len(result)
                    for num,r in enumerate(result):
                        print(f"{num}/{ct-1} -> {r}")
                    def mkSelection(text,data):
                        try:
                            if text in '':
                                return 0
                            else:
                                return int(text)
                        except Exception as e:
                           return
                    edit_which=Prompt.__init2__(None,func=mkSelection,ptext=f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ",helpText='',data=self)
                    #edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ")
                    if edit_which in [None,]:
                        return
                    else:
                        self.setValuePrompt(field,result[edit_which],session)
        elif code and field == None and value == None:
            field=input(f"{Fore.green_yellow}Field(see help|?): {Style.reset}")
            if field.lower() in ['q','quit']:
                    exit("user quit!")
            elif field.lower() in ['back','b','']:
                return
            elif field.lower() in ['?','help']:
                self.helpTextPrint()
                return

            if field not in self.valid_field_names:
                raise Exception(f"InvalidField '{field}:{self.valid_field_names}'")
            if field in ['Timestamp',]:
                raise Exception(f"Field not supported for changes yet!")

            with Session(self.engine) as session:
                ext=code.lower().split('.')[0]
                cd_orig=code.split(".")[-1]
                cd=code.lower().split('.')[-1]
                print(code,cd,ext)
                #result=session.query()
                if ext in ['b']:
                    try:
                        result=session.query(Entry).filter(or_(Entry.Barcode==cd,Entry.Barcode.icontains(cd),Entry.Barcode.icontains(cd_orig))).all()
                        ct=len(result)
                        for num,r in enumerate(result):
                            print(f"{num}/{ct-1} -> {r}")
                        def mkSelection(text,data):
                            try:
                                if text in '':
                                    return 0
                                else:
                                    return int(text)
                            except Exception as e:
                               return
                        edit_which=Prompt.__init2__(None,func=mkSelection,ptext=f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ",helpText='',data=self)
                        #edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ")
                        if edit_which in [None,]:
                            return
                            self.setValuePrompt(field,result[edit_which],session)
                    except Exception as e:
                        raise e
                elif ext in ['c']:
                    try:
                        result=session.query(Entry).filter(or_(Entry.Code==cd,Entry.Code.icontains(cd),Entry.Code.icontains(cd_orig))).all()
                        ct=len(result)
                        for num,r in enumerate(result):
                            print(f"{num}/{ct-1} -> {r}")
                        def mkSelection(text,data):
                            try:
                                if text in '':
                                    return 0
                                else:
                                    return int(text)
                            except Exception as e:
                               return
                        edit_which=Prompt.__init2__(None,func=mkSelection,ptext=f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ",helpText='',data=self)
                        #edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ")
                        if edit_which in [None,]:
                            return
                        else:
                            self.setValuePrompt(field,result[edit_which],session)
                    except Exception as e:
                        raise e
                elif ext in ['e']:
                    #entry id
                    try:
                        cdi=int(cd)
                        result=session.query(Entry)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi)).first()
                        if result:
                            self.setValuePrompt(field,result,session)
                    except Exception as e:
                        raise e
                else:
                    result=session.query(Entry)
                    try:
                        try:
                            cdi=int(eval(cd))
                        except Exception as e:
                            print(e)
                            cdi=int(cd)
                        result=session.query(Entry)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi,Entry.Barcode==cd_orig,Entry.Code==cd_orig))
                    except Exception as e:
                        print(e)
                        result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.Barcode==cd_orig,Entry.Code==cd_orig))
                    result=result.all()
                    ct=len(result)
                    for num,r in enumerate(result):
                        print(f"{num}/{ct-1} -> {r}")
                    def mkSelection(text,data):
                        try:
                            if text in '':
                                return 0
                            else:
                                return int(text)
                        except Exception as e:
                           return
                    edit_which=Prompt.__init2__(None,func=mkSelection,ptext=f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ",helpText='',data=self)
                    #edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ")
                    if edit_which in [None,]:
                        return
                    else:
                        self.setValuePrompt(field,result[edit_which],session)
        elif code == None and field == None and value == None:
            while True:
                fieldname='Menu'
                mode='ItemEdit'
                h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                code=Prompt.__init2__(None,func=self.mkText,ptext=f"{h}{Fore.cyan}Barcode{Style.reset}|{Fore.green_yellow}Code{Style.reset}|{Fore.yellow}EntryId",helpText=self.helpText+"\nBack from here returns to previous menu!",data=None)
                if code in [None,]:
                    return
                #code=input(f"{Fore.cyan}Barcode{Style.reset}|{Fore.green_yellow}Code{Style.reset}|{Fore.yellow}EntryId{Style.reset}: ")
                #get item next

                #field=input(f"{Fore.green_yellow}Field(see help|?): {Style.reset}")
                fieldname='Menu'
                mode='ItemEdit'
                h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                fieldsHelp=f''''''
                fieldsList=[i.name for num,i in enumerate(Entry.__table__.columns)]
                fieldsCountStr=[str(i) for i in range(len(fieldsList))]
                headers_footer=f'{Fore.light_yellow}FieldName -> Quick Select. Option No.{Style.reset}'
                base=255
                mult=2
                colors=[Fore.rgb(base-num*mult,base-num*mult,base-num*mult) for num in range(len(fieldsList))] 
                fieldsMapped2='\n'.join([f'{colors[num]}{f} -> {num}{Style.reset}' for num,f in enumerate(fieldsList)])
                fieldsMapped2=headers_footer+"\n"+fieldsMapped2+"\n"+headers_footer+"\nback from here returns to code prompt"
                which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h}{Fore.green_yellow}Which Field number(see help|h)",helpText=fieldsMapped2,data="integer")
                if which in ['d',]:
                    field=Prompt.__init2__(None,func=self.mkText,ptext=f"{h}{Fore.green_yellow}Field by Literal Name(see help|h)",helpText=fieldsMapped2,data=None)
                    if field in [None,]:
                        if loop == False:
                            return
                        else:
                            continue
                elif which in [None,]:
                    if loop == False:
                        return
                    else:
                        continue
                else:
                    field=fieldsList[which]
                    if field in [None,]:
                        if loop == False:
                            return
                        else:
                            continue

                if field not in self.valid_field_names:
                    if field in fieldsCountStr:
                        field=fieldsList[int(field)]
                    else:
                        raise Exception(f"InvalidField '{field}:{self.valid_field_names}'")
                
                #if field in ['Timestamp',]:
                #    raise Exception(f"Field not supported for changes yet!")

                with Session(self.engine) as session:
                    ext=code.lower().split('.')[0]
                    cd=code.lower().split('.')[-1]
                    cd_orig=code.split(".")[-1]
                    if cd.lower() in ['q','quit']:
                        exit("user quit!")
                    elif cd.lower() in ['back','b']:
                        return
                    elif cd.lower() in ['?','help']:
                        self.helpTextPrint()
                    #result=session.query()
                    if ext in ['b']:
                        try:
                            #5.26.24
                            result=session.query(Entry).filter(or_(Entry.Barcode==cd,Entry.Barcode.icontains(cd_orig))).all()
                            ct=len(result)
                            for num,r in enumerate(result):
                                print(f"{num}/{ct-1} -> {r}")
                            def mkSelection(text,data):
                                try:
                                    if text in '':
                                        return 0
                                    else:
                                        return int(text)
                                except Exception as e:
                                   return
                            edit_which=Prompt.__init2__(None,func=mkSelection,ptext=f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ",helpText='back from here returns to code prompt',data=self)
                            #edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ")
                            if edit_which in [None,]:
                                if loop == False:
                                    return
                                else:
                                    continue
                            else:
                                self.setValuePrompt(field,result[edit_which],session)
                        except Exception as e:
                            raise e
                    elif ext in ['c']:
                        try:
                            result=session.query(Entry).filter(or_(Entry.Code==cd,Entry.Code.icontains(cd),Entry.Code.icontains(cd_orig))).all()
                            ct=len(result)
                            for num,r in enumerate(result):
                                print(f"{num}/{ct-1} -> {r}")
                            def mkSelection(text,data):
                                try:
                                    if text in '':
                                        return 0
                                    else:
                                        return int(text)
                                except Exception as e:
                                   return
                            edit_which=Prompt.__init2__(None,func=mkSelection,ptext=f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ",helpText='back from here returns to code prompt',data=self)
                            #edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ")
                            if edit_which in [None,]:
                                if loop == False:
                                    return
                                else:
                                    continue
                            else:
                                self.setValuePrompt(field,result[edit_which],session)
                        except Exception as e:
                            raise e
                    elif ext in ['e']:
                        #entry id
                        try:
                            cdi=int(cd)
                            result=session.query(Entry)
                            result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi)).first()
                            if result:
                                self.setValuePrompt(field,result,session)
                        except Exception as e:
                            raise e
                    else:
                        result=session.query(Entry)
                        try:
                            try:
                                try:
                                    cdi=int(eval(cd))
                                except Exception as e:
                                    print(e,'#"',cd,cd_orig)
                                    cdi=int(cd)
                            except Exception as e:
                                print(e)
                                cdi=None

                            result=session.query(Entry)
                            if cdi:
                                result=result.filter(or_(Entry.Name.icontains(code),Entry.Name==code,Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.EntryId==cdi,Entry.Barcode==cd_orig,Entry.Code==cd_orig))
                            else:
                                result=result.filter(or_(Entry.Name.icontains(code),Entry.Name==code,Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.Barcode==cd_orig,Entry.Code==cd_orig))

                        except Exception as e:
                            print(e)
                            result=result.filter(or_(Entry.Barcode==str(cd),Entry.Code==str(cd),Entry.Barcode==cd_orig,Entry.Code==cd_orig))
                        result=result.all()
                        ct=len(result)
                        for num,r in enumerate(result):
                            print(f"{num}/{ct-1} -> {r}")
                        print(f"{Fore.light_green}Using {Fore.light_yellow}{field}{Style.reset}")
                        def mkSelection(text,data):
                            try:
                                if text in '':
                                    return 0
                                else:
                                    return int(text)
                            except Exception as e:
                               return
                        edit_which=Prompt.__init2__(None,func=mkSelection,ptext=f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ",helpText='back from here returns to code prompt',data=self)
                        #edit_which=input(f"{Fore.dark_goldenrod}Edit Which result {Style.reset}{Style.bold+Style.underline+Fore.orange_red_1}[num]{Style.reset}/{Fore.yellow}q|quit/b|back({Fore.cyan}Total Results={ct} & Default Entry=0){Style.reset}: ")
                        if edit_which in [None,]:
                            if loop == False:
                                return
                            else:
                                continue
                        else:
                            try:
                                r=int(edit_which)
                                print("At This Point Back will return to Code Prompt")
                                self.setValuePrompt(field,result[edit_which],session)
                            except Exception as e:
                                print(e)
                if not loop:
                    break
        else:
            self.helpTextPrint()

    def setValuePrompt(self,field,entry,session,value=None):
        if field == 'Timestamp':
            while True:
                try:
                    timestamp_new=DateTimePkr()
                    timestamp_new_f=timestamp_new.timestamp()
                    value=timestamp_new_f
                    break
                except Exception as e:
                    print(e)
        elif field == 'Image':
            copySrc(self,entry=entry)
        if not value:
            #value=input(f"{Fore.green_yellow}Value {Fore.yellow}OLD{Style.reset}={Fore.tan}{getattr(entry,field)} {Style.reset}({Fore.green}{self.valid_fields[field]}{Style.reset}): ")
            def mkValue(text,data):
                return text
            value=Prompt.__init2__(None,func=mkValue,ptext=f"{Fore.green_yellow}Value {Fore.yellow}OLD{Style.reset}={Fore.tan}{getattr(entry,field)} {Style.reset}({Fore.green}{self.valid_fields[field]}{Style.reset}): ",helpText='what value do you wish to use?',data=self)
            if value in [None,]:
                return

        if value not in ['',]:
            t=self.valid_fields[field]
            if isinstance(t,String):
                value=str(value)
            elif isinstance(t,Integer):
                try:
                    value=int(eval(value))
                except Exception as e:
                    value=int(value)
            elif isinstance(t,Float):
                try:
                    value=float(eval(value))
                except Exception as e:
                    value=float(value)
            elif isinstance(t,Boolean):
                if value not in ['True','False','1','0']:
                    raise Exception(f"Not a Boolean: {['True','False','1','0']}")
                value=bool(eval(value))
            setattr(entry,field,value)
            #as item was changed, log it in InList==True
            if field != 'InList':
                setattr(entry,"InList",True)
            if field != 'userUpdated':
                setattr(entry,'userUpdated',True)
            session.commit()
            session.flush()
            session.refresh(entry)
            print(entry)
        else:
            print(entry)
            print(f"{Fore.dark_goldenrod}{Style.underline}Nothing was changed!{Style.reset}")

def datePickerF(self,DATE=None,continue_replaced=False):
    y=DatePkr()
    #print(y)
    return y

def datetimePickerF(self,DATE=None,continue_replaced=False):
    y=DateTimePkr(DATE=DATE)  
    return y
    

class Shift(BASE):
    __tablename__="Shift"
    ShiftId=Column(Integer,primary_key=True)
    Date=Column(Date)
    start=Column(DateTime)
    end=Column(DateTime)
    break_start=Column(DateTime)
    break_end=Column(DateTime)

    def __str__(self):
        msg=f"{Fore.chartreuse_1}Shift({Style.reset}"
        for col in self.__table__.columns:
            color_val=''
            color_field=''
            field=col.name
            if field == 'start':
                color_field=Fore.green_yellow
                color_val=Fore.green+Style.bold
            elif field == 'end':
                color_field=Style.bold+Fore.light_red
                color_val=Fore.light_red
            elif field == 'break_start':
                color_field=Fore.cyan
                color_val=Fore.dark_goldenrod
            elif field == 'break_end':
                color_field=Fore.light_magenta
                color_val=Fore.light_yellow
            elif field == 'Date':
                color_field=Fore.pale_violet_red_1
                color_val=Fore.blue_violet
            elif field == 'ShiftId':
                color_field=Style.bold+Style.underline+Fore.orange_red_1+Style.italic
                color_val=Fore.grey_35+Style.underline
            
            msg+=f"{color_field}{col.name}{Style.reset}={color_val}{getattr(self,col.name)}{Style.reset},\n"
        if msg.endswith(",\n"):
            msg=msg[:-2]
        msg+=f"{Fore.chartreuse_1}){Style.reset}"
        return msg

    def __repr__(self):
        return self.__str__()



    def estimatedPunches_8h(self,start_time=datetime.now()):
        shift={}
        shift['Start']=start_time
        shift['lunchStart']=start_time+timedelta(seconds=4*60*60)
        shift['lunchEnd']=shift['lunchStart']+timedelta(seconds=30*60)
        shift['end']=shift['lunchEnd']+timedelta(seconds=4*60*60)
        for I in shift:
            print(f"{Fore.light_yellow}{I}{Style.reset}",shift.get(I).ctime(),sep='-')
        return shift

    def manual_estimate_8(self):
        while True:
            dt=datetimePickerF(None,continue_replaced=True)
            if not dt:
                break
            self.estimatedPunches_8h(None,start_time=dt)

    def manual_estimate_7(self):
        while True:
            dt=datetimePickerF(None,continue_replaced=True)
            if not dt:
                break
            self.estimatedPunches_7h(None,start_time=dt)

    def manual_estimate_6(self):
        while True:
            dt=datetimePickerF(None,continue_replaced=True)
            if not dt:
                break
            self.estimatedPunches_6h(None,start_time=dt)

    def manual_estimate_5(self):
        while True:
            dt=datetimePickerF(None,continue_replaced=True)
            if not dt:
                break
            self.estimatedPunches_5h(None,start_time=dt)

    def manual_estimate_4(self):
        while True:
            dt=datetimePickerF(None,continue_replaced=True)
            if not dt:
                break
            self.estimatedPunches_4h(None,start_time=dt)
        
    def estimatedPunches_4h(self,start_time=datetime.now()):
        shift={}
        shift['Start']=start_time
        #shift['lunchStart']=start_time+timedelta(seconds=4*60*60)
        #shift['lunchEnd']=shift['lunchStart']+timedelta(seconds=30*60)
        shift['end']=shift['Start']+timedelta(seconds=4*60*60)
        for I in shift:
            print(f"{Fore.light_yellow}{I}{Style.reset}",shift.get(I).ctime(),sep='-')
        return shift

    def estimatedPunches_5h(self,start_time=datetime.now()):
        shift={}
        shift['Start']=start_time
        shift['lunchStart']=start_time+timedelta(seconds=4*60*60)
        shift['lunchEnd']=shift['lunchStart']+timedelta(seconds=30*60)
        shift['end']=shift['Start']+timedelta(seconds=0.5*60*60)
        shift['Stay 5H and Clock Out Exactly on the 5H Mark']=shift['Start']+timedelta(seconds=5*60*60)
        for I in shift:
            print(f"{Fore.light_yellow}{I}{Style.reset}",shift.get(I).ctime(),sep='-')
        return shift

    def estimatedPunches_6h(self,start_time=datetime.now()):
        shift={}
        shift['Start']=start_time
        shift['lunchStart']=start_time+timedelta(seconds=4*60*60)
        shift['lunchEnd']=shift['lunchStart']+timedelta(seconds=30*60)
        shift['end']=shift['Start']+timedelta(seconds=2*60*60)
        for I in shift:
            print(f"{Fore.light_yellow}{I}{Style.reset}",shift.get(I).ctime(),sep='-')
        return shift

    def estimatedPunches_7h(self,start_time=datetime.now()):
        shift={}
        shift['Start']=start_time
        shift['lunchStart']=start_time+timedelta(seconds=4*60*60)
        shift['lunchEnd']=shift['lunchStart']+timedelta(seconds=30*60)
        shift['end']=shift['Start']+timedelta(seconds=3*60*60)
        for I in shift:
            print(f"{Fore.light_yellow}{I}{Style.reset}",shift.get(I).ctime(),sep='-')
        return shift

    def gross(self,rate,unit="$"):
        try:
            total_duration=None
            if self.start and self.end:
                total_duration=self.end-self.start
            else:
                raise Exception(f"self.start={self.start},self.end={self.end}")
            break_duration=None
            if (self.break_start and self.break_end) or (not self.break_start and not self.break_end):
                if self.break_start and self.break_end:
                    break_duration=self.break_end-self.break_start

            else:
                raise Exception(f"MUST Have Both Break Start and Break End: self.break_start={self.break_start},self.break_end={self.break_end}")
            
            if break_duration and total_duration:
                total_duration=total_duration-break_duration
                
            if isinstance(rate,float):
                ur=pint.UnitRegistry()
                dur=ur.convert(total_duration.total_seconds(),"seconds","hours")*rate
                dur=round(float(dur),3)
                print(f"{Fore.medium_purple_3b}{unit}{Fore.green}{dur}{Style.reset} @ {Fore.light_salmon_3a}{rate}{Style.reset}/Hr for {Fore.light_magenta}{total_duration}{Style.reset}{Fore.medium_violet_red}[{Fore.light_steel_blue}Hour:Minute:Second.MicroSec's{Style.reset}{Fore.medium_violet_red}]{Style.reset}")
                return dur
        except Exception as e:
            print(e)
        return 0

    def helpCard(self,start_arg=None):
        if self.start:
            start=self.start
        else:
            if start_arg:
                start=start_arg
            else:
                raise Exception("No valid start time!")
        print(f"{Fore.light_green}{'-'*15}\n|=| Estimated Punch Times |=|\n{Fore.light_yellow}{'-'*15}{Style.reset}")
        print(f"{Fore.light_blue} 4 Hr Shift{Style.reset}")
        print(f"{Fore.grey_70}{'*'*15}{Style.reset}")
        self.estimatedPunches_4h(start_time=start)
        print(f"{Fore.light_magenta} 5 Hr Shift{Style.reset}")
        print(f"{Fore.grey_70}{'*'*15}{Style.reset}")
        self.estimatedPunches_5h(start_time=start)
        print(f"{Fore.light_green} 6 Hr Shift{Style.reset}")
        print(f"{Fore.grey_70}{'*'*15}{Style.reset}")
        self.estimatedPunches_6h(start_time=start)
        print(f"{Fore.cyan} 7 Hr Shift{Style.reset}")
        print(f"{Fore.grey_70}{'*'*15}{Style.reset}")
        self.estimatedPunches_7h(start_time=start)
        print(f"{Fore.yellow} 8 Hr Shift{Style.reset}")
        print(f"{Fore.grey_70}{'*'*15}{Style.reset}")
        self.estimatedPunches_8h(start_time=start)
        print(f"{Fore.medium_violet_red}{'-'*15}\n{Fore.light_yellow}{'-'*15}{Style.reset}")


    def dc(self):
        now=datetime.now()
        if self.end:
            try:
                return (self.end-self.start)-(self.break_end-self.break_start)
            except Exception as e:
                return (self.end-self.start)
        else:
            return None

    def duration_completed(self):
        now=datetime.now()
        self.helpCard()
            
        if self.end:
            try:
                print(f"{Style.bold+Style.underline}{Fore.green_yellow}Shift{Style.reset} Has {Fore.light_red}Ended -> Total Duration{Style.reset}: {(self.end-self.start)-(self.break_end-self.break_start)}")
                print(f"{Style.bold+Style.underline}{Fore.green_yellow}Shift Break{Style.reset}{Fore.light_red} Duration{Style.reset}: {(self.break_end-self.break_start)}")
                return (self.end-self.start)-(self.break_end-self.break_start)
            except Exception as e:
                print(f"{Style.bold+Style.underline}{Fore.green_yellow}Shift{Style.reset} Has {Fore.light_red}Ended{Style.reset}: (start:{self.end}-end:{self.start})-(break_end:{self.break_end}-break_start:{self.break_start})")
                print(f"{Style.bold+Style.underline}{Fore.green_yellow}Shift{Style.reset} Has {Fore.light_red}Ended{Style.reset}: {(self.end-self.start)}")
                return (self.end-self.start)
        else:
            if self.break_start != None:
                if self.break_end != None:
                    #break is done
                    try:
                        print(f"{Style.bold+Style.underline}{Fore.green_yellow}Break{Style.reset} Is {Fore.medium_violet_red}Completed{Style.reset} Duration:{(now-self.start)-(self.break_end-self.break_start)}")
                    except Exception as e:
                        print(f"{Style.bold+Style.underline}{Fore.green_yellow}Break{Style.reset} Is {Fore.medium_violet_red}Completed{Style.reset} Duration:({now}-{self.start})-({self.break_end}-{self.break_start})")

                else:
                    #break is started but not ended
                    print(f"{Style.bold+Style.underline}{Fore.green_yellow}Break{Style.reset} Is {Fore.pale_green_1b}Started, But Not {Fore.light_red}Ended{Style.reset}: {now-self.break_start}")
            elif self.break_start == None:
                #break has not started
                print(f"{Style.bold+Style.underline}{Fore.green_yellow}Shift{Style.reset} has {Fore.pale_green_1b}Started, But Not {Style.bold+Style.underline}{Fore.green_yellow}Break{Style.reset} {now-self.start}")  
            print(f"{Fore.orange_red_1}{Style.bold}A Duration cannot be returned until self.end!=None[{self.end}]")
            return None

    def __init__(self,start,Date=date.today(),end=None,break_start=None,break_end=None,ShiftId=None):
        if ShiftId:
            self.ShiftId=ShiftId
        self.Date=Date
        self.start=start
        self.end=end
        self.break_end=break_end
        self.break_start=break_start
        

Shift.metadata.create_all(ENGINE)



from radboy.DB.RandomStringUtil import RandomString


class SystemPreference(BASE,Template):
    __tablename__="SystemPreferences"
    pid=Column(Integer,primary_key=True)
    name=Column(String)
    value_4_Json2DictString=Column(String)
    comment=Column(String)
    default=Column(Boolean)
    doe=Column(Date)
    toe=Column(Time)
    dtoe=Column(DateTime)
    def __init__(self,**kwargs):
            kwargs['__tablename__']=self.__tablename__
            self.init(**kwargs,)
SystemPreference.metadata.create_all(ENGINE)

class Billing(BASE,Template):
    __tablename__="Billing"
    default=Column(Boolean)
    sellerAddress=Column(String)
    sellerName=Column(String)
    sellerPhone=Column(String)
    sellerEmail=Column(String)
    purchaserEmail=Column(String)
    purchaserPhone=Column(String)
    purchaserName=Column(String)
    purchaserAddress=Column(String)
    BillingId=Column(Integer,primary_key=True)
    Date=Column(Date)
    RetailersPermitSerial=Column(String)
    CertofReg=Column(String)
    PaymentType=Column(String)
    def __init__(self,**kwargs):
        #kwargs['__tablename__']="Billing"
        kwargs['__tablename__']=self.__tablename__
        self.init(**kwargs,)

class RecieptEntry(BASE,Template):
    __tablename__="RecieptEntry"
    ReceiptEntryId=Column(Integer,primary_key=True)
    RecieptId=Column(Integer)
    Date=Column(Date)
    EntryCode=Column(String)
    EntryBarcode=Column(String)
    EntryName=Column(String)
    EntryId=Column(Integer)
    EntryPrice=Column(Float)
    QtySold=Column(Float)
    CRV=Column(Float)
    Tax=Column(Float)
    TaxNote=Column(String)
    def __init__(self,**kwargs):
        kwargs['__tablename__']=self.__tablename__
        self.init(**kwargs)

class AdditionalExpenseOrFee(BASE,Template):
    __tablename__="AdditionalExpenseOrFee"
    AdditionalExpenseId=Column(Integer,primary_key=True)
    RecieptId=Column(Integer)
    Value=Column(Integer)
    Name=Column(String)
    Comment=Column(String)
    DOE=Column(Date)#Date of Entry
    DD=Column(Date)#Due Date
    def __init__(self,**kwargs):
        kwargs['__tablename__']=self.__tablename__
        self.init(**kwargs)

Billing.metadata.create_all(ENGINE)
RecieptEntry.metadata.create_all(ENGINE)
AdditionalExpenseOrFee.metadata.create_all(ENGINE)

class DisplayItem(BASE,Template):
    __tablename__="DisplayItem"
    DID=Column(Integer,primary_key=True)
    #closest aisle or aisle range (for end caps)
    Aisle=Column(String)
    Date=Column(Date)
    #display type bools
    #end of aisle
    EndCap=Column(Boolean)
    ShadowBox=Column(Boolean)
    Gondolas=Column(Boolean)
    #Floor-standing display unit (FSDU)
    FreeStandingFSDU=Column(Boolean)
    
    #where the item resides, aisle, aisle range(endcap), 
    #the shelf number of the display where the item resides, 
    #the item number (not Code) of the items on display
    #prefered to be in AISLE/SHELF/MOD#
    #treat items like Shelf Location
    #left bottom to right, upwards
    DisplayLocation=Column(String)
    DisplayLocationStoreFront=Column(Boolean)
    #how much to put on display
    QtyForDisplay=Column(Integer)
    Barcode=Column(String)
    Code=Column(String)
    Name=Column(String)
    EntryId=Column(Integer)
    Note=Column(String)

    def __init__(self,**kwargs):
        kwargs['__tablename__']=self.__tablename__
        self.init(**kwargs,)


DisplayItem.metadata.create_all(ENGINE)

class Reciept(BASE,Template):
    __tablename__="Reciept"
    RecieptId=Column(Integer,primary_key=True)
    BillingId=Column(Integer)
    Date=Column(Date)
    
    def __init__(self,**kwargs):
        self.init(**kwargs)
        __tablename__="Reciept"

Reciept.metadata.create_all(ENGINE)

'''
class Counts(BASE,Template):
    __tablename__="Counts"
    CountsId=Column(Integer,primary_key=True)
    EntryId=Column(Integer)
    #How Much Typically Comes in Load
    LoadCount=Columm(Integer)
    #If product comes in pallets at a time, fill with how much comes
    PalletCount=Column(Integer)
    #how much can be held on the shelf at the time
    ShelfCount=Column(Integer)
    #how much comes in a case
    CaseCount=Column(Integer)

    #date and time of entry
    CountsDate=Column(Date)
    CountsTime=Column(Time)
    #whenever Entry is Deleted check here for corresponding information
    def __init__(self,**kwargs):
        self.init(**kwargs)

Counts.metadata.create_all(ENGINE)
'''

class RepackList(BASE,Template):
    def __init__(self,**kwargs):
        self.init(**kwargs)
    __tablename__="RepackList"
    repackDate=Column(Date)
    repackTime=Column(Time)
    repackDateTime=Column(DateTime)
    repackCaseBarcode=Column(String)

    repackListId=Column(Integer,primary_key=True)
    
    repackNote=Column(Text)

RepackList.metadata.create_all(ENGINE)

class RepackItem(BASE,Template):
    def __init__(self,**kwargs):
        self.init(**kwargs)
    __tablename__="RepackItem"
    RepackItemId=Column(Integer,primary_key=True)
    RepackListId=Column(Integer)

    EntryId=Column(Integer)
    EntryBarcode=Column(String)
    EntryCode=Column(String)
    EntryName=Column(String)
    EntryQty=Column(Integer)
    EntryNote=Column(String)
    EntryPrice=Column(Float)

RepackItem.metadata.create_all(ENGINE)

def detectGetOrSetClipBoord(name,value,setValue=False):
        value=str(value)
        with Session(ENGINE) as session:
            q=session.query(SystemPreference).filter(SystemPreference.name==name).first()
            ivalue=None
            if q:
                try:
                    if setValue:
                        try:
                            q.value_4_Json2DictString=json.dumps({name:eval(value)})
                        except Exception as e:
                            print(e)
                            q.value_4_Json2DictString=json.dumps({name:value})
                        session.commit()
                        session.refresh(q)
                    ivalue=json.loads(q.value_4_Json2DictString)[name]
                except Exception as e:
                    try:
                        q.value_4_Json2DictString=json.dumps({name:eval(value)})
                    except Exception as e:
                        print(e)
                        q.value_4_Json2DictString=json.dumps({name:value})
                    session.commit()
                    session.refresh(q)
                    ivalue=json.loads(q.value_4_Json2DictString)[name]
            else:
                try:
                    q=SystemPreference(name=name,value_4_Json2DictString=json.dumps({name:eval(value)}))
                except Exception as e:
                    print(e)
                    q=SystemPreference(name=name,value_4_Json2DictString=json.dumps({name:value}))
                session.add(q)
                session.commit()
                session.refresh(q)
                ivalue=json.loads(q.value_4_Json2DictString)[name]
            return ivalue
AGELIMIT=detectGetOrSetClipBoord("ClipBoordAgeLimit",7*365*24*60*60)
#for prompt clipboard editor to save a value for later use by selection, with an age limit and doe to auto delete
#basically a notepad
class ClipBoord(BASE,Template):
    __tablename__="ClipBoord"
    cbid=Column(Integer,primary_key=True)
    cbValue=Column(String)
    doe=Column(DateTime)
    ageLimit=Column(Float)
    defaultPaste=Column(Boolean)
    
    def __str__(self,vc=Fore.dark_blue+Style.bold,fc=Fore.light_green,cc=Fore.light_magenta,vg=Back.grey_50):
        m=[]
        m.append(f"{cc}{self.__tablename__}{Style.reset}(")
        fields=[i.name for i in self.__table__.columns]
        for i in fields:
            m.append(f"\t{fc}{i}{Style.reset}={vg}{vc}{getattr(self,i)}{Style.reset}")
        m.append(f"\t{Fore.orange_red_1}DOD={self.doe+timedelta(seconds=self.ageLimit)}{Style.reset}")
        m.append(")")
        return '\n'.join(m)

    def __init__(self,**kwargs):
        kwargs['__tablename__']=self.__tablename__
        self.init(**kwargs,)
ClipBoord.metadata.create_all(ENGINE)

class ClipBoordEditor:
    def reset_table(self):
        ClipBoord.__table__.drop(ENGINE)
        ClipBoord.metadata.create_all(ENGINE)
        exit(f"{Fore.orange_red_1}A restart is required!")

    def mkText(self,text,data):
        return text

    def mkint(self,value,data={'default':0}):
        v=data.get('default')
        try:
            v=int(value)
        except Exception as e:
            print(e)
        return v

    def mkNew(self,data=None):
        if data == None:
            data={
            'cbValue':'',
            'doe':datetime.now(),
            'ageLimit':self.ageLimit,
            'defaultPaste':False
            }
        self.skipTo=None
        while True:  
            #print(self.skipTo,"#loop top")
            for num,f in enumerate(data):
                #print(self.skipTo,'#2',"1 loop for")
                if self.skipTo != None and num < self.skipTo:
                    continue
                else:
                    self.skipTo=None
                keys=['e','p','d']
                otherExcludes=[]
                while True:
                    try:
                        dtmp=Prompt.__init2__(None,func=self.mkText,ptext=f"ClipBoord[default:{data[f]}] {f}",helpText=f"{Fore.light_steel_blue}Enter a value for {f}, or leave blank to use scanned code; 'b' goes back to 'TaskMode'; 'e' to skip/exit entry altogether! 'p' for previous ; 'd' to use default stored value, if you entered a value, then 'd' will use that value when coming back from 'p'{Style.reset}",data=self)
                        if dtmp in [None,]:
                            print(f"{Fore.orange_red_1}User Canceled!{Style.reset}")
                            return

                        if str(dtmp).lower() in ['e',]:
                            return
                        elif str(dtmp).lower() in ['p',]:
                            #print(num,num-1,"#3 loop while")
                            self.skipTo=num-1
                            break
                        elif str(dtmp).lower() in ['d',]:
                            print(f'{Fore.light_green}{data[f]}{Style.reset}',f'{Fore.orange_red_1}using default{Style.reset}')
                            pass
                        else:
                            fields={i.name:str(i.type) for i in ClipBoord.__table__.columns}
                            if f in fields.keys():
                                if fields[f].lower() in ["string",]:
                                    data[f]=dtmp
                                elif fields[f].lower() in ["float",]:
                                    data[f]=float(eval(dtmp))
                                elif fields[f].lower() in ["integer",]:
                                    try:
                                        data[f]=int(eval(dtmp))
                                    except Exception as e:
                                        data[f]=self.ageLimit
                                elif fields[f].lower() in ["boolean",]:
                                    data[f]=bool(eval(dtmp))
                                elif fields[f].lower() in ["datetime",]:
                                    if dtmp.lower() in 'y|yes|1|true|t'.split('|'):
                                        data[f]=DateTimePkr()
                                    else:
                                        data[f]=datetime.now()
                                else:
                                    data[f]=dtmp
                            else:
                                raise Exception(f"{Fore.red}{Style.bold}Unsupported Field {Fore.light_red}'{f}'{Style.reset}")
                                #data[f]=dtmp
                        self.skipTo=None
                        break
                    except Exception as e:
                        print(e)
                        break
                if self.skipTo != None:
                    break
            if self.skipTo == None:
                break
        return data

    def pastable(self):
        with Session(ENGINE) as session:
            paste=session.query(ClipBoord).filter(ClipBoord.defaultPaste==True).order_by(ClipBoord.doe.desc()).first()
            if paste:
                msg=f'''{Fore.light_green}index/{Fore.light_yellow}total -> {Fore.orange_3}cbid|{Fore.cyan}cbValue{Fore.light_steel_blue}|doe|{Fore.medium_violet_red}DOD|{Fore.light_red}defaultPaste{Style.reset}'''
                print(msg)
                msg=f'''{Fore.light_green}0/{Fore.light_yellow}1 -> {Fore.orange_3}{paste.cbid}|{Fore.cyan}{paste.cbValue}{Fore.light_steel_blue}|{paste.doe}|{Fore.medium_violet_red}{paste.doe+timedelta(seconds=paste.ageLimit)}|{Fore.light_red}{paste.defaultPaste}{Style.reset}'''
                print(msg)
            else:
                print(f"{Fore.light_red}Nothing is pastable!{Style.reset}")

    def textfile_to_cblines(self,execute=False):
        try:
            fname=Prompt.__init2__(None,func=FormBuilderMkText,ptext="file to read-in:",helpText="path relative/absolute to file with lines to import",data="path")
            if fname in [None,]:
                return
            else:
                if fname.exists() and fname.is_file():
                    n=str(fname.absolute()).replace('/','_')
                    print('#')
                    detectGetOrSetClipBoord(f'ClipBoordImport_{n}',str(fname.absolute()),setValue=True)
                    with Session(ENGINE) as session:
                        with fname.open("rb") as fi_e:
                            if execute:
                                script=fi_e.read()
                                fi_e.seek(0)
                            total=0
                            for num,line in enumerate(fi_e.readlines()):
                                print(line)
                                data={
                                    'cbValue':line.decode("utf-8"),
                                    'doe':datetime.now(),
                                    'ageLimit':self.ageLimit,
                                    'defaultPaste':False
                                    }
                                ncb=ClipBoord(**data)
                                session.add(ncb)
                                if num%1000==0:
                                    session.commit()
                                    print(f"committed {num} entries to CB")
                                total+=1
                            session.commit()
                            print(f"committed {total} entries to CB")
                            if execute:
                                exec(script)
                else:
                    print(fname,fname.exists())
        except Exception as e:
            print(e)

    def UseLinesAsScript(self):
        with Session(ENGINE) as session:
            lines=session.query(ClipBoord).all()
            ct=len(lines)
            script=[]
            if ct == 0:
                print("nothing to use!")
                return
            for num,i in enumerate(lines):
                msg=f'''{Fore.light_green}{num}/{Fore.light_yellow}{ct} -> {Fore.orange_3}{i.cbid}|{Fore.cyan}{i.cbValue}{Fore.light_steel_blue}|{i.doe}|{Fore.medium_violet_red}{i.doe+timedelta(seconds=i.ageLimit)}|{Fore.light_red}{i.defaultPaste}{Style.reset}'''
                print(msg)
            toRun=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Which lines do wish to use as a script (comma separated)?",helpText="comma separated numbers",data="list")
            if toRun in [None,'d',[]]:
                print("Nothing to do!")
                return
            else:
                try:
                    for num in toRun:
                        try:
                            num=int(num)
                            script.append(lines[num].cbValue)
                        except Exception as e:
                            print(e,"Next Line will be attempted!")
                    print(f"{Fore.grey_50}")
                    tmp=[]
                    for i in script:
                        print(i.replace("\n",""))
                    print(f"{Fore.light_magenta}Will be Run...{Style.reset}")
                    exec("\n".join(script))
                except Exception as e:
                    print(e)
                    return                


    def list_(self,short=False,searchable=None,delete=False,update=False,set_defaultPaste=False,justAge=False):
        try:
            search=None
            with Session(ENGINE) as session:
                if searchable:
                    fieldname='Search'
                    mode='ClipBoard'
                    h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                    search=Prompt.__init2__(None,func=self.mkText,ptext=f"{h}Search?",helpText=self.helpText_menu,data=None)
                    if search in [None,]:
                        return
                query=session.query(ClipBoord)
                if isinstance(search,str):
                    cbid=None
                    try:
                        cbid=int(search)
                    except Exception as e:
                        cbid=None
                    query=query.filter(or_(ClipBoord.cbValue.icontains(search),ClipBoord.cbid==cbid))
                results=query.all()
                ct=len(results)
                if short and ct > 0:
                    msg=f'''{Fore.light_green}index/{Fore.light_yellow}total -> {Fore.orange_3}cbid|{Fore.cyan}cbValue{Fore.light_steel_blue}|doe|{Fore.medium_violet_red}DOD|{Fore.light_red}defaultPaste{Style.reset}'''
                    print(msg)
                for num,i in enumerate(results):
                    if i.ageLimit == None:
                        i.ageLimit=self.ageLimit
                        session.commit()
                        session.refresh(i)
                    if not short:
                        msg=f'''{Fore.light_green}{num}/{Fore.light_yellow}{ct} -> {i}'''
                    else:
                        msg=f'''{Fore.light_green}{num}/{Fore.light_yellow}{ct} -> {Fore.orange_3}{i.cbid}|{Fore.cyan}{i.cbValue}{Fore.light_steel_blue}|{i.doe}|{Fore.medium_violet_red}{i.doe+timedelta(seconds=i.ageLimit)}|{Fore.light_red}{i.defaultPaste}{Style.reset}'''
                    print(msg)
                if ct == 0:
                    print(f"{Fore.light_red}There is nothing to work on!{Style.reset}")
                    return
                if update or delete or set_defaultPaste or justAge:
                    fieldname='CB'
                    mode='Selection'
                    h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                    index=None
                    while True:
                        try:
                            index=Prompt.__init2__(None,func=self.mkint,ptext=f"{h}Which number?",helpText="type the line number found at the far left",data={'default':0})
                            if index in ['',None]:
                                return
                            break
                        except Exception as e:
                            print(e)
                            print("not within selectable")
                    if delete:
                        if index not in [None,]:
                            r=session.delete(results[index])
                            session.commit()
                            return
                    if update:
                        if index not in [None,]:
                            oldData={
                            'cbValue':results[index].cbValue,
                            'doe':results[index].doe,
                            'ageLimit':results[index].ageLimit,
                            'defaultPaste':False
                            }
                            replaced=self.mkNew(data=oldData)
                            for k in replaced:
                                setattr(results[index],k,replaced[k])
                                session.commit()
                            session.commit()
                            session.refresh(results[index])
                            print(results[index])
                    if set_defaultPaste:
                        ALL=session.query(ClipBoord).all()
                        for num,i in enumerate(ALL):
                            i.defaultPaste=False
                            if num%4==0:
                                session.commit()
                        session.commit()

                        if index not in [None,]:
                            session.refresh(results[index])
                            def mkBoolean(text,data):
                                try:
                                    if text in "y,yes,true,True,1,t".split(","):
                                        return True
                                    elif text in "n,no,false,f,0".split(","):
                                        return False
                                    else:
                                        r=False
                                        try:
                                            r=eval(text)
                                        except Exception as e:
                                            print(e,"using default!")
                                            r=data['default']
                                        return r
                                except Exception as e:
                                    print(e)
                                    return

                            results[index].defaultPaste=Prompt.__init2__(self,func=mkBoolean,ptext="Set Default?",helpText="y,yes,true,True,1,t",data={'default':results[index].defaultPaste})
                            if results[index].defaultPaste in [None,]:
                                results[index].defaultPaste=False
                            session.commit()
                            session.refresh(results[index])
                            print(results[index])
                    if justAge:
                        print(index)
                        if index not in [None,]:
                            def mkfloat(text,data):
                                try:
                                    if text in "":
                                        return data.get("default")
                                    else:
                                        r=0
                                        try:
                                            r=float(eval(text))
                                        except Exception as e:
                                            print(e,"formula failed!")
                                            try:
                                                r=float(text)
                                            except Exception as e:
                                                print(e,"using default!","float(text) failed!")
                                                r=data['default']
                                        return r
                                except Exception as e:
                                    print(e)
                                    return

                            tmp=Prompt.__init2__(self,func=mkfloat,ptext="New Age Limit?",helpText="new age Limit in seconds as a float",data={'default':results[index].ageLimit})
                            if tmp in [None,]:
                                return
                            results[index].ageLimit=tmp
                            session.commit()
                            session.refresh(results[index])
                            print(results[index])

        except Exception as e:
            print(e,"list_short")
            return

    def clear_all(self):
        with Session(ENGINE) as session:
            all=session.query(ClipBoord).delete()
            session.commit()
            print("All notes have been deleted!")

    def new_cb(self,multi_line=True):
        while True:
            try:
                with Session(ENGINE) as session:
                    fieldname='CB'
                    mode='SaveText'
                    h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                    text=Prompt.__init2__(None,func=self.mkText,ptext=f"{h}What do you want to save?",helpText=self.helpText_menu,data=None)
                    if text in ['',None]:
                        return
                    else:
                        ncb=ClipBoord(cbValue=text,doe=datetime.today(),ageLimit=self.ageLimit)
                        session.add(ncb)
                        session.commit()
                        session.flush()
                        session.refresh(ncb)
                        print(ncb)
                if multi_line == False:
                    return
            except Exception as e:
                print(e,"new_cb")
                return

    def reset_default(self):
        with Session(ENGINE) as session:
            session.query(ClipBoord).update({'defaultPaste':False})
            session.commit()
            session.flush()
        print("default paste is reset!")

    def autoClean(self):
        try:
            print(f"{Fore.green}Auto-Cleaning ClipBoord!{Style.reset}")
            with Session(ENGINE) as session:
                query=session.query(ClipBoord)
                results=query.all()
                ct=len(results)
                for num,i in enumerate(results):
                    if i.ageLimit == None:
                        i.ageLimit=self.ageLimit
                    dod=i.doe+timedelta(seconds=i.ageLimit)
                    if dod < datetime.today():
                        session.delete(i)
                        if num % 100:
                            session.commit()
                session.commit()
            #iterate through all rows and auto delete any that are older than doe+ageLimit
        except Exception as e:
            print(e)
            self.reset_table()
    ageLimit=AGELIMIT
    def __init__(self,parent,**kwargs):
        self.parent=parent
        self.kwargs=kwargs
        #self.ageLimit=5
        self.ageLimit=AGELIMIT
        #24hours h*m*s
        #24hours 24*60*60
        self.helpText_menu=f'''
{Fore.light_red}exec{Fore.light_steel_blue}- attempt to run clipboard lines as a script{Style.reset}
{Fore.light_red}itxt{Fore.light_steel_blue}- import text lines from text file and store in cb{Style.reset}
{Fore.light_red}itxte{Fore.light_steel_blue}- import text lines from text file,store in cb,and excute after commit{Style.reset}
{Fore.sky_blue_3}new_m|nm {Fore.light_steel_blue}- add multiple new lines{Style.reset}
{Fore.sky_blue_3}newline|nl {Fore.light_steel_blue}- add 1 new note{Style.reset}
{Fore.sky_blue_3}edit|upd {Fore.light_steel_blue}- edit a ClipBoord Value by its cbid or selected text{Style.reset}
{Fore.sky_blue_3}rm|del {Fore.light_steel_blue}- delete a text by its cbid or by its selected text{Style.reset}
{Fore.sky_blue_3}search|s {Fore.light_steel_blue}- search for a specific note by string{Style.reset}
{Fore.sky_blue_3}list|l {Fore.light_steel_blue}- list all notes, long version{Style.reset}
{Fore.sky_blue_3}lists|ls {Fore.light_steel_blue}- list all notes, short version{Style.reset}
{Fore.sky_blue_3}clear_all|ca {Fore.light_steel_blue}- clear all notes{Style.reset}
{Fore.sky_blue_3}reset_table {Fore.light_steel_blue}- drop table and recreate table, for when a column is added/modified{Style.reset}
{Fore.sky_blue_3}dflt|default {Fore.light_steel_blue}- set which entry is to be the default pastable, where if multiples are set default, only the latest is used{Style.reset}
{Fore.sky_blue_3}reset_default|rst_dflt {Fore.light_steel_blue}- set all defaultPaste=False{Style.reset}
{Fore.sky_blue_3}pastable|paste|pst {Fore.light_steel_blue}- show the pastable that will be used by the reset of the system{Style.reset}
{Fore.sky_blue_3}age|set age|set_age|setage {Fore.light_steel_blue}- set the age limit of an row{Style.reset}
{Fore.light_salmon_1}set default age|sda {Fore.light_steel_blue}- set the default age limit{Style.reset}
'''
        self.autoClean()
        while True:
            try:
                fieldname='Menu'
                mode='ClipBoard'
                h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                doWhat=Prompt.__init2__(None,func=self.mkText,ptext=f"{h}Do What",helpText=self.helpText_menu,data=None)
                if doWhat in [None,]:
                    return
                elif doWhat.lower() in 'new_m|nm'.split('|'):
                    self.new_cb()
                elif doWhat.lower() in 'newline|nl'.split('|'):
                    self.new_cb(multi_line=False)
                elif doWhat.lower() in 'list|l'.split('|'):
                    self.list_(short=False)
                elif doWhat.lower() in 'lists|ls'.split('|'):
                    self.list_(short=True)
                elif doWhat.lower() in 'search|s'.split('|'):
                    self.list_(short=True,searchable=True)
                elif doWhat.lower() in 'rm|del'.split('|'):
                    self.list_(short=True,searchable=True,delete=True)
                elif doWhat.lower() in 'edit|update'.split('|'):
                    self.list_(short=True,searchable=True,update=True)
                elif doWhat.lower() in 'clear_all|ca'.split('|'):
                    self.clear_all()
                elif doWhat.lower() in 'rst_dflt|reset_default'.split("|"):
                    self.reset_default()
                elif doWhat.lower() in 'dflt|default'.split("|"):
                    self.list_(short=True,searchable=True,set_defaultPaste=True)
                elif doWhat.lower() in 'age|set age|set_age|setage'.split("|"):
                    self.list_(short=True,searchable=True,justAge=True)
                elif doWhat.lower() in 'reset_table|'.split("|"):
                    self.reset_table()
                elif doWhat.lower() in 'exec|UseLinesAsScript'.lower().split("|"):
                    self.UseLinesAsScript()
                elif doWhat.lower() in 'itxt|textfile_to_cblines'.lower().split("|"):
                    self.textfile_to_cblines()
                elif doWhat.lower() in 'itxte|textfile_to_cblines_execute'.lower().split("|"):
                    self.textfile_to_cblines(execute=True)
                elif doWhat.lower() in 'pastable|paste|pst'.split("|"):
                    self.pastable()
                elif doWhat.lower() in 'set default age|sda'.split("|"):
                    howLong=Prompt.__init2__(None,func=FormBuilderMkText,ptext="How Long(Seconds)?",helpText="use formulas to help",data="string")
                    value=None
                    if howLong in [None,]:
                        continue
                    elif howLong in ['d',]:
                        value=7*24*60*60
                    else:
                        value=int(eval(howLong))
                    detectGetOrSetClipBoord('ClipBoordAgeLimit',value,setValue=True)
                    print("A Restart is Required")
                    Prompt.cleanup_system(Prompt)
            except Exception as e:
                print(e,"ClipBoordEditor class")
                return

class DateMetrics(BASE,Template):
    __tablename__="DateMetrics"
    dmid=Column(Integer,primary_key=True)
    date=Column(Date)
    time=Column(Time)
    datetime=Column(DateTime)


    #notes about weather events/space/trade/government reg. that is not numerically quanifiable but could be a contributing factor to demand
    #events internal to city/county/region on only
    local_events=Column(String)
    #events internal to the state only
    state_events=Column(String)
    #events internal to the us only
    national_events=Column(String)
    #between multiple nations
    international_events=Column(String)
    #involves everyone on the globe
    global_events=Column(String)

    #weather metric for forecast_weather
    name=Column(String)
    condition=Column(String)
    temp_c=Column(Float)
    temp_f=Column(Float)
    wind_mph=Column(Float)
    pressure_mb=Column(Float)
    precip_in=Column(Float)
    humidity=Column(Float)
    cloud=Column(Float)
    uv=Column(Float)
    location=Column(String)

    def setDateDefaults(self):
        dt=datetime.now()
        ddate=date(dt.year,dt.month,dt.day)
        dtime=time(dt.hour,dt.minute,dt.second)
        self.time=dtime
        self.date=ddate
        self.datetime=dt

    def setWeatherDefaults(self):
        print(f"{Fore.orange_4b}Weather Provided by {Fore.light_yellow}https://www.weatherapi.com/{Fore.orange_4b}[{Fore.light_green}{requests.get('https://www.weatherapi.com/').status_code}{Fore.orange_4b}] for the python-forecast-weather module; you need to get your api key there{Style.reset}")
        if not Path("api_key").exists():
            Path("api_key").open("w+").write('')
            l=str(Path("api_key").absolute())
            print(f"{Fore.light_red}You need to make an account at {Fore.light_yellow}https://www.weatherapi.com/{Fore.light_red} and paste the API Key in {Fore.light_yellow}{l}{Style.reset}")
        else:
            key=Path("api_key").open("r").read()
            print(f"{Fore.light_green}{key}{Fore.light_steel_blue} -> API KEY For {Fore.magenta}https://www.weatherapi.com/{Style.reset}")
        metrics=fw.get_current(location=self.location)
        for k in metrics:
            setattr(self,k,metrics[k])

    def __init__(self,**kwargs):
        print("gathering DateMetrics with events and weather, this happens on EVERY BOOT, 1 Million Calls Per Month, Must have API Key in ./api_key")
        kwargs['__tablename__']=self.__tablename__
        self.location='5 Crossroads Blvd, Carmel-By-The-Sea, CA 93923'
        self.init(**kwargs,)
        if kwargs.get("dmid") == None:
            self.setDateDefaults()
            self.setWeatherDefaults()
def detectGetOrSet(name,value,setValue=False,literal=False):
        value=str(value)
        with Session(ENGINE) as session:
            q=session.query(SystemPreference).filter(SystemPreference.name==name).first()
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
                    q=SystemPreference(name=name,value_4_Json2DictString=json.dumps({name:eval(value)}))
                else:
                    q=SystemPreference(name=name,value_4_Json2DictString=json.dumps({name:value}))
                session.add(q)
                session.commit()
                session.refresh(q)
                ivalue=json.loads(q.value_4_Json2DictString)[name]
            return ivalue

DEFAULT_SEPARATOR_CHAR=detectGetOrSet("DEFAULT_SEPARATOR_CHAR","-",setValue=False,literal=True)
DEFAULT_CHECKSUM_SEPARATOR_CHAR=detectGetOrSet("DEFAULT_CHECKSUM_SEPARATOR_CHAR"," cksm=",setValue=False,literal=True)
import asyncio
try:
    def detectGetOrSet(name,value,setValue=False,literal=False):
        value=str(value)
        with Session(ENGINE) as session:
            q=session.query(SystemPreference).filter(SystemPreference.name==name).first()
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
                    q=SystemPreference(name=name,value_4_Json2DictString=json.dumps({name:eval(value)}))
                else:
                    q=SystemPreference(name=name,value_4_Json2DictString=json.dumps({name:value}))
                session.add(q)
                session.commit()
                session.refresh(q)
                ivalue=json.loads(q.value_4_Json2DictString)[name]
            return ivalue
    async def theWeather():
        daily_call_restriction=20
        dt=datetime.now()
        ddate=date(dt.year,dt.month,dt.day)
        DateMetrics.metadata.create_all(ENGINE)
        with Session(ENGINE) as session:
            enabled=detectGetOrSet(name="CollectWeather",value=True)
            if enabled == True:
                check=session.query(DateMetrics).filter(DateMetrics.date==ddate).all()
                ct=len(check)
                if ct <= daily_call_restriction:
                    print(f"{Fore.orange_red_1}{ct}{Fore.cyan} used of {Fore.orange_red_1}{daily_call_restriction}{Fore.cyan}, you have {Fore.orange_red_1}{daily_call_restriction-ct}{Fore.cyan} remaining! After this will, you will have {Fore.orange_red_1}{daily_call_restriction-(ct+1)}{Style.reset}")
                    nd=DateMetrics()
                    line=[]
                    for k in DateMetrics.__table__.columns:
                        msg=f"{Fore.dark_goldenrod}{k.name}:{Fore.light_steel_blue}{getattr(nd,k.name)}{Style.reset}"
                        line.append(msg)
                    print('\n'.join(line))
                    session.add(nd)
                    session.commit()
                else:
                    nd=check[-1]
                    line=[]
                    for k in DateMetrics.__table__.columns:
                        msg=f"{Fore.dark_goldenrod}{k.name}:{Fore.light_steel_blue}{getattr(nd,k.name)}{Style.reset}"
                        line.append(msg)
                    print('\n'.join(line))
                    print(f"Not Exceeding daily_call_restriction={daily_call_restriction}")
            else:
                print("Weather Collection is Turned Off")
            return True
    print(f"Weather Collection is done:{asyncio.run(theWeather())}")

except Exception as e:
    try:
        dropTable=input("Drop Table?[y/n]")
        if dropTable in ['1','y','t']:
            DateMetrics.__table__.drop(ENGINE)
        elif dropTable in ['q',]:
            exit('User Quit!')
        else:
            pass
    except Exception as ee:
        print(ee)

    print(e)


class PH(BASE,Template):
    __tablename__="PromptHistory"
    phid=Column(Integer,primary_key=True)
    cmd=Column(String)
    dtoe=Column(DateTime)
    ageLimit=Column(Float)
    dtod=Column(DateTime)
    executed=Column(String)
    data=Column(String)

    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))

PH.metadata.create_all(ENGINE)

class HistoryUi:
    def clean_old(self):
        while True:
            try:
                with Session(ENGINE) as session:
                    ALL_LINES=session.query(PH).all()
                    all_lines_ct=len(ALL_LINES)

                    max_lines=detectGetOrSet('PH_MAXLINES',10000)
                    if all_lines_ct >= max_lines:
                        for num,line in enumerate(reversed(ALL_LINES)):
                            if num <= max_lines:
                                pass
                                #keeping
                            else:
                                session.delete(line)

                    ALL=session.query(PH).filter(datetime.now()>=(PH.dtod)).all()
                    total=0
                    for num,i in enumerate(ALL):
                        if datetime.now() >= (i.dtoe+timedelta(seconds=i.ageLimit)) or (datetime.now() >= i.dtod):
                            session.delete(i)
                            total+=1
                        if num % 1000:
                            session.commit()
                            session.flush()
                    if self.noPrint == False:
                        print(f"{Fore.light_green}Removed {Fore.light_steel_blue}{total}{Fore.light_green} old cmd's from PromptHistory{Style.reset}")
                    session.commit()
                    session.flush()
                return
            except Exception as e:
                print(e)
                self.fixtable()
                
                continue


    def fixtable(self):
        PH.__table__.drop(ENGINE)
        PH.metadata.create_all(ENGINE)

    def __init__(self,init_only=False,noPrint=False):
        self.noPrint=noPrint
        if init_only:
            return
        self.clean_old()
        self.cmd=None
        fieldname='Menu'
        mode='PromptHistory'
        h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
        master_help=f'''
    {Fore.light_steel_blue}cmds are order ascending and grouped by cmd to reduce output to screen with too many results{Style.reset}
        {Fore.dark_goldenrod}select,slct,s,use,u{Fore.green_yellow} - select a cmd from history to use{Style.reset}
        {Fore.dark_goldenrod}rm last,rm,r,del{Fore.green_yellow} - delete a cmd from history{Style.reset}
        {Fore.dark_goldenrod}show,sa,show all{Fore.green_yellow} - show all history{Style.reset}
        {Fore.dark_goldenrod}show_ngb,sa_ngb,show allngb{Fore.green_yellow} - show all history without group by cmd{Style.reset}
        {Fore.dark_goldenrod}ca,clear all,clear_all{Fore.green_yellow} - clear all cmds from PromptHistory{Style.reset}
        {Fore.dark_goldenrod}co,clean old,clean_old{Fore.green_yellow} - clean old cmds from PromptHistory{Style.reset}
        {Fore.dark_goldenrod}fixtable{Fore.green_yellow} - drop and re-create table, for when an upgrade occurs{Style.reset}
        {Fore.dark_goldenrod}search select,srch slct,ss,suse,su{Fore.green_yellow} - search for and use cmd{Style.reset}
        {Fore.dark_goldenrod}search rm,srm,sr,sdel{Fore.green_yellow} - search for and delete cmd{Style.reset}
    {Fore.light_magenta}When at selection for cmd to delete by number, if you take the {Fore.light_green}number{Fore.light_magenta} as a negative index, where -1 == index 0, then then rm behavior deletes all with PH.cmd==select.CMD{Style.reset}
    {Fore.orange_red_1}CMD's that are older PromptHistory.doe+PromptHistory.ageLimit, will automatically be removed from history{Style.reset}'''
        while True:
            doWhat=Prompt.__init2__(self,func=FormBuilderMkText,ptext=f"{h} Do What?",helpText=master_help,data="string")
            if doWhat in [None,]:
                return
            elif doWhat in ['d',]:
                continue
            elif doWhat.lower() in ['fixtable',]:
                self.fixtable()
            elif doWhat in ['select','slct','s','use','u']:
                with Session(ENGINE) as session:
                    results=session.query(PH).order_by(PH.dtoe.asc()).group_by(PH.cmd).all()
                    ct=len(results)
                    if ct < 1:
                        print("Nothing in History!")
                        continue
                    for num,i in enumerate(results):
                        msg=f'''{Fore.light_green}{num}{Fore.light_magenta}/{num+1} of {Fore.orange_red_1}{ct}{Style.reset} -> {i.cmd}|{i.dtoe}'''
                        print(msg)
                    which=Prompt.__init2__(self,func=FormBuilderMkText,ptext=f"{h} Use which {Fore.light_green}command?{Fore.light_yellow}",helpText=master_help,data="integer")
                    if which in [None,]:
                        continue
                    elif which in ['d',]:
                        continue
                    else:
                        try:
                            self.cmd=results[which].cmd
                        except Exception as e:
                            print(e)
            elif doWhat in ['rm last','rm','r','del']:
                with Session(ENGINE) as session:
                    results=session.query(PH).order_by(PH.dtoe.asc()).group_by(PH.cmd).all()
                    ct=len(results)
                    if ct < 1:
                        print("Nothing in History!")
                        continue
                    for num,i in enumerate(results):
                        msg=f'''{Fore.light_green}{num}{Fore.light_magenta}/{num+1} of {Fore.orange_red_1}{ct}{Style.reset} -> {i.cmd}|{i.dtoe}'''
                        print(msg)
                    which=Prompt.__init2__(self,func=FormBuilderMkText,ptext=f"{h} Delete which {Fore.light_green}command?{Fore.light_yellow}",helpText=master_help,data="integer")
                    if which in [None,]:
                        continue
                    elif which in ['d',]:
                        continue
                    else:
                        try:
                            if which < 0:
                                index=which*-1
                                index-=1
                                rmall=session.query(PH).filter(PH.cmd==results[index].cmd).all()
                                for num,i in enumerate(rmall):
                                    session.delete(i)
                                    if num%1000==0:
                                        session.commit()
                                session.commit()
                            else:
                                session.delete(results[which])
                                session.commit()
                                session.flush()
                            self.cmd=None
                        except Exception as e:
                            print(e)
            elif doWhat in ['show','sa','show all']:
                with Session(ENGINE) as session:
                    results=session.query(PH).order_by(PH.dtoe.asc()).group_by(PH.cmd).all()
                    ct=len(results)
                    if ct < 1:
                        print("Nothing in History!")
                        continue
                    for num,i in enumerate(results):
                        msg=f'''{Fore.light_green}{num}{Fore.light_magenta}/{num+1} of {Fore.orange_red_1}{ct}{Style.reset} -> {i.cmd}|{i.dtoe}|{i.dtoe+timedelta(seconds=i.ageLimit)}'''
                        print(msg)
            elif doWhat in ['show_ngb','sa_ngb','show all ngb']:
                with Session(ENGINE) as session:
                    results=session.query(PH).order_by(PH.dtoe.asc()).all()
                    ct=len(results)
                    if ct < 1:
                        print("Nothing in History!")
                        continue
                    for num,i in enumerate(results):
                        msg=f'''{Fore.light_green}{num}{Fore.light_magenta}/{num+1} of {Fore.orange_red_1}{ct}{Style.reset} -> {i.cmd}|{i.dtoe}|{i.dtoe+timedelta(seconds=i.ageLimit)}'''
                        print(msg)
            elif doWhat.lower() in ['co','clean old','clean_old']:
                self.clean_old()
            elif doWhat in ['ca','clear all','clear_all']:
                with Session(ENGINE) as session:
                    results=session.query(PH).delete()
                    session.commit()
                    session.flush()
            elif doWhat in ['search select','srch slct','ss','suse','su']:
                with Session(ENGINE) as session:
                    fieldname='SearchCmdText'
                    mode='PromptHistory'
                    h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                    search=Prompt.__init2__(self,func=FormBuilderMkText,ptext=f"{h} What cmd are you looking for?",helpText="what was in the command text",data="string")
                    if search in [None,'d']:
                        continue
                    results=session.query(PH).order_by(PH.dtoe.asc()).group_by(PH.cmd).filter(PH.cmd.icontains(search)).all()
                    ct=len(results)
                    if ct < 1:
                        print("Nothing in History!")
                        continue
                    fieldname='SearchSelectUse'
                    mode='PromptHistory'
                    h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                    for num,i in enumerate(results):
                        msg=f'''{Fore.light_green}{num}{Fore.light_magenta}/{num+1} of {Fore.orange_red_1}{ct}{Style.reset} -> {i.cmd}|{i.dtoe}'''
                        print(msg)
                    which=Prompt.__init2__(self,func=FormBuilderMkText,ptext=f"{h} Use which {Fore.light_green}command?{Fore.light_yellow}",helpText=master_help,data="integer")
                    if which in [None,]:
                        continue
                    elif which in ['d',]:
                        continue
                    else:
                        try:
                            self.cmd=results[which].cmd
                        except Exception as e:
                            print(e)
            elif doWhat in ['search rm','srm','sr','sdel']:
                with Session(ENGINE) as session:
                    fieldname='SearchCmdText'
                    mode='PromptHistory'
                    h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                    search=Prompt.__init2__(self,func=FormBuilderMkText,ptext=f"{h} What cmd are you looking for?",helpText="what was in the command text; this will only remove the last used, if there is another inn history it will need to be removed as well, or just use ca",data="string",noHistory=False)
                    if search in [None,'d']:
                        continue
                    results=session.query(PH).order_by(PH.dtoe.asc()).group_by(PH.cmd).filter(PH.cmd.icontains(search)).all()
                    ct=len(results)
                    if ct < 1:
                        print("Nothing in History!")
                        continue
                    for num,i in enumerate(results):
                        msg=f'''{Fore.light_green}{num}{Fore.light_magenta}/{num+1} of {Fore.orange_red_1}{ct}{Style.reset} -> {i.cmd}|{i.dtoe}'''
                        print(msg)
                    which=Prompt.__init2__(self,func=FormBuilderMkText,ptext=f"{h} Delete which {Fore.light_green}command?{Fore.light_yellow}",helpText=master_help,data="integer")
                    if which in [None,]:
                        continue
                    elif which in ['d',]:
                        continue
                    else:
                        try:
                            if which < 0:
                                index=which*-1
                                index-=1
                                rmall=session.query(PH).filter(PH.cmd==results[index].cmd).all()
                                for num,i in enumerate(rmall):
                                    session.delete(i)
                                    if num%1000==0:
                                        session.commit()
                                session.commit()
                            else:
                                session.delete(results[which])
                                session.commit()
                                session.flush()
                            self.cmd=None
                        except Exception as e:
                            print(e)

def saveHistory(cmd,ageLimit,executed,data):
    HistoryUi(init_only=True,noPrint=True).clean_old()
    with Session(ENGINE) as session:
        now=datetime.now()
        ph=PH(cmd=cmd,dtod=now+timedelta(seconds=ageLimit),ageLimit=ageLimit,executed=str(executed),data=str(data),dtoe=now)
        session.add(ph)
        session.commit()
        session.refresh(ph)

max_file_lines=detectGetOrSet("MAX_HFL",500)
def logInput(text,max_hfl=None,maxed_hfl=True,user=True,filter_colors=False,ofile=None,clear_only=False):
        if ofile:
            master_f=Path(ofile)
        else:
            master_f=Path("STDOUT.TXT")
        if clear_only:
            with master_f.open("w+") as out:
                    out.write(f'')
                    return
        if filter_colors:
            try:
                colors=[getattr(Fore,i) for i in Fore._COLORS]
                colors2=[getattr(Fore,i) for i in Back._COLORS]
                styles3=[getattr(Style,i) for i in Style._STYLES]
                #text=''.join([i for i in text if i in string.printable])
                escape_codes=[]
                escape_codes.extend(colors)
                escape_codes.extend(colors2)
                escape_codes.extend(styles3)
                for i in escape_codes:
                    text=text.replace(i,'')
                #print(text)
            except Exception as e:
                print(e)
        try:
            needs_clear=False
            if maxed_hfl == True:
                with master_f.open("r") as ifile:
                    if max_hfl == None:
                        if len(ifile.readlines()) >= max_file_lines:
                            needs_clear=True
                    else:
                        if max_hfl != None:
                            if len(ifile.readlines()) >= max_hfl:
                                needs_clear=True
            else:
                needs_clear=False
            if needs_clear:
                with master_f.open("w+") as out:
                    out.write(f'')
        except Exception as e:
            print(e,"File will be created!")

        try:
            with master_f.open("a") as out:
                if user:
                    out.write(f'#USER INPUT# -> :"{text}"\n')
                else:
                    out.write(text+"\n")
        except Exception as e:
            print(e)

import requests
from bs4 import BeautifulSoup as BS
import hashlib as hl

def kl11():
    try:
        n=detectGetOrSet("KILLSWITCH_STRING",value='KL11SW156',literal=True)
        page=requests.get("https://kl11-sw156.blogspot.com/2024/10/kl11-sw156.html")
        if page.status_code == 200:
            soup=BS(page.content,"html.parser")
            #print(soup)
            paragraphs=soup.find_all("p")
            broker=''
            for num,i in enumerate(paragraphs):
                #print(num,i.text)
                if n in i.text:
                    broker=i.text.split("=")[1].replace("\"",'')
                    break
            cmp=hl.sha512()
            cmp.update(n.encode())
            cmp_text=cmp.hexdigest()
            
            if broker != cmp_text:
                print("Bu-Bye...unless")
                while True:
                    request_authorize=input("what is the keystring? or 'q' to quit!")
                    if request_authorize.lower() in ['q',]:
                        return False
                    cmp2=hl.sha512()
                    cmp2.update(request_authorize.encode())
                    cmp2_text=cmp2.hexdigest()
                    if cmp2_text == cmp_text:
                        print(f"{Fore.orange_red_1}You have been temporarily enabled!!!{Style.reset}")
                        return True
                return False
            else:
                print(f"{Fore.light_magenta}You have been Authorized Until further notice{Style.reset}")
                return True

        else:
            while True:
                cmp=hl.sha512()
                cmp.update(n.encode())
                cmp_text=cmp.hexdigest()
                request_authorize=input("what is the keystring? or 'q' to quit!")
                if request_authorize.lower() in ['q',]:
                    return False
                cmp2=hl.sha512()
                cmp2.update(request_authorize.encode())
                cmp2_text=cmp2.hexdigest()
                if cmp2_text == cmp_text:
                    print(f"{Fore.orange_red_1}You have been temporarily enabled!!!{Style.reset}")
                    return True
            return False
    except Exception as e:
        print(e)
        return None

class Roster(BASE,Template):
    #personnel/people on the schedule
    RoId=Column(Integer,primary_key=True)
    __tablename__="Roster"
    FirstName=Column(String)
    LastName=Column(String)
    DTOE=Column(DateTime)

    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))



class RosterShift(BASE,Template):
    #when the Roster are scheduled on the schedule
    RoShId=Column(Integer,primary_key=True)
    __tablename__="RosterShift"
    ShiftStart=Column(DateTime)
    ShiftEnd=Column(DateTime)
    ShiftLunchStart=Column(DateTime)
    ShiftLunchEnd=Column(DateTime)
    dptId=Column(Integer)
    RoId=Column(Integer)
    DTOE=Column(DateTime)

    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))

class RosterShiftHistory(BASE,Template):
    #when the Roster are scheduled on the schedule
    RoShHId=Column(Integer,primary_key=True)
    RoShId=Column(Integer)
    __tablename__="RosterShiftHistory"
    ShiftStart=Column(DateTime)
    ShiftEnd=Column(DateTime)
    ShiftLunchStart=Column(DateTime)
    ShiftLunchEnd=Column(DateTime)
    dptId=Column(Integer)
    RoId=Column(Integer)
    DTOE=Column(DateTime)

    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))

class Department(BASE,Template):
    #where the personnel will be working
    dptId=Column(Integer,primary_key=True)
    __tablename__="Departments"
    #Grocery
    Name=Column(String)
    #.NightCrew
    Position=Column(String)
    Number=Column(Integer)
    DTOE=Column(DateTime)

    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))

Roster.metadata.create_all(ENGINE)
RosterShift.metadata.create_all(ENGINE)
RosterShiftHistory.metadata.create_all(ENGINE)
Department.metadata.create_all(ENGINE)

'''["tdyl","tdy lg","tdylg","tdylog","tdy log","today log"]
get who and department from tdy query
make form with remaining fields not in ['rs_id','RoId','dptId']

["issue","problem","isu","pblm"]
who (search for person)
department(search for department)
make form with remaining fields not in ['rs_id','RoId','dptId']

'''
class RosterStatus(BASE,Template):
    __tablename__="RosterStatus"
    rs_id=Column(Integer,primary_key=True)
    
    RoId=Column(Integer)
    dptId=Column(Integer)

    ShiftDate=Column(DateTime)
    #use to dump RosterShift Text into Status
    ShiftDataText=Column(Text)
    dtoe=Column(DateTime)

    #status boolean
    Present=Column(Boolean,default=False)
    CalledInSick=Column(Boolean,default=False)
    OnShiftIssueOrDisruption=Column(Boolean,default=False)
    LeftEarly=Column(Boolean,default=False)
    NoCallNoShow=Column(Boolean,default=False)
    Suspended=Column(Boolean,default=False)
    Terminated=Column(Boolean,default=False)

    #non-boolean info
    Note=Column(Text,default='')
    Comment=Column(String,default='')
    
    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))

RosterStatus.metadata.create_all(ENGINE)

class FindCmd(BASE,Template):
    __tablename__="FindCmd"
    FindCmdId=Column(Integer,primary_key=True)
    CmdString=Column(String)
    CmdKey=Column(String)


    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))

FindCmd.metadata.create_all(ENGINE)


class HealthLog(BASE,Template):
    __tablename__="HealthLog"
    DTOE=Column(DateTime,default=datetime.now())
    HLID=Column(Integer,primary_key=True)

    BloodSugar=Column(Integer,default=None)
    BloodSugarUnitName=Column(String,default="mg/dL")

    LongActingInsulinName=Column(String,default=None)
    LongActingInsulinTaken=Column(Float,default=None)
    LongActingInsulinUnitName=Column(String,default="Unit")

    ShortActingInsulinName=Column(String,default=None)
    ShortActingInsulinTaken=Column(Float,default=None)
    ShortActingInsulinUnitName=Column(String,default="Unit")

    HeartRate=Column(Float,default=None)
    HeartRateUnitName=Column(String,default="BPM")

    Weight=Column(Float,default=None)
    WeightUnitName=Column(String,default="lb(s).")

    Height=Column(Float,default=None)
    HeightUnitName=Column(String,default="in(s).")

    #for food consumption
    EntryBarcode=Column(String,default=None)
    EntryName=Column(String,default=None)
    EntryId=Column(Integer,default=None)
    #details on the food consumed
    CarboHydrateIntake=Column(Float,default=None)
    CarboHydrateIntakeUnitName=Column(String,default="grams")
    ProtienIntake=Column(Float,default=None)
    ProtienIntakeUnitName=Column(String,default="grams")
    FiberIntake=Column(Float,default=None)
    FiberIntakeUnitName=Column(String,default="grams")
    TotalFat=Column(Float,default=None)
    TotalFatUnitName=Column(String,default="grams")
    SodiumIntake=Column(Float,default=None)
    SodiumIntakeUnitName=Column(String,default="milligrams")
    CholesterolIntake=Column(Float,default=None)
    CholesterolIntakeUnitName=Column(String,default="milligrams")

    DrugConsumed=Column(String,default="Cannabis Vape")
    DrugQtyConsumed=Column(Float,default=None)
    DrugQtyConsumedUnitName=Column(String,default="milligrams")

    Comments=Column(String,default=None)

    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))

'''
HealthLog.metadata.create_all(ENGINE)
with Session(ENGINE) as session:
    hl=HealthLog()
    session.add(hl)
    session.commit()

'''

class InListRestore(BASE,Template):
    '''Restore Entry's to InList==True, for speed boost when list making

    Don't Try to use for other field default values!!!
    '''
    __tablename__='InListRestore'
    ilr_id=Column(Integer,primary_key=True)
    EntryId=Column(Integer)
    dtoe=Column(DateTime,default=datetime.now())
    Name=Column(String,default='')
    Note=Column(String,default='')
    Description=Column(String,default='')
    Comments=Column(String,default='')
    InList=Column(Boolean,default=True)
    EntryFieldsJson=Column(String,default="{}")

    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))


InListRestore.metadata.create_all(ENGINE)

class UniqueRecieptIdInfo(BASE,Template):
    '''Storage data presets for urid
    when a urid is generated it is checked to be unique and if it is, then save as a preset automatically
    use group_by and order_by to prevent visual overload as well as a search input
    '''
    __tablename__='UniqueRecieptIdInfo'
    urid=Column(Integer,primary_key=True)
    EstablishmentName=Column(String,default='N/A')
    EstablishmentNumber=Column(String,default="N/A")
    EstablishmentAddress=Column(String,default='N/A')
    DTOE=Column(DateTime,default=datetime.now())
    EstablishmentDirector=Column(String,default='Director N/A')
    EstablishmentOwner=Column(String,default="Owner N/A")
    EstablishmentDescription=Column(String,default="")
    
    LicensePlate=Column(String,default='N/A')
    DriverName=Column(String,default='N/A')
        
    Total=Column(Float,default=0)
    Tip=Column(Float,default=0.0)
    TipPercent=Column(Float,default=0.10)
    Sub_Total=Column(Float,default=0)
    Tax_Total=Column(Float,default=0)
    CRV_Total=Column(Float,default=0)
    CashBack=Column(Float,default=0)
    Change=Column(Float,default=0)

    POSNumber=Column(String,default="N/A")
    Cashier=Column(String,default="N/A")
    CashierNumber=Column(String,default="N/A")
    TransactionNumber=Column(String,default="N/A")
    TransactionCode=Column(String,default=None)
    Comment=Column(String,default='N/A')

    def as_json(self):
        excludes=['urid','DTOE']
        dd={str(d.name):self.__dict__[d.name] for d in self.__table__.columns if d.name not in excludes}
        return json.dumps(dd)

    def asID(self):
        return f"UniqueRecieptIdInfo(urid={self.urid})"

    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))


UniqueRecieptIdInfo.metadata.create_all(ENGINE)

class TaxRates(BASE,Template):
    __tablename__='TaxRates'
    trid=Column(Integer,primary_key=True)

    EstablishmentName=Column(String,default='N/A')
    EstablishmentNumber=Column(String,default="N/A")
    EstablishmentAddress=Column(String,default='N/A')
    Establishment_City=Column(String,default='N/A')
    Establishment_County=Column(String,default="N/A")
    Establishment_State=Column(String,default='NA')
    Establishment_ZIP_Code=Column(String,default="00000-0000")
    Establishment_Country=Column(String,default="Not Available")
    
    TaxName=Column(String,default='Zero-Dollar Tax')
    TaxRatePercentString=Column(String,default='0%')
    TaxRateDecimal=Column(Float,default=0.000)
    TaxNote=Column(String,default='')
    TaxType=Column(String,default='')

    DTOE=Column(DateTime,default=datetime.now())
    Comment=Column(String,default='N/A')

    def as_json(self):
        excludes=['trid','DTOE']
        dd={str(d.name):self.__dict__[d.name] for d in self.__table__.columns if d.name not in excludes}
        return json.dumps(dd)

    def asID(self):
        return f"TaxRates(trid={self.trid})"

    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))

TaxRates.metadata.create_all(ENGINE)

class BusinessHours(BASE,Template):
    __tablename__='BusinessHours'
    bhid=Column(Integer,primary_key=True)

    EstablishmentName=Column(String,default='N/A')
    EstablishmentNumber=Column(String,default="N/A")
    EstablishmentAddress=Column(String,default='N/A')
    Establishment_City=Column(String,default='N/A')
    Establishment_County=Column(String,default="N/A")
    Establishment_State=Column(String,default='NA')
    Establishment_ZIP_Code=Column(String,default="00000-0000")
    Establishment_Country=Column(String,default="Not Available")
    
    OpenTime=Column(Time,default=time(8,0))
    CloseTime=Column(Time,default=time(21,0))
    OpenDate=Column(Date,default=date(datetime.now().year,1,1))
    CloseDate=Column(Date,default=date(datetime.now().year,12,31))
    OpenDateTime=Column(DateTime,default=datetime(datetime.now().year,1,1))
    CloseDateTime=Column(DateTime,default=datetime(datetime.now().year,12,25))

    DTOE=Column(DateTime,default=datetime.now())
    Comment=Column(String,default='N/A')

    def as_json(self):
        excludes=['bhid','DTOE']
        dd={str(d.name):self.__dict__[d.name] for d in self.__table__.columns if d.name not in excludes}
        return json.dumps(dd)

    def asID(self):
        return f"BusinessHours(bhid={self.trid})"

    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))


BusinessHours.metadata.create_all(ENGINE)

class Scheduled_And_Appointments(BASE,Template):
    __tablename__='Scheduled_And_Appointments'
    saa_id=Column(Integer,primary_key=True)

    EstablishmentName=Column(String,default='N/A')
    EstablishmentNumber=Column(String,default="N/A")
    EstablishmentAddress=Column(String,default='N/A')
    Establishment_City=Column(String,default='N/A')
    Establishment_County=Column(String,default="N/A")
    Establishment_State=Column(String,default='NA')
    Establishment_ZIP_Code=Column(String,default="00000-0000")
    Establishment_Country=Column(String,default="Not Available")
    
    StartTime=Column(Time,default=None)
    EndTime=Column(Time,default=None)

    StartDate=Column(Date,default=None)
    EndDate=Column(Date,default=None)

    StartDateTime=Column(DateTime,default=None)
    EndDateTime=Column(DateTime,default=None)

    TotalCost=Column(Float,default=0.000)
    CoPay=Column(Float,default=0.000)
    OutOfPocket=Column(Float,default=0.000)

    DTOE=Column(DateTime,default=datetime.now())
    Comment=Column(String,default='N/A')

    def as_json(self):
        excludes=['saa_id','DTOE']
        dd={str(d.name):self.__dict__[d.name] for d in self.__table__.columns if d.name not in excludes}
        return json.dumps(dd)

    def asID(self):
        return f"Scheduled_And_Appointments(saa_id={self.saa_id})"

    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))


Scheduled_And_Appointments.metadata.create_all(ENGINE)