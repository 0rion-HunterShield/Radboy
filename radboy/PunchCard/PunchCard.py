import math
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
from radboy.DB.DatePicker import *
from radboy.PunchCard.CalcTimePad import *

import radboy.possibleCode as pc


def roundup(number):
    return math.ceil(number*100)/100


class PunchCard:
    datePicker=datePickerF
    datetimePicker=datetimePickerF
    """ def datePicker(self):
                    while True:
                        try:
                            def mkT(text,self):
                                return text
                            year=Prompt.__init2__(None,func=mkT,ptext=f"Year[{datetime.now().year}]",helpText="year to look for",data=self)
                            if year == None:
                                return
                            elif year == '':
                                year=datetime.now().year
            
                            month=Prompt.__init2__(None,func=mkT,ptext=f"Month[{datetime.now().month}]",helpText="month to look for",data=self)
                            if month == None:
                                return
                            elif month == '':
                                month=datetime.now().month
            
                            day=Prompt.__init2__(None,func=mkT,ptext=f"Day[{datetime.now().day}]",helpText="day to look for",data=self)
                            if day == None:
                                return
                            elif day == '':
                                day=datetime.now().day
            
                            dt=date(int(year),int(month),int(day))
                            return dt
                        except Exception as e:
                            print(e)
            
            
    def datetimePicker(self,DATE=None):
        while True:
            try:
                if DATE == None:
                    DATE=self.datePicker()
                year=DATE.year
                month=DATE.month
                day=DATE.day

                def mkint(text,self):
                    if text == '':
                        if self == 'hour':
                            return datetime.now().hour
                        elif self == 'minute':
                            return datetime.now().minute
                        elif self == "second":
                            return datetime.now().second
                        else:
                            return 0
                    else:
                        v=int(text)
                        if v < 0:
                            raise Exception("Must be greater than 0")
                        return v

                hour=Prompt.__init2__(None,func=mkint,ptext="Hour",helpText=f"hour to use for {self}",data="hour")
                if hour == None:
                    continue
                minute=Prompt.__init2__(None,func=mkint,ptext="Minute",helpText=f"minute to use for {self}",data="minute")
                if minute == None:
                    continue
                second=Prompt.__init2__(None,func=mkint,ptext="Second",helpText=f"second to use  for {self}",data="second")
                if second == None:
                    continue
                dt=datetime(year,month,day,hour,minute,second)

                return dt
            except Exception as e:
                print(e)"""
    def __init__(self,engine,parent):
        self.engine=engine
        self.parent=parent
        self.helpText=f'''
{Fore.light_green}ps|start{Style.reset} -{Fore.cyan} punch today's card{Style.reset}
{Fore.light_green}pe|end{Style.reset} -{Fore.cyan} punch out{Style.reset}
{Fore.light_green}brks|break_start{Style.reset} -{Fore.cyan} start your break{Style.reset}
{Fore.light_green}brke|break_end{Style.reset} -{Fore.cyan} end your break{Style.reset}
{Fore.light_green}clrd|clear_date{Style.reset} -{Fore.cyan} clear shift for date{Style.reset}
{Fore.light_green}rmd|remove_date|rm_date -{Fore.cyan}Remove Shift by ShiftId{Style.reset}
{Fore.light_green}ca|clear_all{Style.reset} -{Fore.cyan} clear all punches{Style.reset}

{Fore.light_green}ed|edit_date{Style.reset} -{Fore.cyan} edit a date's punch{Fore.orange_red_1}(If no Shift, then a new one will be prompted for creation){Style.reset}
{Fore.light_green}vd|view_date{Style.reset} -{Fore.cyan} view a date's data{Style.reset}
{Fore.light_green}vdr|view_date_range{Style.reset} -{Fore.cyan} view a date ranges data {Style.underline}{Fore.grey_70}Calculates For/With{Style.reset} {Style.bold}{Fore.light_green}Gross/{Fore.light_yellow}Net/{Fore.medium_violet_red}Tax %/{Fore.steel_blue_1a}Union{Style.reset}
{Fore.light_green}vdrtt|view-date-range-total-time{Style.reset} -{Fore.cyan} view a date ranges total duration worked only, {Fore.light_red}{Style.underline}no income calculations!{Style.reset}
{Fore.light_green}d|duration{Style.reset} -{Fore.cyan} view current punch's duration{Style.reset}
{Fore.light_green}va|view_all{Style.reset} -{Fore.cyan} view all punches{Style.reset}
{Fore.light_green}gross{Style.reset} -{Fore.cyan}calculate gross income from prompted date's total duration with rate of pay as hourly{Style.reset}
{Fore.light_green}e[4..8]{Style.reset} -{Fore.cyan}estimate shift punches from datetime.now(){Style.reset}
{Fore.light_green}me[4..8]|manual_estimate_[4..8]h{Style.reset} -{Fore.cyan}manually estimate shift punches from datetime.now(){Style.reset}
{Fore.light_green}enow|estimate_now|shift_help{Style.reset} -{Fore.cyan}show estimated punch data for Right-Now!{Style.reset}
{Fore.light_green}calculate_earnings_1|ce1{Style.reset} -{Fore.cyan}show estimated earnings!{Style.reset}
{Fore.light_green}project_time|pt1{Style.reset} -{Fore.cyan}add time to current time and display, use units like hour, minute second, negatives are allowed!{Style.reset}
{Fore.light_green}mit|earn_est|made_in_time{Style.reset} -{Fore.cyan}estimate gross for duration!{Style.reset}
{Fore.sea_green_1a}2dd|2-date-duration{Style.reset} -{Fore.steel_blue_1a}Duration between 2 datetimes, or 2-date-duration{Style.reset}
{Fore.sea_green_1a}2ddr|2-date-duration-rate{Style.reset} -{Fore.steel_blue_1a}Duration between 2 datetimes calculated with compensation info, 2-date-duration-rate{Style.reset}
{Fore.sea_green_1a}gross2net|g2n{Style.reset} -{Fore.steel_blue_1a}calculate gross to net with union,tax,gross for net{Style.reset}
{Fore.sea_green_1a}cdr|check_date_range{Style.reset} -{Fore.steel_blue_1a}check date range of shifts for missing fields{Style.reset}
{Fore.sea_green_1a}check all|check_all{Style.reset} -{Fore.steel_blue_1a}check all shifts for missing fields{Style.reset}
{Fore.sea_green_1a}vdrs|view_date_range_short{Style.reset} -{Fore.steel_blue_1a}print range of shift dates data, short version{Style.reset}
'''
        def mkT(text,self):
            return text
        while True:
            mode='PunchCard'
            fieldname='Menu'
            h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
            cmd=Prompt.__init2__(None,func=mkT,ptext=f"{h}Do What?",helpText=self.helpText,data=self)
            if cmd in [None,]:
                return

            if cmd.lower() in ['gross',]:
                def mkF(text,self):
                    try:
                        return float(text)
                    except Exception as e:
                        print(e)
                        return -1
                while True:
                    try:
                        with Session(engine) as session:
                            d=self.datePicker()
                            if not d:
                                break
                            s=session.query(Shift).filter(Shift.Date==d).first()
                            if s:
                                print(s)

                                fieldname='PunchCard'
                                mode='GROSS'
                                h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                                rate=Prompt.__init2__(None,func=mkF,ptext=f"{h}Rate of Pay?",helpText="your rate of pay",data=self)
                                if rate in [None,]:
                                    break
                                s.gross(rate=rate)
                            else:
                                print(f"{Fore.light_red}No Punches For that date!{Style.reset}")
                            break
                    except Exception as e:
                        print(e)
            elif cmd.lower() in 'rmd|remove_date|rm_date'.split("|"):
                while True:
                    try:
                        def mkIntegerShift(text,self):
                            try:
                                if text in ['',]:
                                    return
                                else:
                                    asi=int(eval(text))
                                    return asi
                            except Exception as e:
                                print(e)
                        #for use with heade
                        fieldname='ByShiftId'
                        mode='RMD'
                        h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'        
                        shiftId=Prompt.__init2__(None,func=mkIntegerShift,ptext=f"{h}Shift Id:",helpText="shiftId to Delete",data=self)
                        if shiftId not in [None,]:
                            with Session(self.engine) as session:
                                shiftS=session.query(Shift).filter(Shift.ShiftId==shiftId).first()
                                if shiftS:
                                    print(shiftS)
                                    session.delete(shiftS)
                                    session.commit()
                                    session.flush()
                        break
                    except Exception as e:
                        print(e)

            elif cmd.lower() in '2ddr|2-date-duration-rate'.split("|"):
                CalcNetFrom2Pt(rate=True)
            elif cmd.lower() in '2dd|2-date-duration'.split("|"):
                CalcNetFrom2Pt(rate=False)
            elif cmd.lower() in 'calculate_earnings_1|ce1'.split('|'):
                CalculateEarnings()
            elif cmd.lower() in 'gross2net|g2n'.split('|'):
                Gross2Net()
            elif cmd.lower() in 'project_time|pt1'.split('|'):
                ProjectMyTime()
            elif cmd.lower() in 'mit|earn_est|made_in_time'.split('|'):
                MadeInTime()
            elif cmd.lower() in ['e8']:
                Shift.estimatedPunches_8h(None)
            elif cmd.lower() in ['me8','manual_estimate_8h']:
                Shift.manual_estimate_8(Shift)
            elif cmd.lower() in ['e7']:
                Shift.estimatedPunches_7h(None)
            elif cmd.lower() in ['me7','manual_estimate_7h']:
                Shift.manual_estimate_7(Shift)
            elif cmd.lower() in ['e6']:
                Shift.estimatedPunches_6h(None)
            elif cmd.lower() in ['me6','manual_estimate_6h']:
                Shift.manual_estimate_6(Shift)
            elif cmd.lower() in ['e5']:
                Shift.estimatedPunches_5h(None)
            elif cmd.lower() in ['me5','manual_estimate_5h']:
                Shift.manual_estimate_5(Shift)
            elif cmd.lower() in ['e4']:
                Shift.estimatedPunches_4h(None)
            elif cmd.lower() in ['me4','manual_estimate_4h']:
                Shift.manual_estimate_4(Shift)
            elif cmd.lower() in ['ps','start']:
                with Session(engine) as session:
                    d=self.datePicker()
                    #dt=self.datePicker()
                    s=session.query(Shift).filter(Shift.Date==d).first()
                    if s:
                        s.duration_completed()
                    else:
                        pcard=Shift(Date=d,start=datetime.now())
                        session.add(pcard)
                        session.commit()
                        session.refresh(pcard)
                        pcard.duration_completed()
            elif cmd.lower() in ['pe','end']:
                with Session(engine) as session:
                    s=session.query(Shift).filter(Shift.Date==self.datePicker()).first()
                    if s:
                        if s and not s.end:
                            s.end=datetime.now()
                            session.commit()
                            session.flush()
                            session.refresh(s)
                        elif s and s.end:
                            print(f"{Fore.light_yellow}Your Shift {Fore.light_red}End{Fore.light_yellow} has already been punched today... {Fore.medium_violet_red}Nothing will be done!{Style.reset}")

                        s.duration_completed()
                    else:
                        print(f"{Fore.light_red}No Punches Today{Style.reset}")
            elif cmd.lower() in ['d','duration',]:
                with Session(engine) as session:
                    s=session.query(Shift).filter(Shift.Date==self.datePicker()).first()
                    if s:
                        s.duration_completed()
                        print(s)
                    else:
                        print(f"{Fore.light_red}No Punches Today{Style.reset}")
            elif cmd.lower() in ['enow','estimate_now','shift_help']:
                Shift(start=datetime.now()).helpCard()
            elif cmd.lower() in ['brs','break_start','brks']:
                with Session(engine) as session:
                    s=session.query(Shift).filter(Shift.Date==self.datePicker()).first()
                    if s and not s.break_start:
                        s.break_start=datetime.now()
                        session.commit()
                        session.flush()
                        session.refresh(s)
                    elif s and s.break_start:
                        print(f"{Fore.light_yellow}A Break {Fore.sea_green_1a}Start{Fore.light_yellow} has already been punched today... {Fore.medium_violet_red}Nothing will be done!{Style.reset}")
                    if s:
                        s.duration_completed()
                    else:
                        print(f"{Fore.light_red}No Such Punch!{Style.reset}")
            elif cmd.lower() in ['bre','break_end','brke']:
                with Session(engine) as session:
                    s=session.query(Shift).filter(Shift.Date==self.datePicker()).first()
                    if s and not s.break_end:
                        s.break_end=datetime.now()
                        session.commit()
                        session.flush()
                        session.refresh(s)
                    elif s and s.break_end:
                        print(f"{Fore.light_yellow}A Break {Fore.red}End{Fore.light_yellow} has already been punched today... {Fore.medium_violet_red}Nothing will be done!{Style.reset}")
                    if s:
                        s.duration_completed()
                    else:
                        print(f"{Fore.light_red}No Such Punch!{Style.reset}")
                    #s.duration_completed()
            elif cmd.lower() in ['clrd','clear_date',]:
                with Session(engine) as session:
                    s=session.query(Shift).filter(Shift.Date==self.datePicker()).delete()
                    print(f"deleted: {s}")
                    session.commit()
            elif cmd.lower() in ['ed','edit_date']:
                while True:
                    try:
                        '''
                        def mkT(text,self):
                            return text
                        year=Prompt.__init2__(None,func=mkT,ptext=f"Year[{datetime.now().year}]",helpText="year to look for",data=self)
                        if year == None:
                            return
                        elif year == '':
                            year=datetime.now().year

                        month=Prompt.__init2__(None,func=mkT,ptext=f"Month[{datetime.now().month}]",helpText="month to look for",data=self)
                        if month == None:
                            return
                        elif month == '':
                            month=datetime.now().month

                        day=Prompt.__init2__(None,func=mkT,ptext=f"Day[{datetime.now().day}]",helpText="day to look for",data=self)
                        if day == None:
                            return
                        elif day == '':
                            day=datetime.now().day

                        dt=date(int(year),int(month),int(day))
                        '''
                        dt=self.datePicker()
                        if not dt:
                            break
                        noShift=False
                        with Session(self.engine) as session:
                            query=session.query(Shift).filter(Shift.Date==dt)
                            result=query.first()
                            if not result:
                                print(f"{Fore.light_red}No Shift for that date!")
                                while True:
                                    try:
                                        def mklbool(text,data):
                                            bl=None
                                            if text.lower() in ['y','yes']:
                                                bl=True
                                            elif text.lower() in ['','n','no']:
                                                bl=False
                                            else:
                                                try:
                                                    bl=eval(text)
                                                except Exception as e:
                                                    bl=False
                                            return bl

                                        fieldname='PunchCard'
                                        mode='EditDate'
                                        h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                                        newShift=Prompt.__init2__(None,func=mklbool,ptext=f"{h}Make a new punch/shift?",helpText='y|n|b|q')
                                        if newShift == False:
                                            noShift=True
                                            break
                                        else:
                                            result=Shift(Date=dt,start=None,end=None,break_end=None,break_start=None)
                                            session.add(result)
                                            session.commit()
                                            session.refresh(result)
                                            print(f"Created -> {result}")

                                        break
                                    except Exception as e:
                                        print(e)
                            if noShift:
                                break
                            print(f"{Fore.orange_red_1}{Style.bold}Now that that's done, it's time to set datetimes for the {Fore.light_green}shift{Style.reset}")
                            
                            for col in Shift.__table__.columns:
                                while True:
                                    if col.name not in ['Date','ShiftId']:
                                        def mkTime(text,self):
                                            print(text)
                                            if text == 'now':
                                                nv=datetime.now()
                                                return
                                            if text in ['skip','']:
                                                return
                                            elif text.lower() in ['y','yes']:
                                                try:
                                                    '''
                                                    def mkint(text,self):
                                                        if text == '':
                                                            if self == 'hour':
                                                                return datetime.now().hour
                                                            elif self == 'minute':
                                                                return datetime.now().minute
                                                            elif self == "second":
                                                                return datetime.now().second
                                                            else:
                                                                return 0
                                                        else:
                                                            v=int(text)
                                                            if v < 0:
                                                                raise Exception("Must be greater than 0")
                                                            return v

                                                    hour=Prompt.__init2__(None,func=mkint,ptext="Hour",helpText=f"hour to use for {self}",data="hour")
                                                    if hour == None:
                                                        return
                                                    minute=Prompt.__init2__(None,func=mkint,ptext="Minute",helpText=f"minute to use for {self}",data="minute")
                                                    if minute == None:
                                                        return
                                                    second=Prompt.__init2__(None,func=mkint,ptext="Second",helpText=f"second to use  for {self}",data="second")
                                                    if second == None:
                                                        return
                                                    ndt=DatePkr()
                                                    if not ndt:
                                                        ndt=dt
                                                    dtime=datetime(ndt.year,ndt.month,ndt.day,hour,minute,second)
                                                    '''
                                                    #dtime=datetimePickerF(None)
                                                    dtime=DateTimePkr()
                                                    return dtime
                                                except Exception as e:
                                                    print(e)
                                                    return None


                                        fieldname='PunchCard'
                                        mode='EditDateField'
                                        h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                                        value=Prompt.__init2__(None,func=mkTime,ptext=f"{h}{col.name} old[{getattr(result,col.name)}]",helpText=f"set {col} to new value!",data=col.name)
                                        if value == None:
                                            break
                                            
                                        setattr(result,col.name,value)
                                        session.commit()
                                        session.flush()
                                        session.refresh(result)
                                        print(result)
                                        break
                                    else:
                                        break

                        break
                    except Exception as e:
                        print(e)
            elif cmd.lower() in ['ca','clear_all']:
                with Session(self.engine) as session:
                    result=session.query(Shift).delete()
                    session.commit()
                    print(f"deleted {result}!")
            elif cmd.lower() in ['va','view_all']:
                with Session(self.engine) as session:
                    result=session.query(Shift).all()
                    ct=len(result)
                    if ct == 0:
                        print(f"{Fore.red}No Results{Style.reset}")
                    else:
                        for num,r in enumerate(result):
                            print(f"{Fore.light_yellow}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} -> {r}")
            elif cmd.lower() in ['check all','check_all']:
                with Session(self.engine) as session:
                    results=session.query(Shift).all()
                    ct=len(results)
                    if ct == 0:
                        print(f"{Fore.red}No Results{Style.reset}")
                    else:
                        eh=f'{Fore.light_yellow}{Style.bold}*ERROR*--->{Style.reset}'
                        
                        ch=f'\n{Fore.dark_goldenrod}{Style.bold}*CHECKING*--->{Style.reset}'
                        for num,r in enumerate(results):
                            print(f"{ch}{Fore.green_yellow}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} - {r}")
                            if r.start == None:
                                print(f"{eh}{Fore.orange_red_1}Missing {Fore.light_red}start{Fore.light_steel_blue} field{Style.reset}!")
                            if r.end == None:
                                print(f"{eh}{Fore.orange_red_1}Missing {Fore.light_red}end{Fore.light_steel_blue} field{Style.reset}!")
                            if r.break_end == None:
                                print(f"{eh}{Fore.orange_red_1}Missing {Fore.light_red}break_end{Fore.light_steel_blue} field{Style.reset}!")
                            if r.break_start == None:
                                print(f"{eh}{Fore.orange_red_1}Missing {Fore.light_red}break_start{Fore.light_steel_blue} field{Style.reset}!")
                            
            elif cmd.lower() in ['vd','view_date']:
                while True:
                    try:
                        '''
                        def mkT(text,self):
                            return text
                        year=Prompt.__init2__(None,func=mkT,ptext=f"Year[{datetime.now().year}]",helpText="year to look for",data=self)
                        if year == None:
                            return
                        elif year == '':
                            year=datetime.now().year

                        month=Prompt.__init2__(None,func=mkT,ptext=f"Month[{datetime.now().month}]",helpText="month to look for",data=self)
                        if month == None:
                            return
                        elif month == '':
                            month=datetime.now().month

                        day=Prompt.__init2__(None,func=mkT,ptext=f"Day[{datetime.now().day}]",helpText="day to look for",data=self)
                        if day == None:
                            return
                        elif day == '':
                            day=datetime.now().day

                        dt=date(int(year),int(month),int(day))
                        '''

                        dt=self.datePicker()
                        with Session(self.engine) as session:
                            query=session.query(Shift).filter(Shift.Date==dt)
                            results=query.all()
                            ct=len(results)
                            for num,r in enumerate(results):
                                print(f"{Fore.green_yellow}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} -> {r}")
                            print(f"There are {Fore.grey_70}{Style.underline}{ct}{Style.reset} total results!")

                        break
                    except Exception as e:
                        print(e)
            elif cmd.lower() in ['vdrtt','view-date-range-total-time']:
                while True:
                    try:
                        print(f"{Fore.green_yellow}Start Date{Style.reset}")
                        dtS=self.datePicker()
                        print(f"{Fore.medium_violet_red}End Date{Style.reset}")
                        dtE=self.datePicker()
                        

                        total_time=None
                        with Session(self.engine) as session:
                            query=session.query(Shift).filter(Shift.Date.between(dtS,dtE))
                            results=query.all()
                            ct=len(results)
                            
                            for num,r in enumerate(results):
                                print(f"{Fore.green_yellow}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} - Supplementary Data\n{Fore.medium_violet_red}Shift Duration Worked - {Fore.dark_goldenrod}Shift Date - {Fore.light_red}ShiftId{Style.reset}\n{Fore.medium_violet_red}{r.dc()} - {Fore.dark_goldenrod}{r.Date} - {Fore.light_red}{r.ShiftId}{Style.reset}")
                                #duration completed without print
                                d=r.dc()
                                if d != None:
                                    if total_time == None:
                                        total_time=d
                                    else:
                                        total_time+=d
                        print(f"{Fore.light_yellow}Total Duration Worked{Fore.light_green}:{Fore.sea_green_1a}{total_time}{Style.reset}")
                                
                        break
                    except Exception as e:
                        print(e)
            elif cmd.lower() in ['vdr','view_date_range']:
                while True:
                    try:
                        print(f"{Fore.green_yellow}Start Date{Style.reset}")
                        dtS=self.datePicker()
                        print(f"{Fore.medium_violet_red}End Date{Style.reset}")
                        dtE=self.datePicker()
                        def mkF(text,self):
                            try:
                                return float(text)
                            except Exception as e:
                                return -1
                        rate=0
                        while True:
                            try:

                                fieldname='PunchCard'
                                mode='VDR'
                                h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
                                rate=Prompt.__init2__(None,func=mkF,ptext=f"{h}Rate of Pay:",helpText="how much do you make per hour?",data=self)
                                if rate == None:
                                    return
                                elif rate == -1:
                                    continue
                                break
                            except Exception as e:
                                print(e)

                        total_time=None
                        with Session(self.engine) as session:
                            query=session.query(Shift).filter(Shift.Date.between(dtS,dtE))
                            results=query.all()
                            ct=len(results)
                            total_gross=0
                            for num,r in enumerate(results):
                                print(f"{Fore.green_yellow}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} - Supplementary Data")
                                d=r.duration_completed()
                                if d != None:
                                    if total_time == None:
                                        total_time=d
                                    else:
                                        total_time+=d
                                try:
                                    total_gross+=r.gross(rate=rate)
                                except Exception as e:
                                    print(e)
                                print(f"{Fore.green_yellow}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} -> {r}")
                                print(f"{Fore.light_red}{'-'*20}{Style.reset}")
                            
                            ur=pint.UnitRegistry()
                            if float(ur.convert(total_time.total_seconds(),"seconds","hours")) > 40:
                                ot=round(ur.convert(total_time.total_seconds(),"seconds","hours")-40,2)
                                otr=roundup(rate*1.5)
                                otr_total=(ot*otr)
                                dur=otr_total+(40*rate)
                                total_gross=dur
                                print(f"{Fore.light_yellow}{Style.bold}OverTime was accrued: {Fore.light_red}${otr}/Hr{Fore.light_yellow} for {Fore.light_magenta}{ot} {Fore.light_green}Hrs. = [${round(otr_total,2)} (OT Gross)] + [${round(rate*40,2)} (40 Hr * ${rate})] \n= ${round(dur,2)}{Style.reset}")
                            Gross2Net(_gross=round(total_gross,2))
                            print(f"There are {Fore.grey_70}{Style.underline}{ct}{Style.reset} total results!")
                            print(f"A {Fore.green}Total Gross{Style.reset} of {Fore.light_green}${round(total_gross,2)}{Style.reset} was made!")
                            print(f"{Fore.orange_red_1}Total Duration worked is {Fore.cyan} = {Style.bold}{Fore.medium_violet_red}{total_time}{Style.reset}")

                        break
                    except Exception as e:
                        print(e)
            elif cmd.lower() in ['vdrs','view_date_range_short']:
                while True:
                    try:
                        print(f"{Fore.green_yellow}Start Date{Style.reset}")
                        dtS=self.datePicker()
                        if dtS == None:
                            break
                        print(f"{Fore.medium_violet_red}End Date{Style.reset}")
                        dtE=self.datePicker()
                        if dtE == None:
                            break
                        with Session(self.engine) as session:
                            query=session.query(Shift).filter(Shift.Date.between(dtS,dtE))
                            results=query.all()
                            ct=len(results)
                            
                            for num,r in enumerate(results):
                                print(f"{Fore.green_yellow}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} - {r}")
                                
                        break
                    except Exception as e:
                        print(e)
            elif cmd.lower() in ['cdr','check_date_range']:
                while True:
                    try:
                        print(f"{Fore.green_yellow}Start Date{Style.reset}")
                        dtS=self.datePicker()
                        print(f"{Fore.medium_violet_red}End Date{Style.reset}")
                        dtE=self.datePicker()
                        
                        with Session(self.engine) as session:
                            query=session.query(Shift).filter(Shift.Date.between(dtS,dtE))
                            results=query.all()
                            ct=len(results)
                            eh=f'{Fore.light_yellow}{Style.bold}*ERROR*--->{Style.reset}'
                            ch=f'\n{Fore.dark_goldenrod}{Style.bold}*CHECKING*--->{Style.reset}'
                            for num,r in enumerate(results):
                                print(f"{ch}{Fore.green_yellow}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} - {r}")
                                if r.start == None:
                                    print(f"{eh}{Fore.orange_red_1}Missing {Fore.light_red}start{Fore.light_steel_blue} field{Style.reset}!")
                                if r.end == None:
                                    print(f"{eh}{Fore.orange_red_1}Missing {Fore.light_red}end{Fore.light_steel_blue} field{Style.reset}!")
                                if r.break_end == None:
                                    print(f"{eh}{Fore.orange_red_1}Missing {Fore.light_red}break_end{Fore.light_steel_blue} field{Style.reset}!")
                                if r.break_start == None:
                                    print(f"{eh}{Fore.orange_red_1}Missing {Fore.light_red}break_start{Fore.light_steel_blue} field{Style.reset}!")
                                
                                
                        break
                    except Exception as e:
                        print(e)

