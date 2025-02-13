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
from radboy.ExtractPkg.ExtractPkg2 import *
from radboy.Lookup.Lookup import *
from radboy.DayLog.DayLogger import *
from radboy.DB.db import *
from radboy.ConvertCode.ConvertCode import *
from radboy.setCode.setCode import *
from radboy.Locator.Locator import *
from radboy.ListMode2.ListMode2 import *
from radboy.TasksMode.Tasks import *
from radboy.ExportList.ExportListCurrent import *
from radboy.FB.FBMTXT import *
from radboy.DB.Prompt import *


import radboy.possibleCode as pc

class TouchStampC:
    def search(self):
        def mkT(text,self):
            try:
                if len(text.split(".")) == 2:
                    prefix,code=text.split(".")
                elif len(text.split(".")) == 1:
                    code=text.split(".")[0]
                    prefix=''
                else:
                    raise Exception("Correct # of args is 2 or 1 by split off of '.'")
                return prefix,code
            except Exception as e:
                print(e)
                return

        value=Prompt.__init2__(None,func=mkT,ptext="Code|Barcode: ",helpText=self.helpTxt,data=self)
        if not value:
            return
        else:
            prefix,code=value
            with Session(self.engine) as session:
                query=session.query(Entry)
                if prefix.lower() == '':
                    query=query.filter(or_(Entry.Barcode==code,Entry.Code==code,Entry.Barcode.icontains(code),Entry.Code.icontains(code)))
                elif prefix.lower() == 'c':
                    query=query.filter(or_(Entry.Code==code,Entry.Code.icontains(code)))
                elif prefix.lower() == 'b':
                    query=query.filter(or_(Entry.Barcode==code,Entry.Barcode.icontains(code)))
                elif prefix.lower() == 'e':
                    query=query.filter(Entry.EntryId==int(code))
                results=query.all()
                if len(results) < 1:
                    query=session.query(TouchStamp).filter(TouchStamp.EntryId==code)
                    results=query.all()
                    ct=len(results)
                    if len(results) > 0:
                        for num,r in enumerate(results):
                            print(f"{Fore.green}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} -> {r}")
                    else:
                        print("No Results!")
                else:
                    ct=len(results)
                    if len(results) > 0:
                        msg=f"{Fore.light_green}Num{Style.reset}/{Fore.light_red}Total{Style.reset} -> {Fore.dark_goldenrod}Name - Barcode - Code - r.Size - Location - Price - r.EntryId{Style.reset}"
                        print(msg)
                        for num,r in enumerate(results):
                            extra=f'{r.Name} - {r.Barcode} - {r.Code} - {r.Size} - {r.Location} - {r.Price} - {r.EntryId}'
                            if num % 2 == 0:
                                extra=f'{Fore.grey_70}{extra}{Style.reset}'
                            
                            print(f"{Fore.green}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} -> {extra}")
                        
                        def mInt(text,self):
                            if text != '':
                                return int(text)
                            return 0
                        print(msg)
                        whichResult=Prompt.__init2__(None,func=mInt,ptext=f"Which result to use(0-{len(results)-1})[0]?",helpText=self.helpTxt,data=self)
                        print(whichResult)
                        if isinstance(whichResult,int):
                            e=results[whichResult]
                            eid=e.EntryId

                            rs=session.query(TouchStamp).filter(TouchStamp.EntryId==eid).all()
                            rs_ct=len(rs)
                            for num,r in enumerate(rs):
                                print(f"{Fore.green}{num}{Style.reset}/{Fore.light_red}{rs_ct}{Style.reset} -> {r}")
                            print(f"{Fore.light_yellow}There are {Style.reset}{Fore.red}{rs_ct}{Style.reset} TouchStamp Results!")
                        else:
                            print("Please Enter a valid number!")
                    else:
                        print("No Results!")
            
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


    def search_note(self):
        with Session(ENGINE) as session:
            search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What are looking for in Note || as TouchStampId?",helpText="search term",data="string")
            if search in ['d',None]:
                return
            try:
                tcid=int(search)
                results=session.query(TouchStamp).filter(or_(TouchStamp.Note.icontains(search),TouchStamp.TouchStampId==tcid,TouchStamp.EntryId==tcid)).all()
            except Exception as e:
                print(e)
                results=session.query(TouchStamp).filter(TouchStamp.Note.icontains(search)).all()
            ct=len(results)
            if ct == 0:
                print("No Results")
            for num,i in enumerate(results):
                if num%2==0:
                    color=Fore.light_green
                else:
                    color=Fore.light_cyan
                msg=f'{num}/{num+1} of {ct} - Note:\n{i.Note}\nTimestamp:\n{i.Timestamp}\nTouchStampId:\n{i.TouchStampId}\nEntryId:\n{i.EntryId}\n'
                print(f'{color}{msg}{Style.reset}')
                outfile=detectGetOrSet("TouchStampSearchExport",value="TS_NOTE.txt",literal=True)

                saveToFile=Prompt.__init2__(self,func=FormBuilderMkText,ptext="save to file",helpText="yes or no",data="boolean")
                if saveToFile in [None,False,'d']:
                    if not self.next_barcode():
                        continue
                    else:
                        return
                else:
                    with open(outfile,"w") as out:
                        out.write(msg)

    def work_note(self):
        with Session(ENGINE) as session:
            while True:
                excludes=['EntryId','TouchStampId','Timestamp','geojson']
                data={str(i.name):{'default':f'New {i.name} for {datetime.now()}','type':str(i.type)} for i in TouchStamp.__table__.columns if str(i.name) not in excludes}                
                data['Note']['type']='str+'
                fd=FormBuilder(data=data)
                if not fd:
                    print("User Cancelled")
                    if self.next_barcode():
                        continue
                    else:
                        return
                #fd['Timestamp']=datetime.now()
                fd['EntryId']=None
                related_info=[]
                print(f"{Fore.light_red}{Back.grey_70}You CANNOT Go Back now!{Style.reset}")
                print(f"{Fore.light_green}Processing Note for Barcodes/Codes...{Style.reset}")
                tmp=[]
                process=fd['Note'].split(' ')
                fd['Note']=f'''Note Text:\n{fd['Note']}'''
                for i in process:
                    if i.lower() not in tmp:
                        tmp.append(i.lower())
                process=tmp
                for xnum,i in enumerate(process):
                    results=session.query(Entry).filter(or_(Entry.Barcode==i,Entry.Code==i,Entry.Barcode.icontains(i),Entry.Code.icontains(i))).all()
                    ct=len(results)
                    if ct > 0:
                        print(f"There are {ct} Entry Results for - {Fore.light_magenta}{i}{Style.reset}")
                        htext=[]
                        for num,ii in enumerate(results):
                            msg=f"{num}/{num+1} of {ct} -> {ii.seeShort()}"
                            htext.append(msg)
                        htext='\n'.join(htext)
                        print(htext)
                        print(f"There are {ct} Entry Results for - {Fore.light_magenta}{i}/{Fore.dark_goldenrod}{xnum}[Index]/{Fore.cyan}[Count]{xnum+1}{Fore.medium_violet_red} out of {len(process)}[Total] space-deliminated words searched in {Style.bold}{Fore.orange_red_1}Entry.Barcode|Entry.Code{Style.reset}")
                        selected=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Select all that apply, separating with a comma[s=skp=skip]:",helpText=htext,data="list")
                        if selected in [None,]:
                            if self.next_barcode():
                                continue
                            else:
                                return
                        elif selected in ['d',]:
                            selected=None
                        else:
                            skip=False
                            for i in selected:
                                if i.lower() in ['skip','skp','s']:
                                    skip=True
                                    break
                            if skip:
                                break
                            try:
                                for select in selected:
                                    try:
                                        select=int(select)
                                        related_text=''
                                        excludes=['EntryId',]
                                        fields=[i.name for i in Entry.__table__.columns if str(i.name) not in excludes]
                                        for field in fields:
                                            related_text+=f"\t-\t{field} = {getattr(results[select],str(field))}\n"
                                        header=f'{results[select].Barcode} - START - Word({i})\n'
                                        footer=f'{results[select].Barcode} - END - Word({i})\n'
                                        finalText=header+related_text+footer
                                        print(finalText)
                                        if finalText not in related_info:
                                            related_info.append(finalText)
                                    except Exception as e:
                                        print(e)
                            except Exception as e:
                                print(e)
                print(f"{Fore.light_red}{Back.grey_70}You CANNOT Go Back now!{Style.reset}")
                print(f"{Fore.light_green}Processing Note for People in Roster...{Style.reset}")
                for i in process:
                    results=session.query(Roster).filter(or_(Roster.FirstName.icontains(i),Roster.LastName.icontains(i))).all()
                    ct=len(results)
                    if ct > 0:
                        print(f"There are {ct} Roster Results for - {Fore.light_magenta}{i}{Style.reset}")
                        htext=[]
                        for num,ii in enumerate(results):
                            try:
                                msg=f"{num}/{num+1} of {ct} -> {ii.LastName},{ii.FirstName}"
                                htext.append(msg)
                            except Exception as e:
                                print(e,repr(e))
                        htext='\n'.join(htext)
                        print(htext)
                        print(f"There are {ct} Roster Results for - {Fore.light_magenta}{i}/{Fore.dark_goldenrod}{xnum}[Index]/{Fore.cyan}[Count]{xnum+1}{Fore.medium_violet_red} out of {len(process)}[Total] space-deliminated words searched in {Style.bold}{Fore.orange_red_1}Roster{Style.reset}")
                        selected=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Select all that apply, separating with a comma[s=skp=skip]:",helpText=htext,data="list")
                        if selected in [None,]:
                            if self.next_barcode():
                                continue
                            else:
                                return
                        elif selected in ['d',]:
                            selected=None
                        else:
                            skip=False
                            for i in selected:
                                if i.lower() in ['skip','skp','s']:
                                    skip=True
                                    break
                            if skip:
                                break
                            try:
                                for select in selected:
                                    try:
                                        select=int(select)
                                        related_text=''
                                        excludes=['RoId',]
                                        fields=[str(i.name) for i in Roster.__table__.columns if str(i.name) not in excludes]
                                        for field in fields:
                                            related_text+=f"\t-\t{field} = {getattr(results[select],str(field))}\n"
                                        header=f'{results[select].LastName},{results[select].FirstName} - START\n'
                                        footer=f'{results[select].LastName},{results[select].FirstName} - END\n'
                                        finalText=header+related_text+footer
                                        if finalText not in related_info:
                                            related_info.append(finalText)
                                    except Exception as e:
                                        print(e)
                            except Exception as e:
                                print(e)
                print(f"{Fore.light_red}{Back.grey_70}You CANNOT Go Back now!{Style.reset}")
                while True:
                    try:
                        when=Prompt.__init2__(None,func=FormBuilderMkText,ptext="When did this happen?",helpText="when did this happen?",data="datetime")
                        if when in [None,]:
                            if self.next_barcode():
                                continue
                            else:
                                return
                        elif when in ['d',]:
                            msg=f"\nTime of Occurance: {datetime.now()}\n"
                            related_info.append(msg)
                        else:
                            try:
                                msg=f"\nTime of Occurance: {when.ctime()}\n"
                            except Exception as e:
                                f"\n{when}\n"
                            related_info.append(msg)
                        break
                    except Exception as e:
                        print(e)
                        break

                print(f"{Fore.light_red}{Back.grey_70}You CANNOT Go Back now!{Style.reset}")
                while True:
                    try:
                        where=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Where did this happen?",helpText="where did this happen?",data="string")
                        if where in [None,]:
                            if self.next_barcode():
                                continue
                            else:
                                return
                        elif where in ['d',]:
                            msg=f"\nLocation of Occurance: {'UNKNOWN'}\n"
                            related_info.append(msg)
                        else:
                            msg=f"\nLocation of Occurance: {where}\n"
                            related_info.append(msg)
                        break
                    except Exception as e:
                        print(e)
                        break


                fd['Note']+='\n'+'\n'.join(related_info)
                try:
                    tc=TouchStamp(**fd)
                except Exception as e:
                    print(e,str(e),repr(e))
                session.add(tc)
                session.commit()
                session.refresh(tc)
                msg=f'''
{tc.Note}
{tc.Timestamp}
                '''
                print(msg)






    def __init__(self,engine,parent):
        try:
            self.engine=engine
            self.parent=parent
            #print("TouchStamp Locator for Fast Note Logging!")
            self.helpTxt=f"""TouchStamp Locator for Fast Note Logging!
{Fore.cyan}+ | +,Note,Barcode|Code {Style.reset}-{Fore.grey_70} create a new touchstamp entry, '+' on its own will{Style.reset}
                        {Fore.cyan}{Style.reset} {Fore.grey_70} prompt for details; otherwise use details as describe{Style.reset}
{Fore.cyan}s | s,Note,Barcode|Code {Style.reset}-{Fore.grey_70} synthesize barcode for a new touchstamp entry, 's' on its own will{Style.reset}
                        {Fore.cyan}{Style.reset} {Fore.grey_70} prompt for details; otherwise use details as describe
{Fore.cyan}e | e,Note,TouchStampId {Style.reset}-{Fore.grey_70} edit a touchstamp entry, 'e' on its own will{Style.reset}
                        {Fore.cyan}{Style.reset} {Fore.grey_70} prompt for details; otherwise use details as describe
{Fore.cyan}- | -,TouchStampId      {Style.reset}-{Fore.grey_70} remove an entry by prompt ('-' on its own), or by TouchStampId{Style.reset}
{Fore.cyan}l                       {Style.reset}-{Fore.grey_70} list all{Style.reset}
{Fore.cyan}l,$TouchStampId         {Style.reset}-{Fore.grey_70} list touch stamp id{Style.reset}
{Fore.cyan}l,Note|TouchStampId,$searchable {Style.reset}-{Fore.grey_70} search for in fields{Style.reset}
{Fore.cyan}q|quit {Style.reset}-{Fore.grey_70} quit program{Style.reset}
{Fore.cyan}b|back {Style.reset}-{Fore.grey_70} go back a menu{Style.reset}
{Fore.light_magenta}#code is:
W/ PREFIX:
    b.$code - #code is Entry.Barcode
    c.$code - #code is Entry.Code
    e.$code - #code is Entry.EntryId
W/O PREFIX:
    $code - #code is either Entry.Barcode or Entry.Code
{Style.reset}
{Fore.light_yellow}sc|search_code{Style.reset}-{Fore.grey_70}Search using #code{Style.reset}
{Fore.orange_red_1}'work note','wn','note','n','worknote','work_note','wn'{Fore.grey_70}- {Fore.light_green}Create a work note that collects data from Roster and Entry for related data, but does not utilize EntryId, Everything is stored in the TouchStamp.Note{Style.reset}
{Fore.orange_red_1}'scn','searchnote','search note','sch nt','schnt'{Fore.grey_70}- {Fore.light_green}search note text; prompts to save Note to {detectGetOrSet("TouchStampSearchExport",value="TS_NOTE.txt",literal=True)}{Style.reset}
            """
            while True:
                def mkT(text,self):
                    return text
                mode='TouchStamp/Notes'
                fieldname='TaskMode'
                h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                cmd=Prompt.__init2__(None,func=mkT,ptext=f"{h}Do What?",helpText=self.helpTxt,data=self)
                if not cmd:
                    return
                if cmd.lower() in ['sc','search_code']:
                    self.search()
                elif cmd.lower() in ['work note','wn','note','n','worknote','work_note','w']:
                    self.work_note()
                elif cmd.lower() in ['scn','searchnote','search note','sch nt','schnt']:
                    self.search_note()
                elif cmd.split(",")[0].lower() in ['+','a']:
                    cmdline=cmd.split(",")
                    ct=len(cmdline)

                    if ct > 1 and ct == 3:
                        barcode=None
                        with Session(self.engine) as session:
                            bcd=session.query(Entry).filter(or_(Entry.Barcode==cmdline[2],Entry.Code==cmdline[2])).first()
                            print(bcd)
                            if bcd:
                                ts=TouchStamp(Note=cmdline[1],EntryId=bcd.EntryId)
                            else:
                                ts=TouchStamp(Note=cmdline[1],EntryId=None)
                            session.add(ts)
                            session.commit()
                            session.refresh(ts)
                            print(ts)
                    else:
                        while True:
                            try:
                                def mkT(text,self):
                                    return text
                                
                                code=Prompt.__init2__(self,func=mkT,ptext='Barcode|Code',helpText="Please enter the code you will be using!",data=self)
                                print(code)
                                if code in [None,]:
                                    break

                                note=Prompt.__init2__(self,func=mkT,ptext='Note',helpText="Please enter the note you will be writing!",data=self)

                                if note in [None,]:
                                    break
                                
                                with Session(self.engine) as session:
                                    bcd=session.query(Entry).filter(or_(Entry.Barcode==code,Entry.Code==code)).first()
                                    print(bcd)

                                    if bcd:
                                        ts=TouchStamp(Note=note,EntryId=bcd.EntryId)
                                    else:
                                        ts=TouchStamp(Note=note,EntryId=None)
                                    session.add(ts)
                                    session.commit()
                                    session.refresh(ts)
                                    print(ts)
                                    break
                            except Exception as e:
                                print(e)
                elif cmd.split(",")[0].lower() in ['s']:
                    cmdline=cmd.split(",")
                    ct=len(cmdline)

                    if ct > 1 and ct == 2:
                        barcode=None
                        with Session(self.engine) as session:
                            ts=TouchStamp(Note=cmdline[1],EntryId=Entry.synthetic_field_str(None))
                            session.add(ts)
                            session.commit()
                            session.refresh(ts)
                            print(ts)
                    else:
                        while True:
                            try:
                                def mkT(text,self):
                                    return text
                                note=Prompt.__init2__(self,func=mkT,ptext="Note",helpText="The note you need to record!")
                                if note in [None,]:
                                    break
                                with Session(self.engine) as session:
                                    ts=TouchStamp(Note=note,EntryId=Entry.synthetic_field_str(None))
                                    session.add(ts)
                                    session.commit()
                                    session.refresh(ts)
                                    print(ts)
                                break
                            except Exception as e:
                                print(e)
                elif cmd.split(",")[0].lower() in ['-']:
                    cmdline=cmd.split(",")
                    ct=len(cmdline)

                    if ct > 1 and ct == 2:
                        barcode=None
                        with Session(self.engine) as session:
                            r=session.query(TouchStamp).filter(TouchStamp.TouchStampId==int(cmdline[1])).delete()
                            session.commit()
                            print(f"deleted {r}")
                    else:
                        while True:
                            try:
                                def mkT(text,self):
                                    return text
                                
                                code=Prompt.__init2__(self,func=mkT,ptext='TouchStampId',helpText="Please enter the TouchStampId you wish to delete!",data=self)
                                print(code)
                                if code in [None,]:
                                    break
                                else:
                                    with Session(self.engine) as session:
                                        bcd=session.query(TouchStamp).filter(TouchStamp.TouchStampId==int(code)).delete()
                                        session.commit()
                                        print(bcd) 
                                break
                            except Exception as e:
                                print(e)         
                elif cmd.split(",")[0].lower() in ['e']:
                    cmdline=cmd.split(",")
                    ct=len(cmdline)

                    if ct > 1 and ct == 3:
                        with Session(self.engine) as session:
                            tsid=int(cmdline[2])
                            ts=session.query(TouchStamp).filter(TouchStamp.TouchStampId==tsid).first()
                            if ts:
                                note=input("Note: ")
                                if note.startswith("+"):
                                    ts.Note+=note
                                elif note.endswith("+"):
                                    ts.Note=note+ts.Note
                                elif note.startswith("-"):
                                    ts.Note.replace(note,' '*len(note))
                                else:
                                    ts.Note=note
                                print(ts)
                            else:
                                print(f"No Such TouchStampId!")
                            session.commit()
                    else:
                        while True:
                            try:
                                with Session(self.engine) as session:
                                    def mkT(text,self):
                                        try:
                                            return int(text)
                                        except Exception as e:
                                            return None
                                    tsid=Prompt.__init2__(None,func=mkT,ptext="TouchStampId",helpText="The TouchStampId for the Entry you wish to edit!",data=self)
                                    if tsid in [None,]:
                                        break
                                    ts=session.query(TouchStamp).filter(TouchStamp.TouchStampId==tsid).first()
                                    if ts:
                                        note=input("Note: ")
                                        if note.startswith("+"):
                                            ts.Note+=note[1:]
                                        elif note.endswith("+"):
                                            ts.Note=note[:-1]+ts.Note
                                        elif note.startswith("-"):
                                            ts.Note=ts.Note.replace(note[1:],'')
                                        else:
                                            ts.Note=note
                                        print(ts)
                                    else:
                                        print(f"No Such TouchStampId!")
                                    session.commit()
                                    break
                            except Exception as e:
                                print(e)
                elif cmd.split(",")[0].lower() in ['l']:
                    cmdline=cmd.split(",")
                    ct=len(cmdline)
                    if ct == 1:
                        with Session(self.engine) as session:
                            results=session.query(TouchStamp).all()
                            ct=len(results)
                            for num,i in enumerate(results):
                                print(f"{num}/{ct} -> {i}")
                    elif ct > 1 and ct == 2:
                       with Session(self.engine) as session:
                            results=session.query(TouchStamp).filter(TouchStamp.TouchStampId==int(cmdline[1])).all()
                            ct=len(results)
                            for num,i in enumerate(results):
                                print(f"{num}/{ct} -> {i}")
                    elif ct > 1 and ct == 3:
                        field=cmdline[1]
                        if field not in ['Timestamp',]:
                            if field == 'Note':
                                with Session(self.engine) as session:
                                    results=session.query(TouchStamp).filter(TouchStamp.Note.icontains(cmdline[2].lower())).all()
                                    ct=len(results)
                                    for num,i in enumerate(results):
                                        print(f"{num}/{ct} -> {i}")
                                    print(f"Total Results {ct}")
                            elif field == "TouchStampId":
                                with Session(self.engine) as session:
                                    results=session.query(TouchStamp).filter(TouchStamp.TouchStampId==int(cmdline[2])).all()
                                    ct=len(results)
                                    for num,i in enumerate(results):
                                        print(f"{num}/{ct} -> {i}")
                                    print(f"Total Results {ct}") 
                            else:
                                print("Unsupported Field to Search!")
                        #list items by searching field
                    else:
                        print(self.helpTxt)
                        #prompt for field to search
                        #print relevant touchstamps
                
        except Exception as e:
            print(e)
        except Exception as e:
            print(e)
