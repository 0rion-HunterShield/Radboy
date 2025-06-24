from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta as relativedelta
import pint
import numpy as np
from radboy.DB.db import *
from radboy.DB.Prompt import *
from radboy.FB.FBMTXT import *
from radboy.FB.FormBuilder import *
from colored import Fore,Back,Style

def dateAhead(sep=' / '):
    def static_colorize(m,n,c):
        msg=f'{Fore.cyan}{n}/{Fore.light_yellow}{n+1}{Fore.light_red} of {c} {Fore.dark_goldenrod}{m}{Style.reset}'
        return msg
    today=datetime.now()
    data={
    'dt1':{
    'type':'datetime',
    'default':today
    },
    'months':{
    'type':'integer',
    'default':0},
    'days':{
    'type':'integer',
    'default':0},
    'years':{
    'type':'integer',
    'default':0},
    'leapdays':{
    'type':'integer',
    'default':0},
    'weeks':{
    'default':0,
    'type':'integer'
    },
    'hours':{
    'type':'integer',
    'default':0,
    },
    'minutes':{
    'type':'integer',
    'default':0,
    },
    'seconds':{
    'type':'integer',
    'default':0,
    },
    'microseconds':{
    'type':'integer',
    'default':0
    },
    }
    fd=FormBuilder(data=data)
    if fd in [None,]:
        return
    end_delta=relativedelta(**fd)
    o= (fd['dt1'],end_delta,fd['dt1']+end_delta)
    print(static_colorize(f"{sep}".join([str(i) for i in o]),0,1))
    return o
#documentation @
'''
https://dateutil.readthedocs.io/en/stable/relativedelta.html
'''
'''
start_date=datetime(2026,9,1)
months=120
end_date=start_date+relativedelta(months=months)
between=end_date-datetime.now()
print(end_date,between)
'''
