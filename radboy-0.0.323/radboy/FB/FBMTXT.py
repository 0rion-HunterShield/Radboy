import radboy.TasksMode as TM
import radboy.DB.db as db
import string
from datetime import datetime
from pathlib import Path
from decimal import Decimal,getcontext
import re
from datetime import timedelta
import calendar
from colored import Fore,Back,Style
fm_data={
        'Decimal':{
            'type':'decimal',
            'default':Decimal('0.0')
            },
        'Name':{
            'type':'str',
            'default':'',
            },
        'Value':{
            'type':'int',
            'default':0,
            },
        'Price':{
           'type':'float',
           'default':0.0,
            },
        'Barcode':{
            'type':'str',
            'default':'000000000000',
            },
        'Code':{
            'type':'str',
            'default':'12345678',
            },
        'DOE':{
            'type':'date',
            'default':None,
            },
        'TOE':{
            'type':'time',
            'default':None,
            },
        'DTOE':{
            'type':'datetime',
            'default':None,
            },
        'DEFAULT':{
            'type':'bool',
            'default':False,
            },
        'List':{
            'type':'list',
            'default':[],
            },
      }
def FormBuilderHelpText():
    TODAY_IS=datetime.now()
    z=TODAY_IS
    msg=f'''{Fore.light_magenta}FormBuilder(data=dict()) Help{Style.reset}
    {Fore.light_yellow}Dates useable by KeyWord (Cheat Sheet for DateTime){Style.reset}
    {Fore.light_cyan}'y','yes','1','t','true','+' {Fore.light_green}-{Fore.light_steel_blue} calls the datepicker{Style.reset}
    {Fore.light_cyan}"n,no,false,f,0,-" {Fore.light_green}-{Fore.light_steel_blue} returns default{Style.reset}
    {Fore.light_cyan}now {Fore.light_green}-{Fore.light_steel_blue} {datetime.now()}{Style.reset}
    {Fore.light_cyan}today {Fore.light_green}-{Fore.light_steel_blue} {datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)}{Style.reset}
    {Fore.light_cyan}tomorrow {Fore.light_green}-{Fore.light_steel_blue} {datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)+timedelta(seconds=60*60*24)}{Style.reset}
    {Fore.light_cyan}yesterday {Fore.light_green}-{Fore.light_steel_blue} {datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)-timedelta(seconds=60*60*24)}{Style.reset}
    {Fore.light_cyan}last month {Fore.light_green}-{Fore.light_steel_blue} {datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)-timedelta(seconds=60*60*24*30)} {Style.reset}
    {Fore.light_cyan}last year {Fore.light_green}-{Fore.light_steel_blue} {datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)-timedelta(seconds=60*60*24*365)}{Style.reset}
    {Fore.light_cyan}next month {Fore.light_green}-{Fore.light_steel_blue} {datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)+timedelta(seconds=60*60*24*30)}{Style.reset}
    {Fore.light_cyan}next week {Fore.light_green}-{Fore.light_steel_blue} {datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)+timedelta(seconds=60*60*24*7)}{Style.reset}
    {Fore.light_cyan}last week {Fore.light_green}-{Fore.light_steel_blue} {datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)-timedelta(seconds=60*60*24*30)}{Style.reset}
    {Fore.light_cyan}next year {Fore.light_green}-{Fore.light_steel_blue} {datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)+timedelta(seconds=60*60*24*365)}{Style.reset}
    {Fore.light_cyan}end week {Fore.light_green}-{Fore.light_steel_blue} {TODAY_IS+timedelta(days=TODAY_IS.weekday())}{Style.reset}
    {Fore.light_cyan}end month {Fore.light_green}-{Fore.light_steel_blue} {datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=calendar.monthrange(z.year,TODAY_IS.month)[-1])}{Style.reset}
    {Fore.light_cyan}end year {Fore.light_green}-{Fore.light_steel_blue} {datetime(year=TODAY_IS.year,month=12,day=calendar.monthrange(z.year,12)[-1])}{Style.reset}
    {Fore.light_cyan}start week {Fore.light_green}-{Fore.light_steel_blue} {TODAY_IS-timedelta(days=TODAY_IS.weekday())}{Style.reset}
    {Fore.light_cyan}start month {Fore.light_green}-{Fore.light_steel_blue} {datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=1)}{Style.reset}
    {Fore.light_cyan}start year {Fore.light_green}-{Fore.light_steel_blue} {datetime(year=TODAY_IS.year,month=1,day=1)}{Style.reset}
    {Fore.grey_70}**{Fore.light_yellow}A Date Can be represented as {Fore.light_cyan}10.26.25={Fore.cyan}10/26/25=10/26/2025={Fore.light_green}oct.26.25={Fore.spring_green_3a}oct/26/25={Fore.light_steel_blue}oct.26.2025{Style.reset}
    {Fore.grey_70}**{Fore.light_yellow}Any of {Fore.yellow}{string.punctuation} {Fore.light_cyan}in `datetime` can be use as the separator, as long as they are the same throughout the string{Style.reset}
    {Fore.grey_70}**{Fore.light_yellow}10.26.1993@4:30{Fore.light_cyan} represents 10/26/1993 at 4:30am, where at indicates a separation to the time string{Style.reset}
    {Fore.grey_70}**{Fore.light_yellow}when {Fore.light_cyan}-{Fore.light_yellow} is used, ususally when a daterange is expected, needs to be between two(2) datestrings, i.e. {Fore.light_steel_blue}10.26.1993-12.15.1997{Style.reset}
    {Fore.grey_70}**{Fore.light_yellow}RETRY{Fore.light_cyan} is issued when parsing fails.{Style.reset}
    '''
    print(msg)


def FormBuilderMkText(text,data,passThru=[],PassThru=True,alternative_false=None,alternative_true=None):
    
    try:
        #if text in passThru:
        #    return text
        if PassThru:
            if text in ['f','m','p','d']:
                return text
        if text == '':
            return 'd'
        value=None
        if data.lower() == 'float':
            try:
                value=float(eval(text))
            except Exception as e:
                try:
                    value=float(text)
                except Exception as e:
                    return 'd'
        elif data.lower() in ['decimal','dec']:
            try:
                getcontext().prec=3
                old_str=text
                old_str_list=list(reversed(sorted([i for i in re.findall(r"[0-9.]+",text)],key=len)))
                newstr_list=list(reversed(sorted([str(f'Decimal({i})') for i in re.findall(r"[0-9.]+",text)],key=len)))
                for num,x in enumerate(old_str_list):
                    #print(num,x,newstr_list[num])
                    old_str=old_str.replace(x,newstr_list[num])

                value=eval(old_str)
                print(value)
                return float(value)
            except Exception as e:
                print(e)
                return 'd'
        elif data.lower() in ['int','integer']:
            try:
                value=int(eval(text))
            except Exception as e:
                try:
                    value=int(text)
                except Exception as e:
                    return 'd'
        elif data.lower() in ['bool','boolean','boolean_basic']:
            if alternative_true not in [None,]:
                if text == alternative_true:
                    return True
            if alternative_false not in [None,]:
                if text == alternative_false:
                    return False
            try:
                value=bool(eval(text))
            except Exception as e:
                try:
                    if data.lower() in ['boolean_basic',]:
                        for i in ['n','no','false','f']:
                            if i in text.lower():
                                return False
                        for i in ['y','yes','true','t']:
                            if i in text.lower():
                                return True
                        return None
                    if text.lower() in ['y','yes','true','t','1']:
                        value=True
                    elif text.lower() in ['n','no','false','f','0']:
                        value=False
                    else:
                        try:
                            if data.lower() not in ['boolean_basic',]:
                                value=bool(eval(text))
                            else:
                                return False
                        except Exception as e:
                            return 'd'
                except Exception as e:
                    return 'd'
        elif data.lower() in ['str','string',"varchar",]:
            value=text
        elif data.lower() == 'date':
            if text.lower() in ['y','yes','1','t','true']:
                value=DatePkr()
        elif data.lower() == 'time':
            if text.lower() in ['y','yes','1','t','true']:
                value=TimePkr()
        elif data.lower() in ['datetime','datetime-','datetime~']:
            try:
                
                TODAY_IS=datetime.now()
                z=TODAY_IS
                if text.lower() in ['y','yes','1','t','true','+']:
                    value=TM.Tasks.TasksMode(parent=None,engine=db.ENGINE,init_only=True).DateTimePkr()
                elif text.lower() in ['now',]:
                    return datetime.now()
                elif text.lower() in ['today',]:
                    return datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)
                elif text.lower() in ['tomorrow',]:
                    return datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)+timedelta(seconds=60*60*24)
                elif text.lower() in ['yesterday',]:
                    return datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)-timedelta(seconds=60*60*24)
                    #I might add more for these phrases, where its literally that amount of time to
                elif text.lower() in ['last month',]:
                    return datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)-timedelta(seconds=60*60*24*30)
                elif text.lower() in ['last year',]:
                    return datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)-timedelta(seconds=60*60*24*365)
                elif text.lower() in ['next month',]:
                    return datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)+timedelta(seconds=60*60*24*30)
                elif text.lower() in ['next week',]:
                    return datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)+timedelta(seconds=60*60*24*7)
                elif text.lower() in ['last week',]:
                    return datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)-timedelta(seconds=60*60*24*30)
                elif text.lower() in ['next year',]:
                    TODAY_IS=datetime.now()
                    return datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=TODAY_IS.day)+timedelta(seconds=60*60*24*365)
                
                elif text.lower() in ['end week',]:
                    return TODAY_IS+timedelta(days=TODAY_IS.weekday())
                elif text.lower() in ['end month',]:
                    return datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=calendar.monthrange(z.year,TODAY_IS.month)[-1])
                elif text.lower() in ['end year',]:
                    return datetime(year=TODAY_IS.year,month=12,day=calendar.monthrange(z.year,12)[-1])
                elif text.lower() in ['start week',]:
                    return TODAY_IS-timedelta(days=TODAY_IS.weekday())
                elif text.lower() in ['start month',]:
                    return datetime(year=TODAY_IS.year,month=TODAY_IS.month,day=1)
                elif text.lower() in ['start year',]:
                    return datetime(year=TODAY_IS.year,month=1,day=1)

                
                elif text.lower() in "n,no,false,f,0,-".split(","):
                    return 'd'
                else:
                    def try_date(ds,format='%m%d%Y'):
                        try:
                            #print(format)
                            return datetime.strptime(ds,format)
                        except Exception as e:
                            #print(e)
                            return None
                    def process_ds(ds):
                        months=['january','february','march','april','may','june','july','august','september','october','november','december']
                        predate="%m{c}%d{c}{year}"
                        t1=[]
                        chars=[i for i in string.punctuation]
                        chars.pop(chars.index('%'))
                        for i in chars:
                            test=ds.split(i)
                            if len(test) == 3:
                                for num,m in enumerate(months):
                                    if test[0].lower() == m or m.startswith(test[0].lower()):
                                        test[0]=str(num+1).zfill(2)
                                        ds=f'{i}'.join(test)
                                        break
                        for i in chars:
                            for year in ['%y','%Y']:
                                t1.append(predate.format(c=i,year=year))
                                for ii in chars:
                                    for year in ['%y','%Y']:
                                        t1.append(f"%m{i}%d{ii}{year}")
                        for f in t1:
                                dt=try_date(format=f,ds=ds)
                                if dt:
                                    return dt
                    if data.lower().endswith('~'):
                        try:
                            text,timeStr=text.split("@")
                        except Exception as e:
                            print(e)
                            return 'RETRY'
                    value=process_ds(text)
                    if value == None:
                        if data.lower() == 'datetime':
                            value=TM.Tasks.TasksMode(parent=None,engine=db.ENGINE,init_only=True).DateTimePkr()
                    if value != None:
                        if data.lower().endswith('~'):
                            def processTS(value,TS):
                                start_end=TS.split("-")
                                
                                start,end=start_end
                                start_hour,start_minute=[int(i) for i in start.split(":")]
                                end_hour,end_minute=[int(i) for i in end.split(":")]
                                start_dt=datetime(value.year,value.month,value.day,start_hour,start_minute)
                                end_dt=datetime(value.year,value.month,value.day,end_hour,end_minute)
                                print(end_dt,"#end#")
                                if (end_dt - start_dt).total_seconds() < 0:
                                    try:
                                        end_dt=datetime(value.year,value.month,value.day+1,end_hour,end_minute)
                                    except ValueError as ve:
                                        print(ve)
                                        try:
                                            end_dt=datetime(value.year,value.month+1,1,end_hour,end_minute)
                                        except Exception as e:
                                            end_dt=datetime(value.year+1,1,1,end_hour,end_minute)
                                        
                                return [start_dt,end_dt]
                            value=processTS(value,timeStr)
            except Exception as e:
                print(repr(e),e,f"String needs to be month/day/year@hh:mm(FROM)-hh:mm(TO) {value}")
                return 'RETRY'
        elif data.lower() == 'list':
            value=text.split(',')
            tmp=[]
            try:
                for i in value:
                    if '-' in i:
                        r=[int(ii) for ii in i.split('-')]
                        r[-1]+=1
                        tmp.extend([str(i) for i in range(*r)])
                    else:
                        tmp.append(i)
                value=tmp
                #print(value,tmp)
            except Exception as e:
                value=text.split(",")
                print(e)
        elif data.lower() == 'path':
            value=Path(text).absolute()
        return value
    except Exception as e:
        print(e)