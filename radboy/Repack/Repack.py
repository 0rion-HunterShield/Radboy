#Cimport pandas as pd
import csv
import random
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
from radboy.DB.Prompt import *
from radboy.ConvertCode.ConvertCode import *
from radboy.setCode.setCode import *
from radboy.Locator.Locator import *
from radboy.ListMode2.ListMode2 import *
from radboy.TasksMode.Tasks import *
from radboy.Collector2.Collector2 import *
from radboy.LocationSequencer.LocationSequencer import *
from radboy.PunchCard.PunchCard import *
from radboy.Conversion.Conversion import *
from radboy.POS.POS import *
import radboy.possibleCode as pc
import radboy.Unified.Unified as unified
from radboy.FB.FBMTXT import *
from radboy.FB.FormBuilder import *
from radboy.DB.DatePicker import *
from datetime import time as TIME
from datetime import date as DATE
import string


class RepackExec(TasksMode):
    def listRepack(self,short=False):
        while True:
            try:
                def mkBarcode(text,data):
                    return text

                caseBarcode=Prompt.__init2__(None,func=mkBarcode,ptext="Case Barcode",helpText="this will display all dates with the last line printed to be the latest",data=self)
                if caseBarcode in [None,]:
                    return
                with Session(self.engine) as session:
                    query=session.query(RepackList).filter(RepackList.repackCaseBarcode==caseBarcode).order_by(RepackList.repackDateTime.asc())
                    results=query.all()
                    if len(results) < 1:
                        print("There were 0 results!")
                        continue
                    for num,i in enumerate(results):
                        print("----------Case---------------")
                        print(num,i)
                        itemsQuery=session.query(RepackItem).filter(RepackItem.RepackListId==i.repackListId)
                        items=itemsQuery.all()
                        if len(items) < 1:
                            print("This Case hase 0 items in it, cleaning up now...")
                            session.delete(i)
                            session.commit()
                            session.flush()
                            print(f"Delete {i}")
                            continue
                        print("----------Contents-----------")
                        rpk=i
                        NTE=''
                       
                        if i.repackNote != '':
                            NTE=f"-{i.repackNote}"
                        else:
                            NTE=''
                        if short:
                            print(f"Case #|Rpk Barcode|Rpk Date|Rpk Item Ct.# -> EntryName|EntryBarcode|EntryCode|EntryPrice|EntryQty")
                        totalItems=0
                        totalCaseValue=0
                        for num2,item in enumerate(items):
                            totalItems=num2+1
                            totalCaseValue+=(item.EntryPrice*item.EntryQty)
                            if not short:
                                ITEM=item
                            else:
                                ITEM=f"""{item.EntryName}|{item.EntryBarcode}|{item.EntryCode}|{item.EntryPrice}|{item.EntryQty}"""
                            m=f"{Fore.grey_70}{num}{Style.reset}/{Fore.cyan}{i.repackCaseBarcode}|{Style.reset}{Fore.orange_red_1}'{rpk.repackDate.month}.{rpk.repackDate.day}.{str(rpk.repackDate.year)[-2:]}{NTE}'{Style.reset}/{num2+1} -> {ITEM}"
                            print(m)
                        print(f"{Fore.grey_66}Total Count in Case:{Fore.light_yellow} {totalItems}{Style.reset}")
                        print(f"{Fore.grey_70}Total Case Value:{Fore.light_green}${totalCaseValue}{Style.reset}")
            except Exception as e:
                print(e)
    
    def appendRpk2Rpk(self):
        #left to right
        #repackListId:15 -> repackListId:16
        selected_from=None
        selected_to=None
        with Session(ENGINE) as session:
            def selectListId():
                lists=session.query(RepackList).all()
                listsCt=len(lists)
                if listsCt < 1:
                    print("Nothing to work on")
                    return
                for num,i in enumerate(lists):
                    #msg=f'''{num}/{num+1} of {ct} -> {i}'''
                    msg=f"{num}/{Fore.light_green}{num+1} of {Fore.light_red}{ct} - {Fore.light_yellow}{i.repackCaseBarcode}|{Fore.grey_70}{i.repackNote}|{Fore.cyan}{i.repackDateTime}{Style.reset}"
                    print(msg)

                which=Prompt.__init2__(self,func=FormBuilderMkText,ptext="Which index?",helpText="a valid index please!",data="integer")
                if which in [None,]:
                    return
                try:
                    selected_from=lists[which]
                    return selected_from.repackListId
                except Exception as e:
                    print(e)

            selected_from=selectListId()
            if selected_from in [None,]:
                return
            selected_to=selectListId()
            if selected_to in [None,]:
                return

            rpk_items=session.query(RepackItem).filter(RepackItem.RepackListId==selected_from).all()
            for num,item in enumerate(rpk_items):
                if num % 100:
                    item.RepackListId=selected_to
                    session.commit()
            session.commit()
            session.query(RepackList).filter(RepackList.repackListId==selected_from).delete()
            session.commit()



    def editRpkList(self):
        excludes=['repackListId',]
        with Session(ENGINE) as session:
            lists=session.query(RepackList).all()
            listsCt=len(lists)
            if listsCt < 1:
                print("Nothing to work on")
                return
            for num,i in enumerate(lists):
                #msg=f'''{num}/{num+1} of {ct} -> {i}'''
                msg=f"{num}/{Fore.light_green}{num+1} of {Fore.light_red}{ct} - {Fore.light_yellow}{i.repackCaseBarcode}|{Fore.grey_70}{i.repackNote}|{Fore.cyan}{i.repackDateTime}{Style.reset}"
                print(msg)

            which=Prompt.__init2__(self,func=FormBuilderMkText,ptext="Which index?",helpText="a valid index please!",data="integer")
            if which in [None,]:
                return
            try:
                selected=lists[which]
                predata={str(i.name):{'type':str(i.type),'default':getattr(selected,str(i.name))} for i in selected.__table__.columns if str(i.name) not in excludes}
                data=FormBuilder(data=predata)
                if data not in [None,]:
                    data['repackListId']=selected.repackListId
                    session.query(RepackList).filter(RepackList.repackListId==selected.repackListId).update(data)
                    session.commit()
                    session.refresh(selected)
                    print(selected)
            except Exception as e:
                print(e)
                    


    def repackExec(self,entry,rpk):
        print(entry.seeShort())
        with Session(self.engine) as e:
            item=e.query(Entry).filter(Entry.EntryId==entry.EntryId)
            item=item.first()
            e.commit()
            rpkitem=RepackItem(
                RepackListId=rpk.repackListId,
                EntryId=item.EntryId,
                EntryBarcode=item.Barcode,
                EntryCode=item.Code,
                EntryPrice=item.Price,
                EntryName=item.Name,
                EntryNote=item.Note,
                EntryQty=item.BackRoom,
                )
            e.add(rpkitem)
            e.commit()
            e.refresh(rpkitem)
            fields=[i.name for i in rpkitem.__table__.columns]
            values=[getattr(rpkitem,i) for i in fields]
            fields=f'{Fore.medium_violet_red}|{Style.reset}{Fore.light_steel_blue}'.join([f'{i} col:[{Fore.light_green}{num}{Fore.light_steel_blue}]' for num,i in enumerate(fields)])
            values=f'{Fore.medium_violet_red}|{Style.reset}{Fore.light_steel_blue}'.join([f'{str(i)} col:[{Fore.light_green}{num}{Fore.light_steel_blue}]' for num,i in enumerate(values)])
            print(f'{Fore.light_red}{fields}{Style.reset}')
            print(f'{Fore.light_red}{values}{Style.reset}')

            item.BackRoom=0
            e.commit()
            e.refresh(item)

    def listAllRepackNamesAndBarcodes(self):
        with Session(self.engine) as session:
            results=session.query(RepackList).all()
            if len(results) < 0:
                print("No RepackList's presently available!")
            ct=len(results)
            for num,i in enumerate(results):
                print(f"{Fore.light_green}{num+1}/{Fore.light_red}{ct} - {Fore.light_yellow}{i.repackCaseBarcode}|{Fore.grey_70}{i.repackNote}|{Fore.cyan}{i.repackDateTime}{Style.reset}")

    def addToRepack(self,repackCaseBarcode=None):
        while True:
            try:
                bcd=''
                if repackCaseBarcode in ['',None]:
                    def mkBarcode(text,data):
                        return text
                    bcd=Prompt.__init2__(None,func=mkBarcode,ptext="Repack Case Barcode",helpText="repackCaseBarcode you are wanting to add to.",data=self)
                    if bcd in [None,]:
                        return
                else:
                    bcd=repackCaseBarcode
                    #search
                print(bcd)
                with Session(self.engine) as session:
                    results=session.query(RepackList).filter(RepackList.repackCaseBarcode==bcd).all()
                    ct=len(results)
                    if ct < 1:
                        print("Nothing to delete!")
                        return
                    for num,r in enumerate(results):
                        msg=f"{Fore.light_red}{num}{Style.reset}/{Fore.light_yellow}{ct-1}{Style.reset} -> {r}"
                        print(msg)
                    def mkInt(text,data):
                        try:
                            if text == '':
                                return 0
                            else:
                                return int(text)
                        except Exeption as e:
                            print(e)
                            return
                    whichIndex=Prompt.__init2__(None,func=mkInt,ptext=f"which {Fore.light_red}number{Style.reset}{Fore.light_yellow}",helpText=f"the number in {Fore.light_red}light red{Style.reset}",data=self)
                    if whichIndex in [None,]:
                        return
                    rpk=results[whichIndex]
                    if rpk.repackNote in ['',None]:
                        note=''
                    else:
                        note=rpk.repackNote
                    today=DATE.today()
                    
                    print(f"{Fore.orange_red_1}Find & Cross-Out {Fore.medium_violet_red}(M.D.Y[2 Digit]) {Fore.orange_red_1}'{rpk.repackDate.month}.{rpk.repackDate.day}.{str(rpk.repackDate.year)[-2:]}{note}'{Style.reset} next to {Fore.cyan}Scanned Barcode{Fore.light_green}(repackCaseBarcode) and update w/ {Fore.orange_red_1}'{today.month}.{today.day}.{today.year}'{Style.reset}")
                    rpk.repackDate=today
                    rpk.repackTime=TIME(datetime.now().hour,datetime.now().minute,datetime.now().second)
                    rpk.repackDateTime=datetime(rpk.repackDate.year,rpk.repackDate.month,rpk.repackDate.day,rpk.repackTime.hour,rpk.repackTime.minute,rpk.repackTime.second)
                    session.commit()
                    while True:
                        productBarcode=Prompt.__init2__(None,func=mkBarcode,ptext="Product Barcode",helpText="add an RepackItem to RepackList",data=self)
                        if productBarcode in [None,]:
                            return
                        self.setFieldInList('BackRoom',barcode=productBarcode,repack_exec=lambda entry,self=self,session=session,rpk=rpk:self.repackExec(entry,rpk=rpk))

            except Exception as e:
                print(e)        


    def addRepack(self):
        while True:
            try:
                def mkBarcode(text,data):
                    if text == '' and data == 'Barcode':
                        code=[]
                        chars=string.hexdigits
                        for i in range(5):
                            code.append(chars[random.randint(0,len(chars)-1)])
                        text=''.join(code).upper()
                    return text

                caseBarcode=Prompt.__init2__(None,func=mkBarcode,ptext="Case Barcode",helpText="this will display all dates with the last line printed to be the latest",data="Barcode")
                if caseBarcode in [None,]:
                    return
                with Session(self.engine) as session:
                    dt=datetime.now()
                    t=TIME(dt.hour,dt.minute,dt.second)
                    d=DATE(dt.year,dt.month,dt.day)
                    rpkNote=Prompt.__init2__(None,func=mkBarcode,ptext="Notes",helpText="any notes about this case worth mentioning",data=self)
                    if rpkNote in [None,]:
                        return
                    rpk=RepackList(repackCaseBarcode=caseBarcode,repackTime=t,repackDate=d,repackDateTime=dt,repackNote=rpkNote)
                    session.add(rpk)
                    session.commit()
                    session.flush()
                    session.refresh(rpk)
                    print(rpk)
                    if rpk.repackNote != '':
                        note=f"-{rpk.repackNote}"
                    else:
                        note=''
                    print(f"{Fore.orange_red_1}Write {Fore.medium_violet_red}(M.D.Y[2 Digit]) {Fore.orange_red_1}'{rpk.repackDate.month}.{rpk.repackDate.day}.{str(rpk.repackDate.year)[-2:]}{note}'{Style.reset} next to {Fore.cyan}Scanned Barcode{Fore.light_green}(repackCaseBarcode){Style.reset}")
                    while True:
                        productBarcode=Prompt.__init2__(None,func=mkBarcode,ptext="Product Barcode",helpText="add an RepackItem to RepackList",data=self)
                        if productBarcode in [None,]:
                            return
                        self.setFieldInList('BackRoom',barcode=productBarcode,repack_exec=lambda entry,self=self,session=session,rpk=rpk:self.repackExec(entry,rpk=rpk))

            except Exception as e:
                print(e)

    def help(self,text):
        lines=[]
        for k in self.cmds:
            line=f'{Fore.light_green}{self.cmds[k]["cmd"]}{Style.reset} {Fore.light_yellow}-{Style.reset} {Fore.cyan}{self.cmds[k]["desc"]}{Style.reset}'
            lines.append(line)
        return '\n'.join(lines)+"\n"+self.helpText


    def addCmd(self,EXEC=lambda:print("dummy"),cmd=["dummy teSt"],desc="dummy"):
        cmd.append(f'#{str(self.option)}')
        self.cmds[f'#{str(self.option)}']={
            'cmd':cmd,
            'exec':EXEC,
            'desc':desc
        }
        tmp=[]
        for i in self.cmds[f'#{str(self.option)}']['cmd']:
            z=i.lower()
            z=z.replace(" ","_")
            tmp.append(z)
        self.cmds[f'#{str(self.option)}']['cmd']=tmp
        self.option+=1


    def clearAllRepacks(self):
        with Session(self.engine) as session:
            repacklists=session.query(RepackList).all()
            ct=len(repacklists)
            if len(repacklists) < 1:
                print(f"RepackList is Empty!")
            for num,r in enumerate(repacklists):
                print(f"{Fore.light_red}Deleting RepackList{Style.reset} {Fore.light_yellow}{num+1}{Fore.orange_red_1}/{ct}{Style.reset} -> '{r.repackCaseBarcode}'!")
                session.delete(r)
                if num%10==0:
                    session.commit()
            session.commit()
            repackItems=session.query(RepackItem).all()
            ct=len(repackItems)
            if len(repackItems) < 1:
                print(f"There are no repack items present!")
            for num,r in enumerate(repackItems):
                print(f"{Fore.light_red}Deleting RepackItem{Style.reset} {Fore.light_yellow}{num+1}{Fore.orange_red_1}/{ct}{Style.reset} -> {r.EntryBarcode}|{r.EntryCode}|{r.EntryName}!")
                session.delete(r)
                if num%10==0:
                    session.commit()
            session.commit()

    def EditRepack(self,repackCaseBarcode=''):
        while True:
            try:
                bcd=''
                if repackCaseBarcode in ['',None]:
                    def mkBarcode(text,data):
                        return text
                    bcd=Prompt.__init2__(None,func=mkBarcode,ptext="Repack Case Barcode",helpText="repackCaseBarcode you are wanting to delete.",data=self)
                    if bcd in [None,]:
                        return
                else:
                    bcd=repackCaseBarcode
                    #search
                print(bcd)
                with Session(self.engine) as session:
                    results=session.query(RepackList).filter(RepackList.repackCaseBarcode==bcd).all()
                    ct=len(results)
                    if ct < 1:
                        print("Nothing to Edit!")
                        return
                    #edit RepackList

                    for num,r in enumerate(results):
                        msg=f"{Fore.light_red}{num}{Style.reset}/{Fore.light_yellow}{ct-1}{Style.reset} -> {r}"
                        print(msg)
                    def mkInt(text,data):
                        try:
                            if text == '':
                                return 0
                            else:
                                return int(text)
                        except Exeption as e:
                            print(e)
                            return
                    whichIndex=Prompt.__init2__(None,func=mkInt,ptext=f"which {Fore.light_red}number {Style.reset}{Fore.light_yellow}to edit",helpText=f"the number in {Fore.light_red}light red{Style.reset}",data=self)
                    if whichIndex in [None,]:
                        return

                    def mkBool(text,data):
                        try:
                            if text.lower() in ['1','y','yes','true']:
                                return True
                            elif text.lower() in ['','0','n','no','false']:
                                return False
                            else:
                                return bool(eval(text))
                        except Exception as e:
                            print(e)
                            return
                    editRepackList=Prompt.__init2__(None,func=mkBool,ptext="Edit RepackList[Y/n]",helpText="edit RepackList y/N",data=self)
                    if editRepackList in [None,]:
                        return
                    if editRepackList in [True,]:
                        for col in RepackList.__table__.columns:
                            editField=editRepackList=Prompt.__init2__(None,func=mkBool,ptext=f"Edit RepackList[{col.name}]",helpText="edit RepackList y/N",data=self)
                            if editField in [None,]:
                                continue
                            if editField in [True,]:
                                print(f"Editing {Fore.light_red}RepackList!{Style.reset}")
                                def mkType(text,TYPE):
                                    print(TYPE)
                                    if text == '':
                                        return
                                    if str(TYPE) == 'FLOAT':
                                        if text == '':
                                            return float(0)
                                        return float(eval(text))
                                    elif str(TYPE) == 'INTEGER':
                                        if text == '':
                                            return int(1)
                                        return int(eval(text))
                                    elif str(TYPE) == 'VARCHAR':
                                        return text
                                    elif str(TYPE) == 'DATE':
                                        return DatePkr()
                                    elif str(TYPE) == 'TIME':
                                        return TimePkr()
                                    elif str(TYPE) == 'DATETIME':
                                        return DateTimePkr()
                                    return text

                                if str(col.type) == 'DATE':
                                    edit=DatePkr()
                                elif str(col.type) == 'TIME':
                                    edit=TimePkr()
                                elif str(col.type) == 'DATETIME':
                                    edit=DateTimePkr()
                                else:
                                    edit=Prompt.__init2__(None,func=mkType,ptext=f"OLD [{col.name}={getattr(results[whichIndex],col.name)}]",helpText="new field value",data=col.type)
                                if edit in [None,]:
                                    continue
                                else:
                                    if col.name == 'repackDate':
                                        dt=datetime(edit.year,edit.month,edit.day,results[whichIndex].repackTime.hour,results[whichIndex].repackTime.minute,results[whichIndex].repackTime.second)
                                        setattr(results[whichIndex],'repackDateTime',dt)
                                    elif col.name=='repackTime':
                                        dt=datetime(results[whichIndex].repackDate.year,results[whichIndex].repackDate.month,results[whichIndex].repackDate.day,edit.hour,edit.minute,edit.second)
                                        setattr(results[whichIndex],'repackDateTime',dt)
                                    elif col.name == 'repackDateTime':
                                        tm=TIME(edit.hour,edit.minute,edit.second)
                                        dt=DATE(edit.year,edit.month,edit.day)
                                        setattr(results[whichIndex],'repackTime',tm)
                                        setattr(results[whichIndex],'repackDate',dt)
                                    setattr(results[whichIndex],col.name,edit)
                                    session.commit()

                    #stop
                    items=session.query(RepackItem).filter(RepackItem.RepackListId==results[whichIndex].repackListId).all()
                    ct2=len(items)
                    if ct2 < 1:
                        print("No Repack Items To Edit related to list!")

                    def mkType(text,TYPE):
                        if text == '':
                            return
                        if str(TYPE) == 'FLOAT':
                            if text == '':
                                return float(0)
                            return float(eval(text))
                        elif str(TYPE) == 'INTEGER':
                            if text == '':
                                return int(1)
                            return int(eval(text))
                        elif str(TYPE) == 'VARCHAR':
                            return text
                        elif str(TYPE) == 'DATE':
                            return DatePkr()
                        elif str(TYPE) == 'TIME':
                            return TimePkr()
                        elif str(TYPE) == 'DATETIME':
                            return DateTimePkr()
                        return text

                    for num,i in enumerate(items):
                        msg=f"{Fore.light_red}Edit {num}{Style.reset}/{Fore.light_yellow}{ct2-1}{Style.reset} -> {i}"
                        print(msg)
                        def mkBool(text,data):
                            try:
                                if text.lower() in ['1','y','yes','true']:
                                    return True
                                elif text.lower() in ['','0','n','no','false']:
                                    return False
                                else:
                                    return bool(eval(text))
                            except Exception as e:
                                print(e)
                                return
                        editRepackItem=Prompt.__init2__(None,func=mkBool,ptext="Edit RepackItem[Y/n]",helpText="edit RepackList y/N",data=self)
                        if editRepackItem in [None,]:
                            return
                        if editRepackItem in [True,]:
                            for col in RepackItem.__table__.columns:
                                #ask to edit/delete item here
                                edit=Prompt.__init2__(None,func=mkType,ptext=f"OLD [{col.name}={getattr(i,col.name)}]",helpText="new field value, b skips",data=col.type)
                                if edit in [None,]:
                                    continue
                                else:
                                    setattr(i,col.name,edit)
                                session.commit()
                        elif editRepackItem in [False,]:
                            delRepackItem=Prompt.__init2__(None,func=mkBool,ptext="Delete RepackItem[Y/n]",helpText="delete RepackList y/N",data=self)
                            if delRepackItem in [None,]:
                                return
                            elif delRepackItem in [True,]:
                                print(f"{Fore.light_red}Deleting{Style.reset} -> {i}")
                                session.delete(i)
                                session.commit()
                    session.commit()
                    
                #use bcd in search
                #use prefix notation to be specific
            except Exception as e:
                print(e)


    def DeleteRepack(self,repackCaseBarcode=''):
        while True:
            try:
                bcd=''
                if repackCaseBarcode in ['',None]:
                    def mkBarcode(text,data):
                        return text
                    bcd=Prompt.__init2__(None,func=mkBarcode,ptext="Repack Case Barcode",helpText="repackCaseBarcode you are wanting to delete.",data=self)
                    if bcd in [None,]:
                        return
                else:
                    bcd=repackCaseBarcode
                    #search
                print(bcd)
                with Session(self.engine) as session:
                    results=session.query(RepackList).filter(RepackList.repackCaseBarcode==bcd).all()
                    ct=len(results)
                    if ct < 1:
                        print("Nothing to delete!")
                        return
                    for num,r in enumerate(results):
                        msg=f"{Fore.light_red}{num}{Style.reset}/{Fore.light_yellow}{ct-1}{Style.reset} -> {r}"
                        print(msg)
                    def mkInt(text,data):
                        try:
                            if text == '':
                                return 0
                            else:
                                return int(text)
                        except Exeption as e:
                            print(e)
                            return
                    whichIndex=Prompt.__init2__(None,func=mkInt,ptext=f"which {Fore.light_red}number{Style.reset}{Fore.light_yellow}",helpText=f"the number in {Fore.light_red}light red{Style.reset}",data=self)
                    if whichIndex in [None,]:
                        return

                    items=session.query(RepackItem).filter(RepackItem.RepackListId==results[whichIndex].repackListId).all()
                    ct2=len(items)
                    if ct2 < 1:
                        print("No Repack Items To Delete related to list!")
                    for num,i in enumerate(items):
                        msg=f"{Fore.light_red}Deleting {num}{Style.reset}/{Fore.light_yellow}{ct2-1}{Style.reset} -> {i}"
                        print(msg)
                        session.delete(items[num])
                        if num%10==0:
                            session.commit()
                        session.commit()
                    d=session.delete(results[whichIndex])
                    session.commit()
                    
                #use bcd in search
                #use prefix notation to be specific
            except Exception as e:
                print(e)

   
    def searchAllRepacks(self,barcode=''):
        while True:
            try:
                bcd=''
                if barcode in ['',None]:
                    def mkBarcode(text,data):
                        return text
                    bcd=Prompt.__init2__(None,func=mkBarcode,ptext="Barcode",helpText="Barcode|code|name you are looking to find the case for.",data=self)
                    if bcd in [None,]:
                        return
                else:
                    bcd=barcode
                    #search
                print(bcd)
                with Session(self.engine) as session:
                    query=session.query(RepackItem)
                    query=query.filter(or_(RepackItem.EntryName.icontains(bcd),RepackItem.EntryBarcode.icontains(bcd),RepackItem.EntryCode.icontains(bcd)))
                    results=query.all()
                    caseids=[]
                    ct=len(results)
                    print(f"{'-'*10}Content Data{'-'*10}")
                    for num,r in enumerate(results):
                        print(f"{Fore.light_red}RepackItem{Style.reset} {Fore.light_yellow}{num+1}{Fore.orange_red_1}/{ct}{Style.reset} -> {Fore.light_magenta}{r.EntryBarcode}{Style.reset}|{r.EntryCode}|{r.EntryName}!")
                        if r.RepackListId not in caseids:
                            caseids.append(r.RepackListId)
                    print(f"{'-'*10}Content Data End{'-'*10}")
                    print()
                    print(f"{'-'*10}Possible Cases{'-'*10}")
                    for num,c in enumerate(caseids):
                        r=session.query(RepackList).filter(RepackList.repackListId==c).first()
                        print(f"{Fore.light_red}RepackList{Style.reset} {Fore.light_yellow}{num+1}{Fore.orange_red_1}/{1}{Style.reset} -> {Fore.magenta}{r.repackCaseBarcode}{Style.reset}|{r.repackDateTime}|{r.repackNote}!")
                    print(f"{'-'*10}Possible Cases End{'-'*10}")
                    

                #use bcd in search
                
            except Exception as e:
                print(e)

    def export_all_to_excel(self):
        with Session(self.engine) as session:
            query=session.query(RepackList,RepackItem).join(RepackItem,RepackItem.RepackListId==RepackList.repackListId)
            results=query.all()
            df=pd.read_sql(query.statement.compile(compile_kwargs={"literal_binds": True}),self.engine,dtype=str)
            def mkPath(text,data):
                try:
                    if text == '':
                        return
                    if Path(text).exists() and Path(text).is_file():
                        Path(text).unlink()
                    else:
                        return Path(text)
                except Exception as e:
                    print(e)
                    return
            default=f"case-export-{datetime.now()}.xlsx".replace(":","-").replace(" ","-")
            save=Prompt.__init2__(None,func=mkPath,ptext=f"save where [{default}]",helpText="saves to ./{default} if nothing")
            if save in [None,]:
                pass
            else:
                default=str(save.absolute()).replace(":","-").replace(" ","-")
            df.to_excel(default)

    def export_case_to_excel(self,caseBarcode=None):
        def mkBarcode(text,data):
            return text

        if caseBarcode == None:
            cbc=Prompt.__init2__(self,func=mkBarcode,ptext="Case Barcode",helpText="Case Barcode where latest date is written.",data=self)
        else:
            cbc=caseBarcode

        with Session(self.engine) as session:
            query=session.query(RepackList,RepackItem).join(RepackItem,RepackItem.RepackListId==RepackList.repackListId).filter(RepackList.repackCaseBarcode==cbc)
            results=query.all()
            df=pd.read_sql(query.statement.compile(compile_kwargs={"literal_binds": True}),self.engine,dtype=str)
            def mkPath(text,data):
                try:
                    if text == '':
                        return
                    if Path(text).exists() and Path(text).is_file():
                        Path(text).unlink()
                    else:
                        return Path(text)
                except Exception as e:
                    print(e)
                    return
            default=f"case-export-{datetime.now()}.xlsx".replace(":","-").replace(" ","-")
            save=Prompt.__init2__(None,func=mkPath,ptext=f"save where [{default}]",helpText="saves to ./{default} if nothing")
            if save in [None,]:
                pass
            else:
                default=str(save.absolute()).replace(":","-").replace(" ","-")
            df.to_excel(default)

    def remove_from_case(self,caseBarcode=None,productBarcode=None):
        def mkBarcode(text,data):
            return text

        if caseBarcode == None:
            cbc=Prompt.__init2__(self,func=mkBarcode,ptext="Case Barcode",helpText="Case Barcode where latest date is written.",data=self)
        else:
            cbc=caseBarcode


        with Session(self.engine) as session:
            results=session.query(RepackList).filter(RepackList.repackCaseBarcode==cbc).all()
            ct=len(results)
            if ct < 1:
                print(f"{Fore.light_red}No Cases Found!{Style.reset}")
                return
            for num,r in enumerate(results):
                print(f"{Fore.light_red}RepackList{Style.reset} {Fore.light_yellow}{num}{Fore.orange_red_1}/{ct-1}{Style.reset} -> {Fore.light_magenta}{r.repackCaseBarcode}{Style.reset}|{r.repackNote}|{r.repackDate}!")
            def mkInt(text,data):
                try:
                    if text == '':
                        return 0
                    else:
                        return int(text)
                except Exeption as e:
                    print(e)
                    return
            whichIndex=Prompt.__init2__(None,func=mkInt,ptext=f"Which {Fore.light_red}number{Style.reset}{Fore.light_yellow}",helpText=f"the number in {Fore.light_red}light red{Style.reset}",data=self)
            if whichIndex in [None,]:
                return

            today=DATE.today()
            rpk=results[whichIndex]
            if rpk.repackNote in ['',None]:
                note=''
            else:
                note=rpk.repackNote
            print(f"{Fore.orange_red_1}Find & Cross-Out {Fore.medium_violet_red}(M.D.Y[2 Digit]) {Fore.orange_red_1}'{rpk.repackDate.month}.{rpk.repackDate.day}.{str(rpk.repackDate.year)[-2:]}{note}'{Style.reset} next to {Fore.cyan}Scanned Barcode{Fore.light_green}(repackCaseBarcode) and update w/ {Fore.orange_red_1}'{today.month}.{today.day}.{today.year}'{Style.reset}")
            rpk.repackDate=today
            rpk.repackTime=TIME(datetime.now().hour,datetime.now().minute,datetime.now().second)
            rpk.repackDateTime=datetime(rpk.repackDate.year,rpk.repackDate.month,rpk.repackDate.day,rpk.repackTime.hour,rpk.repackTime.minute,rpk.repackTime.second)
            session.commit()
            
            rpklid=results[whichIndex].repackListId
            while True:
                try:
                    if productBarcode == None:
                        pbc=Prompt.__init2__(self,func=mkBarcode,ptext="Product Barcode",helpText="Product Barcode of item being removed from present case",data=self)
                        if pbc in [None,]:
                            break
                    else:
                        pbc=productBarcode
                        

                    items=session.query(RepackItem).filter(RepackItem.RepackListId==rpklid,or_(RepackItem.EntryBarcode.icontains(pbc),RepackItem.EntryCode.icontains(pbc))).all()
                    ct2=len(items)
                    if ct2 < 1:
                        print(f"{Fore.light_red}No Item in this case by that code/barcode{Style.reset}")
                        continue
                    for num,r in enumerate(items):
                        print(f"{Fore.light_red}RepackItem{Style.reset} {Fore.light_yellow}{num}{Fore.orange_red_1}/{ct2-1}{Style.reset} -> {Fore.light_magenta}{r.EntryBarcode}{Style.reset}|{r.EntryCode}|{r.EntryName}|{Fore.light_steel_blue}RID={r.RepackItemId}|{Fore.light_red}EntryQty={r.EntryQty}!{Style.reset}")
                    def mkInt(text,data):
                        try:
                            if text == '':
                                return 0
                            else:
                                return int(text)
                        except Exeption as e:
                            print(e)
                            return
                    whichIndex2=Prompt.__init2__(None,func=mkInt,ptext=f"Which {Fore.light_red}number{Style.reset}{Fore.light_yellow}",helpText=f"the number in {Fore.light_red}light red{Style.reset}",data=self)
                    if whichIndex2 in [None,]:
                        return
                    session.delete(items[whichIndex2])
                    session.commit()
                except Exception as e:
                    print(e)

    def __init__(self,engine,parent):
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
        self.engine=engine
        self.parent=parent
        self.option=0
        self.helpText=f'''
        DOE=Date of Entry
        $NUM/$Barcode|$DOE-$NOTE/$NUM2 - referes to case number, case barcode, case item number in case number

        '''
        self.cmds={}
        self.addCmd(cmd=['list repack','lr','list case'],desc="list contents of a case using its barcode and the latest Date and Time written next to the Barcode used!",EXEC=self.listRepack)
        self.addCmd(cmd=['list repack short','lrs','list case short'],desc="list contents of a case using its barcode and the latest Date and Time written next to the Barcode used! short version",EXEC=lambda self=self:self.listRepack(short=True))
        self.addCmd(cmd=['add repack','ar','add case'],desc="add a new RepackList and add RepackItems to it!",EXEC=self.addRepack)
        self.addCmd(cmd=['edit repack','er','edit case'],desc="edit/Delete a RepackList or a RepackList's items and delete RepackItems from it!",EXEC=self.EditRepack)
        self.addCmd(cmd=['clear all repacks','clar','clear repacks'],desc=f"delete all repack lists and repack items{Fore.light_red}[Reset]{Style.reset}",EXEC=self.clearAllRepacks)
        self.addCmd(cmd=['search all repacks','search','lookup','lu',],desc=f"search repackitem for item by barcode/code/name and display repackCaseBarcode with items registered{Fore.light_red}{Style.reset}",EXEC=self.searchAllRepacks)
        self.addCmd(cmd=['list repack names','list just repack','ljr','lrn',],desc=f"list repack lists only{Fore.light_red}{Style.reset}",EXEC=self.listAllRepackNamesAndBarcodes)
        self.addCmd(cmd=['delete case','del rpk','drpk',],desc=f"delete repacklist and its items by barcode{Fore.light_red}{Style.reset}",EXEC=self.DeleteRepack)
        self.addCmd(cmd=['remove from case','rf rpk','rfc','delete from repack','dfr',],desc=f"remove repack by code|barcode{Fore.light_red}{Style.reset}",EXEC=self.remove_from_case)
        self.addCmd(cmd=['export case to excel','ec2e',],desc=f"export a case to excel{Fore.light_red}{Style.reset}",EXEC=self.export_case_to_excel)
        self.addCmd(cmd=['export all to excel','ea2e',],desc=f"export all cases to excel{Fore.light_red}{Style.reset}",EXEC=self.export_all_to_excel)
        self.addCmd(cmd=['a2r','add 2 repack',],desc=f"add something to an existing case{Fore.light_red}{Style.reset}",EXEC=self.addToRepack)
        self.addCmd(cmd=['erpkl','edit rpk list',],desc=f"edit a repack list/case{Fore.light_red}{Style.reset}",EXEC=self.editRpkList)
        self.addCmd(cmd=['appendRpk2Rpk','extend rpk','ar2r',],desc=f"append rpk list to rpk list from left to right{Fore.light_red}{Style.reset}",EXEC=self.appendRpk2Rpk)
        def mkCmd(text,data):
            return text

        while True:
            mode='RePack'
            fieldname='Menu'
            h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
            doWhat=Prompt.__init2__(None,func=mkCmd,ptext=f"{h} Do What",helpText=self.help(self.helpText),data=self)
            if doWhat in [None,]:
                return
            for k in self.cmds:
                c=self.cmds.get(k)
                if c:
                    cl=c.get("cmd")
                    if doWhat.lower() in cl:
                        c['exec']()

