import sys,os,calendar
from datetime import datetime,date,timedelta
from datetime import time as TIME
from datetime import time as _time_
from radboy.DB.Prompt import *
from radboy.DB.Prompt import Prompt
from datetime import datetime,timedelta
import pint
from colored import Fore,Style
from pathlib import Path

def mkint(text,TYPE):
    try:
        if text.lower() in ['sun_we','sat_we','mon_ws','sun_ws','sat_ws','fri_we']:
            return text.lower()
        elif text.lower() in ['y','yesterday',] and TYPE in ['day','month','year']:
            return 'y'
        elif text.lower() in ['t','today',] and TYPE in ['day','month','year']:
            return 't'
        elif text.lower() in ['n','now'] and TYPE in ['hour','minute','seconds']:
            return 'n'
        elif text not in ['',]:
            drange=(0,calendar.monthrange(date.today().year,date.today().month)[-1])
            if TYPE == 'day':
                if int(text) not in [i+1 for i in range(*drange)]:
                    raise Exception(f"Not in {drange}")
            elif TYPE == 'month':
                if int(text) not in [i for i in range(1,13)]:
                    raise Exception(f"Not in {[i for i in range(1,13)]}")
            elif TYPE == 'year':
                pass
            elif TYPE == 'hour':
                if int(text) not in [i for i in range(24)]:
                    raise Exception(f"Not in {[i for i in range(24)]}")
            elif TYPE == 'minute':
                if int(text) not in [i for i in range(60)]:
                    raise Exception(f"Not in {[i for i in range(60)]}")
            elif TYPE == 'second':
                if int(text) not in [i for i in range(60)]:
                    raise Exception(f"Not in {[i for i in range(60)]}")
            elif TYPE == 'float':
                return float(text)
            return int(text)
        else:
            if TYPE == 'day':
                return datetime.now().day
            elif TYPE == 'month':
                return datetime.now().month
            elif TYPE == 'year':
                return datetime.now().year
            elif TYPE == 'hour':
                return datetime.now().hour
            elif TYPE == 'minute':
                return datetime.now().minute
            elif TYPE == 'second':
                return datetime.now().second
            elif TYPE == 'float':
                return float(0)
            else:
                return 0
    except Exception as e:
        print(e)
        if TYPE == 'day':
            return datetime.now().day
        elif TYPE == 'month':
            return datetime.now().month
        elif TYPE == 'year':
            return datetime.now().year
        elif TYPE == 'hour':
            return datetime.now().hour
        elif TYPE == 'minute':
            return datetime.now().minute
        elif TYPE == 'second':
            return datetime.now().second
        else:
            return 0

def sun_weekstart():
    day=datetime.today()
    ws=day-timedelta(days=day.weekday()+1)
    return ws

def sat_weekend():
    day=datetime.today()
    ws=day-timedelta(days=day.weekday()+1)
    we=ws+timedelta(days=6+1)
    we=date(we.year,we.month,we.day)
    return we

def mon_weekstart():
    day=datetime.today()
    ws=day-timedelta(days=day.weekday())
    ws=date(ws.year,ws.month,ws.day)
    return ws

def sun_weekend():
    day=datetime.today()
    ws=day-timedelta(days=day.weekday())
    we=ws+timedelta(days=6)
    we=date(we.year,we.month,we.day)
    return we

def sat_weekstart():
    day=datetime.today()
    ws=day-timedelta(days=day.weekday()+2)
    ws=date(ws.year,ws.month,ws.day)
    return ws

def fri_weekend():
    day=datetime.today()
    ws=day-timedelta(days=day.weekday()+2)
    we=ws+timedelta(days=6+2)
    we=date(we.year,we.month,we.day)
    return we

def DatePkr():
    def mkYesterday():
        yesterday_dt=datetime.today()-timedelta(seconds=pint.UnitRegistry().convert(24,'hours','seconds'))
        yesterday=date(yesterday_dt.year,yesterday_dt.month,yesterday_dt.day)
        return yesterday
    extra=f'''
--------------------------
{Fore.light_salmon_1}{Style.underline}sunday week start {Style.reset}-{Fore.light_sea_green} sun_ws {Fore.orange_red_1}{Style.bold}({Fore.light_steel_blue}{sun_weekend()}{Style.reset}{Style.bold}{Fore.orange_red_1}){Style.reset}
{Fore.light_salmon_1}{Style.underline}monday week start {Style.reset}-{Fore.light_sea_green} mon_ws {Fore.orange_red_1}{Style.bold}({Fore.light_steel_blue}{mon_weekstart()}{Style.reset}{Style.bold}{Fore.orange_red_1}){Style.reset}
{Fore.light_salmon_1}{Style.underline}sunday week end {Style.reset}-{Fore.light_sea_green} sun_we {Fore.orange_red_1}{Style.bold}({Fore.light_steel_blue}{sun_weekend()}{Style.reset}{Style.bold}{Fore.orange_red_1}){Style.reset}
{Fore.light_salmon_1}{Style.underline}saturday week end {Style.reset}-{Fore.light_sea_green} sat_we {Fore.orange_red_1}{Style.bold}({Fore.light_steel_blue}{sat_weekend()}{Style.reset}{Style.bold}{Fore.orange_red_1}){Style.reset}
{Fore.light_salmon_1}{Style.underline}saturday week start {Style.reset}-{Fore.light_sea_green} sat_ws {Fore.orange_red_1}{Style.bold}({Fore.light_steel_blue}{sat_weekstart()}{Style.reset}{Style.bold}{Fore.orange_red_1}){Style.reset}
{Fore.light_salmon_1}{Style.underline}friday week end {Style.reset}-{Fore.light_sea_green} fri_we {Fore.orange_red_1}{Style.bold}({Fore.light_steel_blue}{fri_weekend()}{Style.reset}{Style.bold}{Fore.orange_red_1}){Style.reset}
{Fore.light_salmon_1}{Style.underline}yesterday {Style.reset}-{Fore.light_sea_green} y|yesterday {Fore.orange_red_1}{Style.bold}({Fore.light_steel_blue}{mkYesterday()}{Style.reset}{Style.bold}{Fore.orange_red_1}){Style.reset}
{Fore.light_salmon_1}{Style.underline}today {Style.reset}-{Fore.light_sea_green} t|today {Fore.orange_red_1}{Style.bold}({Fore.light_steel_blue}{datetime.today()}{Style.reset}{Style.bold}{Fore.orange_red_1}){Style.reset}
    '''
    
    yesterday=None
    while True:
        try:
            pass
            year=Prompt.__init2__(None,func=mkint,ptext=f"Year[Default:{date.today().year}]",helpText=f"year to be used in date returned{extra}",data='year')
            if year in [None,]:
                return None
            elif year in ['y',]:
               return mkYesterday()
            elif year in ['t']:
                return date(datetime.today().year,datetime.today().month,datetime.today().day)
            elif year in ['sun_ws',]:
                return sun_weekstart()
            elif year in ['sat_we',]:
                return sun_weekend()
            elif year in ['mon_ws',]:
                return mon_weekstart()
            elif year in ['sun_we']:
                return sun_weekend()
            elif year in ['sat_ws',]:
                return sat_weekstart()
            elif year in ['fri_we']:
                return fri_weekend()
            break
        except Exception as e:
            print(e)
    
    while True:
        try:
            pass
            month=Prompt.__init2__(None,func=mkint,ptext=f"Month[1..12|Default:{date.today().month}]",helpText=f"month to be used in date returned{extra}",data='month')
            if month in [None,]:
                return None
            elif month in ['y',]:
               return mkYesterday()
            elif month in ['t']:
                return date(datetime.today().year,datetime.today().month,datetime.today().day)
            elif month in ['sun_ws',]:
                return sun_weekstart()
            elif month in ['sat_we',]:
                return sun_weekend()
            elif month in ['mon_ws',]:
                return mon_weekstart()
            elif month in ['sun_we']:
                return sun_weekend()
            elif year in ['sat_ws',]:
                return sat_weekstart()
            elif year in ['fri_we']:
                return fri_weekend()
            break
        except Exception as e:
            print(e)
        
    while True:
        try:
            pass
            day=Prompt.__init2__(None,func=mkint,ptext=f"Day[{'..'.join((str(1),str(calendar.monthrange(date.today().year,date.today().month)[-1])))}|Default:{date.today().day}]",helpText=f"day to be used in date returned{extra}",data='day')
            if day in [None,]:
                return None
            elif day in ['y',]:
               return mkYesterday()
            elif day in ['t']:
                return date(datetime.today().year,datetime.today().month,datetime.today().day)
            elif day in ['sun_ws',]:
                return sun_weekstart()
            elif day in ['sat_we',]:
                return sun_weekend()
            elif day in ['mon_ws',]:
                return mon_weekstart()
            elif day in ['sun_we']:
                return sun_weekend()
            elif year in ['sat_ws',]:
                return sat_weekstart()
            elif year in ['fri_we']:
                return fri_weekend()
            break
        except Exception as e:
            print(e)
    return date(year,month,day)


def TimePkr():
    while True:
        try:
            pass
            hour=Prompt.__init2__(None,func=mkint,ptext=f"hour [0..24|Default:{datetime.now().hour}]",helpText="hour to be used in date returned; use n/now to use current time",data='hour')
            if hour in [None,]:
                return None
            elif hour in ['n',]:
                x=datetime.now()
                return _time_(x.hour,x.minute,x.second)
            break
        except Exception as e:
            print(e)
        #print(hour)
        
    while True:
        try:
            pass
            minute=Prompt.__init2__(None,func=mkint,ptext=f"minute [0..59|Default:{datetime.now().minute}]]",helpText="minute to be used in date returned; use n/now to use current time",data='minute')
            if minute in [None,]:
                return None
            elif minute in ['n',]:
                x=datetime.now()
                return _time_(x.hour,x.minute,x.second)
            break
        except Exception as e:
            print(e)
        
    while True:
        try:
            pass
            second=Prompt.__init2__(None,func=mkint,ptext=f"second [0..59|Default:Current Second of The Clock]",helpText="second to be used in date returned; use n/now to use current time",data='second')
            if second in [None,]:
                return None
            elif second in ['n',]:
                x=datetime.now()
                return _time_(x.hour,x.minute,x.second)
            break
        except Exception as e:
            print(e)
        
    return _time_(hour,minute,second)



def DateTimePkr(DATE=None):
    tm=None
    while True:
        tm=TimePkr()
        if not tm:
            raise Exception("Time is Missing!")
            tm=TimePkr()
        else:
            break
    while True:
        if DATE:
            dt=DATE
        else:
            dt=DatePkr()
        if not dt:
            raise Exception("Date is Missing!")
        else:
            break

    return datetime(dt.year,dt.month,dt.day,tm.hour,tm.minute,tm.second)

def CalculateEarnings(tax_percent_dec=0.178):
    try:
        reg=pint.UnitRegistry()
        month=datetime.now().month
        year=datetime.now().year
        today=datetime.now().day
        tomorrow=today+1
        s=None
        while True:
            try:
                print(f"{Fore.cyan}Please enter the shift Start data.{Style.reset}")
                s=DateTimePkr()
                if not s:
                    raise Exception("Must Have a Start DateTime")
                break
            except Exception as ee:
                print(ee)
                return
        e=None
        while True:
            try:
                print(f"{Fore.cyan}Please enter the shift End data.{Style.reset}")
                e=DateTimePkr()
                if not e:
                    raise Exception("Must have a End DateTime")
                break
            except Exception as ee:
                print(ee)
                return
        d=e-s
        while True:
            try:
                period=Prompt.__init2__(None,func=mkint,ptext="Lunch Length in minutes [0..59]",helpText="how long your lunch was in minutes upto 59 minutes",data="minute")
                if period in [None,]:
                    print("Lunch must a value!")
                    return
                break
            except Exception as e:
                print(e)

        lunch=timedelta(seconds=60*period)
        d=d-lunch

        while True:
            try:
                rate=Prompt.__init2__(None,func=mkint,ptext="Your payrate per hour?",helpText="$/Hr rate",data="float")
                if rate in [None,]:
                    print("You need need to provide an hourly rate!")
                    return
                break
            except Exception as e:
                print(e)
        
        gross=round(rate*float(reg.convert(d.total_seconds(),'seconds','hours')),2)

        while True:
            try:
                tdays=Prompt.__init2__(None,func=mkint,ptext="Total Days?",helpText="$/Hr rate",data="integer")
                if tdays in [None,]:
                    print("You need to provide total days")
                    return
                break
            except Exception as e:
                print(e)

        fourdayg=round(gross*tdays,2)
        tax=round(fourdayg*0.178,2)
        union=10
        msg=f'''
{Fore.cyan}duration{Style.reset}:
 {d} =
 {Fore.light_red}({e}(end) {Style.reset}
 -{Fore.green_yellow}{s}(start)){Style.reset}
 -{Fore.light_yellow}{lunch}(lunch){Style.reset}
{Fore.light_green}gross{Style.reset}:
 {Fore.light_green}1 Shift Gross ${gross}{Style.reset}={Fore.light_magenta}$/Hr(${rate})*duration in Hr's ({d}){Style.reset}
{Fore.green}Total ({tdays}) Days Total Gross{Style.reset}:
 {Fore.green}Gross = ${fourdayg}{Style.reset}=days({tdays}) *{Fore.light_green}gross(${gross})
{Fore.cyan}{Style.bold}Net{Style.reset}:
{Fore.cyan}-tax{Style.reset} = (${Fore.green}{fourdayg}{Style.reset}*{Fore.yellow}0.178(Rough Estimate for 17.8%)){Style.reset} = {Fore.dark_goldenrod}${round(tax,2)}{Style.reset}
{Fore.cyan}-union{Style.reset} = {Fore.medium_violet_red}${union}{Style.reset}
{Fore.cyan}Net{Style.reset} = ${fourdayg-tax-union}
'''
        print(msg)
    except Exception as e:
        print(e)

def MadeInTime():
    registry=pint.UnitRegistry()
    def mkSeconds(text,data):
        try:
            return pint.Quantity(text).m_as('hours'),text
        except Exception as e:
            raise e

    while True:
        try:
            z=Prompt.__init2__(None,func=mkSeconds,ptext="amount of time to calculate pay for?",helpText="amount of time to add to now, the number with h(hour),m(minutes),s(seconds), nothing will assume h(hour)",data=None)
            if z in [None,]:
                return None
            forwards,text=z
            if forwards in [None,]:
                return None
           
            while True:
                try:
                    rate=Prompt.__init2__(None,func=mkint,ptext="Your payrate per hour?",helpText="$/Hr rate",data="float")
                    break
                except Exception as e:
                    print(e)
            if rate in [None,]:
                return

            gross=round(float(forwards)*rate,2)

            print(f'{Fore.light_green}${rate}/Hr * ({Fore.light_yellow}{text}) -> {Fore.light_red}${gross}{Style.reset}')
            return
        except Exception as e:
            print(e)

def ProjectMyTime():
    registry=pint.UnitRegistry()
    def mkSeconds(text,data):
        try:
            return pint.Quantity(text).m_as('seconds'),text
        except Exception as e:
            raise e

    while True:
        try:
            forwards,text=Prompt.__init2__(None,func=mkSeconds,ptext="amount of time to add to now?",helpText="amount of time to add to now, the number with h(hour),m(minutes),s(seconds), nothing will assume h(hour)",data=None)
            if forwards in [None,]:
                return None
            now=datetime.now()
            projected=now+timedelta(seconds=forwards)
            print(f'{Fore.light_green}{now} ({Fore.light_yellow}{text}) -> {Fore.light_red}{projected}{Style.reset}')
            break
        except Exception as e:
            print(e)

