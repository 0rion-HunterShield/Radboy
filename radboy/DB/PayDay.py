from datetime import datetime,date,timedelta
import calendar
from pathlib import Path
import sys
from collections import OrderedDict
from radboy.DB.db import *
from radboy.DB.Prompt import *
from radboy.FB.FBMTXT import *
from radboy.FB.FormBuilder import *


rcpt=Path("EstimatedPayCalendarWorkSheet.txt")
rcpt=detectGetOrSet("EstimatedPayCalendarExportFile",rcpt,setValue=False,literal=True)
if rcpt not in [None,]:
    rcpt=Path(rcpt)
if rcpt.exists():
    try:
        rcpt.unlink()
    except Exception as e:
        print(e)
        exit()


from colored import Fore,Back,Style
def DayNamesPerMonthForYear(year,dayName_target,quiet=True):
    months={}
    for month,i in enumerate(calendar.mdays):
        for day in range(1,i+1):
            if not isinstance(year,int):
                year=datetime.now().year
            
            d=datetime(year,month,day)
            dayName=d.strftime("%A")
            if dayName in dayName_target or dayName == dayName_target:
                if not quiet:
                    print(d,dayName)
                if d.strftime("%b") in months:
                    months[d.strftime("%b")]+=1
                else:
                    months[d.strftime("%b")]=1
    return months


DAYNAMES=[i.lower() for i in calendar.day_name]



def display(msg):
    global rcpt
    msg=f"{msg}".ljust(10,' ')
    with open(rcpt,"a") as out:
        out.write(msg)
        sys.stdout.write(msg)
        sys.stdout.flush()

def setup():
    data={
        'min_hours':{
        'type':'float',
        'default':24.0
        },
        'med_hours':{
        'type':'float',
        'default':32.0
        },
        'max_hours':{
        'type':'float',
        'default':40.0
        },
        'taxRate':{
        'type':'float',
        'default':0.2227
        },
        'rate':{
        'type':'float',
        'default':27.73
        },
        'roundTo':{
        'type':'int',
        'default':4
        },
        'quiet':{
        'type':'boolean',
        'default':False
        },
    }
    revsedDsp=Prompt.__init2__(None,func=FormBuilderMkText,ptext="reverse the display order?",helpText="yes or no booleans",data="boolean")
    if revsedDsp in [None,]:
        return
    elif revsedDsp in ['d',False]:
        order=False
    else:
        order=True
    fd=FormBuilder(data=data)
    if fd in [None,]:
        return
    fd['order']=order
    return fd

def EstimatedPayCalendar(min_hours=None,med_hours=None,max_hours=None,rate=None,taxRate=None,roundTo=None,quiet=False,order=False):
    payday=detectGetOrSet("PayDayName","Thursday",setValue=False,literal=True)
    display(f"Your Estimated PayDay Calendar Worksheet TDY(is={datetime.now().ctime()})\n")
    work_paydays=DayNamesPerMonthForYear(datetime.now().year,payday)
    if not min_hours:
        min_hours=24.0
    if not med_hours:
        med_hours=32.0
    if not max_hours:
        max_hours=40.0
    if not taxRate:
        taxRate=0.2227
    if not rate:
        rate=27.73
    
    linestart="\t"
    roundTo=4
    eq=" = "
    max_mins=OrderedDict()
    max_mins[f'annual total max-TotalTaxRate({taxRate})']=0
    max_mins[f'annual total min-TotalTaxRate({taxRate})']=0
    max_mins[f'annual total med-TotalTaxRate({taxRate})']=0
    max_mins[f'annual total [Untaxed] max']=0
    max_mins[f'annual total [Untaxed] med']=0
    max_mins[f'annual total [Untaxed] min']=0
    max_mins['Annual Total Pay Accrued (the total of \nwhat was on your paystubs)\n\t']=f'$______.___'
    max_mins['Annual Total Hours for Pay Accrued (the total of number of hours \nto get what was on your paystubs)\n\t']=f'$______._____'

   

    max_mins['min_hours']=min_hours
    max_mins['med_hours']=med_hours
    max_mins['max_hours']=max_hours
    max_mins['min_hours annual']=0
    max_mins['med_hours annual']=0
    max_mins['max_hours annual']=0
    max_mins['taxRate']=taxRate
    max_mins['rate']=rate
    
    for month in work_paydays:
        if month not in max_mins:
            max_mins[month]=OrderedDict()
            max_mins[month][f'max pay-TotalTaxRate({taxRate})']=0
            max_mins[month][f'med pay-TotalTaxRate({taxRate})']=0
            max_mins[month][f'min pay-TotalTaxRate({taxRate})']=0
            max_mins[month]['min_hours monthly']=0
            max_mins[month]['med_hours monthly']=0
            max_mins[month]['max_hours monthly']=0
        max_mins[month]['max pay[untaxed]']=round((work_paydays[month]*(max_hours*rate)),roundTo)
        max_mins[month]['med pay[untaxed]']=round((work_paydays[month]*(med_hours*rate)),roundTo)
        max_mins[month]['min pay[untaxed]']=round((work_paydays[month]*(min_hours*rate)),roundTo)
        max_mins[month][f'max pay-TotalTaxRate({taxRate})']=max_mins[month]['max pay[untaxed]']-(max_mins[month]['max pay[untaxed]']*taxRate)
        max_mins[month][f'med pay-TotalTaxRate({taxRate})']=max_mins[month]['med pay[untaxed]']-(max_mins[month]['med pay[untaxed]']*taxRate)
        max_mins[month][f'min pay-TotalTaxRate({taxRate})']=max_mins[month]['min pay[untaxed]']-(max_mins[month]['min pay[untaxed]']*taxRate)

        max_mins[month]['min pay per week[untaxed]']=round((work_paydays[month]*(min_hours*rate))/work_paydays[month],roundTo)
        max_mins[month]['med pay per week[untaxed]']=round((work_paydays[month]*(med_hours*rate))/work_paydays[month],roundTo)
        max_mins[month]['max pay per week[untaxed]']=round((work_paydays[month]*(max_hours*rate))/work_paydays[month],roundTo)
        max_mins[month][f'min pay per week-TotalTaxRate({taxRate})']=max_mins[month]['min pay per week[untaxed]']-(max_mins[month]['min pay per week[untaxed]']*taxRate)
        max_mins[month][f'med pay per week-TotalTaxRate({taxRate})']=max_mins[month]['med pay per week[untaxed]']-(max_mins[month]['med pay per week[untaxed]']*taxRate)
        max_mins[month][f'max pay per week-TotalTaxRate({taxRate})']=max_mins[month]['max pay per week[untaxed]']-(max_mins[month]['max pay per week[untaxed]']*taxRate)

        for num in range(1,work_paydays[month]+1):
            max_mins[month][f'Weekly({num}) Total Pay Accrued\n\t (What was on your paystub)\n\t']=f'$________.____\n'
            max_mins[month][f'Hours Worked_per_week({num}) for Total Pay Accrued\n\t']=f'________.__\n'
        max_mins[month]['max_hours monthly']=max_mins['max_hours']*work_paydays[month]
        max_mins[month]['med_hours monthly']=max_mins['med_hours']*work_paydays[month]
        max_mins[month]['min_hours monthly']=max_mins['min_hours']*work_paydays[month]
        max_mins[month][f'Monthly({month}) Total Pay Accrued\n\t (What was on your paystub)\n\t']=f'$________.____\n'
        max_mins[month][f'Hours Worked({month}) for Total Pay Accrued\n\t']=f'________.____\n'
        max_mins[f'annual total max-TotalTaxRate({taxRate})']+=max_mins[month][f'max pay-TotalTaxRate({taxRate})']
        max_mins[f'annual total med-TotalTaxRate({taxRate})']+=max_mins[month][f'med pay-TotalTaxRate({taxRate})']
        max_mins[f'annual total min-TotalTaxRate({taxRate})']+=max_mins[month][f'min pay-TotalTaxRate({taxRate})']
        max_mins[f'annual total [Untaxed] max']+=max_mins[month]['max pay[untaxed]']
        max_mins[f'annual total [Untaxed] med']+=max_mins[month]['med pay[untaxed]']
        max_mins[f'annual total [Untaxed] min']+=max_mins[month]['min pay[untaxed]']
        max_mins['max_hours annual']+=max_mins['max_hours']*work_paydays[month]
        max_mins['med_hours annual']+=max_mins['med_hours']*work_paydays[month]
        max_mins['min_hours annual']+=max_mins['min_hours']*work_paydays[month]
    if not quiet:
        if order == False:
            gen=max_mins.keys()
        else:
            gen=reversed(max_mins.keys())
        for month in gen:
            if isinstance(max_mins[month],str):
                msg=' '.join([str(i) for i in (month,eq,max_mins[month])])+"\n"
                display(msg)
            elif isinstance(max_mins[month],float):
                msg=' '.join([str(i) for i in (month,linestart,eq,round(max_mins[month],roundTo))])+"\n"
                display(msg)

            elif isinstance(max_mins[month],OrderedDict):
                for info in max_mins[month]:
                    if isinstance(max_mins[month][info],str):
                        msg=' '.join([str(i) for i in (month,linestart,info,eq,max_mins[month][info])])+"\n"
                        display(msg)
                    else:
                        msg=' '.join([str(i) for i in (month,linestart,info,eq,round(max_mins[month][info],roundTo))])+"\n"
                        display(msg)

    return max_mins
'''uses prompt to setup
'''
#EstimatedPayCalendar(**setup())
'''
uses hardcoded defaults
 EstimatedPayCalendar()
'''
