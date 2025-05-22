import pandas as pd
import csv
from datetime import datetime
from pathlib import Path
from colored import Fore,Style,Back
from barcode import Code39,UPCA,EAN8,EAN13
import barcode,qrcode,os,sys,argparse
from datetime import datetime,timedelta,date
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
from radboy.DB.Prompt import *
from radboy.FB.FormBuilder import *
from radboy.FB.FBMTXT import *

import radboy.possibleCode as pc

class POS:
    def __init__(self,engine,parent):
        try:
            if not self.LCL_ANDROID.exists():
                self.LCL_ANDROID.mkdir(parents=True)
        except Exception as e:
            print(e,"android directory!")
        self.engine=engine
        self.parent=parent
        cmd_color=Fore.light_yellow
        explanation_color=Fore.light_green

        self.helpText=f'''
{cmd_color}CMD{Style.reset}- {explanation_color}Explanation{Style.reset}
{Fore.cyan}Billing Info -----------{Style.reset}
{cmd_color}new_b|newb|nb{Style.reset}- {explanation_color}create new business information{Style.reset}
{cmd_color}view_db|viewb|vdb{Style.reset}- {explanation_color}view DEFAULT business information{Style.reset}
{cmd_color}view_all_billing|view_ab|vab{Style.reset}- {explanation_color}view ALL business information{Style.reset}
{cmd_color}remove_bid{Style.reset}- {explanation_color}remove business information by id, or comma separated list of id's{Style.reset}
{cmd_color}setdefaultid|sdi{Style.reset}- {explanation_color}set default business, and all others are set to non-default{Style.reset}
{cmd_color}edit_business|eb{Style.reset}- {explanation_color}edit business details {Fore.light_red}{Style.bold}You will be asked for a 'yes' or 'no' before being asked for the value!{Style.reset}
{cmd_color}search_billing_text|sbt{Style.reset}- {explanation_color}search billing text fields{Style.reset}
{Fore.spring_green_3a}ReceiptEntry CMD's ----{Style.reset}
{cmd_color}mkrcpt|make_receipt|pos{Style.reset}- {explanation_color}add entry items to {Style.reset}
{cmd_color}dltr|del_receipt|rr{Style.reset}- {explanation_color}remove Reciept.RecieptId and ReceiptEntry.RecieptId{Style.reset}
{cmd_color}listr|ls_rcpt|lr{Style.reset}- {explanation_color}list all reciepts{Style.reset}
{cmd_color}are|add_rcpt_ent|add_reciept_entry{Style.reset}- {explanation_color}add a new RecieptEntry{Style.reset}
{cmd_color}clear_all_reciepts|car{Style.reset}- {explanation_color}clear all reciepts{Style.reset}
'''
        print("under dev!")
        while True:
            try:
                def mkT(text,self):
                    return text
                mode='POS'
                fieldname='Menu'
                h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                cmd=Prompt.__init2__(None,func=mkT,ptext=f"{h}Do What",helpText=self.helpText,data=self)
                if cmd in [None,]:
                    return
                if cmd.lower() in ['new_b','newb','nb']:
                    self.mkBusiness()
                elif cmd.lower() in ['view_db','viewdb','vdb']:
                    self.viewDefault()
                elif cmd.lower() in ['view_all_billing','view_ab','vab']:
                    self.viewAll()
                elif cmd.lower() in ['remove_bid',]:
                    self.removeId()
                elif cmd.lower() in ['edit_business','eb']:
                    self.edit_business()
                elif cmd.lower() in ['setdefaultid','sdi']:
                    self.setdefaultid()
                elif cmd.lower() in ['search_billing_text','sbt']:
                    self.searchBillingText()
                elif cmd.lower() in 'mkrcpt|make_receipt|pos'.split('|'):
                    self.mkreciept()
                elif cmd.lower() in 'dltr|del_receipt|rr'.split('|'):
                    self.delreceipt()
                elif cmd.lower() in 'listr|ls_rcpt|lr'.split('|'):
                    self.listAllReceipts()
                elif cmd.lower() in 'are|add_rcpt_ent|add_reciept_entry'.split('|'):
                    self.addRecieptEntry()
                elif cmd.lower() in 'clear_all_reciepts|car'.split("|"):
                    self.clear_all_reciepts()
            except Exception as e:
                print(e)

    def clear_all_reciepts(self):
        with Session(self.engine) as session:
            reciepts=session.query(Reciept).all()
            ct=len(reciepts)
            if ct == 0:
                print("No Reciepts to Delete!")
                return
            for reciept in reciepts:
                rid=reciept.RecieptId
                if reciept:
                    session.delete(reciept)
                    session.commit()
                    session.flush()
                    print(f"Deleted {reciept}!")
                recieptEntries=session.query(RecieptEntry).filter(RecieptEntry.RecieptId==rid).all()
                if len(recieptEntries) > 0:
                    for num,r in enumerate(recieptEntries):
                        msg=f"{Fore.light_red}Deleting{Style.reset} -> {r}"
                        print(msg)
                        result=session.delete(r)
                        
                        if num%50==0:
                            session.commit()
                            session.flush()
                    session.commit()
                    session.flush() 
                else:
                    print("No RecieptEntries To Delete!") 


    def listAllReceipts(self):
        with Session(self.engine) as session:
            results=session.query(Reciept).all()
            ct=len(results)
            if ct == 0:
                print("No Results!")
                return

            for num,r in enumerate(results):
                print(f"{'-'*10} Start Reciept {num}/{ct} {'-'*10}")
                text=self.render(r.RecieptId,session)
                print(f"{'-'*10} Start Reciept {num}/{ct} {'-'*10}")

    def delreceipt(self):
        while True:
            try:
                def mkint(text,self):
                    try:
                        return int(eval(text))
                    except Exception as e:
                        print(e)
                        return
                rid=Prompt.__init2__(None,func=mkint,ptext="Reciept Id To Delete?",helpText="what is the reciept id you need to delete? it must be an integer!",data=self)
                if rid in [None,]:
                    break
                with Session(self.engine) as session:
                    reciept=session.query(Reciept).filter(Reciept.RecieptId==rid).first()
                    if reciept:
                        session.delete(reciept)
                        session.commit()
                        session.flush()
                        print(f"Deleted {reciept}!")
                    recieptEntries=session.query(RecieptEntry).filter(RecieptEntry.RecieptId==rid).all()
                    if len(recieptEntries) > 0:
                        for num,r in enumerate(recieptEntries):
                            msg=f"{Fore.light_red}Deleting{Style.reset} -> {r}"
                            print(msg)
                            result=session.delete(r)
                            print("Deleted {r}!")
                            if num%50==0:
                                session.commit()
                                session.flush()
                        session.commit()
                        session.flush() 
                    else:
                        print("No RecieptEntries To Delete!")
                break
            except Exception as e:
                print(e)

    LCL=Path("LCL_IMG")
    LCL_ANDROID=Path("/storage/emulated/0/DCIM/Screenshots")

    def render(self,rid,session):
        try:
            text=[]
            reciept=session.query(Reciept).filter(Reciept.RecieptId==rid).first()
            billing=session.query(Billing).filter(Billing.BillingId==reciept.BillingId).first()
            entries=session.query(RecieptEntry).filter(RecieptEntry.RecieptId==rid).all()
            #for now render just prints
            #print(reciept)
            #print(billing)
            if not billing:
                raise Exception("No Such Billing; please add a Billing with BillingId={Reciept.BillingId}")

            btext=f"""
    Seller:{billing.sellerName}
    Seller Addr:{billing.sellerAddress}
    Seller Phone:{billing.sellerPhone}
    Seller Email:{billing.sellerEmail}
    Pur. Name:{billing.purchaserName}
    Pur. Addr:{billing.purchaserAddress}
    Pur. Phone:{billing.purchaserPhone}
    Pur. Email:{billing.purchaserEmail}
    RetailersPermitSerial:{billing.RetailersPermitSerial}
    CertofReg:{billing.CertofReg}
    Date={reciept.Date}
    ReceiptId={reciept.RecieptId}
    """     
            ttl_sold=0
            text.append(btext)
            ct=len(entries)
            total=0
            for num,r in enumerate(entries):
                ttl_sold+=r.QtySold
                total+=(r.EntryPrice*r.QtySold)
                if r.Tax == None:
                    r.Tax=0
                if r.CRV == None:
                    r.CRV=0
                specific=f"{r.EntryName}|{r.EntryBarcode}|{round(r.EntryPrice,2)}*QTY({r.QtySold})={round(r.EntryPrice*r.QtySold,2)} + Tax[{r.TaxNote}]({r.Tax*r.QtySold}) + CRV({r.CRV*r.QtySold})|{round((r.EntryPrice*r.QtySold)+(r.Tax*r.QtySold)+(r.CRV*r.QtySold),2)}"
                msg=f"{num}/{ct} -> {specific}"
                text.append(msg)

            text.append(f"Total Due: ${round(total+(r.Tax*r.QtySold)+(r.CRV*r.QtySold),2)}\nTotal Qty Sold/Billed For: {ttl_sold}")
            print('\n'.join(text))
            def mkBool(text,self):
                try:
                    if text in ['y','yes','true','True','1','t']:
                        return True
                    else:
                        return False
                except Exception as e:
                    print(e)
                    return None

            while True:
                try:
                    if self.LCL_ANDROID.exists():
                        self.LCL=self.LCL_ANDROID
                   
                    #LCL=Path("LCL_IMG")
                    if not self.LCL.exists():
                        self.LCL.mkdir()
                    fname=str(self.LCL/Path(str(f"{reciept.RecieptId}-{reciept.Date}.png")))
                    saveR=Prompt.__init2__(None,func=mkBool,ptext=f"Save Reciept to Img '{fname}'",helpText="answer yes or no, default is No",data=self)
                    if saveR in [None,]:
                        return
                    if saveR == False:
                        break
                    else:
                        data='\n'.join(text)
                        renderImageFromText(fname,data,barcode_file=None,code_file=None,img_file=None)
                        break
                except Exception as e:
                    print(e)
            return text
        except Exception as e:
            print(e)

    def addRecieptEntry(self):
        with Session(self.engine) as session:
            def mkint(text,self):
                    try:
                        return int(eval(text))
                    except Exception as e:
                        print(e)
                        return
            rid=Prompt.__init2__(None,func=mkint,ptext="Reciept Id To Update with new RecieptEntries?",helpText="what is the reciept id you need to add RecieptEntries to? it must be an integer!",data=self)
            if rid in [None,]:
                return
            reciept=session.query(Reciept).filter(Reciept.RecieptId==rid).first()
            if reciept:
                print(reciept)
                try:
                    print(session.query(Billing).filter(Billing.BillingId==reciept.BillingId).first())
                except Exception as e:
                    print(e)
                while True:
                    def mkT(text,self):
                        return text
                    barcode=Prompt.__init2__(None,func=mkT,ptext="Item Barcode",helpText="Barcode to Scan for Entry!",data=self)
                    if barcode in [None,]:
                        break
                    if barcode.lower() in ['done','finish','d','f']:
                        self.render(reciept.RecieptId,session)
                        break
                    test=session.query(RecieptEntry).filter(RecieptEntry.RecieptId==reciept.RecieptId,RecieptEntry.EntryBarcode==barcode).first()
                    if test:
                        test.QtySold+=1
                        session.commit()
                        session.flush()
                        session.refresh(test)
                        print(f"Updated {test}")
                    else:
                        #entry=session.query(Entry).filter(Entry.Barcode==barcode).all()
                        entry=session.query(Entry).filter(
                                    or_(
                                        Entry.Barcode==barcode,
                                        Entry.Barcode.icontains(barcode),
                                        Entry.Code==barcode,
                                        Entry.Code.icontains(barcode),
                                        Entry.Name.icontains(barcode)
                                        )
                                    ).all()
                        ct=len(entry)
                        for num,r in enumerate(entry):
                            msg=f"{Fore.light_green}{num}/{num+1} of {Fore.light_red}{ct}{Style.reset} -> {r.seeShort()}"
                            print(msg)
                        if ct > 0:
                            def mkint(text,self):
                                try:
                                    if text == '':
                                        return 0
                                    return int(text)
                                except Exception as e:
                                    print(e)
                            which=Prompt.__init2__(None,func=mkint,ptext=f"Which Entry Would you like to use?",helpText=f"use a integer between 0-{ct-1}",data=self)
                            if which in [None,]:
                                return
                            e=entry[which]
                            qty=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Qty Sold, or Enter == 1: ",helpText="Type a value, or hit enter for default",data="float")
                            if qty in [None,]:
                                continue
                            elif qty in ['d',]:
                                qty=1
                            nre=RecieptEntry(RecieptId=reciept.RecieptId,Date=date.today(),EntryName=e.Name,EntryCode=e.Code,EntryBarcode=e.Barcode,EntryId=e.EntryId,EntryPrice=e.Price,QtySold=qty,CRV=e.CRV,Tax=e.Tax,TaxNote=e.TaxNote)
                            session.add(nre)
                            session.commit()
                            session.flush()
                            session.refresh(nre)
                            print(f"Added {nre}!")
                        else:
                            print(f"{Fore.light_red}No Such Item!{Style.reset}")

    def mkreciept(self):
        while True:
            try:
                with Session(self.engine) as session:
                    #get billing
                    billings=session.query(Billing)
                    default_billing=billings.filter(Billing.default==True).first()
                    if default_billing:
                        m=f"d=default={default_billing.BillingId}"
                    else:
                        m="default N/A"
                    billings=billings.all()
                    ct=len(billings)
                    for num,r in enumerate(billings):
                        msg=f"{Fore.light_green}{num}/{Fore.light_red}{ct}{Style.reset} -> {r}"
                        print(msg)
                    def mkint(text,self):
                        try:
                            if text == '':
                                return 'd'
                            elif text == 'd':
                                return 'd'
                            return int(text)
                        except Exception as e:
                            print(e)
                    which=Prompt.__init2__(None,func=mkint,ptext=f"Which Bussiness Would you like use[d=default]?",helpText=f"use a integer between 0-{ct-1} or d for default",data=self)
                    bill=None
                    if which in [None,]:
                        return
                    elif isinstance(which,str) and which.lower() in ['d',]:
                        if default_billing:
                            bill=default_billing
                        else:
                            raise Exception("No Default Billing Available!")
                    else:
                        bill=billings[which]
                    if bill:
                        reciept=Reciept(BillingId=bill.BillingId,Date=date.today())
                        session.add(reciept)
                        session.commit()
                        session.flush()
                        session.refresh(reciept)
                        #begin adding items by barcode or item code
                        print(reciept)
                        while True:
                            def mkT(text,self):
                                return text
                            barcode=Prompt.__init2__(None,func=mkT,ptext="Item Barcode",helpText="Barcode to Scan for Entry!",data=self)
                            if barcode in [None,]:
                                break
                            if barcode.lower() in ['done','finish','d','f']:
                                self.render(reciept.RecieptId,session)
                                break
                            test=session.query(RecieptEntry).filter(RecieptEntry.RecieptId==reciept.RecieptId,RecieptEntry.EntryBarcode==barcode).first()
                            if test:
                                test.QtySold+=1
                                session.commit()
                                session.flush()
                                session.refresh(test)
                                print(f"Updated {test}")
                            else:
                                entry=session.query(Entry).filter(
                                    or_(
                                        Entry.Barcode==barcode,
                                        Entry.Barcode.icontains(barcode),
                                        Entry.Code==barcode,
                                        Entry.Code.icontains(barcode),
                                        Entry.Name.icontains(barcode)
                                        )
                                    ).all()
                                ct=len(entry)
                                for num,r in enumerate(entry):
                                    msg=f"{Fore.light_green}{num}/{num+1} of {Fore.light_red}{ct}{Style.reset} -> {r.seeShort()}"
                                    print(msg)
                                if ct > 0:
                                    def mkint(text,self):
                                        try:
                                            if text == '':
                                                return 0
                                            return int(text)
                                        except Exception as e:
                                            print(e)
                                    which=Prompt.__init2__(None,func=mkint,ptext=f"Which Entry Would you like to use?",helpText=f"use a integer between 0-{ct-1}",data=self)
                                    if which in [None,]:
                                        return
                                    e=entry[which]
                                    qty=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Qty Sold, or Enter == 1: ",helpText="Type a value, or hit enter for default",data="float")
                                    if qty in [None,]:
                                        continue
                                    elif qty in ['d',]:
                                        qty=1
                                    nre=RecieptEntry(RecieptId=reciept.RecieptId,Date=date.today(),EntryName=e.Name,EntryCode=e.Code,EntryBarcode=e.Barcode,EntryId=e.EntryId,EntryPrice=e.Price,QtySold=qty,CRV=e.CRV,Tax=e.Tax,TaxNote=e.TaxNote)
                                    session.add(nre)
                                    session.commit()
                                    session.flush()
                                    session.refresh(nre)
                                    print(f"Added {nre}!")
                                else:
                                    print(f"{Fore.light_red}No Such Item!{Style.reset}")
                    else:
                        raise Exception("No Billing Selected!")
                    
                break
            except Exception as e:
                print(e)

    def searchBillingText(self):
        try:
            #print([{i.name:str(i.type)} for i in Billing.__table__.columns])
            textFields=[i.name for i in Billing.__table__.columns if str(i.type) == "VARCHAR"]
            #print(textFields)
            with Session(self.engine) as session:
                def mkT(text,self):
                    return text
                searchText=Prompt.__init2__(None,func=mkT,ptext=f"Search Text?",helpText=f"searches {textFields} for your text",data=self)
                if searchText in [None,]:
                    return
                query=session.query(Billing)
                f=[]
                for field in textFields:
                    try:
                        f.append(getattr(Billing,field).icontains(searchText))
                    except Exception as e:
                        print(e)
                        continue
                query=query.filter(or_(*f))
                results=query.all()
                ct=len(results)
                for num,r in enumerate(results):
                    msg=f"{Fore.light_green}{num}/{Fore.light_red}{ct}{Style.reset} -> {r}"
                    print(msg)
        except Exception as e:
            print(e)


    def setdefaultid(self):
        print(f"{Fore.light_red}Setting Default Business!{Style.reset}")
        while True:
            try:
                with Session(self.engine) as session:
                    results=session.query(Billing).all()
                    ct=len(results)
                    for num,r in enumerate(results):
                        r.default=False
                        if num%50==0:
                            session.commit()
                        msg=f"{Fore.light_green}{num}/{Fore.light_red}{ct}{Style.reset} -> {r}"
                        print(msg)
                    session.commit()
                    while True:
                        try:
                            def mkint(text,self):
                                try:
                                    if text == '':
                                        return 0
                                    return int(text)
                                except Exception as e:
                                    print(e)
                            which=Prompt.__init2__(None,func=mkint,ptext=f"Which Bussiness Would you like to set the default for?",helpText=f"use a integer between 0-{ct-1}",data=self)
                            if which in [None,]:
                                return
                            results[which].default=True
                            session.commit()
                            session.flush()
                            session.refresh(results[which])
                            msg=f"{Fore.light_green}{num}/{Fore.light_red}{ct}{Style.reset} -> {results[which]}\n{Fore.light_magenta}Default Set!{Style.reset}"

                            break
                        except Exception as e:
                            print(e)


                break
            except Exception as e:
                print(e)
        #start a while loop with exceptions forcing loop to continue
        #print businesses
        #ask for which business to set default on and set default
        #commit
        #return to menu


    def edit_business(self):
        print(f"{Fore.light_red}Editing a Business has begun!{Style.reset}")
        while True:
            try:
                with Session(self.engine) as session:
                    results=session.query(Billing).all()
                    ct=len(results)
                    for num,r in enumerate(results):
                        msg=f"{Fore.light_green}{num}/{Fore.light_red}{ct}{Style.reset} -> {r}"
                        print(msg)
                    while True:
                        try:
                            def mkint(text,self):
                                try:
                                    if text == '':
                                        return 0
                                    return int(text)
                                except Exception as e:
                                    print(e)
                            which=Prompt.__init2__(None,func=mkint,ptext=f"Which Bussiness Would you like to edit?",helpText=f"use a integer between 0-{ct-1}",data=self)
                            if which in [None,]:
                                return

                            patient=results[which]
                            fields={i.name:i.type for i in Billing.__table__.columns}
                            for i in fields:
                                while True:
                                    def mkBool(text,self):
                                        try:
                                            if text in ['y','yes','true','True','1','t']:
                                                return True
                                            else:
                                                return False
                                        except Exception as e:
                                            print(e)
                                            return None

                                    while True:
                                        editField=Prompt.__init2__(None,func=mkBool,ptext=f"Edit {i}(Type:{str(fields[i])}|OLD:{getattr(patient,i)})",helpText="answer yes or no, default is No",data=self)
                                        if editField in [None,]:
                                            return
                                        if editField == False:
                                            break
                                        else:
                                            while True:
                                                try:
                                                    def mkType(text,typeT):
                                                        try:
                                                            if str(typeT) == 'FLOAT':
                                                                return float(eval(text))
                                                            elif str(typeT) == 'INTEGER':
                                                                return int(eval(text))
                                                            elif str(typeT) == 'DATE':
                                                                return datePickerF(None)
                                                            elif str(typeT) == 'BOOLEAN':
                                                                return mkBool(text,None)
                                                            else:
                                                                return str(text)
                                                        except Exception as e:
                                                            print(e)
                                                    nvalue=Prompt.__init2__(None,func=mkType,ptext="Set New Value to?",helpText="New value for {i} with type {fields[i]}",data=fields[i])
                                                    if nvalue in [None,]:
                                                        break
                                                    print(nvalue)
                                                    setattr(results[which],i,nvalue)
                                                    session.commit()
                                                    session.flush()
                                                    session.refresh(results[which])
                                                    msg=f"{Fore.light_green}{num}/{Fore.light_red}{ct}{Style.reset} -> {results[which]}\n{Fore.light_magenta}Changed!{Style.reset}"
                                                    break
                                                except Exception as e:
                                                    print(e)
                                            break
                                    break



                            session.commit()
                            session.flush()
                            session.refresh(results[which])
                            msg=f"{Fore.light_green}{num}/{Fore.light_red}{ct}{Style.reset} -> {results[which]}\n{Fore.light_magenta}Default Set!{Style.reset}"
                            break
                        except Exception as e:
                            print(e)


                break
            except Exception as e:
                print(e)
        #start a while loop with exceptions forcing loop to continue
        #print businesses
        #ask for which business
        #loop from fields and prompt to change or leave,
        #if change, prompt for new value
        #once edits are done and committed, ask if more are needed to be edited
        #if yes, stay in while loop,else break

    def removeId(self):
        def mkint(text,self):
            try:
                if text == '':
                    return 0
                return int(text)
            except Exception as e:
                print(e)
        with Session(self.engine) as session:
            def mkList(text,data):
                try:
                    tmp=[]
                    l=text.split(",")
                    for i in l:
                        try:
                            tmp.append(int(i))
                        except Exception as e:
                            print(e)
                    return tmp
                except Exception as e:
                    print(e)
                    return None
            ids=Prompt.__init2__(None,func=mkList,ptext="BillingId's to remove",helpText="BillingId or BillingId's separated by a comma",data=self)
            if ids in [None,]:
                return
            ct=len(ids)

            for num,i in enumerate(ids):
                result=session.query(Billing).filter(Billing.BillingId==mkint(i,None)).first()
                if ct == 0:
                    print(f"{Fore.light_red}No Results were found to be default!{Style.reset}")
                else:
                    print(f"Deleting {Fore.light_yellow}{num}{Style.reset}/{Fore.light_red}{ct}{Style.reset} -> {result}")
                    session.delete(result)
                    session.commit()
            print(f"{Fore.light_green}There are {Style.reset}{Fore.light_magenta}{ct}{Style.reset}{Fore.light_green} deletions!")       

    def viewDefault(self):
        with Session(self.engine) as session:
            result=session.query(Billing).filter(Billing.default==True).all()
            ct=len(result)
            if ct == 0:
                print(f"{Fore.light_red}No Results were found to be default!{Style.reset}")
            else:
                for num,r in enumerate(result):
                    print(f"{Fore.light_yellow}{num}{Style.reset}/{Fore.light_red}{ct}{Style.reset} -> {r}")
                print(f"{Fore.light_green}There are {Style.reset}{Fore.light_magenta}{ct}{Style.reset}{Fore.light_green} results!")

    def viewAll(self):
        with Session(self.engine) as session:
            result=session.query(Billing).all()
            ct=len(result)
            if ct == 0:
                print(f"{Fore.light_red}No Results were found!{Style.reset}")
            else:
                for num,r in enumerate(result):
                    print(f"{Fore.light_yellow}{num}{Style.reset}/{Fore.light_red}{ct}{Style.reset} -> {r}")
                print(f"{Fore.light_green}There are {Style.reset}{Fore.light_magenta}{ct}{Style.reset}{Fore.light_green} results!")

    def mkBusiness(self):
        while True:
            try:
                with Session(self.engine) as session:
                    MAP={}
                    for column in Billing.__table__.columns:
                        if column.name in ['BillingId',]:
                            continue
                        def cmdMethod(text,typeT):
                            try:
                                if typeT == "FLOAT":
                                    if text == '':
                                        return 0
                                    return float(text)
                                elif typeT == "INTEGER":
                                    if text == '':
                                        return 0
                                    return int(text)
                                elif typeT == "BOOLEAN":
                                    if text in ['y','yes','true','t','1','']:
                                        return True
                                    else:
                                        return False
                                elif typeT == "DATE":
                                    if text == '':
                                        return datePickerF(None)
                                    else:
                                        try:
                                            return date(datetime.strptime(text,TIMEFORMAT)).date()
                                        except Exception as e:
                                            return datePickerF(None)
                                else:
                                    return str(text)
                            except Exception as e:
                                raise e
                        while True:
                            try:
                                msgText=f"{column.name}({str(column.type)})"
                                col=Prompt.__init2__(self,func=cmdMethod,ptext=msgText,helpText=f"add data to {column.name} field as {column.type}",data=str(column.type))
                                if col in [None,]:
                                    return
                                MAP[column.name]=col
                                break
                            except Exception as e:
                                print(e,repr(e))
                    new_billing=Billing(**MAP)
                    session.add(new_billing)
                    session.commit()
                    session.flush()
                    session.refresh(new_billing)
                break
            except Exception as e:
                print(e,f"{Fore.light_yellow}{Style.bold}...restarting!{Style.reset}")