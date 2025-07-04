import pandas as pd
import csv
from datetime import datetime
from pathlib import Path
from colored import Fore,Style,Back
from barcode import Code39,UPCA,EAN8,EAN13
import barcode,qrcode,os,sys,argparse
from datetime import datetime,timedelta
import zipfile,tarfile
import base64,json
from ast import literal_eval
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base as dbase
from sqlalchemy.ext.automap import automap_base
from pathlib import Path
import upcean
import platform

from radboy.ExtractPkg.ExtractPkg2 import *
from radboy.Lookup2.Lookup2 import *
from radboy.DayLog.DayLogger import *
from radboy.DB.db import *
from radboy.DB.glossary_db import *
from radboy.DB.DisplayItemDb import *
from radboy.DB.Prompt import *
from radboy.DB.ExerciseTracker import *
from radboy.ConvertCode.ConvertCode import *
from radboy.setCode.setCode import *
from radboy.Locator.Locator import *
from radboy.ListMode2.ListMode2 import *
from radboy.TasksMode.Tasks import *
from radboy.Collector2.Collector2 import *
from radboy.LocationSequencer.LocationSequencer import *
from radboy.PunchCard.PunchCard import *
from radboy.Conversion.Conversion import *
from radboy.Repack.Repack import *
from radboy.POS.POS import *
from radboy.BNC.BnC import *
import radboy.possibleCode as pc
import radboy.Unified.Unified as unified
from radboy.EntryRating.ER import *
from radboy.FB.FormBuilder import *
from radboy.SystemSettings.SystemSettings import *
from radboy.Comm.RxTx import *
from radboy.Roster.Roster import *
from radboy.HealthLog.HealthLog import *
#from radboy
from radboy.Solver.Solver import *
import time,random
import sys
from colored import Fore,Back,Style
from radboy.Of.of import *
from radboy.Orders import MilkWaterOrder


verify=kl11()
if verify == False:
    exit("You are not authorized to use this product")

msg='''MobileInventoryCLI
An Android/Linux Retail Calculator/ListMaker
written in Python 3.9-12; A product by

If the people do not read the signs
saying road-block ahead, 
what good is it to scream it at them;
some times you have to let the world cull itself,
such that balance is restored, 
with which that omission can be used,
as necessary when the unwilling is less than eager
to listen when hearing;

some lessons must be learned with pain;

that with greater hope,
a lesson can be learned
by the values taught.

Take care that the misuse of values,
be of riddence to your daily's,
For each carries in its own grain,
the hallows of a curse,
that if used against the proper,
be a sharpened edge that which to fall upon,
In haste to end one's own shame,
For which many have trully already fallen.

Carl Joseph Hirner III
'''
def startupMsg(msg):
    useMe=detectGetOrSet(name="UseStartMsg",value=True,setValue=False)
    if useMe:
        sys.stdout.write(f"{Fore.light_green}")
        for i in msg:
            s=random.randint(1,3)*0.0001
            if s == 0.0001:
                sys.stdout.write(f"{Fore.light_yellow}")
            elif s == 0.0002:
                sys.stdout.write(f"{Fore.light_steel_blue}")
            else:
                sys.stdout.write(f"{Fore.light_green}")
            sys.stdout.write(i)
            sys.stdout.flush()
            time.sleep(s)
        sys.stdout.write(f"{Style.reset}")

if __name__ == "__main__":
    startupMsg(msg)
async def protect():
    while True:
        try:
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
            protect_unassigned=detectGetOrSet("protect_unassigned",True,setValue=False)
            print(f"{Fore.light_green}Protect protect_unassigned: {Fore.light_red}{protect_unassigned}{Style.reset}")
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
                    graveyard=Prompt.__init2__(None,func=lambda text,data,passThru=[],PassThru=False:FormBuilderMkText(text,data,passThru=[],PassThru=PassThru),ptext="Are working overnight?/skip backup==True.",helpText="type a boolean yes or no",data="boolean",alt_input=timedout)
                    print(graveyard,"x",type(graveyard))
                    if graveyard in ['d',True]:
                        graveyard=True
                        return
                    elif graveyard in [None,]:
                        exit("User quit Early!")
                    if not graveyard:
                        try:
                            DayLogger.addTodayP(ENGINE)
                        except Exception as e:
                            print(e)
                        bare_ca(None,protect_unassigned=protect_unassigned,inList=True)
                    return
                elif clred == tdt:
                    bu=detectGetOrSet("daily_backups_count",1,setValue=False,literal=False)
                    cleared_times=detectGetOrSet("cleared_times",0,setValue=False)
                    if cleared_times >= bu:
                        graveyard=Prompt.__init2__(None,func=lambda text,data,passThru=[],PassThru=False:FormBuilderMkText(text,data,passThru=[],PassThru=PassThru),ptext="Are working overnight?/skip backup==True.",helpText="type a boolean yes or no",data="boolean",alt_input=timedout)
                        if graveyard in ['d',True]:
                            graveyard=True
                            return
                        elif graveyard in [None,]:
                            exit("User quit Early!")

                        print(f"Too Many backups! only {bu} is permitted!")
                        today=datetime.now()
                        tomorrow=datetime(today.year,today.month,today.day)+timedelta(seconds=24*60*60)
                        waiting=tomorrow-today
                        print(f"{Fore.grey_70}cleared at {Fore.green_3a}{cleared_date}{Fore.grey_70}for a duration of {Fore.green_3a}{dur}{Fore.light_blue} :{Fore.light_cyan} clear protection is enabled and you have to wait ({Fore.light_steel_blue}to alter use the following cmd set {Fore.cyan}`sysset`;`se`;$INDEX_FOR==bypass_clear_time_clear_protection;`true` or `false`{Fore.light_cyan}) {Fore.light_cyan}{waiting}{Fore.orange_red_1} or @ {tomorrow} to clear data to zero to {Fore.light_yellow}prevent {Fore.light_red}duplicate logs!{Style.reset}")
                        return
                    else:
                        graveyard=Prompt.__init2__(None,func=lambda text,data,passThru=[],PassThru=False:FormBuilderMkText(text,data,passThru=[],PassThru=PassThru),ptext="Are working overnight?/skip backup==True.",helpText="type a boolean yes or no",data="boolean",alt_input=timedout)
                        if graveyard in ['d']:
                            graveyard=True
                            return
                        elif graveyard in [None,]:
                            exit("User quit Early!")
                        new_date=datetime.now()
                        new_date=datetime(new_date.year,new_date.month,new_date.day)
                        x_day=new_date.day
                        x_month=new_date.month
                        x_year=new_date.year
                        new_cleared_date=detectGetOrSet("cleared_date",f"{x_month}/{x_day}/{x_year}",setValue=True,literal=True)
                        cleared_times=detectGetOrSet("cleared_times",cleared_times+1,setValue=True)
                        DayLogger.addTodayP(ENGINE)
                        bare_ca(None,protect_unassigned=protect_unassigned,inList=True)                      
                        return
                else:
                    
                    today=datetime.now()
                    tomorrow=datetime(today.year,today.month,today.day)+timedelta(seconds=24*60*60)
                    waiting=tomorrow-today

                    print(f"{Fore.grey_70}cleared at {Fore.green_3a}{cleared_date}{Fore.grey_70}for a duration of {Fore.green_3a}{dur}{Fore.light_blue} :{Fore.light_cyan} clear protection is enabled and you have to wait ({Fore.light_steel_blue}to alter use the following cmd set {Fore.cyan}`sysset`;`se`;$INDEX_FOR==bypass_clear_time_clear_protection;`true` or `false`{Fore.light_cyan}) {Fore.light_cyan}{waiting}{Fore.orange_red_1} or @ {tomorrow} to clear data to zero to {Fore.light_yellow}prevent {Fore.light_red}duplicate logs!{Style.reset}")
                    return
        except Exception as e:
            print(e)

import asyncio
asyncio.run(protect())
#ensure readline on boot
with Session(ENGINE) as session:
    READLINE_PREFERECE=session.query(SystemPreference).filter(SystemPreference.name=='readline').order_by(SystemPreference.dtoe.desc()).all()
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
            print(f"Readline is : {cfg}")
            if cfg =='':
                READLINE_PREFERECE[f].value_4_Json2DictString=json.dumps({"readline":True})
                import readline
                session.commit()
                session.refresh(READLINE_PREFERECE[f])
            else:
                try:
                    x=json.loads(READLINE_PREFERECE[f].value_4_Json2DictString)
                    if x.get("readline") == True:
                        try:
                            import readline
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

#VERSION="0.3.0177"
def readCL():
    text=''
    with open(Path(__file__).parent/Path("changelog.txt"),"r") as log:
        while True:
            d=log.read(1024)
            if not d:
                break
            text+=d
        return text

max_file_lines=detectGetOrSet("MAX_HFL",500)


class Main:
    def collector2(self):
        self.Collector2=Collector2(engine=self.engine,parent=self)

    ChangeLog='''
    '''
    def __init__(self,engine,tables,error_log):
        #fix fields not mean to be None Type
        with Session(ENGINE) as session:
            results=session.query(Entry).filter(Entry.Distress==None).update({"Distress":0})
            session.commit()
            session.flush()


        startupMsg(globals().get("msg"))
        nowFloat=datetime.now().timestamp()
        detectGetOrSet("InShellStart",nowFloat,setValue=True)
        RandomStringUtilUi(parent=self,engine=engine,justClean=True)
        self.ageLimit=AGELIMIT
        ClipBoordEditor.autoClean(self)

        asyncio.run(Expiration(init_only=True).show_warnings_async())
        #Expiration(init_only=True).show_warnings()
        print(f"{Fore.light_cyan}Running on Android:{Fore.slate_blue_1}{onAndroid()}{Style.reset}")
        print(f"{Fore.light_cyan}Running on {Fore.slate_blue_1}{platform.system()} {Fore.light_cyan}Rel:{Fore.orange_red_1}{platform.release()}{Style.reset}")
        self.ChangeLog=readCL()
        self.ExtractPkg=ExtractPkg
        self.DayLogger=DayLogger
        self.Lookup=Lookup
        self.engine=engine
        self.tables=tables
        self.error_log=error_log
        self.unified=lambda line,self=self:unified.Unified.unified(self,line=line)
        self.modes={
        '1':{
        'cmds':['collect','1','item'],
        'exec':self.startCollectItemMode,
        'desc':'use to collect item data rapidly by barcode and code with auto editing enabled'
        },
        '1.1':{
        'cmds':['collect2','11','c2l_sep',],
        'exec':self.collector2,
        'desc':'collect barcode/itemcode pairs for later export separate of Entry Table used in PairCollections Table'
        },
        '2':{
        'cmds':['list','2','+/-','cnt','count','ct'],
        'exec':self.startListMode,
        'desc':"similar to 'collect' but adds InList=True to Entry, and requests a quantity for ListQty; not as useful as using 'Task' Mode Tho",
        },
        '3':{
        'cmds':['quit','q','3','e'],
        'exec':lambda self=self:Prompt.cleanup_system(None),
        'desc':"exit program"
        },
        '4':{
        'cmds':['import','system_import','si','4'],
        'exec':lambda self=self:self.ExtractPkg(tbl=self.tables,engine=self.engine,error_log=self.error_log),
        'desc':"Import Codes from MobileInventory Pro Backup File with *.bck"
        },
        '5':{
        'cmds':['lu','5','lookup','search'],
        'exec':lambda self=self:self.Lookup(),
        
        'desc':"Lookup product info!",
            },
        '6':{
        'cmds':['dl','6','daylog','history','log','hist'],
        'exec':lambda self=self:self.DayLogger(engine=engine),
        
        'desc':"DB History System for the Changes made to the Entry Table",
            },
        '7':{
        'cmds':['convert','7','cnvt',],
        'exec':lambda self=self:ConvertCode(),
        
        'desc':"convert codes upce2upca also creates a saved img!",
            },
        '8':{
        'cmds':['setCode','8','setcd',],
        'exec':lambda self=self:SetCode(engine=engine),
        
        'desc':"convert codes upce2upca also creates a saved img!",
            },
            '9':{
        'cmds':['shelf_locator','9','shelf_locator','shf_lct'],
        'exec':lambda self=self:Locator(engine=engine),
        
        'desc':"find shelf location using barcode to shelf tag code from Entry Table",
            },
        '99':{
        'cmds':['pc_sl','99','paircollection_shf_lctr','shf_lct_pc'],
        'exec':lambda self=self:Locator2(engine=engine),
        
        'desc':"find shelf location using barcode to shelf tag code from PairCollections Table",
            },
        '999':{
        'cmds':['bis','999','barcode_is_shelf','bc_i_shf'],
        'exec':lambda self=self:LocatorUPCisShelf(engine=engine),
        
        'desc':"find shelf location using barcode to shelf tag code where barcode is identical to shelf tag barcode, data-wise",
            },
            '10':{
        'cmds':['lm2','10','list_mode2'],
        'exec':lambda self=self:ListMode2(engine=engine,parent=self),
        
        'desc':"list mode using only one code input!",
            },
        '11':{
        'cmds':['tag_data','td','5d','tag-var','tv'],
        'exec':lambda:pc.run(engine=self.engine),
        
        'desc':f"Scan a code, and see related data to code ; searches only Barcode field; shows {Fore.light_red}Safeway {Fore.orange_red_1}Shelf Tag Variants!{Style.reset}",
            },
        '12':{
        'cmds':['tasks','t','job'],
        'exec':lambda self=self:TasksMode(engine=engine,parent=self,root_modes=self.modes),
        
        'desc':"job related tasks! [Task Mode]",
            },
        'lsq':{
            'cmds':['lsq','13','location_sequencer'],
            'exec':lambda self=self:LocationSequencer(engine=self.engine,parent=self),
            'desc':'set Entry.Location like with a Telethon!'
            },
        'pc':{
            'cmds':['pc','14','punch_card'],
            'exec':lambda self=self:PunchCard(engine=self.engine,parent=self),
            'desc':'Perform punchcard operations!'
            },
        'converter':{
            'cmds':['cvtu','15','convert_unit'],
            'exec':lambda self=self:Conversion(engine=self.engine,parent=self),
            'desc':'Convert a value from one unit to another!'
            },
        'ChangeLog':{
            'cmds':['cl','16','changelog'],
            'exec':lambda self=self:print(self.ChangeLog),
            'desc':'print dev messages'
            },
        'POS':{
            'cmds':['pos','17','point_of_sale'],
            'exec':lambda self=self:POS(engine=self.engine,parent=self),
            'desc':'print dev messages'
            },
        'Repack':{
            'cmds':['rpk','repack','18'],
            'exec':lambda self=self:RepackExec(engine=self.engine,parent=self),
            'desc':'repack materials for backroom storage, and id'
            },
        'glossary':{
            'cmds':['glossary','19','g'],
            'exec':lambda self=self:GlossaryUI(engine=self.engine,parent=self),
            'desc':'terms and definitions related to inventory management'
            },
        'displays':{
            'cmds':['displays','20','disp'],
            'exec':lambda self=self:DisplayItemUI(engine=self.engine,parent=self),
            'desc':'temporary display information'

        },
        'BnC':{
            'cmds':['bnc','21','banking and cashpool','banking_and_cashpool','bank','piggy-bank'],
            'exec':lambda self=self:BnCUi(parent=self),
            'desc':'Banking and CashPool'
        },
        'ExT':{
            'cmds':['et','exercise_tracker','exercise tracker'],
            'exec':lambda self=self:ExerciseTracker(),
            'desc':'Track my exercise routine'
        },
        'Roster':{
            'cmds':['roster','rstr','trollingus explicitus'],
            'exec':lambda self=self:RosterUi(),
            'desc':'Work Schedule;some cmds are explicit phrases, so get used to it, or dont use this part of the toolset'
        },
        'HealthLog':{
            'cmds':['hlthlg','hl','health log','healthlog'],
            'exec':lambda self=self:HealthLogUi(),
            'desc':'health data records for you as a person; but fuck, if you wish it be for your machine, make the values match on your terms, bitches!'
        },
        'Solver':{
            'cmds':['slv','solver','slvr',],
            'exec':lambda self=self:solverUi(),
            'desc':'run externally written python3 code loaded from input()/saved from a previous run under SolverFormulasStore table/read from external file'
        },
        }
        
        #
        #self.modeString=''.join([f"{Fore.cyan}{self.modes[i]['cmds']} - {self.modes[i]['desc']}{Style.reset}\n" for i in self.modes])
        def printHelp(self):
            st=[]
            for num,i in enumerate(self.modes):
                color1=Fore.sea_green_2
                color2=Fore.dark_goldenrod
                st.append(f"{color1}{'|'.join([i for i in self.modes[i]['cmds']])}{Style.reset} - {color2}{self.modes[i]['desc']}{Style.reset}")
            for num,i in enumerate(st):
                if num%2==0:
                    color1=Fore.sea_green_2
                    color2=Fore.dark_goldenrod
                else:
                    color1=Fore.light_green
                    color2=Fore.light_yellow
                st[num]=i.replace("|",f"{color1}{Style.bold}|{Style.reset}{color2}")
            return '\n'.join(st)
        self.modeString=printHelp(self)
       
        while True:
            self.currentMode=input(f"{Fore.light_green}[{Fore.light_steel_blue}Root{Style.reset}{Fore.light_green}]{Style.reset}which mode do you want to use[?/m]:{Fore.green_yellow} ").lower()
            logInput(self.currentMode)
            if self.currentMode.lower() in ['?','h']:
                print(self.modeString)
                continue
            elif self.currentMode in ['system_settings','system settings','sysset']:
                systemSettingsMenu()
            elif self.currentMode in ['m',]:
                print(f"""
{Fore.light_magenta}PEMDAS {Fore.light_salmon_3a}->{Fore.light_yellow}Left To Right{Style.reset}
{Fore.light_magenta}UPCA/UPCE {Fore.light_salmon_3a}->{Fore.dark_goldenrod}
If your product barcode is an 8-digit UPCE,
then you are going to need to ensure you have its
ALT_Barcode filled with the corresponding code manually
to enable searches that have that code when using updated data
from MobileInventoryPro Backup file
{Fore.light_green}{Style.bold}
This Code will automatically fill the ALT_Barcode field if one
is not provided, i.e. ALT_Barcode==None, and UPCE->UPCA==True.
{Style.reset}
{Fore.light_magenta}Switch to PunchCard Mode [pc or 14]{Style.reset}
{Fore.cyan}Task Order{Style.reset}{Fore.light_yellow} ->{Style.reset} Task Mode Cmd [{Fore.light_green}Explanation{Style.reset}]
{Fore.cyan}1{Style.reset} ->{Fore.light_yellow} ps{Style.reset} [{Fore.light_green}Start Shift{Style.reset}]
{Fore.cyan}2{Style.reset} ->{Fore.light_yellow} brks{Style.reset} [{Fore.light_green}Break Start{Style.reset}]
{Fore.cyan}3{Style.reset} ->{Fore.light_yellow} brke{Style.reset} [{Fore.light_green}Break End{Style.reset}]
{Fore.cyan}4{Style.reset} ->{Fore.light_yellow} end{Style.reset} [{Fore.light_green}End Shift{Style.reset}]

{Fore.light_magenta}Switch to Task Mode [t]{Style.reset}
{Fore.cyan}Task Order{Style.reset}{Fore.light_yellow} ->{Style.reset} Task Mode Cmd [{Fore.light_green}Explanation{Style.reset}]
{Fore.cyan}10{Style.reset} -{Fore.light_yellow} lu{Style.reset}  [{Fore.light_green}Lookup items in List for needed Qty's{Style.reset}]
{Fore.cyan}11{Style.reset} -{Fore.light_yellow} ts{Style.reset}  [{Fore.light_green}TouchStamp - create a note related to barcode(+) or synthetically-generated barcode(s){Style.reset}]

{Fore.light_magenta}Switch to Daylog Mode/Entry History [6 or dl or daylog]{Style.reset}
{Fore.cyan}Task Order{Style.reset}{Fore.light_yellow} ->{Style.reset} Task Mode Cmd [{Fore.light_green}Explanation{Style.reset}]
{Fore.cyan}1{Style.reset} ->{Fore.light_yellow} a{Style.reset} [{Fore.light_green}add a daylog{Style.reset}]
{Fore.cyan}2{Style.reset} ->{Fore.light_yellow} b{Style.reset} [{Fore.light_green}return to previous menu{Style.reset}]

{Fore.light_magenta}Switch to PairCollection Tag Locator Mode [99]{Style.reset}
{Fore.light_green}Scan a Product Barcode, then scan shelf tags until a match is found or use quits(q)/backs up a menu(b)
this option uses the PairCollection's Table which is independent of the Entry's table.
{Style.reset}
{Fore.light_magenta}Switch to Shelf Tag Locator Mode [9]{Style.reset}
{Fore.light_green}Scan a Product Barcode, then scan shelf tags until a match is found or use quits(q)/backs up a menu(b)
this option uses the Entry's Table which is independent of the PairCollection's table.
{Style.reset}

{Fore.light_magenta}Switch to POS Mode[16 or {Style.bold}pos{Style.reset}{Fore.light_magenta}]{Style.reset}
{Fore.cyan}Task Order{Style.reset}{Fore.light_yellow} ->{Style.reset} Task Mode Cmd [{Fore.light_green}Explanation{Style.reset}]
{Fore.cyan}newb|new_b|nb{Style.reset} ->{Fore.light_yellow} Create New Billing Information Entry{Style.reset}
{Fore.cyan}view_db|viewdb|vdb{Style.reset} ->{Fore.light_yellow}View Default Billing Information Entry{Style.reset}
{Fore.cyan}view_all_billing|view_ab|vab{Style.reset} ->{Fore.light_yellow}View All Billing information{Style.reset}
{Fore.cyan}listr|ls_rcpt|lr{Style.reset} ->{Fore.light_yellow} List Reciepts{Style.reset}
{Fore.cyan}deltr|del_reciept|rr{Style.reset} ->{Fore.light_yellow} Delete a reciept by RecieptId{Style.reset}
{Fore.cyan}newb|new_b|nb{Style.reset} ->{Fore.light_yellow} Create New Business Information Entry{Style.reset}
{Fore.cyan}mkrcpt|make_receipt|{Style.bold}pos{Style.reset} ->{Fore.light_yellow} Create New Reciept/Invoice{Style.reset}
{Fore.cyan}are|add_rcpt_ent|add_reciept_entry{Style.reset} ->{Fore.light_yellow} Update Reciept Entry with new items{Style.reset}
{Fore.cyan}search_billing_text|{Style.bold}sbt{Style.reset} ->{Fore.light_yellow}Search Billing text{Style.reset}

{Fore.light_magenta}Switch to Task Mode [t]{Style.reset}
{Fore.cyan}Task Order{Style.reset}{Fore.light_yellow} ->{Style.reset} Task Mode Cmd [{Fore.light_green}Explanation{Style.reset}]
{Fore.cyan}1{Style.reset} ->{Fore.light_yellow} ca{Style.reset} [{Fore.light_green}Clear All List Maker Qty's{Style.reset}]

{Fore.light_magenta}Switch to Task Mode [t]{Style.reset}
{Fore.cyan}Task Order{Style.reset}{Fore.light_yellow} ->{Style.reset} Task Mode Cmd [{Fore.light_green}Explanation{Style.reset}]
{Fore.cyan}1{Style.reset} ->{Fore.light_yellow} #40{Style.reset} [{Fore.light_green}Starbux water Display Barge and Display at end of Self-Checkout{Style.reset}]
{Fore.cyan}2{Style.reset} ->{Fore.light_yellow} #42{Style.reset} [{Fore.light_green}Starbux Water Kooler{Style.reset}]
{Fore.cyan}3{Style.reset} ->{Fore.light_yellow} #46{Style.reset} [{Fore.light_green}Check Stand Supplies{Style.reset}]
{Fore.cyan}4{Style.reset} ->{Fore.light_yellow} #45{Style.reset} [{Fore.light_green}Wood Display By Front Mgmnt Office{Style.reset}]
{Fore.cyan}5{Style.reset} ->{Fore.light_yellow} #44{Style.reset} [{Fore.light_green}Water Display on Floral Barge{Style.reset}]
{Fore.cyan}6{Style.reset} ->{Fore.light_yellow} #43{Style.reset} [{Fore.light_green}Chip/Popcorn on Aisle 4/3/2{Style.reset}]
{Fore.cyan}7{Style.reset} ->{Fore.light_yellow} #25{Style.reset} [{Fore.light_green}Aisle 10 Wood{Style.reset}]
{Fore.cyan}8{Style.reset} ->{Fore.light_yellow} #27{Style.reset} [{Fore.light_green}Display on Front End Cap of 13 and 12{Style.reset}]
{Fore.cyan}9{Style.reset} ->{Fore.light_yellow} #25{Style.reset} [{Fore.light_green}Water Aisle{Style.reset}]

{Fore.light_magenta}Switch to PairCollection Mode [11]{Style.reset}
{Fore.cyan}Task Order{Style.reset}{Fore.light_yellow} ->{Style.reset} Task Mode Cmd [{Fore.light_green}Explanation{Style.reset}]
{Fore.cyan}1{Style.reset} ->{Fore.light_yellow} 1bnuc{Style.reset} [{Fore.light_green}Add Barcode and Code with Code being Non-Unique{Style.reset}]
{Fore.cyan}2{Style.reset} ->{Fore.light_yellow} 1bnoc{Style.reset} [{Fore.light_green}Add Barcode and Code=='No_CODE'{Style.reset}]
{Fore.cyan}3{Style.reset} ->{Fore.light_yellow} 4,a{Style.reset} [{Fore.light_green}List All PairCollections{Style.reset}]
{Fore.cyan}4{Style.reset} ->{Fore.light_yellow} 7,$PairCollectionId{Style.reset} [{Fore.light_green}Remove a Pair Collection By Id{Style.reset}]
{Fore.cyan}5{Style.reset} ->{Fore.light_yellow} rmby{Style.reset} [{Fore.light_green}remove a PairCollection by field==value{Style.reset}]
{Fore.cyan}6{Style.reset} ->{Fore.light_yellow} 5{Style.reset} [{Fore.light_green}Save PairCollections to ScreenShots Folder{Style.reset}]
                    """)
            print(Style.reset,end="")
            for k in self.modes:
                if self.currentMode in self.modes[k]['cmds']:
                    self.modes[k]['exec']()

    def Unified(self,line):
        try:
            return self.unified(line)
        except Exception as e:
            print(e)
            return False



    upc_other_cmds=False
    code_other_cmds=False
    def startCollectItemMode(self):
        code=''
        barcode=''
        options=['q - quit - 1','2 - b - back','skip','?']
        while True:
            self.upc_other_cmds=False
            self.code_other_cmds=False
            while True:
                fail=False
                upce=''
                barcode=input(f"{Fore.green_yellow}Barcode{Style.reset}{options}{Style.bold}\n: ")
                logInput(barcode)
                print(f"{Style.reset}")
                if barcode.lower() in ['q','quit','1']:
                    exit('user quit!')
                elif barcode in ['2','b','back']:
                    return
                elif barcode.lower() in ['skip','sk','skp']:
                    #barcode='1'*11
                    break
                elif barcode.lower() in ['?']:
                    self.help()
                    self.upc_other_cmds=True
                elif self.Unified(barcode):
                    self.upc_other_cmds=True
                elif barcode == '':
                    #barcode='0'*11
                    break
                else:   
                    if len(barcode) == 8:
                        try:
                            upce=upcean.convert.convert_barcode(intype="upce",outtype="upca",upc=barcode)
                        except Exception as e:
                            print(e)                
                    for num,test in enumerate([UPCA,EAN8,EAN13]):
                        try:
                            if test == UPCA:
                                if len(barcode) >= 11:
                                    t=test(barcode) 
                                elif len(barcode) == 8:
                                    t=test(upce)
                            else:
                                t=test(barcode)
                                print(t)
                            break
                        except Exception as e:
                            print(e)
                            if num >= 3:
                                fail=True
                #print("break",fail)
                if fail:
                    barcode='0'*11
                    break
                else:
                    break

            while True:
                fail=False
                code=input(f"{Style.reset}{Fore.green}Code{Style.reset}{options}{Style.bold}\n: ")
                logInput(code)
                print(f"{Style.reset}")
                if code.lower() in ['q','quit','1']:
                    exit('user quit!')
                elif code in ['2','b','back']:
                    return
                elif code.lower() in ['skip','sk','skp']:
                    #code='1'*8
                    break
                elif code.lower() in ['?']:
                    self.help()
                    self.code_other_cmds=True
                elif self.Unified(code):
                    self.code_other_cmds=True
                elif code == '':
                    #code='0'*8
                    break
                elif code == 'tlm':
                    self.listMode=not self.listMode
                    print(f"ListMode is now: {Fore.red}{self.listMode}{Style.reset}")
                    break
                elif code == 'slm':
                    print(f"ListMode is: {Fore.red}{self.listMode}{Style.reset}")
                    break
                else:
                    fail=False
                    for num,test in enumerate([Code39,]):
                        try:
                            t=test(code,add_checksum=False)
                            break
                        except Exception as e:
                            print(e)
                            if num >= 1:
                                fail=True
                if fail:
                    code='0'*8
                    break
                else:
                    break
            
            if self.code_other_cmds == False and self.upc_other_cmds == False:
                with Session(self.engine) as session:
                    if len(barcode) == 8:
                        if code == '#skip':
                            try:
                                query=session.query(self.tables['Entry']).filter(self.tables['Entry'].barcode.icontains(barcode))
                            except Exception as e:
                                query=session.query(self.tables['Entry']).filter(self.tables['Entry'].barcode.icontains(upce))
                        elif barcode == '#skip':
                            query=session.query(self.tables['Entry']).filter(self.tables['Entry'].Code.icontains(upce))
                        else:   
                            query=session.query(self.tables['Entry']).filter(or_(self.tables['Entry'].Barcode.icontains(barcode),self.tables['Entry'].Code.icontains(code)))

                    else:
                        print(code,barcode)
                        if code in ['#skip','']:
                            query=session.query(self.tables['Entry']).filter(self.tables['Entry'].Barcode.icontains(barcode))
                        elif barcode == ['#skip','']:
                            query=session.query(self.tables['Entry']).filter(self.tables['Entry'].Code.icontains(code))

                        else:
                            query=session.query(self.tables['Entry']).filter(or_(self.tables['Entry'].Barcode.icontains(barcode),self.tables['Entry'].Code.icontains(code)))
                    results=query.all()
                    if len(results) < 1:
                        print(code)
                        print(barcode)
                        if (code != '0'*8 and barcode != '0'*11):
                            if upce != '':
                                entry=self.tables['Entry'](Barcode=upce,Code=barcode,upce2upca=barcode,InList=True)
                            else:
                                entry=self.tables['Entry'](Barcode=barcode,Code=code,InList=True)
                            session.add(entry)
                            session.commit()
                            session.flush()
                            session.refresh(entry)
                            print(entry)
                    else:
                        for num,e in enumerate(results):
                            print(f"{Fore.light_red}{num}{Style.reset}->{e}")
                        while True:
                            msg=input(f"Do you want to edit one? if so enter its {Fore.light_red}entry number{Style.reset}(or {Fore.yellow}-1|q|quit{Style.reset} to {Fore.yellow}quit{Style.reset},{Fore.cyan}-2|b|back{Style.reset} to {Fore.cyan}go back{Style.reset}{Fore.green}[or Hit <Enter>]{Style.reset}): ")
                            logInput(msg)
                            try:                                
                                if msg == '':
                                    if self.listMode and len(results) >=1:
                                        qty=input("How Much to add? ")
                                        logInput(qty)
                                        if qty == '':
                                            qty=1
                                        qty=float(qty)
                                        setattr(results[0],'InList',True)
                                        setattr(results[0],'ListQty',getattr(results[0],'ListQty')+qty)
                                        session.commit()
                                        session.flush()
                                        session.refresh(results[0])
                                    break
                                if msg.lower() in ['-1','q','quit']:
                                    exit("user quit!")
                                elif msg.lower() in ['-2','b','back']:
                                    break
                                else:
                                    num=int(msg)
                                    if num < 0:
                                        raise Exception("Invalid Id:Hidden CMD!")
                                    else:
                                        if self.listMode:
                                            while True:
                                                qty=input("How Much to add? ")
                                                logInput(qty)
                                                print(qty)
                                                if qty == '':
                                                    qty=1
                                                qty=float(qty)
                                                setattr(results[num],'InList',True)
                                                setattr(results[num],'ListQty',getattr(results[num],'ListQty')+qty)
                                                session.commit()
                                                session.flush()
                                                session.refresh(results[num])
                                                break
                                        else:
                                            print(results[num])
                                            self.editEntry(session,results[num])
                                        break
                            except Exception as e:
                                print(e)
                            #use first result as found as entry and display it while incrementing it
                            

    listMode=False
    def editEntry(self,session,item):
        print(session,item)
        for column in item.__table__.columns:
            while True:
                try:
                    if column.name not in ['Timestamp','EntryId','Image']:
                        new_value=input(f"{column.name}->{getattr(item,column.name)}('n','s','d','q'): ")
                        logInput(new_value)
                        if new_value in ['s','n','']:
                            break
                        elif new_value in ['#clear_field']:
                            if isinstance(column.type,Float):
                                new_value=float(0)
                            elif isinstance(column.type,Integer):
                                new_value=int(0)
                            elif str(column.type) == "VARCHAR":
                                new_value=''
                            elif isinstance(column.type,Boolean):
                                setattr(item,column.name,0)
                        elif new_value in ['d']:
                            session.query(self.tables['Entry']).filter(self.tables['Entry'].EntryId==item.EntryId).delete()
                            print(item,"Was Deleted!")
                            return
                        elif new_value in ['b']:
                            return  
                        elif new_value in ['q']:
                            exit("user quit!")

                        if isinstance(column.type,Float):
                            new_value=float(new_value)
                        elif isinstance(column.type,Integer):
                            new_value=int(new_value)
                        elif str(column.type) == "VARCHAR":
                            pass
                        elif isinstance(column.type,Boolean):
                            if new_value.lower() in ['true','yes','1','y',]:
                                setattr(item,column.name,1)
                            else:
                                setattr(item,column.name,0)
                        if str(column.type) not in ['BOOLEAN',]:
                            #exit(str((column.name,column.type,isinstance(column.type,Boolean))))
                            setattr(item,column.name,new_value)
                            
                        session.commit()
                    break
                except Exception as e:
                    print(e)




    def startListMode(self):
        print(f"{Fore.yellow}List Mode{Style.reset}")
        self.listMode=True
        self.startCollectItemMode()

    def help(self,print_no=False):
        with open(Path(__file__).parent/Path("helpMsg.txt"),"r") as msgr:
            msg=f"""{msgr.read().format(Style=Style,Fore=Fore,Back=Back)}"""
            if not print_no:
                print(msg)
            return msg

def quikRn():
    Main(engine=ENGINE,tables=tables,error_log=Path("error_log.log"))

if __name__ == "__main__":
    Main(engine=ENGINE,tables=tables,error_log=Path("error_log.log"))
