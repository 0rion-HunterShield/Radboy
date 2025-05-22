from radboy.DB.db import *
from radboy.DB.Prompt import *
from radboy.FB.FBMTXT import *
from radboy.FB.FormBuilder import *
from radboy.DB.DatePicker import *

from radboy.TasksMode.Tasks import *

import pandas as pd
import csv
from copy import deepcopy as copy
from datetime import datetime,date,timedelta
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
from collections import OrderedDict,namedtuple



DEFAULT_NEW={'DisplayLocationStoreFront':None,'EndCap':False,'ShadowBox':False,'Gondolas':True,'FreeStandingFSDU':False,'Barcode':'','Code':'','Name':'','EntryId':0,'Note':'','QtyForDisplay':1,'DisplayLocation':'///'}
DEFAULT_NEW2={'Code':'','Name':'','Note':'','QtyForDisplay':1}
DEFAULT_NEWLOCATIONS=OrderedDict(Aisle='',DisplayLocationStoreFront=None,EndCap=False,ShadowBox=False,Gondolas=False,FreeStandingFSDU=False,Date=date(datetime.now().year,datetime.now().month,datetime.now().day))
class DisplayItemUI(TasksMode):
    helpText=f'''
    '''
    def mkText(self,text,data):
        return text

    def mkNewDisp(self,data=DEFAULT_NEW,ignore_fields=False):
        if data == None:
            DATA=DEFAULT_NEW
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
                while True:
                    try:
                        def lclt(text,data):
                            return text
                        dtmp=Prompt.__init2__(None,func=lclt,ptext=f"DisplayItem [default:{data[f]}] {f}",helpText=f"{Fore.light_steel_blue}Enter a value for {f}, or leave blank to use scanned code; 'b' goes back to 'TaskMode'; 'e' to skip/exit entry altogether! 'p' for previous ; 'd' to use default stored value, if you entered a value, then 'd' will use that value when coming back from 'p'{Style.reset}",data=self)
                        if dtmp in [None,]:
                            print(f"{Fore.orange_red_1}User Canceled!{Style.reset}")
                            return
                        elif isinstance(dtmp,str):
                            if str(dtmp).lower() in ['e',]:
                                return
                            elif str(dtmp).lower() in ['p',]:
                                #print(num,num-1,"#3 loop while")
                                self.skipTo=num-1
                                break
                            elif str(dtmp).lower() in ['d',]:
                                print(f'{Fore.light_green}{data[f]}{Style.reset}',f'{Fore.orange_red_1}using default{Style.reset}')
                                pass
                            elif dtmp in ['i','n']:
                                try:
                                    data[f]=int(data[f]+1)
                                except Exception as e:
                                    print(e,"using default value instead as incrementation is not supported for this Type")
                            else:
                                fields={i.name:str(i.type) for i in DisplayItem.__table__.columns}
                                if ignore_fields:
                                    if dtmp != '':
                                        data[f]=dtmp
                                    elif dtmp == '':
                                        pass
                                elif f in fields.keys():
                                    if fields[f].lower() in ["string",]:
                                        data[f]=dtmp
                                    elif fields[f].lower() in ["float",]:
                                        data[f]=float(eval(dtmp))
                                    elif fields[f].lower() in ["integer",]:
                                        data[f]=int(eval(dtmp))
                                    elif fields[f].lower() in ["boolean",]:
                                        if dtmp.lower() in ['y','yes','t','true','1']:
                                            data[f]=True
                                        else:
                                            data[f]=False
                                    elif fields[f].lower() in ['date',]:
                                        data[f]=DatePkr()
                                    else:
                                        data[f]=dtmp
                                else:
                                    raise Exception(f"{Fore.red}{Style.bold}Unsupported Field {Fore.light_red}'{f}'{Style.reset}")
                                #data[f]=dtmp
                        else:
                            data[f]=dtmp
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

    #RND
    #make another version of SDS, to just select which display to view out of listed instead of typing blindly; keep both there are caveats to having to methods
    
    def SDS2(self):
        with Session(ENGINE) as session:
            displays=session.query(DisplayItem).group_by(DisplayItem.Aisle,DisplayItem.Date,DisplayItem.DisplayLocation)

            displays=displays.all()
            ct=len(displays)
            if ct < 1:
                print(f"{Fore.light_red}No Displays Present!{Style.reset}")
            items=[]
            for num,d in enumerate(displays):
                i=f"{d.Date}@{d.Aisle}"
                if i not in items:
                    items.append(i)

            header=f"{Fore.light_green}Total Displayed/{Fore.light_yellow}Total DID's {Fore.orange_red_1} -> Display.Date@Display.Aisle{Style.reset}"
            print(header)
            for num,d in enumerate(items):
                msg=f"{Fore.light_green}{num}/{Fore.dark_slate_gray_1}{num+1}/{Fore.light_yellow}{ct} {Fore.orange_red_1} -> {d}{Style.reset}"
                print(msg)

            aisle_index=Prompt.__init2__(self,func=FormBuilderMkText,ptext="which number?",helpText=f"number in {Fore.light_green}light_green{Style.reset}",data="integer")
            if aisle_index in [None,'d',]:
                print("Nothing Selected!")
                return
            aisle=displays[aisle_index].Aisle
            D=displays[aisle_index].Date

            query=session.query(DisplayItem).filter(DisplayItem.Date==D,DisplayItem.Aisle==aisle).order_by(DisplayItem.Date)
            displays=query.all()
            

            ct=len(displays)
            headers=f"\n{Fore.light_salmon_1}Date/{Fore.light_green}QTY/DisplayItem No./{Fore.light_yellow} Total Display Items {Fore.orange_red_1} ->[DID] Code|{Fore.cyan}Barcode|{Fore.light_steel_blue}Name|{Fore.medium_purple_3b}DisplayLocation|{Fore.light_sea_green}Note{Style.reset}\n"
            print(headers)
            for num,d in enumerate(displays):
                if d.Note in [None,]:
                    setattr(d,'Note','')
                    session.commit()
                    session.refresh(d)
                short_display=f'''{d.Code}|{Fore.cyan}{d.Barcode}|{Fore.light_steel_blue}{d.Name}|{Fore.medium_purple_3b}{d.DisplayLocation}|{Fore.light_sea_green}{d.Note}'''
                msg=f"{Fore.light_salmon_1}{d.Date}/{Fore.light_green}Qty({Fore.light_blue}{d.QtyForDisplay}{Fore.light_green})/{num+1}/{Fore.light_yellow}{ct} {Fore.orange_red_1} ->[{d.DID}] {short_display}{Style.reset}"
                print(msg)
            print(headers)


    def new2ShelfBatchNumeric_Plus(self):
        shelfNum=0
        shelfItemNum=0
        aisle=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Aisle Number/Designator:",helpText="what is the aisle",data="string")
        if aisle in [None,]:
            return
        elif aisle in ['d',]:
            aisle='A!A'
        while True:
            barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Barcode|Code|Search",helpText="type your search ; type 'nxt shlf' to increment shelf",data="string")
            if barcode in [None,]:
                return
            elif barcode in ['next shelf','nxtshlf','nxt shlf']:
                nextShelf=Prompt.__init2__(self,func=FormBuilderMkText,ptext="Next Shelf?",helpText="yes or no",data="boolean")
                if nextShelf in ['d',None]:
                    return
                elif nextShelf:
                    shelfNum+=1
                    shelfItemNum=0
                    continue
                else:
                    return
            item=None
            with Session(ENGINE) as session:
                results=session.query(Entry).filter(or_(
                    Entry.Barcode==barcode,
                    Entry.Code==barcode,
                    Entry.Code.icontains(barcode),
                    Entry.Barcode.icontains(barcode),
                    Entry.Name.icontains(barcode)
                    ))
                results=results.all()
                ct=len(results)
                dummy=False
                if ct <= 0:
                    print("No results")
                    dummy=True
                if not dummy:
                    for num,r in enumerate(results):
                        msg=f"{num}/{num+1}/{ct} - {r.seeShort()}"
                        print(msg)
                    while True:
                        which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which Entry number?",helpText="select the index",data="integer")
                        if which in [None,]:
                            return
                        elif which in ['d',]:
                            item=results[0]
                        else:
                            try:
                                item=results[which]
                                break
                            except Exception as e:
                                print(e)
                data={
                'QtyForDisplay':{
                    'type':'integer',
                    'default':1,
                },
                'Shelf Number':{
                    'default':shelfNum,
                    'type':'integer'
                    },
                'Shelf Item Number':{
                    'default':shelfItemNum,
                    'type':'integer'
                    },
                }
                data_after=FormBuilder(data=data)
                shelfNum=data_after['Shelf Number']
                if data_after == None:
                    nextShelf=Prompt.__init2__(self,func=FormBuilderMkText,ptext="Next Shelf?",helpText="yes or no",data="boolean")
                    if nextShelf in ['d',None]:
                        return
                    elif nextShelf:
                        shelfNum+=1
                        shelfItemNum=0
                        continue
                    else:
                        return
                data_after['Aisle']=aisle
                data_after['DisplayLocation']=f"{str(data_after['Aisle']).zfill(3)}/{str(data_after['Shelf Number']).zfill(3)}/{str(data_after['Shelf Item Number']).zfill(3)}"
                data_after.pop('Shelf Item Number')
                data_after.pop('Shelf Number')
                today=datetime.now()
                data_after['Date']=date(today.year,today.month,today.day)
                data_after['EndCap']=False
                data_after['ShadowBox']=False
                data_after['Gondolas']=False
                data_after['FreeStandingFSDU']=False
                data_after['DisplayLocationStoreFront']=False
                
                if item != None:
                    data_after['Name']=item.Name
                    data_after['Code']=item.Code
                    data_after['Note']=f"For the Shelf on {data_after['Aisle']}"
                    data_after['EntryId']=item.EntryId
                    self.create_ditem(data_after,"new2Shelf")
                else:
                    print("No Result Found... creating a dummy")
                    data_after['Barcode']=barcode
                    data_after['Name']="New Item Not Found in MiCLI db.Entry Table"
                    data_after['Code']="NI-NF-i-MiCLI"
                    data_after['Note']=f"Placeholder for missing item on the Shelf on {data_after['Aisle']}"
                    data_after['EntryId']=None
                    self.create_ditem(data_after,"new2Shelf")
                shelfItemNum+=1

    def new2ShelfBatch_sys_loc(self):
        aisle=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Aisle Number/Designator:",helpText="what is the aisle",data="string")
        if aisle in [None,]:
            return
        elif aisle in ['d',]:
            aisle='A!A'
        while True:
            barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Barcode|Code|Search",helpText="type your search",data="string")
            if barcode in [None,]:
                return
            item=None
            with Session(ENGINE) as session:
                results=session.query(Entry).filter(or_(
                    Entry.Barcode==barcode,
                    Entry.Code==barcode,
                    Entry.Code.icontains(barcode),
                    Entry.Barcode.icontains(barcode),
                    Entry.Name.icontains(barcode)
                    ))
                results=results.all()
                ct=len(results)
                dummy=False
                if ct <= 0:
                    print("No results")
                    dummy=True
                if not dummy:
                    for num,r in enumerate(results):
                        msg=f"{num}/{num+1}/{ct} - {r.seeShort()}"
                        print(msg)
                    while True:
                        which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which Entry number?",helpText="select the index",data="integer")
                        if which in [None,]:
                            return
                        elif which in ['d',]:
                            item=results[0]
                        else:
                            try:
                                item=results[which]
                                break
                            except Exception as e:
                                print(e)
                if item:
                    l=item.Location
                else:
                    l='///'

                data={
                'QtyForDisplay':{
                    'type':'integer',
                    'default':1,
                },
                'DisplayLocation':{
                    'type':'string',
                    'default':l,
                    }
                }

                data_after=FormBuilder(data=data)
                data_after['Aisle']=aisle
                today=datetime.now()
                data_after['Date']=date(today.year,today.month,today.day)
                data_after['EndCap']=False
                data_after['ShadowBox']=False
                data_after['Gondolas']=False
                data_after['FreeStandingFSDU']=False
                data_after['DisplayLocationStoreFront']=False
                
                if item != None:
                    data_after['Name']=item.Name
                    data_after['Code']=item.Code
                    data_after['Barcode']=barcode
                    data_after['Note']=f"For the Shelf on {data_after['Aisle']}"
                    data_after['EntryId']=item.EntryId
                    self.create_ditem(data_after,"new2Shelf")
                else:
                    print("No Result Found... creating a dummy")
                    data_after['Name']="New Item Not Found in MiCLI db.Entry Table"
                    data_after['Code']="NI-NF-i-MiCLI"
                    data_after['Note']=f"Placeholder for missing item on the Shelf on {data_after['Aisle']}"
                    data_after['EntryId']=None
                    self.create_ditem(data_after,"new2Shelf")

    def new2ShelfBatch(self):
        aisle=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Aisle Number/Designator:",helpText="what is the aisle",data="string")
        if aisle in [None,]:
            return
        elif aisle in ['d',]:
            aisle='A!A'
        while True:
            barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Barcode|Code|Search",helpText="type your search",data="string")
            if barcode in [None,]:
                return
            item=None
            with Session(ENGINE) as session:
                results=session.query(Entry).filter(or_(
                    Entry.Barcode==barcode,
                    Entry.Code==barcode,
                    Entry.Code.icontains(barcode),
                    Entry.Barcode.icontains(barcode),
                    Entry.Name.icontains(barcode)
                    ))
                results=results.all()
                ct=len(results)
                dummy=False
                if ct <= 0:
                    print("No results")
                    dummy=True
                if not dummy:
                    for num,r in enumerate(results):
                        msg=f"{num}/{num+1}/{ct} - {r.seeShort()}"
                        print(msg)
                    while True:
                        which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which Entry number?",helpText="select the index",data="integer")
                        if which in [None,]:
                            return
                        elif which in ['d',]:
                            item=results[0]
                        else:
                            try:
                                item=results[which]
                                break
                            except Exception as e:
                                print(e)
                data={
                'QtyForDisplay':{
                    'type':'integer',
                    'default':1,
                },
                'Shelf Number':{
                    'default':'0',
                    'type':'String'
                    },
                'Shelf Item Number':{
                    'default':'0',
                    'type':'String'
                    },
                }
                data_after=FormBuilder(data=data)
                data_after['Aisle']=aisle
                data_after['DisplayLocation']=f"{data_after['Aisle']}/{data_after['Shelf Number']}/{data_after['Shelf Item Number']}"
                data_after.pop('Shelf Item Number')
                data_after.pop('Shelf Number')
                today=datetime.now()
                data_after['Date']=date(today.year,today.month,today.day)
                data_after['EndCap']=False
                data_after['ShadowBox']=False
                data_after['Gondolas']=False
                data_after['FreeStandingFSDU']=False
                data_after['DisplayLocationStoreFront']=False
                
                if item != None:
                    data_after['Name']=item.Name
                    data_after['Code']=item.Code
                    data_after['Barcode']=barcode
                    data_after['Note']=f"For the Shelf on {data_after['Aisle']}"
                    data_after['EntryId']=item.EntryId
                    self.create_ditem(data_after,"new2Shelf")
                else:
                    print("No Result Found... creating a dummy")
                    data_after['Name']="New Item Not Found in MiCLI db.Entry Table"
                    data_after['Code']="NI-NF-i-MiCLI"
                    data_after['Note']=f"Placeholder for missing item on the Shelf on {data_after['Aisle']}"
                    data_after['EntryId']=None
                    self.create_ditem(data_after,"new2Shelf")

    def new2Shelf_sys_loc(self):
        while True:
            barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Barcode|Code|Search",helpText="type your search",data="string")
            if barcode in [None,]:
                return
            item=None
            with Session(ENGINE) as session:
                results=session.query(Entry).filter(or_(
                    Entry.Barcode==barcode,
                    Entry.Code==barcode,
                    Entry.Code.icontains(barcode),
                    Entry.Barcode.icontains(barcode),
                    Entry.Name.icontains(barcode)
                    ))
                results=results.all()
                ct=len(results)
                dummy=False
                if ct <= 0:
                    print("No results")
                    dummy=True
                if not dummy:
                    for num,r in enumerate(results):
                        msg=f"{num}/{num+1}/{ct} - {r.seeShort()}"
                        print(msg)
                    while True:
                        which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which Entry number?",helpText="select the index",data="integer")
                        if which in [None,]:
                            return
                        elif which in ['d',]:
                            item=results[0]
                        else:
                            try:
                                item=results[which]
                                break
                            except Exception as e:
                                print(e)
                if item:
                    l=item.Location
                else:
                    l='///'
                data={
                'QtyForDisplay':{
                    'type':'integer',
                    'default':1,
                },
                'Aisle':{
                    'type':'String',
                    'default':'A!A'
                    },
                'DisplayLocation':{
                    'type':'String',
                    'default':l,
                    }
                }
                data_after=FormBuilder(data=data)
                data_after['DisplayLocation']=l
                today=datetime.now()
                data_after['Date']=date(today.year,today.month,today.day)
                data_after['EndCap']=False
                data_after['ShadowBox']=False
                data_after['Gondolas']=False
                data_after['FreeStandingFSDU']=False
                data_after['DisplayLocationStoreFront']=False
                
                if item != None:
                    data_after['Name']=item.Name
                    data_after['Code']=item.Code
                    data_after['Note']=f"For the Shelf on {data_after['Aisle']}"
                    data_after['EntryId']=item.EntryId
                    self.create_ditem(data_after,"new2Shelf")
                else:
                    print("No Result Found... creating a dummy")
                    data_after['Barcode']=barcode
                    data_after['Name']="New Item Not Found in MiCLI db.Entry Table"
                    data_after['Code']="NI-NF-i-MiCLI"
                    data_after['Note']=f"Placeholder for missing item on the Shelf on {data_after['Aisle']}"
                    data_after['EntryId']=None
                    self.create_ditem(data_after,"new2Shelf")


    def new2Shelf(self):
        while True:
            barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Barcode|Code|Search",helpText="type your search",data="string")
            if barcode in [None,]:
                return
            item=None
            with Session(ENGINE) as session:
                results=session.query(Entry).filter(or_(
                    Entry.Barcode==barcode,
                    Entry.Code==barcode,
                    Entry.Code.icontains(barcode),
                    Entry.Barcode.icontains(barcode),
                    Entry.Name.icontains(barcode)
                    ))
                results=results.all()
                ct=len(results)
                dummy=False
                if ct <= 0:
                    print("No results")
                    dummy=True
                if not dummy:
                    for num,r in enumerate(results):
                        msg=f"{num}/{num+1}/{ct} - {r.seeShort()}"
                        print(msg)
                    while True:
                        which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which Entry number?",helpText="select the index",data="integer")
                        if which in [None,]:
                            return
                        elif which in ['d',]:
                            item=results[0]
                        else:
                            try:
                                item=results[which]
                                break
                            except Exception as e:
                                print(e)
                data={
                'QtyForDisplay':{
                    'type':'integer',
                    'default':1,
                },
                'Aisle':{
                    'type':'String',
                    'default':'A!A'
                    },
                'Shelf Number':{
                    'default':'0',
                    'type':'String'
                    },
                'Shelf Item Number':{
                    'default':'0',
                    'type':'String'
                    },
                }
                data_after=FormBuilder(data=data)
                data_after['DisplayLocation']=f"{data_after['Aisle']}/{data_after['Shelf Number']}/{data_after['Shelf Item Number']}"
                data_after.pop('Shelf Item Number')
                data_after.pop('Shelf Number')
                today=datetime.now()
                data_after['Date']=date(today.year,today.month,today.day)
                data_after['EndCap']=False
                data_after['ShadowBox']=False
                data_after['Gondolas']=False
                data_after['FreeStandingFSDU']=False
                data_after['DisplayLocationStoreFront']=False
                
                if item != None:
                    data_after['Name']=item.Name
                    data_after['Code']=item.Code
                    data_after['Note']=f"For the Shelf on {data_after['Aisle']}"
                    data_after['EntryId']=item.EntryId
                    self.create_ditem(data_after,"new2Shelf")
                else:
                    print("No Result Found... creating a dummy")
                    data_after['Barcode']=barcode
                    data_after['Name']="New Item Not Found in MiCLI db.Entry Table"
                    data_after['Code']="NI-NF-i-MiCLI"
                    data_after['Note']=f"Placeholder for missing item on the Shelf on {data_after['Aisle']}"
                    data_after['EntryId']=None
                    self.create_ditem(data_after,"new2Shelf")

    '''
    -Aisle=Column(String)
    -Date=Column(Date)
    -#display type bools
    -#end of aisle
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
    '''

    def clear_all_displays(self):
        with Session(ENGINE) as session:
            clearemall=session.query(DisplayItem).delete()
            session.commit()
            session.flush()
            check=session.query(DisplayItem).all()
            print(f"{Fore.light_red}{len(check)}{Fore.light_green} DisplayItem's remain!{Style.reset}")

    def clear_DID(self):
        def mkint(text,self):
            try:
                if text in ['',]:
                    return
                else:
                    return int(text)
            except Exception as e:
                print(e)

        did=Prompt.__init2__(None,func=mkint,ptext="DID",helpText="DisplayID (DID)",data=self)
        if did not in [None,]:
            with Session(ENGINE) as session:
                clearemall=session.query(DisplayItem).filter(DisplayItem.DID==did).delete()
                session.commit()
                session.flush()
                check=session.query(DisplayItem).all()
                print(f"{Fore.light_red}{len(check)}{Fore.light_green} DisplayItem's remain!{Style.reset}")

    def list_displays(self):
        with Session(ENGINE) as session: 
            displays=session.query(DisplayItem).all()
            ct=len(displays)
            if ct < 1:
                print(f"{Fore.light_red}No Displays Present!{Style.reset}")
            for num,d in enumerate(displays):
                msg=f"{Fore.light_green}{num+1}/{Fore.light_yellow}{ct} {Fore.orange_red_1} -> {Fore.light_sea_green}{d.Date}@{Fore.dark_goldenrod}{d.Aisle} - {Fore.magenta_3a}DID:{Fore.light_magenta}{d.DID}{Style.reset}"
                print(msg)

    def showAllDisplays(self):
        with Session(ENGINE) as session: 
            displays=session.query(DisplayItem).group_by(DisplayItem.Aisle,DisplayItem.Date,DisplayItem.DisplayLocation)

            displays=displays.all()
            ct=len(displays)
            if ct < 1:
                print(f"{Fore.light_red}No Displays Present!{Style.reset}")
            for num,d in enumerate(displays):
                msg=f"{Fore.light_green}{num+1}/{Fore.light_yellow}{ct} {Fore.orange_red_1} -> {d}{Style.reset}"
                print(msg)

    def laad(self):
        with Session(ENGINE) as session: 
            displays=session.query(DisplayItem).group_by(DisplayItem.Aisle,DisplayItem.Date,DisplayItem.DisplayLocation)

            displays=displays.all()
            ct=len(displays)
            if ct < 1:
                print(f"{Fore.light_red}No Displays Present!{Style.reset}")
            items=[]
            for num,d in enumerate(displays):
                i=f"{d.Date}@{d.Aisle}"
                if i not in items:
                    items.append(i)

            header=f"{Fore.light_green}Total Displayed/{Fore.light_yellow}Total DID's {Fore.orange_red_1} -> Display.Date@Display.Aisle{Style.reset}"
            print(header)
            for num,d in enumerate(items):
                msg=f"{Fore.light_green}{num+1}/{Fore.light_yellow}{ct} {Fore.orange_red_1} -> {d}{Style.reset}"
                print(msg)
    
    def lookup(self):
        while True:
            barcode=Prompt.__init2__(None,func=self.mkText,ptext="Code|Barcode|Name|Note: ",helpText="What are you looking for? [Code,Barode,Name,Note]")
            if barcode in [None,]:
                return
            if barcode.endswith(".DID"):
                DID=None
                try:
                    DID=int(eval(barcode.replace(".DID","")))
                except Exception as e:
                    DID=None
                try:
                    DID=int(barcode.replace(".DID",""))
                except Exception as e:
                    DID=None
            print(DID)
            with Session(ENGINE) as session:
                query=session.query(DisplayItem).filter(or_(DisplayItem.Code.icontains(barcode),DisplayItem.Barcode.icontains(barcode),DisplayItem.Name.icontains(barcode),DisplayItem.Note.icontains(barcode),DisplayItem.DID==DID))
                query=query.group_by(DisplayItem.Aisle,DisplayItem.Date,DisplayItem.DisplayLocation)
                displays=query.all()
                ct=len(displays)
                if ct < 1:
                    print(f"{Fore.light_red}No Displays Present{Style.reset}")
                    return
                headers=f"\n{Fore.light_green}DisplayItem No./{Fore.light_yellow} Total Display Items {Fore.orange_red_1} -> Code|{Fore.cyan}Barcode|{Fore.light_steel_blue}Name|{Fore.medium_purple_3b}DisplayLocation|{Fore.light_sea_green}Note|{Fore.green_yellow}Date{Style.reset}\n"
                print(headers)
                for num,d in enumerate(displays):
                    if d.Note in [None,]:
                        setattr(d,'Note','')
                        session.commit()
                        session.refresh(d)
                    short_display=f'''{d.Code}|{Fore.cyan}{d.Barcode}|{Fore.light_steel_blue}{d.Name}|{Fore.medium_purple_3b}{d.DisplayLocation}|{Fore.light_sea_green}{d.Note}|{Fore.green_yellow}{d.Date}'''
                    msg=f"{Fore.light_green}{num+1}/{Fore.light_yellow}{ct} {Fore.orange_red_1} -> {short_display}{Style.reset}"
                    print(msg)
                print(headers)


   
    def showDisplayShort(self):
        today=Prompt.__init2__(self,func=FormBuilderMkText,ptext="Date To Use",helpText="its required!",data="datetime")
        if not isinstance(today,datetime):
            print("Need Date!")
            return
        D=date(today.year,today.month,today.day)
        if not D:
            print("Need Date!")
            return
        aisle=None
        aisle_dict=self.mkNewDisp(data={'Aisle':None})
        if aisle_dict:
            aisle=aisle_dict.get("Aisle")
        if not aisle:
            print(f"{Fore.light_red}Aisle was not Specified using '' for aisle{Style.reset}")
            aisle=''
        with Session(ENGINE) as session:
            query=session.query(DisplayItem).filter(DisplayItem.Date==D,DisplayItem.Aisle==aisle)
            displays=query.all()
            ct=len(displays)
            headers=f"\n{Fore.light_green}DisplayItem No./{Fore.light_yellow} Total Display Items {Fore.orange_red_1} -> Code|{Fore.cyan}Barcode|{Fore.light_steel_blue}Name|{Fore.medium_purple_3b}DisplayLocation|{Fore.light_sea_green}Note{Style.reset}\n"
            print(headers)
            for num,d in enumerate(displays):
                if d.Note in [None,]:
                    setattr(d,'Note','')
                    session.commit()
                    session.refresh(d)
                short_display=f'''{d.Code}|{Fore.cyan}{d.Barcode}|{Fore.light_steel_blue}{d.Name}|{Fore.medium_purple_3b}{d.DisplayLocation}|{Fore.light_sea_green}{d.Note}'''
                msg=f"{Fore.light_green}{num+1}/{Fore.light_yellow}{ct} {Fore.orange_red_1} -> {short_display}{Style.reset}"
                print(msg)
            print(headers)


    def showDisplay(self):
        D=DatePkr()
        if not D:
            print("Need Date!")
            return
        aisle=None
        aisle_dict=self.mkNewDisp(data={'Aisle':None})
        if aisle_dict:
            aisle=aisle_dict.get("Aisle")
        if not aisle:
            print(f"{Fore.light_red}Aisle was not Specified using '' for aisle{Style.reset}")
            aisle=''
        with Session(ENGINE) as session:
            query=session.query(DisplayItem).filter(DisplayItem.Date==D,DisplayItem.Aisle==aisle)
            displays=query.all()
            ct=len(displays)
            for num,d in enumerate(displays):
                msg=f"{Fore.light_green}{num+1}/{Fore.light_yellow}{ct} {Fore.orange_red_1} -> {d}{Style.reset}"
                print(msg)

    def clear_display(self):
        D=DatePkr()
        if not D:
            print("Need Date!")
            return
        aisle=None
        aisle_dict=self.mkNewDisp(data={'Aisle':None})
        if aisle_dict:
            aisle=aisle_dict.get("Aisle")
        if not aisle:
            print(f"{Fore.light_red}Aisle was not Specified using '' for aisle{Style.reset}")
            aisle=''
        with Session(ENGINE) as session:
            query=session.query(DisplayItem).filter(DisplayItem.Date==D,DisplayItem.Aisle==aisle)
            cla=query.delete()
            session.commit()
            session.flush()
            check=query.all()
            print(f"{Fore.light_red}{len(check)}{Fore.light_green} DisplayItem's remain!{Style.reset}")

    #use groupby fields Aisle,Date to get displays grouped by Aisle,Date for 1 Total display for Date
    def NewDisplay(self):
        while True:
            with Session(ENGINE) as session:
                data=self.mkNewDisp(data=copy(DEFAULT_NEWLOCATIONS))
                if not data:
                    print("Not Enought data to continue")
                    return
                shelfItemNoCounter=1
                while True:
                    data_tmp=dict(copy(data))
                    barcode=Prompt.__init2__(None,self.mkText,ptext="barcode",helpText="product for display",data=self)
                    if barcode == '':
                        print(f"{Fore.light_steel_blue}Barcode Must Not be {Fore.light_yellow}''{Style.reset}")
                        continue
                    if barcode in [None,]:
                        return
                    #data_pertinent=self.mkNewDisp(data=DEFAULT_NEW2)
                    CHECK=session.query(Entry).filter(or_(Entry.Barcode==barcode,Entry.Code==barcode)).all()
                    ct=len(CHECK)
                    for num,entry in enumerate(CHECK):
                        print(f"{num+1}/{ct} -> {entry}")
                    if ct > 0:
                        def selectInt(text,self):
                            try:
                                if text in ['',]:
                                    return False
                                else:
                                    return int(eval(text))
                            except Exception as e:
                                print(e)
                                return False
                        continueYes=False
                        while True:
                            select=Prompt.__init2__(self,func=selectInt,ptext="which Entry number?",helpText=f"the {Fore.green}green{Fore.light_yellow} number before the slash")
                            if isinstance(select,int):
                                if ct == 1:
                                    selected=0
                                    break
                                elif select in list(range(0,ct-1)):
                                    selected=select
                                    break
                                else:
                                    print("You need to specify one of the green numbers before the slash")
                            else:
                                continueYes=True
                                break
                        if continueYes:
                            continue
                        data_tmp['EntryId']=CHECK[select].EntryId
                        data_tmp['Barcode']=CHECK[select].Barcode
                        data_tmp['Code']=CHECK[select].Code
                        data_tmp['Name']=CHECK[select].Name

                        print(f"{Fore.light_red}Use '{Fore.orange_red_1}n|i{Style.reset}{Fore.light_red}' to increment the Next 2 Fields{Style.reset}")
                        data_tmp2=self.mkNewDisp(ignore_fields=True,data={'Shelf Number':1,'Shelf Item Number':shelfItemNoCounter})

                        if data_tmp2 != None:
                            if data_tmp2['Shelf Number'] in ['',]:
                               data_tmp2['Shelf Number']=1
                            if data_tmp2['Shelf Item Number'] in ['',]:
                               data_tmp2['Shelf Item Number']=1
                                
                            location=f"{data['Aisle']}/{data_tmp2['Shelf Number']}/{data_tmp2['Shelf Item Number']}"
                            data_tmp['DisplayLocation']=location
                        else:
                            print("Location Creation Failed!")
                            return
                        qfd=self.mkNewDisp(data={'QtyForDisplay':1,'Note':''})
                        #print(type(data),type(data_tmp))
                        if qfd:
                            data_tmp['QtyForDisplay']=qfd['QtyForDisplay']
                            for k in data_tmp:
                                data[k]=data_tmp[k]
                        self.create_ditem(data,f"{Fore.light_sea_green}From DB{Style.reset}")
                        shelfItemNoCounter+=1
                    else:
                        self.setFieldInList('BackRoom',barcode=barcode,repack_exec=lambda entry,self=self,session=session,data=data:self.repackExec(entry,data=data))

    def create_ditem(self,data,msg):
        with Session(ENGINE) as session:
            di=DisplayItem(**data)
            session.add(di)
            session.commit()
            session.flush()
            session.refresh(di)
            print(di)

    def repackExec(self,entry,data):
        data_tmp=dict(copy(data))
        data_tmp['EntryId']=entry.EntryId
        with Session(self.engine) as e:
            e.commit()
            CHECK=e.query(Entry).filter(Entry.EntryId==entry.EntryId)
            CHECK=CHECK.first()
            if CHECK:
                data_tmp['Barcode']=CHECK.Barcode
                data_tmp['Code']=CHECK.Code
                data_tmp['Name']=CHECK.Name

                data_tmp2=self.mkNewDisp(ignore_fields=True,data={'Shelf Number':1,'Shelf Item Number':1})

                if data_tmp2 != None:        
                    if data_tmp2['Shelf Number'] in ['',]:
                       data_tmp2['Shelf Number']=1
                    if data_tmp2['Shelf Item Number'] in ['',]:
                       data_tmp2['Shelf Item Number']=1
                    location=f"{data['Aisle']}/{data_tmp2['Shelf Number']}/{data_tmp2['Shelf Item Number']}"
                    data_tmp['DisplayLocation']=location
                else:
                    print("Location Creation Failed!")
                    return
                qfd=self.mkNewDisp(data={'QtyForDisplay':1,'Note':''})
                #print(type(data),type(data_tmp))
                if qfd:
                    data_tmp['QtyForDisplay']=qfd['QtyForDisplay']
                    for k in data_tmp:
                        data[k]=data_tmp[k]
                data['EntryId']=CHECK.EntryId
                self.create_ditem(data,f"{Fore.light_sea_green}From DB{Style.reset}")

    def __init__(self,engine,parent):
        while True:
            self.engine=engine
            self.parent=parent
            self.special=['Tags','ALT_Barcode','DUP_Barcode','CaseID_6W','CaseID_BR','CaseID_LD','Facings']
            self.valid_fields=['Shelf',
            'BackRoom',
            'Display_1',
            'Display_2',
            'Display_3',
            'Display_4',
            'Display_5',
            'Display_6',
            'ALT_Barcode',
            'DUP_Barcode',
            'CaseID_BR',
            'CaseID_LD',
            'CaseID_6W',
            'Tags',
            'Facings',
            'SBX_WTR_DSPLY',
            'SBX_CHP_DSPLY',
            'SBX_WTR_KLR',
            'FLRL_CHP_DSPLY',
            'FLRL_WTR_DSPLY',
            'WD_DSPLY',
            'CHKSTND_SPLY',
            ]
            '''
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
            '''
            #self.display_field("Shelf")
            self.options={
                    '1':{
                        'cmds':['q','quit','#1'],
                        'desc':"quit program",
                        'exec':lambda: exit("user quit!"),
                        },
                    '2':{
                        'cmds':['b','back','#2'],
                        'desc':'go back menu if any',
                        'exec':None
                        },
                    }
            #autogenerate duplicate functionality for all valid fields for display
            count=3
            location_fields={
                "Shelf":None,
                "BackRoom":None,
                "Display_1":None,
                "Display_2":None,
                "Display_3":None,
                "Display_4":None,
                "Display_5":None,
                "Display_6":None,
                "ListQty":None,
                "SBX_WTR_DSPLY":None,
                "SBX_CHP_DSPLY":None,
                "SBX_WTR_KLR":None,
                "FLRL_CHP_DSPLY":None,
                "FLRL_WTR_DSPLY":None,
                "WD_DSPLY":None,
                "CHKSTND_SPLY":None,

                "set Shelf":None,
                "set BackRoom":None,
                "set Display_1":None,
                "set Display_2":None,
                "set Display_3":None,
                "set Display_4":None,
                "set Display_5":None,
                "set Display_6":None,
                "set ListQty":None,
                "set ListQty":None,
                "set SBX_WTR_DSPLY":None,
                "set SBX_CHP_DSPLY":None,
                "set SBX_WTR_KLR":None,
                "set FLRL_CHP_DSPLY":None,
                "set FLRL_WTR_DSPLY":None,
                "set WD_DSPLY":None,
                "set CHKSTND_SPLY":None,
            }
            try:
                self.helpText=f'''
{Fore.orange_red_1}CMD {Fore.light_salmon_3a}ACTION{Style.reset}
{'-'*30}
{Fore.light_magenta}new|n{Style.reset} {Fore.light_steel_blue}New Display and add Items to Display{Style.reset}
{Fore.light_magenta}list|l{Style.reset} {Fore.light_steel_blue}list displays{Style.reset} 
{Fore.light_magenta}search|s|lu|lookup{Style.reset} {Fore.light_steel_blue}search displays for product info.{Style.reset} 
{Fore.light_magenta}list all aisle date|list_all_aisle_date|laad{Style.reset} {Fore.light_steel_blue}list all display aisle and date, consolidated{Style.reset} 
{Fore.light_magenta}clear display|clear_display|cd{Style.reset} {Fore.light_steel_blue}clear displayItem by Aisle and Location{Style.reset}
{Fore.light_magenta}del id|del_id|delid{Style.reset} {Fore.light_steel_blue}delete DisplayItem by DID{Style.reset}
{Fore.light_magenta}clear all|clear_all|clral{Style.reset} {Fore.light_steel_blue}Delete All DisplayItems{Style.reset}
{Fore.light_magenta}show display|show_display|sd{Style.reset} {Fore.light_steel_blue}show display content by Aisle and Location{Style.reset}
{Fore.light_magenta}show all|show_all|sa{Style.reset} {Fore.light_steel_blue}show all display content, grouped by aisle,date,location{Style.reset}
{Fore.light_magenta}show display short|show_display_short|sds{Fore.light_steel_blue} show short version of 'Show Display'{Style.reset}
{Fore.orange_red_1}Aisle{Fore.green_yellow} Number may be any definable string, even '', but some standards should be set{Style.reset}
{Fore.grey_70}A Single Aisle is 1- to 2-digit, so aisle 1 == 1, Aisle 10 == 10, etc
Defining An Aisle (OR {Fore.light_steel_blue}Shelf Number [{Fore.light_blue}if the same product occupies multiple contiguous shelves{Fore.light_steel_blue}]{Fore.grey_70}) for an EndCap can be of the following: 
For An EndCap Residing at the Front of the Store on Aisle's 1 
and 2, the aisle would be spec'ed as:
 #1 {Fore.orange_4b}1-{Fore.green}2,{Fore.orange_4b}01-{Fore.green}02{Fore.grey_70} - takes longer to type but doable
 #2 {Fore.orange_4b}01{Fore.green}02    {Fore.grey_70}  - if this format, zfill to the largest aisle integer, 2-digit aisle
 #3 {Fore.orange_4b}NO Aisle No. {Fore.grey_70} - a string that might represent the display's location:{Fore.sky_blue_2}
            STB_WTR_DSPLY
            CHCK_STD_SPLY
            FLRL_WTR_DSPLY
            etc...
   
    {Fore.orange_red_1}n2s,new2Shelf{Fore.light_steel_blue} create a new schematic record for display asking for aisle each time{Style.reset}
    {Fore.orange_red_1}n2sb,new2ShelfBatch{Fore.light_steel_blue} create a new schematic record for display asking for aisle once{Style.reset}
    {Fore.orange_red_1}n2sbn+,new2ShelfBatchNumber+{Fore.light_steel_blue} create a new schematic record for display asking for aisle once,using auto-incrementing integers from 0{Style.reset}
    {Fore.orange_red_1}show display short 2,show_display_short_2,sds2{Fore.light_steel_blue} display selected display schematic{Style.reset}
    {Fore.orange_red_1}'n2s sl','new2shelf sys loc'{Fore.light_steel_blue} create new display item using Entry.Location for DisplayItem.DisplayLocation{Style.reset}
    {Fore.orange_red_1}'n2sb sl','new2shelfBatch sys loc{Fore.light_steel_blue} batch create new display item using Entry.Location for DisplayItem.DisplayLocation{Style.reset}
    {Fore.light_sea_green}
    Make It Cell-Phone Typeable, As-Short-As-Possible, ASAP{Style.reset}
{'-'*30}'''
                fieldname='Menu'
                mode='Displays'
                h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                doWhat=Prompt.__init2__(None,func=self.mkText,ptext=f"{h}Do What?",helpText=self.helpText,data=self)
                if doWhat in [None,]:
                    return
                elif doWhat.lower() in ['new',"n",]:
                    self.NewDisplay()
                elif doWhat.lower() in ['list','l']:
                    self.list_displays()
                elif doWhat.lower() in ['list all aisle date','list_all_aisle_date','laad']:
                    self.laad()
                elif doWhat.lower() in ['clear display',"clear_display",'cd']:
                    self.clear_display()
                elif doWhat.lower() in ['del id',"del_id",'delid']:
                    self.clear_DID()
                elif doWhat.lower() in ['clear all',"clear_all",'clral']:
                    self.clear_all_displays()
                elif doWhat.lower() in ['show display',"show_display",'sd']:
                    self.showDisplay()
                elif doWhat.lower() in ['show all',"show_all",'sa']:
                    self.showAllDisplays()
                elif doWhat.lower() in ['show display short','show_display_short','sds']:
                    self.showDisplayShort()
                elif doWhat.lower() in ['show display short 2','show_display_short_2','sds2']:
                    self.SDS2()
                elif doWhat.lower() in ['search','s','lu','lookup']:
                    self.lookup()
                elif doWhat.lower() in ['n2s','new2shelf']:
                    self.new2Shelf()
                elif doWhat.lower() in ['n2sb','new2shelfBatch']:
                    self.new2ShelfBatch()
                elif doWhat.lower() in ['n2sbn+','new2shelfBatchNumber+']:
                    self.new2ShelfBatchNumeric_Plus()
                elif doWhat.lower() in ['n2sb sl','new2shelfBatch sys loc']:
                    self.new2ShelfBatch_sys_loc()
                elif doWhat.lower() in ['n2s sl','new2shelf sys loc']:
                    self.new2Shelf_sys_loc()
            except Exception as e:
                print(e)