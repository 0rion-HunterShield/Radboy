from radboy.DB.db import *
from radboy.FB.FormBuilder import *
from radboy.FB.FBMTXT import *
from radboy.DB.Prompt import *
from radboy.DB.Prompt import prefix_text
import pandas as pd
from datetime import date
import calendar
import plotext as plt
import numpy as np
from radboy.BNC.BnC import *
from scipy.fft import fft,fftfreq,rfft,rfftfreq,irfft
import tarfile
import uuid
from radboy.whatIs15 import get_bill_combinations
from radboy.DB.PayDay import EstimatedPayCalendar,setup
from radboy.DB.CoinCombo import *
from radboy.DayLog.Wavelength4Freq import HoleSize
from radboy.DayLog.TaxiFares import TaxiFare
from radboy.Compare.Compare import *
from sqlalchemy.sql import functions as func
from collections import OrderedDict
from radboy.DayLog.BhTrSa.bhtrsaa import *

class DayLogger:
    helpText=f"""
{Fore.light_red}
prefixes for #code:
        .d - DayLog id
        .b - barcode
        .c - code/shelf tag barcode/cic
{Style.reset}
{Fore.orange_red_1}{Style.bold}DayLog is your EntryChanges History, {Fore.green_yellow}should you decide to save your lists for later review{Style.reset}
{Fore.light_magenta}''|?|help{Style.reset} -{Fore.light_yellow} help info{Style.reset}
{Fore.light_magenta}q|quit{Style.reset}   -{Fore.light_yellow} quit{Style.reset}
{Fore.light_magenta}b|back{Style.reset}    -{Fore.light_yellow} back{Style.reset}
{Fore.light_magenta}rm|del{Style.reset}   -{Fore.light_yellow} remove a DayLog{Style.reset}
{Fore.light_magenta}a|add|+{Style.reset}   -{Fore.light_yellow} store todays data values as a DayLog snapshot{Style.reset}
{Fore.light_magenta}l|list|*{Style.reset}  -{Fore.light_yellow} list * entries{Style.reset}
{Fore.light_magenta}ld|list_date{Style.reset}  -{Fore.light_yellow} list * entries from DayLogDate from prompt{Style.reset}
{Fore.light_magenta}'ldr','list date range','ls dt rng' -{Fore.light_yellow}list entry totals for time between dates{Style.reset}
{Fore.light_magenta}cd|clear_date{Style.reset}  -{Fore.light_yellow} clear * entries from DayLogDate from prompt for date{Style.reset}
{Fore.light_magenta}reset DayLog{Style.reset}  -{Fore.light_yellow} clear * entries from DayLogDate{Style.reset}
{Fore.light_magenta}ed|export_date{Style.reset}  -{Fore.light_yellow} export * entries from DayLogDate from prompt{Style.reset}
{Fore.light_magenta}ea|export_all{Style.reset}  -{Fore.light_yellow} export * entries from DayLogDate from prompt{Style.reset}
{Fore.light_magenta}ec|export_code{Style.reset}  -{Fore.light_yellow} export * entries from DayLogDate by Barcode from prompt{Style.reset}
{Fore.light_magenta}lc|list_code{Style.reset}  -{Fore.light_yellow} export * entries from DayLogDate by Barcode from prompt{Style.reset}
{Fore.light_magenta}ecd|export_code_date{Style.reset}  -{Fore.light_yellow} export * entries from DayLogDate by Barcode and Date from prompt{Style.reset}
{Fore.light_magenta}lcd|list_code_date{Style.reset}  -{Fore.light_yellow} list * entries from DayLogDate by Barcode and Date from prompt{Style.reset}
{Fore.light_sea_green}sch|search{Style.reset}  -{Fore.medium_violet_red} search DayLog Fields DayLog {Fore.light_magenta}Barcode,Name,Code,Note,Description{Fore.medium_violet_red} for data relating to search term, with DateMetrics Data included [{Fore.light_steel_blue}if Any].{Style.reset}
{Fore.light_sea_green}sch ohd|search only holidays{Style.reset}  -{Fore.medium_violet_red} search DayLog Fields DayLog {Fore.light_magenta}Barcode,Name,Code,Note,Description{Fore.medium_violet_red} for data relating to search term, with DateMetrics Data included [{Fore.light_steel_blue}if Any]. by holiday date{Style.reset}
{Fore.light_sea_green}coin{Style.reset}  -{Fore.medium_violet_red}all possible coins/bills combos as a list restricted to what you have{Style.reset}
{Back.green_4} {Fore.black}Reciepts {Style.reset} 
{Back.turquoise_4} {Fore.black}'review reciept','rvwrcpt','rvw rcpt' -{Fore.dark_red_1}Lookup a receipt by its urid {Style.reset}
{Back.turquoise_4} {Fore.black}'lsa rcpt','list all rcpt','ls*rcpt' -{Fore.dark_red_1}List All Reciepts {Style.reset}
{Back.turquoise_4} {Fore.black}'lsabv','ls abv' -{Fore.dark_red_1}List All Reciepts above/equal to a value {Style.reset}
{Back.turquoise_4} {Fore.black}'lsblw','ls blw' -{Fore.dark_red_1}List All Reciepts below/or equal to value{Style.reset}
{Back.turquoise_4} {Fore.black}'lsddr rcpt','ls d dr rcpt','list date/daterange rcpt' -{Fore.dark_red_1}List Reciepts for a date or date range {Style.reset}
{Back.turquoise_4} {Fore.black}'sft','search for text','search receipt for text','srft'{Fore.dark_red_1}- search reciepts for text{Style.reset}
{Back.deep_pink_4c} {Fore.black}'rm rcpt','rmrcpt','remove receipt'{Fore.navy_blue}- delete a receipt and possibly related DayLogs{Style.reset}
{Back.turquoise_2} {Fore.black}'ed rcpt','edrcpt','edit receipt','edt rcpt','edtrcpt'{Fore.dark_blue}- edit a receipt's data{Style.reset}
{Back.deep_pink_4c} {Fore.black}'clear_all_receipts','clear all reciepts' {Back.grey_15}{Fore.dark_orange_3b} - Completely delete {Style.underline}ALL{Style.res_underline} reciepts.{Style.reset}

{Fore.light_magenta}Analisys{Style.reset}
'avg field','af', - prompt for a numeric field total an average for code/barcode
fxtbl - update table with correct columns
'avg field graph','afg' - create a graph of avg field
'fft','fast fourier transform' - create fast fourier transform of the data and graph data
'restore bckp','rfb' - restore DayLogs from backup file
{Fore.light_magenta}"compare product","p1==p2?","compare"{Fore.medium_violet_red}compare two products qty and price{Style.reset}
{Fore.light_magenta}Banking/{Fore.medium_violet_red}Petty-Cash{Style.reset}
{Fore.light_sea_green}'bnc','21','banking and cashpool','banking_and_cashpool','bank','piggy-bank' {Fore.light_steel_blue}- Banking and CashPool tools{Style.reset}
{Fore.light_sea_green}'prc chng','prcchng','prc.chng','prc_chng','prc-chng','price change' {Fore.light_steel_blue}- detect price change over a date-range{Style.reset}
{Fore.light_sea_green}'cr','ttl spnt','ttlspnt','cost report','cst rpt'{Fore.light_steel_blue}- generate an expense/cost report for a date-range{Style.reset}
{Fore.light_sea_green}'epdc','estimated pay day calendar'{Fore.light_steel_blue}- review your estimated paydays{Style.reset}
{Fore.light_sea_green}'taxi fare','calc taxi fare','ctf','taxi'{Fore.light_steel_blue}- Calculate Taxi Fares{Style.reset}
{Fore.light_sea_green}'faraday','holesize','frdy hs'{Fore.light_steel_blue}- get wavelength needed for a frequency/for making a faraday cage {Fore.orange_red_1}[Indirectly Related]{Style.reset}
{Fore.light_sea_green}'bhtrsa','business hours tax rates scheduled and appointments'{Fore.light_steel_blue}- Business Hours, Tax Rates, Scheduled and Appointments {Fore.orange_red_1}[Indirectly Related]{Style.reset}
"""
    def listAllDL(self):
        with Session(self.engine) as session:
            results=session.query(DayLog).all()
            ct=len(results)
            if ct == 0:
                print(f"{Style.bold}{Fore.light_red}No Items!{Style.reset}")
            for r in results:
                print(r)

    def clear_all_receipts(self):
        code=''.join([str(random.randint(0,9)) for i in range(10)])
        verification_protection=detectGetOrSet("Protect Reciepts From Delete",code,setValue=False,literal=True)
        while True:
            try:
                really=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Do You really want to delete everything in UniqueRecieptIdInfo?",helpText="yes or no boolean,default is NO",data="boolean")
                if really in [None,]:
                    return
                elif really in ['d',False]:
                    return
                else:
                    pass
                really=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"To {Fore.orange_red_1}Delete everything completely,{Fore.light_steel_blue}what is today's date?[{'.'.join([str(int(i)) for i in datetime.now().strftime("%m.%d.%y").split(".")])}]{Style.reset}",helpText="type y/yes for prompt or type as m.d.Y",data="datetime")
                if really in [None,'d']:
                    return
                today=datetime.today()
                if really.day == today.day and really.month == today.month and really.year == today.year:
                    really=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Please type the verification code {Style.reset}'{DayLog.cfmt(None,verification_protection)}'?",helpText=f"type '{DayLog.cfmt(None,verification_protection)}' to finalize!",data="string")
                    if really in [None,]:
                        return
                    elif really in ['d',False]:
                        return
                    elif really == verification_protection:
                        break
                else:
                    pass
            except Exception as e:
                print(e)
            with Session(ENGINE) as session:
                x=session.query(UniqueRecieptIdInfo).delete()
                session.commit()



    def display_results(self,results,ct,returnable=False,short=False):
        if ct < 1:
            print(f"{Fore.light_red}No Results!{Style.reset}")
            return
        else:
            if returnable:
                msg_text_whole=[]
            for num, i in enumerate(results):
                if not short:
                    msg=f"{Fore.cyan}{num}/{Fore.light_cyan}{num+1} {Fore.light_sea_green}of {ct} -> {Fore.green_yellow}{i}{Style.reset}"
                else:
                    msg=f"{Fore.cyan}{num}/{Fore.light_cyan}{num+1} {Fore.light_sea_green}of {ct} -> {Fore.green_yellow}{i.seeShort()}{Style.reset}"
                if returnable:
                    msg_text_whole.append(msg)
                while True and not returnable:
                    print(msg)
                    if not returnable:
                        if ((num % 20) == 0 and num > 0):
                            page=Prompt.__init2__(None,func=FormBuilderMkText,ptext="next?",helpText="y/n/skip page[s]",data="string")
                            if page in [None,]:
                                return
                            elif page.lower() in ['d','y','yes','1','true']:
                                break
                            elif page.lower() in ['n','0','no','false']:
                                continue
                        else:
                            break

            if returnable:
                return '\n'.join(msg_text_whole)


    def edit_reciept(self):
        with Session(ENGINE) as session:
            urid=Prompt.__init2__(None,func=FormBuilderMkText,ptext="reciept urid to Edit/Modify:",helpText="id of reciept to edit/modify",data="integer")
            if urid in ['d',None]:
                return
            elif isinstance(urid,int):
                reciept=session.query(UniqueRecieptIdInfo).filter(UniqueRecieptIdInfo.urid==urid).first()
                if reciept is not None:
                    print(reciept)
                    searchStr=f"[UniqueRecieptIdInfo(urid={urid})]"
                    excludes=["DTOE","urid"]
                    fields={i.name:{'type':str(i.type).lower(),'default':getattr(reciept,i.name)} for i in reciept.__table__.columns if i.name not in excludes}
                    fd=FormBuilder(data=fields)
                    if fd is not None:
                        try:
                            session.query(UniqueRecieptIdInfo).filter(UniqueRecieptIdInfo.urid==urid).update(fd)
                            session.commit()
                            session.refresh(reciept)
                            print(reciept)
                        except Exception as e:
                            print(e)
                            session.rollback()
                else:
                    print(f"{Fore.light_red}No Such UniqueRecieptIdInfo(urid={Fore.light_magenta}{urid}{Fore.light_red}){Style.reset}")

    def rm_receipt(self):
        with Session(ENGINE) as session:
            urid=Prompt.__init2__(None,func=FormBuilderMkText,ptext="reciept urid to Delete:",helpText="id of reciept to delete",data="integer")
            if urid in ['d',None]:
                return
            elif isinstance(urid,int):
                reciept=session.query(UniqueRecieptIdInfo).filter(UniqueRecieptIdInfo.urid==urid).first()
                if reciept is not None:
                    print(reciept)
                    searchStr=f"[UniqueRecieptIdInfo(urid={urid})]"
                    session.delete(reciept)
                    session.commit()
                    search_and_remove_related=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Search for DayLog's whose name includes '{searchStr}'",data="boolean")
                    if search_and_remove_related in ['d',None,False]:
                        return
                    else:
                        to_delete=session.query(DayLog).filter(DayLog.Name.icontains(searchStr)).all()
                        ct_toDelete=len(to_delete)
                        if ct_toDelete == 0:
                            print(f"{Fore.light_red}Nothing to Delete!{Style.reset}")
                            return
                        helpText=self.display_results(to_delete,ct_toDelete,returnable=True,short=True)
                        print(helpText)
                        doDelete=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Delete which index(es)[A Comma Separated List]: ",helpText=helpText,data="list")
                        if doDelete in [None,'d',[]]:
                            return
                        else:
                            while True:
                                try:
                                    xct=len(doDelete)
                                    if xct == 0:
                                        print("Nothing was selected to delete!")
                                        break
                                    for num,i in enumerate(doDelete):
                                        try:
                                            index=int(i)
                                            print(f"{Fore.light_yellow}{num}/{Fore.green_yellow}{num+1}{Fore.cyan} of {xct}: {Fore.light_red}Deleted -> {to_delete[index]}")
                                            session.delete(to_delete[index])
                                            session.commit()
                                        except Exception as ee:
                                            print(ee)
                                    return
                                except Exception as e:
                                    print(e)
                        
                        session.commit()
                        session.flush()

    def ls_all_receipts(self):
        '''list all reciepts'''
        with Session(ENGINE) as session:
            query=session.query(UniqueRecieptIdInfo)
            results=query.all()
            ct=len(results)
            self.display_results(results,ct)
            

    def ls_dt_dr_rcpts(self):
         with Session(ENGINE) as session:
            query=session.query(UniqueRecieptIdInfo)
            date_from=Prompt.__init2__(None,func=FormBuilderMkText,ptext="From Date:",helpText="from date",data="datetime")
            print(date_from)
            
            if date_from in ['d',None]:
                return
            date_to=Prompt.__init2__(None,func=FormBuilderMkText,ptext="To Date:",helpText="from date",data="datetime")
            if date_to in ['d',None]:
                return
            print(date_to,date_from,date_to==date_from)

            if date_from == date_to:
                query=query.filter(func.DATE(UniqueRecieptIdInfo.DTOE)==date(date_from.year,date_from.month,date_from.day))
            else:
                query=query.filter(and_(UniqueRecieptIdInfo.DTOE>=date_from,UniqueRecieptIdInfo.DTOE<=date_to))
            results=query.all()
            ct=len(results)
            self.display_results(results,ct)

    def search_rcpts_for_text(self):
        with Session(ENGINE) as session:
            search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What are you looking for?",helpText="text to search for",data="string")
            if search in [None,'d']:
                return

            query=session.query(UniqueRecieptIdInfo)
            textfields=["string","text","varchar"]
            excludes=["urid","DTOE"]
            fields=[str(i.name) for i in UniqueRecieptIdInfo.__table__.columns if i.name not in excludes and str(i.type).lower() in textfields]
            q=[]
            for i in fields:
                q.append(getattr(UniqueRecieptIdInfo,i).icontains(search))

            results=query.filter(or_(*q,and_(*q))).all()
            ct=len(results)
            self.display_results(results,ct)


    def ls_rcpt_abv_or_equal_to(self):
        with Session(ENGINE) as session:
            search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Above?",helpText="a value to search above",data="float")
            if search in [None,'d']:
                return

            query=session.query(UniqueRecieptIdInfo)
            textfields=["float","integer",]
            excludes=["urid","DTOE"]
            fields=[str(i.name) for i in UniqueRecieptIdInfo.__table__.columns if i.name not in excludes and str(i.type).lower() in textfields]
            q=[]
            for i in fields:
                q.append(getattr(UniqueRecieptIdInfo,i)>=search)

            results=query.filter(or_(*q,and_(*q))).all()
            ct=len(results)
            self.display_results(results,ct)

    def ls_rcpt_blw_or_equal_to(self):
        with Session(ENGINE) as session:
            search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Below?",helpText="a value to search Below",data="float")
            if search in [None,'d']:
                return

            query=session.query(UniqueRecieptIdInfo)
            textfields=["float","integer",]
            excludes=["urid","DTOE"]
            fields=[str(i.name) for i in UniqueRecieptIdInfo.__table__.columns if i.name not in excludes and str(i.type).lower() in textfields]
            q=[]
            for i in fields:
                q.append(getattr(UniqueRecieptIdInfo,i)<=search)

            results=query.filter(or_(*q,and_(*q))).all()
            ct=len(results)
            self.display_results(results,ct)

    def reviewReciept(self):
        with Session(ENGINE) as session:
            urid=Prompt.__init2__(None,func=FormBuilderMkText,ptext="reciept urid:",helpText="id of reciept to view data for",data="integer")
            if urid in ['d',None]:
                return
            elif isinstance(urid,int):
                reciept=session.query(UniqueRecieptIdInfo).filter(UniqueRecieptIdInfo.urid==urid).first()
                if reciept is not None:
                    print(reciept)


    def clearAllDL(self):
        code=''.join([str(random.randint(0,9)) for i in range(10)])
        verification_protection=detectGetOrSet("Protect From Delete",code,setValue=False,literal=True)
        while True:
            try:
                really=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Do You really want to delete everything in DayLog?",helpText="yes or no boolean,default is NO",data="boolean")
                if really in [None,]:
                    return
                elif really in ['d',False]:
                    return
                else:
                    pass
                really=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"To {Fore.orange_red_1}Delete everything completely,{Fore.light_steel_blue}what is today's date?[{'.'.join([str(int(i)) for i in datetime.now().strftime("%m.%d.%y").split(".")])}]{Style.reset}",helpText="type y/yes for prompt or type as m.d.Y",data="datetime")
                if really in [None,'d']:
                    return
                today=datetime.today()
                if really.day == today.day and really.month == today.month and really.year == today.year:
                    really=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Please type the verification code {Style.reset}'{DayLog.cfmt(None,verification_protection)}'?",helpText=f"type '{DayLog.cfmt(None,verification_protection)}' to finalize!",data="string")
                    if really in [None,]:
                        return
                    elif really in ['d',False]:
                        return
                    elif really == verification_protection:
                        break
                else:
                    pass
            except Exception as e:
                print(e)
        with Session(self.engine) as session:
            results=session.query(DayLog).all()
            ct=len(results)
            if ct == 0:
                print(f"{Style.bold}{Fore.light_red}No Items to Clear!{Style.reset}")
            else:
                print(f"{Fore.light_magenta}Deleting {Fore.light_steel_blue}{ct}{Fore.light_magenta} Logs.{Style.reset}")
                r=session.query(DayLog).delete()
                session.commit()
                session.flush()
                print(r)
        code=''.join([str(random.randint(0,9)) for i in range(10)])
        verification_protection=detectGetOrSet("Protect From Delete",code,setValue=True,literal=True)

    def restoreDayLogs(self):
        filename=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What backup do you wish to use?",helpText="a file name ending with *.tar.gz",data="string")
        if filename in [None,]:
            return
        
        print('s1')
        tmp=Path("tmp")
        if tmp.exists():
            shutil.rmtree(tmp)
        
        print('s2')
        with tarfile.open(filename,"r") as tar:
            tar.extract("codesAndBarcodes.db",tmp)
        dbf="sqlite:///"+str("tmp/codesAndBarcodes.db")
        
        print(dbf)
        #import sqlite3
        #z=sqlite3.connect(filename)
        #print(z)
        print('s3')
        ENG=create_engine(dbf)
        with Session(ENG) as bck,Session(ENGINE) as session:
            src=bck.query(DayLog).all()
            srcCt=len(src)
            x=session.query(DayLog).delete()
            session.commit()
            for num,x in enumerate(src):
                msg=f"""{Fore.light_sea_green}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{srcCt} - {Fore.grey_50}{x.Barcode}|{x.Code}|{x.Name}"""
                dl=DayLog(**{i.name:getattr(x,i.name) for i in x.__table__.columns})
                session.add(dl)
                print(msg)
                if num % 50 == 0:
                    session.commit()
            session.commit()
        print('s4')
        shutil.rmtree(tmp)

    def addToday(self):
        with Session(self.engine) as session:
            recieptID=Prompt.__init2__(None,func=FormBuilderMkText,ptext="reciept id info (If Any)",helpText="anything to identify the reciept",data="string")
            if recieptID is None:
                return
            elif recieptID in ['d',]:
                recieptID=f'No_Receipt_ID_Provided:{datetime.now().strftime("%m/%d/%Y @ %H:%M:%S")}:Grouping UUID:{uuid.uuid1()}'
            state=f"{Fore.orange_red_1}{Style.bold}will be{Style.reset}"
            rcpt_msg=f'{Fore.light_sea_green}RecieptId({Fore.light_yellow}"{recieptID}"{Fore.light_sea_green}) {state} embedded into DayLog.Name for grouped searches!{Style.reset}'
            print(rcpt_msg)
            results=session.query(Entry).filter(Entry.InList==True).all()
            ct=len(results)
            if ct < 1:
                print(f"{Fore.light_red}No Items InList==True!{Style.reset}")
            else:
                for num,entry in enumerate(results):
                    print(f"Adding Log For\n{'-'*12}{Fore.green}{num}{Style.reset}/{Fore.red}{ct}{Style.reset} -> {entry}")
                    #ndl=DayLog()
                    d={}
                    for column in Entry.__table__.columns:
                        d[column.name]=getattr(entry,column.name)
                    ndl=DayLog(**d)
                    ndl.Name=f"{ndl.Name}[{recieptID}]"
                    session.add(ndl)
                    if num % 25 == 0:
                        session.commit()
                session.commit()
                session.flush()
                print(f"{Fore.light_magenta}Done Adding Log Data!{Style.reset}")
            state=f"{Fore.orange_red_1}{Style.bold}has been{Style.reset}"
            rcpt_msg=f'{Fore.light_sea_green}RecieptId({Fore.light_yellow}"{recieptID}"{Fore.light_sea_green}) {state} embedded into DayLog.Name for grouped searches!{Style.reset}'
            print(rcpt_msg)

    def searchTags(self):
        with Session(ENGINE) as session:
            tags=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What do you want to search in DayLog?:",helpText="A Comma Separated List of Tag Names",data="list")
            if tags in ['d',None]:
                tags=[]
            for tag in tags:
                search=session.query(DayLog).filter(
                    or_(DayLog.Tags.icontains(tag),
                        DayLog.Barcode.icontains(tag),
                        DayLog.Name.icontains(tag),
                        DayLog.Code.icontains(tag),
                        DayLog.Note.icontains(tag),
                        DayLog.Description.icontains(tag)
                        )
                ).order_by(DayLog.Barcode,DayLog.DayLogDate.desc()).all()
                ct=len(search)
                if ct == 0:
                    print("Nothing was Found")
                for num,log in enumerate(search):
                    while True:
                        datemetrics=session.query(DateMetrics).filter(DateMetrics.date==log.DayLogDate).first()
                        if not datemetrics:
                            datemetrics=f'{Fore.orange_red_1}No DateMetrics Data For {Fore.light_magenta}{log.DayLogDate}{Fore.orange_red_1} Available!{Style.reset}'
                        next_holi=next_holiday(today=log.DayLogDate)
                        UNTIL=next_holi[0]-log.DayLogDate
                        msg=f'''{num}/{num+1} of {ct} -{log}{datemetrics}
    {Fore.medium_violet_red}Next Holiday:{Fore.light_steel_blue}{next_holi[1]}{Style.reset}
    {Fore.medium_violet_red}Next Holiday Date:{Fore.light_steel_blue}{next_holi[0]}{Style.reset}
    {Fore.light_yellow}Time{Fore.medium_violet_red} Until Holiday:{Fore.light_steel_blue}{UNTIL}{Style.reset}
    {Fore.light_magenta}{log.DayLogDate}{Fore.medium_violet_red} Is Holiday:{Fore.light_steel_blue}{log.DayLogDate in holidays.USA(years=log.DayLogDate.year)}{Style.reset}
    {Fore.medium_violet_red}Holiday Name:{Fore.light_steel_blue}{holidays.USA(years=log.DayLogDate.year).get(log.DayLogDate.strftime("%m/%d/%Y"))}{Style.reset}
    {Fore.magenta}TAG/INDEX/Count of TTL:{Fore.light_red} {tag} - {num}/{num+1} of {ct}{Style.reset}
    {Fore.light_sea_green}Name:{Fore.green_yellow}{log.Name}{Style.reset}
    {Fore.light_sea_green}Barcode:{Fore.green_yellow}{log.Barcode}{Style.reset}
    {Fore.light_sea_green}Code:{Fore.green_yellow}{log.Code}{Style.reset}
    {Fore.light_green}DOE:{Fore.light_magenta}{log.DayLogDate}{Style.reset}'''
                        print(msg)
                        editKeys=['ed','edit','modify','e','chng','change','ch']
                        remind=['remind','rmnd','refresh','rfrsh']
                        rmkeys=['delete log',]
                        nxt=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Next?",helpText=f"{Fore.light_sea_green}hit enter for next/{Fore.dark_goldenrod}to edit current{editKeys}/{Fore.light_magenta}to re-display the current log{remind}/{Fore.light_red}to delete{rmkeys}{Style.reset}\n{'.'*os.get_terminal_size().columns}",data="string")

                        if nxt in [None,]:
                            return
                        elif nxt.lower() in ['d','next','nxt']:
                            pass
                        elif nxt.lower() in editKeys:
                            excludes=['DayLogId','EntryId','TimeStamp','DayLogDate']
                            data={i.name:{'default':getattr(log,i.name),'type':str(i.type)} for i in log.__table__.columns if i.name not in excludes}
                            chngd=FormBuilder(data=data)
                            if chngd in [None,]:
                                print("Nothing was done!")
                                pass
                            session.query(DayLog).filter(DayLog.DayLogId==log.DayLogId).update(chngd)
                            session.commit()
                            #for additional functionality
                        elif nxt.lower() in remind:
                            continue
                        elif nxt.lower() in rmkeys:
                            code=''.join([str(random.randint(0,9)) for i in range(10)])
                            verification_protection=detectGetOrSet("Protect DayLog From Delete",code,setValue=False,literal=True)
                            while True:
                                try:
                                    really=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Do You really want to delete this DayLog?",helpText="yes or no boolean,default is NO",data="boolean")
                                    if really in [None,]:
                                        return
                                    elif really in ['d',False]:
                                        return
                                    else:
                                        pass
                                    really=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"To {Fore.orange_red_1}Delete DayLog completely,{Fore.light_steel_blue}what is today's date?[{'.'.join([str(int(i)) for i in datetime.now().strftime("%m.%d.%y").split(".")])}]{Style.reset}",helpText="type y/yes for prompt or type as m.d.Y",data="datetime")
                                    if really in [None,'d']:
                                        return
                                    today=datetime.today()
                                    if really.day == today.day and really.month == today.month and really.year == today.year:
                                        really=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Please type the verification code {Style.reset}'{DayLog.cfmt(None,verification_protection)}'?",helpText=f"type '{DayLog.cfmt(None,verification_protection)}' to finalize!",data="string")
                                        if really in [None,]:
                                            return
                                        elif really in ['d',False]:
                                            return
                                        elif really == verification_protection:
                                            break
                                    else:
                                        pass
                                except Exception as e:
                                    print(e)
                            session.delete(log)
                            session.commit()
                        else:
                            pass
                        break



    def updateTable(engine):
        tableName="DayLog"
        fields=[]
        with Session(ENGINE) as session:
            for field in Entry.__table__.columns:
                fields.append(text(f"ALTER TABLE {tableName} ADD {field.name} {field.type}"))
            for update in fields:
                try:
                    session.execute(update)
                except Exception as e:
                    print(e)
            session.commit()

    def addTodayP(engine,addTag=False,tags=[]):
        if addTag == True:
            tags=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What tags do you want to add to the DayLog?:",helpText="A Comma Separated List of Tag Names",data="list")
            if tags in ['d',None]:
                tags=[]
            #tags=[''.join([ii.replace("'","_1x_quote_") for ii in i]) for i in tags]               
        print(f"{Fore.light_magenta}Backing Data up to DayLog{Style.reset}")
        with Session(engine) as session:
            results=session.query(Entry).filter(Entry.InList==True).all()
            ct=len(results)
            if ct < 1:
                print(f"{Fore.light_red}No Items InList==True!{Style.reset}")
            else:
                for num,entry in enumerate(results):
                    print(f"Adding Log For\n{'-'*12}{Fore.green}{num}{Style.reset}/{Fore.red}{ct}{Style.reset} -> {entry}")
                    #ndl=DayLog()
                    d={}
                    for column in Entry.__table__.columns:
                        d[column.name]=getattr(entry,column.name)
                    if d.get('Tags')==None:
                        d['Tags']='[]'
                    if addTag:
                        for tag in tags:
                            try:
                                tags_tmp=json.loads(d.get("Tags"))
                            except Exception as e:
                                print(e)
                                tags_tmp=[]
                            if tag not in tags_tmp:
                                tags_tmp.append(tag)
                            d['Tags']=json.dumps(tags_tmp)
                    ndl=DayLog(**d)
                    session.add(ndl)
                    if num % 25 == 0:
                        session.commit()
                session.commit()
                session.flush()
                print(f"{Fore.light_magenta}Done Adding Log Data!{Style.reset}")

    def clearDate(self,month=None,day=None,year=None):
        d=self.dateParser()
        with Session(self.engine) as session:
            results=session.query(DayLog).filter(DayLog.DayLogDate==d).all()
            ct=len(results)
            #results=session.query(DayLog).all()
            if ct == 0:
                print(f"{Style.bold}{Fore.light_red}No Items to Clear!{Style.reset}")
            for num,r in enumerate(results):
                print(f"clearing {num}/{ct} -> {r}")
                session.delete(r)
                if num % 25 == 0:
                    session.commit()
            session.commit()

    def listDateRange(self):
        date_from=Prompt.__init2__(None,func=FormBuilderMkText,ptext="From Date:",helpText="from date",data="datetime")
        print(date_from)
        if date_from in ['d',None]:
            return
        date_to=Prompt.__init2__(None,func=FormBuilderMkText,ptext="To Date:",helpText="from date",data="datetime")
        if date_to in ['d',None]:
            return

        occurances=Prompt.__init2__(None,func=FormBuilderMkText,ptext="All Fields Qty Above or Equal To How Many(d=2)?",helpText="above or == To this number",data="integer")
        if occurances in [None,]:
            return
        elif occurances in ['d',]:
            occurances=2

        occurances_max=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"All Fields Qty Below or Equal To How Many(d={sys.maxsize})?",helpText="Below or == To this number",data="integer")
        if occurances_max in [None,]:
            return
        elif occurances_max in ['d',]:
            occurances_max=sys.maxsize

        excludes=['EntryId','DayLogId','TimeStamp'
"CaseCount",
"UnitsDeep",
"ShelfCount",
"UnitsHigh",
"PalletCount",]
        fields_for_total=[
        "Shelf",
        "BackRoom",
        "Display_1",
        "Display_2",
        "Display_3",
        "Display_4",
        "Display_5",
        "Display_6",
        "ListQty",
        "SBX_WTR_DSPLY",
        "SBX_CHP_DSPLY",
        "SBX_WTR_KLR",
        "FLRL_CHP_DSPLY",
        "FLRL_WTR_DSPLY",
        "WD_DSPLY",
        "CHKSTND_SPLY",
        "Distress",
        ]
        #fields_for_total=[i.name for i in DayLog.__table__.columns if str(i.type).lower() == "integer" and str(i.name) not in excludes]

        with Session(ENGINE) as session:
            code=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What are looking for(Enter == ALL):",helpText="barcode|code|name",data="string")
            if code in [None,]:
                return
            if code in ['d',]:
                query=session.query(DayLog).filter(DayLog.DayLogDate.between(date_from,date_to)).all()
            else:
                query=session.query(DayLog).filter(
                    DayLog.DayLogDate.between(date_from,date_to),
                        or_(
                        DayLog.Barcode.icontains(code),
                        DayLog.Code.icontains(code),
                        DayLog.Name.icontains(code))
                ).all()
                
            totals={}
            totals_dl={}
            skip=False

            max_cost=0
            min_cost=sys.maxsize
            min_date=None
            max_date=None
            totals_dl2={}

            for num,i in enumerate(query):
                if i.EntryId not in totals:
                    #total from fields not occurances
                    totals[i.EntryId]=0
                    totals_dl[i.EntryId]=i
                for x in fields_for_total:
                    print(f"{Fore.light_green}Totaling: {Style.reset}",getattr(i,x),x,f'{Fore.light_red}Field for Total{Style.reset}')
                    totals[i.EntryId]+=getattr(i,x)
                    if i.DayLogId in totals_dl2:
                        totals_dl2[i.DayLogId]+=getattr(i,x)
                    else:
                        totals_dl2[i.DayLogId]=getattr(i,x)

                if totals_dl2[i.DayLogId] > max_cost:
                    max_cost=totals_dl2[i.DayLogId]
                    max_date=i.DayLogDate
                if totals_dl2[i.DayLogId] < min_cost:
                    min_cost=totals_dl2[i.DayLogId]
                    min_date=i.DayLogDate
                if skip:
                    continue
                next2=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{i}\n{Fore.light_magenta}Final Total:{Fore.light_steel_blue}{totals[i.EntryId]}{Style.reset} next?",helpText="<Enter>/y/yes/n/no/s or -1(skip prompt and print info)",data="string")
                if next2 in [None,]:
                    return
                elif next2.lower() in ['f','n','no','0','false']:
                    return
                elif next2.lower() in ['s','-1']:
                    skip=True
                else:
                    pass

            ct=len(totals)
            avgs={}
            avg_cost=0
            avg_qty=0
            fields={"Shelf":0,
            "BackRoom":0,
            "Display_1":0,
            "Display_2":0,
            "Display_3":0,
            "Display_4":0,
            "Display_5":0,
            "Display_6":0,
            "ListQty":0,
            "SBX_WTR_DSPLY":0,
            "SBX_CHP_DSPLY":0,
            "SBX_WTR_KLR":0,
            "FLRL_CHP_DSPLY":0,
            "FLRL_WTR_DSPLY":0,
            "WD_DSPLY":0,
            "CHKSTND_SPLY":0,
            "Distress":0,
            }
            ct=len(totals)
            for num,i in enumerate(totals):
                extra_keys=[]
                if totals_dl[i].Price == None:
                    totals_dl[i].Price=0
                if totals_dl[i].CaseCount == None:
                    totals_dl[i].CaseCount=1
                query=session.query(DayLog).filter(DayLog.EntryId==i)
                df=pd.read_sql_query(query.statement,session.bind)
                for k in fields.keys():
                    extra_keys.append(f'Price*AvgQty@{k}{Fore.light_yellow}[Avg Value]{Fore.orange_red_1}')
                    df[f'Price*AvgQty@{k}{Fore.light_yellow}[Avg Value]{Fore.orange_red_1}']=df['Price']*df[k]
                    df[f'Price*AvgQty@{k}{Fore.light_yellow}[Avg Value]{Fore.orange_red_1}']=df[f'Price*AvgQty@{k}{Fore.light_yellow}[Avg Value]{Fore.orange_red_1}'].mean()
                avg_cost=df['Price'].mean()
                
                total_price=totals[i]*totals_dl[i].Price
                total_price_per_case=totals[i]*(totals_dl[i].Price*totals_dl[i].CaseCount)
                msg=f"""{Fore.light_cyan}{num}/{num+1} of {ct} - {totals_dl[i].seeShort()} {Fore.light_magenta}Total{Fore.green_yellow}={Fore.light_sea_green}{totals[i]}, {Fore.light_cyan}Total Price({totals_dl[i].Price}) Per Unit(1):{total_price}, {Fore.orange_red_1}Total Price(One={totals_dl[i].Price}) Per Case({totals_dl[i].CaseCount}):{total_price_per_case}{Style.reset}
\t{Fore.light_green}- Avg Price:{Fore.light_steel_blue}{avg_cost}
\t{Fore.light_sea_green}- Avg Qty: {Fore.light_cyan}
{df[[i for i in fields.keys()]].mean()}{Style.reset}
{Fore.light_magenta}{df[extra_keys].sum()}{Style.reset}
{Fore.medium_violet_red}Data Set Length:{Fore.light_magenta}{len(df['EntryId'])}{Style.reset}
"""
                
                '''
                for k in fields:
                    try:
                        print(f"\t- Avg Qty {k}:{float(df[[i for i in fields.keys()]].mean().iloc[0])}")
                    except Exception as e:
                        print(e)
                '''
                print(f"""{Fore.light_magenta}{num}/{Fore.light_yellow}{num+1} of {Fore.medium_violet_red}{ct}{Fore.orange_red_1} Max Cost:{Fore.light_steel_blue}{max_cost} on {Fore.light_magenta}{max_date}
{Fore.green_yellow}Min Cost:{Fore.light_sea_green}{min_cost} on {Fore.light_magenta}{min_date}{Style.reset}
                    """)
                if totals[i] >= occurances and totals[i] <= occurances_max: 
                    print(msg)
    def f_orderByTotalValue(self,query):
        #just a dummy extra filtering can be here
        return query

    def TotalSpent(self):
        local_start=datetime.now()
        LookUpState=db.detectGetOrSet('list maker lookup order',False,setValue=False,literal=False)
        if not isinstance(LookUpState,bool):
            LookUpState=db.detectGetOrSet('list maker lookup order',False,setValue=True,literal=False)
        '''
        if LookUpState == True:
            results=results_query.order_by(db.Entry.Timestamp.asc()).all()
        else:
            results=results_query.order_by(db.Entry.Timestamp.desc()).all()
        '''
        #cost report
        #export results Both text and xlsx
        #yes no
        orderByTotalValue=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Order Final Results by total qty value[y/N]:",helpText="yes or no; default is No.",data="boolean")
        
        if orderByTotalValue in [None,]:
            return
        elif orderByTotalValue in ['d',]:
            orderByTotalValue=False

        reverse=True
        if orderByTotalValue:
            reverse=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Order Asc(True/Yes/First Line Newest or Smallest & Last Line Biggest or Oldest)[Default]/Desc(false/no/First Line Oldest or Biggest & Last Line Newest or Smallest):",helpText="yes or no; default is yes.",data="boolean")
            
            if reverse in [None,]:
                return
            elif reverse in ['d',]:
                reverse=True

        graph_it=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Graph Results (if possible)[y/N]:",helpText="yes or no; default is No.",data="boolean")
        
        if graph_it in [None,]:
            return
        elif graph_it in ['d',]:
            graph_it=False


        export=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Export[y/N]:",helpText="yes or no; default is No.",data="boolean")
        
        if export in [None,]:
            return
        elif export in ['d',]:
            export=False

        text_cr_export=detectGetOrSet("text_cr_export","cost_report.txt",setValue=False,literal=True)
        xlsx_cr_export=detectGetOrSet("xlsx_cr_export","cost_report.xlsx",setValue=False,literal=True)
        
        date_from=Prompt.__init2__(None,func=FormBuilderMkText,ptext="From Date:",helpText="from date",data="datetime")
        print(date_from)
        if date_from in ['d',None]:
            return
        date_to=Prompt.__init2__(None,func=FormBuilderMkText,ptext="To Date:",helpText="from date",data="datetime")
        if date_to in ['d',None]:
            return

        occurances=Prompt.__init2__(None,func=FormBuilderMkText,ptext="All Fields Qty Above or Equal To How Many(d=2)?",helpText="above or == To this number",data="integer")
        if occurances in [None,]:
            return
        elif occurances in ['d',]:
            occurances=2

        occurances_max=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"All Fields Qty Below or Equal To How Many(d={sys.maxsize})?",helpText="Below or == To this number",data="integer")
        if occurances_max in [None,]:
            return
        elif occurances_max in ['d',]:
            occurances_max=sys.maxsize

        excludes=['EntryId','DayLogId','TimeStamp'
"CaseCount",
"UnitsDeep",
"ShelfCount",
"UnitsHigh",
"PalletCount",]
        fields_for_total=[
        "Shelf",
        "BackRoom",
        "Display_1",
        "Display_2",
        "Display_3",
        "Display_4",
        "Display_5",
        "Display_6",
        "ListQty",
        "SBX_WTR_DSPLY",
        "SBX_CHP_DSPLY",
        "SBX_WTR_KLR",
        "FLRL_CHP_DSPLY",
        "FLRL_WTR_DSPLY",
        "WD_DSPLY",
        "CHKSTND_SPLY",
        "Distress",
        ]
        htext=[]
        xct=len(fields_for_total)
        for num,z in enumerate(fields_for_total):
            htext.append(f"{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{xct} -> {z}")
        htext='\n'.join(htext)
        tmp=[]
        print(htext)
        selectfields=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Select indexes for fields to use or all(<ENTER>)",helpText=htext,data="list")
        if selectfields in [[],None]:
            return
        elif isinstance(selectfields,str) and selectfields.lower() in ['d',]:
            pass
        else:
            try:
                for index in selectfields:
                    try:
                        index=int(index)
                        tmp.append(fields_for_total[index])
                    except Exception as eeee:
                        print(eeee)

            except Exception as eee:
                print(eee)
            if len(tmp) > 0:
                fields_for_total=tmp
        #exit([fields_for_total,len(fields_for_total),selectfields,tmp])
        #fields_for_total=[i.name for i in DayLog.__table__.columns if str(i.type).lower() == "integer" and str(i.name) not in excludes]
        total_expense=0
        with Session(ENGINE) as session:
            def exporter_excel(query,file):
                try:
                    df = pd.read_sql(query.statement, query.session.bind)
                    df.to_excel(file)
                except Exception as e:
                    print(e,str(e),repr(e))
            def GraphIt(query,fields=['Shelf','BackRoom','Display_1','Display_2','Display_3','Display_4','Display_5','Display_6','SBX_WTR_DSPLY','SBX_CHP_DSPLY','SBX_WTR_KLR','FLRL_CHP_DSPLY','FLRL_WTR_DSPLY','WD_DSPLY','CHKSTND_SPLY','Distress','ListQty']):
                while True:
                    print(f"{Fore.light_magenta}Dates on the Graph(s) are in the format of {Fore.orange_red_1}Day/Month/Year{Fore.light_magenta}, whereas Date Input will remain {Fore.light_steel_blue}Month/Day/Year{Style.reset}")
                    df_from_records = pd.read_sql_query(query.statement,session.bind)
                    unique_ids=df_from_records['EntryId'].unique()
                    for num,field in enumerate(fields):
                        for idx in unique_ids:
                            rows=df_from_records.loc[df_from_records['EntryId']==idx]
                            series=rows[field]
                            series_price=rows['Price']
                            series_tax=rows['Tax']
                            net_series=(series*series_price)+((series*series_tax))
                           
                            time_x=df_from_records.loc[df_from_records['EntryId']==idx]['DayLogDate']
                            time_x=pd.to_datetime(time_x)
                            time_x=time_x.dt.strftime("%d/%m/%Y")
                            try:
                                pd.set_option('expand_frame_repr', True)
                                pd.set_option('display.max_colwidth', len(rows['Name'].iloc[0]))
                                msg=f"{Fore.light_green}{rows['Name'].iloc[0]}{Style.reset}"
                                print(msg)
                            except Exception as e:
                                print(e)
                                print(rows['Name'])
                            plt.scatter(time_x, net_series, label=f'Original Data From {field}')
                            plt.show()
                            plt.clf()
                    print(f"{Fore.light_magenta}Dates on the Graph(s) are in the format of {Fore.orange_red_1}Day/Month/Year{Fore.light_magenta}, whereas Date Input will remain {Fore.light_steel_blue}Month/Day/Year{Style.reset}")
                    n=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Next?",helpText="next y/n",data="boolean")
                    if n in ['None',]:
                        return None
                    elif n in [True,]:
                        return True



            code=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What are looking for(Enter == ALL)[Separate Searches with Comma ',']:",helpText="barcode|code|name",data="list")
            if code in [None,]:
                return
            if code in ['d',[]]:
                if date(date_from.year,date_from.month,date_from.day) == date(date_to.year,date_to.month,date_to.day):
                    print(f"{Fore.orange_red_1}Same Day Results!{Style.reset}")
                    query=session.query(DayLog).filter(DayLog.DayLogDate==date(date_from.year,date_from.month,date_from.day))
                    if LookUpState == True:
                        query=query.order_by(DayLog.DayLogDate.asc())
                    elif LookUpState == False:
                        query=query.order_by(DayLog.DayLogDate.desc())
                    if export:
                        exporter_excel(query,xlsx_cr_export)
                    if graph_it:
                        x=GraphIt(query,fields_for_total)
                        if x is None:
                            return
                    if orderByTotalValue:
                        query=self.f_orderByTotalValue(query)
                    
                    query=query.all()
                else:
                    query=session.query(DayLog).filter(DayLog.DayLogDate.between(date_from,date_to))
                    if LookUpState == True:
                        query=query.order_by(DayLog.DayLogDate.asc())
                    elif LookUpState == False:
                        query=query.order_by(DayLog.DayLogDate.desc())
                    if export:
                        exporter_excel(query,xlsx_cr_export)
                    if graph_it:
                        x=GraphIt(query,fields_for_total)
                        if x is None:
                            return

                    if orderByTotalValue:
                        query=self.f_orderByTotalValue(query)
                    query=query.all()
            else:
                exclude_code=Prompt.__init2__(None,func=FormBuilderMkText,ptext="exclude this code from results:",helpText="yes or no",data="boolean")
                if exclude_code in [None,]:
                    return
                if date(date_from.year,date_from.month,date_from.day) == date(date_to.year,date_to.month,date_to.day):
                    print(f"{Fore.orange_red_1}Same Day Results for '{code}'!{Style.reset}")
                    if not exclude_code:
                        filt=[]
                        for q in code:
                            filt.extend([
                            DayLog.Barcode.icontains(q),
                            DayLog.Code.icontains(q),
                            DayLog.Name.icontains(q)
                            ])

                        query=session.query(DayLog).filter(
                            DayLog.DayLogDate==date(date_from.year,date_from.month,date_from.day),
                                or_(*filt)        
                            )
                        if LookUpState == True:
                            query=query.order_by(DayLog.DayLogDate.asc())
                        elif LookUpState == False:
                            query=query.order_by(DayLog.DayLogDate.desc())

                        if orderByTotalValue:
                            query=self.f_orderByTotalValue(query)
                        
                    else:
                        filt=[]
                        for q in code:
                            filt.extend([or_(
                                not_(DayLog.Barcode.icontains(q)),
                                not_(DayLog.Code.icontains(q)),
                                not_(DayLog.Name.icontains(q))),
                            not_(DayLog.Barcode.icontains(q)),
                            not_(DayLog.Code.icontains(q)),
                            not_(DayLog.Name.icontains(q)),
                            and_(
                                not_(DayLog.Barcode.icontains(q)),
                                not_(DayLog.Code.icontains(q)),
                                not_(DayLog.Name.icontains(q)))
                            ])
                        query=session.query(DayLog).filter(DayLog.DayLogDate==date(date_from.year,date_from.month,date_from.day),*filt)
                        if LookUpState == True:
                            query=query.order_by(DayLog.DayLogDate.asc())
                        elif LookUpState == False:
                            query=query.order_by(DayLog.DayLogDate.desc())
                        if orderByTotalValue:
                            query=self.f_orderByTotalValue(query)
                    if export:
                        exporter_excel(query,xlsx_cr_export)
                    if graph_it:
                        x=GraphIt(query,fields_for_total)
                        if x is None:
                            return

                    if orderByTotalValue:
                        query=self.f_orderByTotalValue(query)
                    query=query.all()
                else:
                    if not exclude_code:
                        filt=[]
                        for q in code:
                            filt.extend([
                            DayLog.Barcode.icontains(q),
                            DayLog.Code.icontains(q),
                            DayLog.Name.icontains(q)
                            ])
                        query=session.query(DayLog).filter(
                            DayLog.DayLogDate.between(date_from,date_to),
                                or_(
                                *filt)
                        )
                        if LookUpState == True:
                            query=query.order_by(DayLog.DayLogDate.asc())
                        elif LookUpState == False:
                            query=query.order_by(DayLog.DayLogDate.desc())
                        if orderByTotalValue:
                            query=self.f_orderByTotalValue(query)
                    else:
                        filt=[]
                        for q in code:
                            filt.extend([or_(
                                not_(DayLog.Barcode.icontains(q)),
                                not_(DayLog.Code.icontains(q)),
                                not_(DayLog.Name.icontains(q))),
                            not_(DayLog.Barcode.icontains(q)),
                            not_(DayLog.Code.icontains(q)),
                            not_(DayLog.Name.icontains(q)),
                            and_(
                                not_(DayLog.Barcode.icontains(q)),
                                not_(DayLog.Code.icontains(q)),
                                not_(DayLog.Name.icontains(q)))
                            ])
                        query=session.query(DayLog).filter(
                            DayLog.DayLogDate.between(date_from,date_to),
                                *filt
                        )
                        if LookUpState == True:
                            query=query.order_by(DayLog.DayLogDate.asc())
                        elif LookUpState == False:
                            query=query.order_by(DayLog.DayLogDate.desc())
                        if orderByTotalValue:
                            query=self.f_orderByTotalValue(query)
                    if export:
                        exporter_excel(query,xlsx_cr_export)
                    if graph_it:
                        x=GraphIt(query,fields_for_total)
                        if x is None:
                            return
                    if orderByTotalValue:
                        query=self.f_orderByTotalValue(query)
                    query=query.all()
                
            totals=OrderedDict({})
            totals_dl=OrderedDict({})
            total_price=OrderedDict({})
            total_tax=OrderedDict({})
            total_crv=OrderedDict({})
            if export:
                msg=f'{datetime.now()}[NOW]/[{date_from}(From)]-[{date_to}(To)]'
                logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=text_cr_export,clear_only=True)
                logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=text_cr_export,clear_only=False)

            ROUNDTO=int(detectGetOrSet("TotalSpent ROUNDTO default",3,setValue=False,literal=True))

            for num,i in enumerate(query):
                print(num,len(query))
                if num >= len(query):
                    break
                try:
                    if i.EntryId not in totals:
                        #total from fields not occurances
                        totals[i.EntryId]=0
                        totals_dl[i.EntryId]=i
                        
                        total_crv[i.EntryId]=i.CRV*0
                        total_tax[i.EntryId]=i.Tax*0
                        total_price[i.EntryId]=i.Price*0
                    for x in fields_for_total:
                        try:
                            
                            totals[i.EntryId]+=round(getattr(i,x),ROUNDTO)
                            crv=round(i.CRV*getattr(i,x),ROUNDTO)
                            tax=round(i.Tax*getattr(i,x),ROUNDTO)
                            price=round(i.Price*getattr(i,x),ROUNDTO)
                            msg=f"{num}/{num+1} of {len(query)}{i.seeShort()}\t{Fore.light_sea_green}CRV:{Fore.light_steel_blue}{crv}\n\t{Fore.light_sea_green}TAX:{Fore.light_steel_blue}{tax}\n\t{Fore.light_sea_green}Price:{Fore.light_steel_blue}{price}\n\t{Fore.light_green}Total:{Fore.light_steel_blue}{round(crv+tax+price,ROUNDTO)}\n{Fore.light_sea_green}For Date:{Fore.dark_goldenrod}{i.DayLogDate}({datetime(i.DayLogDate.year,i.DayLogDate.month,i.DayLogDate.day).strftime('%B[Mnth]/%A[DayNm]/%V[WK#]')}){Style.reset}"
                            print(msg)
                            if export:
                                logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=text_cr_export)
                            msg2=' '.join([str(i) for i in (f"{Fore.light_green}Totaling: {Style.reset}",getattr(i,x),x,f'{Fore.light_red}Field for Total{Style.reset}')])
                            msg2+=f"""{Fore.orange_red_1}(Estimated/Inverted Shelf Qty) Shelf=ShelfCount - Qty {Fore.light_yellow}[{Fore.cyan}{i.ShelfCount}{Fore.light_yellow} -{Fore.cyan}{i.Shelf}{Fore.light_yellow}]={Fore.pale_green_1b}{i.ShelfCount-i.Shelf}{Style.reset}\n"""
                            print(msg2)
                            if export:
                                logInput(msg2,user=False,filter_colors=True,maxed_hfl=False,ofile=text_cr_export)

                            total_crv[i.EntryId]+=crv
                            total_crv[i.EntryId]=round(total_crv[i.EntryId],ROUNDTO)
                            
                            total_tax[i.EntryId]+=tax
                            total_tax[i.EntryId]=round(total_tax[i.EntryId],ROUNDTO)
                            
                            total_price[i.EntryId]+=price
                            total_price[i.EntryId]=round(total_price[i.EntryId],ROUNDTO)
                            total_expense+=(tax+price+crv)
                            total_expense=round(total_expense,ROUNDTO)
                        except Exception as ee:
                            print(ee,repr(ee),x,i.seeShort())
                except Exception as e:
                    print(e,repr(e),num,i,len(query))
                    break
                #next2=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{i}\n{Fore.light_magenta}Final Total:{Fore.light_steel_blue}{totals[i.EntryId]}{Style.reset} next?",helpText="yes or no(f will result in yes for str reasons)",data="boolean")
                #if next2 in [None,]:
                #    return
                #elif next2 in ['f',False]:
                #    return
                #else:
                #    pass
        #
        if orderByTotalValue:
            totals_ordered_keys=OrderedDict({})
            for key in totals:
                totals_ordered_keys[key]=round(((total_crv[key]+total_tax[key]+total_price[key])/total_expense)*100,ROUNDTO)
            #need to sort dictionary
            #according to -> round(((total_crv[key]+total_tax[key]+total_price[key])/total_expense)*100,ROUNDTO)
            totals_ordered_keys=OrderedDict(sorted(totals_ordered_keys.items(),key=lambda item:item[1],reverse=not reverse))
            tmp=OrderedDict()
            for key in totals_ordered_keys.keys():
                tmp[key]=totals[key]
            totals=tmp

        totals_len=len(totals)
        for num,key in enumerate(totals):
            if LookUpState == True:
                dl=session.query(DayLog).filter(DayLog.EntryId==key).order_by(DayLog.DayLogDate.desc()).first()
            else:
                dl=session.query(DayLog).filter(DayLog.EntryId==key).first()
            if dl:
                counter=0
                for f in fields_for_total:
                    if getattr(dl,f) == 0:
                        counter+=1
                if counter >= len(fields_for_total):
                    continue
                msg=f"{Fore.orange_red_1}{round(((total_crv[key]+total_tax[key]+total_price[key])/total_expense)*100,ROUNDTO)}% of {round(total_expense,ROUNDTO)} ** {Fore.light_cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{totals_len}{Fore.light_sea_green} '{dl.Name}' = {Fore.grey_70}{round(totals[key],ROUNDTO)} acquired,{Fore.dark_goldenrod} From {date_from} {Fore.dark_green}To {date_to},{Fore.spring_green_3a}for a period of {date_to-date_from},{Fore.medium_violet_red} for a total cost of {round(total_crv[key]+total_tax[key]+total_price[key],ROUNDTO)} [{Fore.light_steel_blue}DayLogId({Fore.green_yellow}{dl.DayLogId}{Fore.light_steel_blue}),{Fore.cadet_blue_1}EntryId({Fore.light_sea_green}{dl.EntryId}{Fore.cadet_blue_1}){Fore.medium_violet_red}].{Style.reset}\n"
                if export:
                    logInput(msg,user=False,filter_colors=True,maxed_hfl=False,ofile=text_cr_export)
                print(msg)
        ex=f"{Fore.light_red}Duration:{Fore.light_steel_blue}{datetime.now()-local_start}|{Fore.light_cyan}OrderByFinalValue[{Fore.deep_pink_4c}{orderByTotalValue}{Fore.light_cyan}]|GraphIt[{Fore.deep_pink_4c}{graph_it}{Fore.light_cyan}]|Export[{Fore.deep_pink_4c}{export}{Fore.light_cyan}]"
        if orderByTotalValue:
            reverse_state={False:'False - Desc. (First Line Oldest/Biggest,Last Line Newest/Smallest)',True:'True - Asc. (Firt Line Newest/Smallest,Last Line Newest/Biggest)'}
            ex+=f": Final Results Reverse:{reverse_state[reverse]}|{Fore.orange_red_1}\n"
        else:
            ex+=f'{Fore.orange_red_1}\n'
        msg3=f"{ex}Total Expense:{Fore.light_magenta}{total_expense}{Style.reset}"
        print(msg3)
        if export:
            logInput(msg3,user=False,filter_colors=True,maxed_hfl=False,ofile=text_cr_export)

    def PriceChange(self):
        #cost report
        date_from=Prompt.__init2__(None,func=FormBuilderMkText,ptext="From Date:",helpText="from date",data="datetime")
        print(date_from)
        if date_from in ['d',None]:
            return
        date_to=Prompt.__init2__(None,func=FormBuilderMkText,ptext="To Date:",helpText="from date",data="datetime")
        if date_to in ['d',None]:
            return

        with Session(ENGINE) as session:
            #code=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What are looking for(Enter == ALL):",helpText="barcode|code|name",data="string")
            #if code in [None,]:
            #    return
            #if code in ['d',]:
            code='d'
            different={}
            query=session.query(DayLog).filter(DayLog.DayLogDate.between(date_from,date_to)).distinct(DayLog.Price).all()
            for i in query:
                if i.EntryId not in different:
                    different[i.EntryId]=[]
                    different[i.EntryId].append(i)
                else:
                    if different[i.EntryId][-1].Price != i.Price:
                        different[i.EntryId].append(i)
            simmer=0
            znum1=0
            diffcount=0
            for i in different:
                if len(different[i]) > 1:
                    diffcount+=1
            for znum,k in enumerate(different):
                if len(different[k]) > 1:
                    print(f"{Fore.light_magenta}{znum1}/{Fore.medium_violet_red}{znum1+1} of {Fore.light_steel_blue}{diffcount}{Style.reset}\n")
                    znum1+=1
                if len(different[k]) > 1:
                    for num,z in enumerate(different[k]):
                        msg=f"{Fore.light_cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{len(different[k])} -> {z.seeShort()} - {Fore.light_steel_blue}Price:{z.Price}{Fore.orange_red_1}{Back.grey_15}Price Changed!{Fore.medium_violet_red}{z.DayLogDate}{Style.reset}"
                        print(msg)
                        simmer+=1
            if simmer == 0:
                print("No Price Changes Detected!")

            print("Tax Changes? Checking...")
            different={}
            query=session.query(DayLog).filter(DayLog.DayLogDate.between(date_from,date_to)).distinct(DayLog.Tax).all()
            for i in query:
                if i.EntryId not in different:
                    different[i.EntryId]=[]
                    different[i.EntryId].append(i)
                else:
                    if different[i.EntryId][-1].Tax != i.Tax:
                        different[i.EntryId].append(i)

            simmer=0
            znum1=0
            diffcount=0
            for i in different:
                if len(different[i]) > 1:
                    diffcount+=1
            for znum,k in enumerate(different):
                if len(different[k]) > 1:
                    print(f"{Fore.light_magenta}{znum1}/{Fore.medium_violet_red}{znum1+1} of {Fore.light_steel_blue}{diffcount}{Style.reset}\n")
                    znum1+=1
                if len(different[k]) > 1:
                    for num,z in enumerate(different[k]):
                        msg=f"{Fore.light_cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{len(different[k])} -> {z.seeShort()} - {Fore.light_steel_blue}Tax:{z.Tax}{Fore.orange_red_1}{Back.grey_15}Tax Changed!{Fore.medium_violet_red}{z.DayLogDate}{Style.reset}"
                        print(msg)
                        simmer+=1
            if simmer == 0:
                print("No Tax Changes Detected!")

            print("CRV Changes? Checking...")
            different={}
            query=session.query(DayLog).filter(DayLog.DayLogDate.between(date_from,date_to)).distinct(DayLog.CRV).all()
            for i in query:
                if i.EntryId not in different:
                    different[i.EntryId]=[]
                    different[i.EntryId].append(i)
                else:
                    if different[i.EntryId][-1].CRV != i.CRV:
                        different[i.EntryId].append(i)
            
            simmer=0
            znum1=0
            diffcount=0
            for i in different:
                if len(different[i]) > 1:
                    diffcount+=1
            for znum,k in enumerate(different):
                if len(different[k]) > 1:
                    print(f"{Fore.light_magenta}{znum1}/{Fore.medium_violet_red}{znum1+1} of {Fore.light_steel_blue}{diffcount}{Style.reset}\n")
                    znum1+=1
                    for num,z in enumerate(different[k]):
                        msg=f"{Fore.light_cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{len(different[k])} -> {z.seeShort()} - {Fore.light_steel_blue}CRV:{z.CRV}{Fore.orange_red_1}{Back.grey_15}CRV Changed!{Fore.medium_violet_red}{z.DayLogDate}{Style.reset}"
                        print(msg)
                        simmer+=1

            if simmer == 0:
                print("No CRV Changes Detected!")

            '''
                #print(query)
            else:
                query=session.query(DayLog).filter(
                    DayLog.DayLogDate.between(date_from,date_to),
                        or_(
                        DayLog.Barcode.icontains(code),
                        DayLog.Code.icontains(code),
                        DayLog.Name.icontains(code))
                ).distinct(DayLog.Price).all()
                print(query)
            '''   
            



    def listDate(self,month=None,day=None,year=None):
        d=self.dateParser()
        with Session(self.engine) as session:
            results=session.query(DayLog).filter(DayLog.DayLogDate==d).all()
            #results=session.query(DayLog).all()
            ct=len(results)
            if ct == 0:
                print(f"{Style.bold}{Fore.light_red}No Items For that Date!{Style.reset}")
            for r in results:
                print(r)


    def exportAllDL(self):
        with Session(self.engine) as session:
            results=session.query(DayLog).all()
            ct=len(results)
            if ct == 0:
                print(f"{Style.bold}{Fore.light_red}No Items!{Style.reset}")
            for num,r in enumerate(results):
                r.saveItemData(num=num)

    def dateParser(self,month=None,day=None,year=None):
        if not year:
            year=input(f"Year? [{datetime.now().year}]: ")
            if year.lower()  in ['q','quit']:
                exit('user quit!')
            elif year.lower() in ['b','back']:
                raise Exception("User Request to back a menu")
            elif year == '':
                year=datetime.now().year
        try:
            year=int(year)
        except Exception as e:
            raise e

        if not month:
            month=input(f"Month?: [1..12]: ")
            if month.lower()  in ['q','quit']:
                exit('user quit!')
            elif month.lower() in ['b','back']:
                raise Exception("User Request to back a menu")
            elif month == '':
                month=datetime.now().month
        try:
            month=int(month)
            if month < 1:
                raise Exception("Month Must be within 1..12")
            if month > 12:
                raise Exception("Month Must be within 1..12")
        except Exception as e:
            raise e
        if not day:
            day=input(f"Day? [1..{calendar.monthrange(year=year,month=month)[-1]}]: ")
            if day.lower()  in ['q','quit']:
                exit('user quit!')
            elif day.lower() in ['b','back']:
                raise Exception("User Request to back a menu")
            elif day == '':
                day=datetime.now().day
        try:
            day=int(day)
            if day < 1:
                raise Exception("Month Must be within 1..31")

            #february
            if month == 2:
                if day > 28 and not calendar.isleap(year):
                    raise Exception("Day Must be within 1..28")
                elif day > 29 and calendar.isleap(year):
                    raise Exception("Day Must be within 1..29")
                
            else:
                if day > 28 and month in [num for num,i in enumerate(calendar.mdays) if i == 28]:
                    raise Exception("Day Must be within 1..28")
                elif day > 29 and month in [num for num,i in enumerate(calendar.mdays) if i == 29]:
                    raise Exception("Day Must be within 1..29")
                elif day > 30 and month in [num for num,i in enumerate(calendar.mdays) if i == 30]:
                    raise Exception("Day Must be within 1..30")
                elif day > 31 and month in [num for num,i in enumerate(calendar.mdays) if i == 31]:
                    raise Exception("Day Must be within 1..31")
        except Exception as e:
            raise e
        d=date(year,month,day)
        print(f"{Fore.green}Date Generated: {Style.reset}{Fore.light_yellow}{d}{Style.reset}")
        return d

    def exportDate(self,month=None,day=None,year=None):
        d=self.dateParser()
        print(d)
        with Session(self.engine) as session:
            results=session.query(DayLog).filter(DayLog.DayLogDate==d).all()
            #results=session.query(DayLog).all()
            ct=len(results)
            if ct == 0:
                print(f"{Style.bold}{Fore.light_red}No Items For that Date!{Style.reset}")
            for num,r in enumerate(results):
                #print(f"{num}/{ct} -> {r}")
                r.saveItemData(num=num)

    def listCode(self,code=None):
        #d=self.dateParser()
        #print(d)
        if not code:
            code=input("Barcode|Code|ItemCode: ")
            if code.lower() in ['quit','q']:
                exit("user quit!")
            elif code.lower() in ['back','b']:
                return
        prefix=code.split(".")[0]
        cd=code.split(".")[-1]

        with Session(self.engine) as session:
            results=session.query(DayLog)
            if prefix.lower() in ['d',]:
                results=results.filter(DayLog.DayLogId==int(cd))
            elif prefix.lower() in ['b',]:
                results=results.filter(DayLog.Barcode==cd)
            elif prefix.lower() in ['c']:
                results=results.filter(DayLog.Code==cd)
            else:
                results=results.filter(or_(DayLog.Barcode==cd,DayLog.Code==cd))
            results=results.all()
            #results=session.query(DayLog).all()
            ct=len(results)
            if ct == 0:
                print(f"{Style.bold}{Fore.light_red}No Items For that Code!{Style.reset}")
            for num,r in enumerate(results):
                print(f"{num}/{ct} -> {r}")
                #r.saveItemData(num=num)

    def exportCode(self,code=None):
        #d=self.dateParser()
        #print(d)
        if not code:
            code=input("Barcode|Code|ItemCode: ")
            if code.lower() in ['quit','q']:
                exit("user quit!")
            elif code.lower() in ['back','b']:
                return
        prefix=code.split(".")[0]
        cd=code.split(".")[-1]

        with Session(self.engine) as session:
            results=session.query(DayLog)
            if prefix.lower() in ['d',]:
                results=results.filter(DayLog.DayLogId==int(cd))
            elif prefix.lower() in ['b',]:
                results=results.filter(DayLog.Barcode==cd)
            elif prefix.lower() in ['c']:
                results=results.filter(DayLog.Code==cd)
            else:
                results=results.filter(or_(DayLog.Barcode==cd,DayLog.Code==cd))
            results=results.all()
            #results=session.query(DayLog).all()
            ct=len(results)
            if ct == 0:
                print(f"{Style.bold}{Fore.light_red}No Items For that Code!{Style.reset}")
            for num,r in enumerate(results):
                #print(f"{num}/{ct} -> {r}")
                r.saveItemData(num=num)

    def listCodeDate(self,code=None):
        d=self.dateParser()
        #print(d)
        if not code:
            code=input("Barcode|Code|ItemCode: ")
            if code.lower() in ['quit','q']:
                exit("user quit!")
            elif code.lower() in ['back','b']:
                return
        prefix=code.split(".")[0]
        cd=code.split(".")[-1]

        with Session(self.engine) as session:
            results=session.query(DayLog)
            if prefix.lower() in ['d',]:
                results=results.filter(DayLog.DayLogId==int(cd),DayLog.DayLogDate==d)
            elif prefix.lower() in ['b',]:
                results=results.filter(DayLog.Barcode==cd,DayLog.DayLogDate==d)
            elif prefix.lower() in ['c']:
                results=results.filter(DayLog.Code==cd,DayLog.DayLogDate==d)
            else:
                results=results.filter(or_(DayLog.Barcode==cd,DayLog.Code==cd),DayLog.DayLogDate==d)
            results=results.all()
            #results=session.query(DayLog).all()
            ct=len(results)
            if ct == 0:
                print(f"{Style.bold}{Fore.light_red}No Items For that Code!{Style.reset}")
            for num,r in enumerate(results):
                print(f"{num}/{ct} -> {r}")
                #r.saveItemData(num=num)

    def exportCodeDate(self,code=None):
        d=self.dateParser()
        #print(d)
        if not code:
            code=input("Barcode|Code|ItemCode: ")
            if code.lower() in ['quit','q']:
                exit("user quit!")
            elif code.lower() in ['back','b']:
                return
        prefix=code.split(".")[0]
        cd=code.split(".")[-1]

        with Session(self.engine) as session:
            results=session.query(DayLog)
            if prefix.lower() in ['d',]:
                results=results.filter(DayLog.DayLogId==int(cd),DayLog.DayLogDate==d)
            elif prefix.lower() in ['b',]:
                results=results.filter(DayLog.Barcode==cd,DayLog.DayLogDate==d)
            elif prefix.lower() in ['c']:
                results=results.filter(DayLog.Code==cd,DayLog.DayLogDate==d)
            else:
                results=results.filter(or_(DayLog.Barcode==cd,DayLog.Code==cd),DayLog.DayLogDate==d)
            results=results.all()
            #results=session.query(DayLog).all()
            ct=len(results)
            if ct == 0:
                print(f"{Style.bold}{Fore.light_red}No Items For that Code!{Style.reset}")
            for num,r in enumerate(results):
                #print(f"{num}/{ct} -> {r}")
                r.saveItemData(num=num)
    def fft(self):
        h='DayLog@Avg Field'
        includes=["integer","float"]
        integer_fields=[i.name for i in DayLog.__table__.columns if str(i.type).lower() in includes]
        ct=len(integer_fields)
        for num,i in enumerate(integer_fields):
            msg=f'''{Fore.orange_red_1}{num}{Fore.green_yellow}/{num+1}{Fore.light_sea_green}/{ct}{Fore.light_steel_blue} - {i}{Style.reset}'''
            print(msg)
        while True:
            try:
                which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} which index?",helpText="select the index for the field to avg",data="integer")
                if which in [None,]:
                    return
                elif which in ['d',]:
                    which=0
                field=integer_fields[which]
                with Session(ENGINE) as session:
                    barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} Barcode|Code|Name: ",helpText="what are you looking to avg",data="string")
                    if barcode in [None,'d']:
                        return
                    which_codes=session.query(DayLog).filter(or_(
                        DayLog.Barcode==barcode,
                        DayLog.Code==barcode,
                        DayLog.Code.icontains(barcode),
                        DayLog.Barcode.icontains(barcode),
                        DayLog.Name.icontains(barcode)
                        )).group_by(DayLog.Barcode).all()
                    wc_ct=len(which_codes)
                    if wc_ct == 0:
                        print("nothing found to avg")
                        return
                    for num0,wc in enumerate(which_codes):
                        msg=f"{num0}/{num0+1} of {wc_ct} - {wc.Name} | {wc.Barcode} | {wc.Code} | {getattr(wc,field)}"
                        print(msg)
                    #session.query(DayLog).filter(DayLog.Barcode=='')
                    which0=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} which index?",helpText="select the index for the field to avg",data="integer")
                    if which0 in [None,]:
                        return
                    elif which in ['d',]:
                        which0=0
                    avg_query=session.query(DayLog).filter(DayLog.Barcode==which_codes[which0].Barcode)
                    df_from_records = pd.read_sql_query(avg_query.statement,session.bind)

                    # Create a series
                    series = df_from_records[field].to_numpy()
                    frequency=1
                    amplitude=1
                    phase=0
                    
                    # Generate x-values for the sine wave
                    TIME_X = np.arange(0, len(series),step=1,dtype=int)

                    # Convert the series into a sine wave
                    sine_wave = amplitude * np.sin(2 * np.pi * frequency * TIME_X + phase)

                    sr=frequency
                    dur=len(series)
                    n=sr*dur
                    yf = rfft(sine_wave)
                    xf = rfftfreq(n, 1 / sr)
                    iyf= irfft(yf)

                    plt.bar(xf, np.abs(yf),label=f'fft {field} (SR={sr})')
                    plt.show()
                    plt.clf()

                    plt.plot(iyf,label=f"ifft {field}")
                    plt.show()
                    plt.clf()
                    # Plot the original series and the sine wave
                    
                    

                    plt.plot(TIME_X, series, label=f'Original Data From {field} (SR={sr})')
                    plt.show()
                    plt.clf()

                    plt.plot(TIME_X, sine_wave, label=f'Signal Generated For {field} (SR={sr})')
                    plt.show()
                    print("I do not even know what is going on here")
                    break
            except Exception as e:
                print(e)
                break

    def avg_field(self,graph=False):
        h='DayLog@Avg Field'
        includes=["integer","float"]
        integer_fields=[i.name for i in DayLog.__table__.columns if str(i.type).lower() in includes]
        ct=len(integer_fields)
        for num,i in enumerate(integer_fields):
            msg=f'''{Fore.orange_red_1}{num}{Fore.green_yellow}/{num+1}{Fore.light_sea_green}/{ct}{Fore.light_steel_blue} - {i}{Style.reset}'''
            print(msg)
        while True:
            try:
                which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} which index?",helpText="select the index for the field to avg",data="integer")
                if which in [None,]:
                    return
                elif which in ['d',]:
                    which=0
                field=integer_fields[which]
                with Session(ENGINE) as session:
                    barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} Barcode|Code|Name: ",helpText="what are you looking to avg",data="string")
                    if barcode in [None,'d']:
                        return
                    which_codes=session.query(DayLog).filter(or_(
                        DayLog.Barcode==barcode,
                        DayLog.Code==barcode,
                        DayLog.Code.icontains(barcode),
                        DayLog.Barcode.icontains(barcode),
                        DayLog.Name.icontains(barcode)
                        )).group_by(DayLog.Barcode).all()
                    wc_ct=len(which_codes)
                    if wc_ct == 0:
                        print("nothing found to avg")
                        return
                    for num0,wc in enumerate(which_codes):
                        msg=f"{num0}/{num0+1} of {wc_ct} - {wc.Name} | {wc.Barcode} | {wc.Code} | {getattr(wc,field)}"
                        print(msg)
                    #session.query(DayLog).filter(DayLog.Barcode=='')
                    which0=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} which index?",helpText="select the index for the field to avg",data="integer")
                    if which0 in [None,]:
                        return
                    elif which in ['d',]:
                        which0=0
                    avg_query=session.query(DayLog).filter(DayLog.Barcode==which_codes[which0].Barcode)
                    df_from_records = pd.read_sql_query(avg_query.statement,session.bind)
                    if graph:
                            x=df_from_records[['DayLogDate']]
                            x['DayLogDate']=pd.to_datetime(x['DayLogDate'])
                            x['date_str'] = x['DayLogDate'].dt.strftime('%Y-%m-%d')
                            y=df_from_records[[field]]
                            plt.clf()
                            plt.date_form('Y-m-d')
                            plt.plot(x['date_str'],y[field])
                            plt.title(f"Data for '{field}'")
                            plt.show()
                    print(df_from_records[[field,'DayLogId','DayLogDate']])
                    print(f"{Fore.dark_green}{Back.white}Total AVG:{Fore.dark_blue}{df_from_records[field].mean()} Avg Cost: ${(df_from_records['Price']*df_from_records[field]).mean()}{Style.reset}")
                    tr=avg_query.all()
                    split_totals={}
                    split_price={}
                    for i in tr:
                        key=str(date(i.DayLogDate.year,i.DayLogDate.month,i.DayLogDate.day).strftime("%A"))
                        #print(key)
                        if split_totals.get(key) == None:
                            split_totals[key]=[getattr(i,field),]
                            split_price[key]=[getattr(i,'Price')]
                        else:
                            split_totals[key].append(getattr(i,field))
                            split_price[key].append(getattr(i,'Price'))
                    for i in tr:
                        key=str(date(i.DayLogDate.year,i.DayLogDate.month,i.DayLogDate.day).strftime("%B"))
                        #print(key)
                        if split_totals.get(key) == None:
                            split_totals[key]=[getattr(i,field),]
                            split_price[key]=[getattr(i,'Price')]
                        else:
                            split_totals[key].append(getattr(i,field))
                            split_price[key].append(getattr(i,'Price'))
                    #print(split_totals)
                                        
                    for i in split_totals:
                        n=pd.Series(split_totals[i])
                        p=pd.Series(split_price[i])*n
                        b=pd.Series(split_price[i])
                        all_months=[datetime(datetime.now().year,i,1).strftime("%B") for i in range(1,13)]
                        all_days=[i for i in calendar.weekheader(12).split(" ") if i != '']
                        if i in all_months:
                            print(f"""{Fore.light_magenta}{i}{Fore.light_red}
 Avg {field}: {round(n.mean(),2)} 
 Avg BS Cst: ${round(b.mean(),2)}
 Avg Cst: ${round(p.mean(),2)}
 Max {field}: {round(n.max(),2)}
 Min {field}: {round(n.min(),2)}{Style.reset}""")
                        elif i in all_days:
                            print(f"""{Fore.light_yellow}{i}{Fore.light_green} 
 Avg {field}: {round(n.mean(),2)}
 Avg BS Cst: ${round(b.mean(),2)}
 Avg Cst: ${round(p.mean(),2)}
 Max {field}: {round(n.max(),2)}
 Min {field}: {round(n.min(),2)}{Style.reset}""")
                break
            except Exception as e:
                print(e)
                break

    def del_id(self):
        h='DayLog@Delete ID'
        did=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} DayLogId?",helpText="select the index for the field to avg",data="integer")
        if did in [None,'d']:
            return
        with Session(ENGINE) as session:
            toRM=session.query(DayLog).filter(DayLog.DayLogId==did).delete()
            session.commit()

    def edit_id(self):
        h='DayLog@Edit ID'
        did=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} which DayLogId?",helpText="select the index for the field to avg",data="integer")
        if did in [None,'d']:
            return
        with Session(ENGINE) as session:
            toUp=session.query(DayLog).filter(DayLog.DayLogId==did).first()
            ct=len(toUp.__table__.columns)
            for num,i in enumerate(toUp.__table__.columns):
                msg=f'{num}/{num+1}/{ct} - {i.name}({i.type})'
                print(msg)
            which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} which index?",helpText="select the index for the field to avg",data="integer")
            if which in [None,]:
                return
            elif which in ['d',]:
                which=0
            field=toUp.__table__.columns[which]
            h='DayLog@Edit ID'
            nv=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h} old [{getattr(toUp,str(field.name))}] : ",helpText=f"new value of type {str(field.type)}",data=str(field.type))
            if nv in [None,'d']:
                print("Nothing was changed!")
                return
            setattr(toUp,str(field.name),nv)
            session.commit()
    def rmDayLog(self):
        with Session(ENGINE) as session:
            results=[]
            search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="what are you looking to delete?",helpText="Code|Barcode|EntryId|DayLogId|Name",data="string")
            try:
                integer_value=int(search)
                x=session.query(DayLog).filter(or_(DayLog.EntryId==integer_value,DayLog.DayLogId==integer_value))
                for i in x:
                    if i not in results:
                        results.append(i)
            except Exception as e:
                print(e)
            try:
                x=session.query(DayLog).filter(or_(DayLog.Barcode.icontains(search),DayLog.Code.icontains(search),DayLog.Name.icontains(search)))
                for i in x:
                    if i not in results:
                        results.append(i)
            except Exception as e:
                print(e)
            ct=len(results)
            mtext=[]
            for num,dl in enumerate(results):
                mtext.append(f"{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct} -> {Fore.light_steel_blue} - {dl}")
            mtext='\n'.join(mtext)
            while True:
                try:
                    print(mtext)
                    which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Which indexs do you wish to delete?",helpText=f"{mtext}\na comma Separated list will do",data="list")
                    if which in [None,'d']:
                        return
                    for i in which:
                        try:
                            i=int(i)
                            check_entry=session.query(Entry).filter(Entry.EntryId==results[i].EntryId).first()
                            if not check_entry:
                                '''Delete Extras if no other EntryId's are found.'''
                                check_DayLog=session.query(DayLog).filter(DayLog.EntryId==results[i].EntryId).all()
                                if len(check_DayLog) < 1:
                                    extras=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==results[i].EntryId).all()
                                    for ii in extras:
                                        session.delete(ii)
                                        session.commit()
                            session.delete(results[i])
                            session.commit()
                        except Exception as ee:
                            print(ee)

                    break
                except Exception as e:
                    print(e)
    def searchOnlyShowHoliday(self=None):
        with Session(ENGINE) as session:
            tags=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What do you want to search in DayLog?:",helpText="A Comma Separated List of Tag Names",data="list")
            if tags in ['d',None]:
                tags=[]
            for tag in tags:
                search=session.query(DayLog).filter(
                    or_(DayLog.Tags.icontains(tag),
                        DayLog.Barcode.icontains(tag),
                        DayLog.Name.icontains(tag),
                        DayLog.Code.icontains(tag),
                        DayLog.Note.icontains(tag),
                        DayLog.Description.icontains(tag)
                        )
                ).order_by(DayLog.Barcode,DayLog.DayLogDate.desc()).all()
                ct=len(search)
                if ct == 0:
                    print("Nothing was Found")
                for num,log in enumerate(search):
                    datemetrics=session.query(DateMetrics).filter(DateMetrics.date==log.DayLogDate).first()
                    if log.DayLogDate not in holidays.USA():
                        print(f"Skipping as not a holiday! {log.DayLogDate}")
                        continue
                    if not datemetrics:
                        datemetrics=f'{Fore.orange_red_1}No DateMetrics Data For {Fore.light_magenta}{log.DayLogDate}{Fore.orange_red_1} Available!{Style.reset}'
                    next_holi=next_holiday(today=log.DayLogDate)
                    UNTIL=next_holi[0]-log.DayLogDate
                    msg=f'''{num}/{num+1} of {ct} -{log}{datemetrics}
{Fore.medium_violet_red}Next Holiday:{Fore.light_steel_blue}{next_holi[1]}{Style.reset}
{Fore.medium_violet_red}Next Holiday Date:{Fore.light_steel_blue}{next_holi[0]}{Style.reset}
{Fore.light_yellow}Time{Fore.medium_violet_red} Until Holiday:{Fore.light_steel_blue}{UNTIL}{Style.reset}
{Fore.light_magenta}{log.DayLogDate}{Fore.medium_violet_red} Is Holiday:{Fore.light_steel_blue}{log.DayLogDate in holidays.USA(years=log.DayLogDate.year)}{Style.reset}
{Fore.medium_violet_red}Holiday Name:{Fore.light_steel_blue}{holidays.USA(years=log.DayLogDate.year).get(log.DayLogDate.strftime("%m/%d/%Y"))}{Style.reset}
{Fore.magenta}TAG/INDEX/Count of TTL:{Fore.light_red} {tag} - {num}/{num+1} of {ct}{Style.reset}
{Fore.light_sea_green}Name:{Fore.green_yellow}{log.Name}{Style.reset}
{Fore.light_sea_green}Barcode:{Fore.green_yellow}{log.Barcode}{Style.reset}
{Fore.light_sea_green}Code:{Fore.green_yellow}{log.Code}{Style.reset}
{Fore.light_green}DOE:{Fore.light_magenta}{log.DayLogDate}{Style.reset}'''
                    print(msg)
                    nxt=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Next?",helpText="hit enter",data="boolean")
                    if nxt in [None,]:
                        return
                    elif nxt in ['d']:
                        pass
                    else:
                        #for additional functionality
                        pass

    def __init__(self,engine):
        self.engine=engine
        code=''.join([str(random.randint(0,9)) for i in range(10)])
        verification_protection=detectGetOrSet("Protect From Delete",code,setValue=False,literal=True)
        while True:
            try:
                mode='DayLog/History'
                fieldname='Menu'
                h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                ptext=f"{h}{Fore.light_red}Do what? {Style.reset}[{Fore.green_yellow}h{Style.reset}|{Fore.green_yellow}help{Style.reset}]:"
                #what=input(ptext)
                what=Prompt.__init2__(None,func=FormBuilderMkText,ptext=ptext,helpText=self.helpText,data="string")
                if what in ['d',]:
                    print(self.helpText)
                elif what in [None,]:
                    return
                else:
                    '''
                    'BnC':{
                            'cmds':['bnc','21','banking and cashpool','banking_and_cashpool','bank','piggy-bank'],
                            'exec':lambda self=self:BnCUi(parent=self),
                            'desc':'Banking and CashPool'
                            },
                    '''
                    if what.lower() in ['a','add','+']:
                        self.addToday()
                    elif what.lower() in 'l|list|*'.split('|'):
                        self.listAllDL()
                    elif what.lower() in ['bnc','21','banking and cashpool','banking_and_cashpool','bank','piggy-bank']:
                        BnCUi(parent=self)
                    elif what.lower() in 'ld|list_date'.split('|'):
                        self.listDate()
                    elif what.lower() in 'cd|clear_date'.split("|"):
                        self.clearDate()
                    elif what.lower() in 'reset DayLog'.split("|"):
                        self.clearAllDL()
                    elif what.lower() in 'ea|export_all'.split("|"):
                        self.exportAllDL()
                    elif what.lower() in 'ed|export_date'.split("|"):
                        self.exportDate()
                    elif what.lower() in 'ec|export_code'.split("|"):
                        self.exportCode()
                    elif what.lower() in 'lc|list_code'.split("|"):
                        self.listCode()
                    elif what.lower() in 'ecd|export_code_date'.split("|"):
                        self.exportCodeDate()
                    elif what.lower() in 'lcd|list_code_date'.split("|"):
                        self.listCodeDate()
                    elif what.lower() in ['avg field','af',]:
                        self.avg_field()
                    elif what.lower() in ['edit id',]:
                        self.edit_id()
                    elif what.lower() in ['del id',]:
                        self.del_id()
                    elif what.lower() in ['fxtbl']:
                        DayLogger.updateTable(ENGINE)
                    elif what.lower() in ['sch','search']:
                        DayLogger.searchTags(ENGINE)
                    elif what.lower() in 'sch ohd|search only holidays'.split("|"):
                        DayLogger.searchOnlyShowHoliday()
                    elif what.lower() in ['avg field graph','afg']:
                        self.avg_field(graph=True)
                    elif what.lower() in ['fft','fast fourier transform']:
                        self.fft()
                    elif what.lower() in 'rm|del'.split("|"):
                        self.rmDayLog()
                    elif what.lower() in ['restore bckp','rfb']:
                        self.restoreDayLogs()
                    elif what.lower() in ['ldr','list date range','ls dt rng']:
                        self.listDateRange()
                    elif what.lower() in ['cr','ttl spnt','ttlspnt','cost report','cst rpt']:
                        self.TotalSpent()
                    elif what.lower() in ['prc chng','prcchng','prc.chng','prc_chng','prc-chng','price change',]:
                        self.PriceChange()
                    elif what.lower() in ['review reciept','rvwrcpt','rvw rcpt']:
                        self.reviewReciept()
                    elif what.lower() in ['lsddr rcpt','ls d dr rcpt','list date/daterange rcpt']:
                        self.ls_dt_dr_rcpts()
                    elif what.lower() in ['lsblw','ls blw']:
                        self.ls_rcpt_blw_or_equal_to()
                    elif what.lower() in ['lsabv','ls abv']:
                        self.ls_rcpt_abv_or_equal_to()
                    elif what.lower() in ['lsa rcpt','list all rcpt','ls*rcpt']:
                        self.ls_all_receipts()
                    elif what.lower() in ['sft','search for text','search receipt for text','srft']:
                        self.search_rcpts_for_text()
                    elif what.lower() in ['rm rcpt','rmrcpt','remove receipt']:
                        self.rm_receipt()
                    elif what.lower() in ['clear_all_receipts','clear all reciepts']:
                        self.clear_all_receipts()
                    elif what.lower() in ['ed rcpt','edrcpt','edit receipt','edt rcpt','edtrcpt']:
                        self.edit_reciept()
                    elif what.lower() in ['epdc','estimated pay day calendar']:
                        EstimatedPayCalendar(**setup())
                    elif what.lower() in ['coin']:
                        CoinComboUtil()
                    elif what.lower() in ['faraday','faraday holesize','frdy hs']:
                        HoleSize()
                    elif what.lower() in ['taxi fare','calc taxi fare','ctf','taxi']:
                        TaxiFare()
                    elif what.lower() in [f"compare product","p1==p2?","compare"]:
                        CompareUI()
                    elif what.lower() in ['bhtrsa','business hours tax rates scheduled and appointments']:
                        BhTrSa_Gui()


                                        
            except Exception as e:
                print(e)

