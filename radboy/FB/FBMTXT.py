import radboy.TasksMode as TM
import radboy.DB.db as db
import string
from datetime import datetime
from pathlib import Path
fm_data={'Name':{
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
def FormBuilderMkText(text,data,passThru=[]):
    try:
        #if text in passThru:
        #    return text
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
        elif data.lower() in ['int','integer']:
            try:
                value=int(eval(text))
            except Exception as e:
                try:
                    value=int(text)
                except Exception as e:
                    return 'd'
        elif data.lower() in ['bool','boolean','boolean_basic']:
            try:
                value=bool(eval(text))
            except Exception as e:
                try:
                    if data.lower() in ['boolean_basic']:
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
                            if data.lower() not in ['boolean_basic']:
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
                if text.lower() in ['y','yes','1','t','true','+']:
                    value=TM.Tasks.TasksMode(parent=None,engine=db.ENGINE,init_only=True).DateTimePkr()
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