from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta as relativedelta
import pint
import numpy as np
from radboy.DB.db import *
from radboy.DB.Prompt import *
from radboy.FB.FBMTXT import *
from radboy.FB.FormBuilder import *
from colored import Fore,Back,Style
from uuid import uuid1
#rates provided as default and as user input via formbuilder
class TaxiFare:
    def static_colorize(self,m,n,c):
        msg=f'{Fore.cyan}{n}/{Fore.light_yellow}{n+1}{Fore.light_red} of {c} {Fore.dark_goldenrod}{m}{Style.reset}'
        return msg
    per_xparts_mile_multiplier=14
    per_xparts_mile=0.25
    flag_drop=3.50
    per_mile=per_xparts_mile*per_xparts_mile_multiplier
    airport_surcharge_pickup=3
    airport_surcharge_dropoff=3
    wait_time_per_hour_cost=35
    def RateData_SalinasYellowCab(self,per_xparts_mile,per_mile,flag_drop,airport_surcharge_pickup,airport_surcharge_dropoff,wait_time_per_hour_cost,per_xparts_mile_multiplier): 
        rate_data={
        'per_xparts_mile_multiplier':{
        'type':'float',
        'default':per_xparts_mile_multiplier,
        },
        'per_xparts_mile':{
        'type':'float',
        'default':per_xparts_mile,
        },
        'flag_drop':{
        'type':'float',
        'default':flag_drop
        },
        'per_mile':{
        'type':'float',
        'default':per_mile,
        },
        'airport_surcharge_pickup':{
        'type':'float',
        'default':airport_surcharge_pickup
        },
        'airport_surcharge_dropoff':{
        'type':'float',
        'default':airport_surcharge_dropoff
        },
        'wait_time_per_hour_cost':{
        'type':'float',
        'default':wait_time_per_hour_cost
        },
        }
        rate_data=FormBuilder(data=rate_data)
        if rate_data is None:
            print(self.QUIT_EARLY)
            return None
            
        recalculate_miles_from_xparts_mile=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Recalculate Per_Mile Cost using {per_xparts_mile}*{rate_data['per_xparts_mile_multiplier']}:",helpText="Boolean True/Y/n/Boolean False (but not f)",data="boolean")
        if recalculate_miles_from_xparts_mile is None:
            print(self.QUIT_EARLY)
            return None
        elif recalculate_miles_from_xparts_mile in ['d',True]:
            rate_data['per_mile']=rate_data['per_xparts_mile']*rate_data['per_xparts_mile_multiplier']
        for k in rate_data:
            try:
                setattr(self,k,rate_data[k])
            except Exception as e:
                print(e)
        self.print_rates()
        self.per_xparts_mile=float((detectGetOrSet("per_xparts_mile",rate_data["per_xparts_mile"],setValue=True,literal=True)))
        self.flag_drop=float((detectGetOrSet("flag_drop",rate_data["flag_drop"],setValue=True,literal=True)))
        self.per_mile=float((detectGetOrSet("per_mile",rate_data["per_mile"],setValue=True,literal=True)))
        self.airport_surcharge_pickup=float((detectGetOrSet("airport_surcharge_pickup",rate_data["airport_surcharge_pickup"],setValue=True,literal=True)))
        self.airport_surcharge_dropoff=float((detectGetOrSet("airport_surcharge_dropoff",rate_data["airport_surcharge_dropoff"],setValue=True,literal=True)))
        self.wait_time_per_hour_cost=float((detectGetOrSet("wait_time_per_hour_cost",rate_data["wait_time_per_hour_cost"],setValue=True,literal=True)))
        self.per_xparts_mile_multiplier=float((detectGetOrSet("per_xparts_mile_multiplier",rate_data["per_xparts_mile_multiplier"],setValue=True,literal=True)))
        return rate_data
    
    def print_rates(self):
        x=7
        msf=[
        self.static_colorize(f"{Fore.light_cyan}Per 1/{self.per_xparts_mile_multiplier} Mile{Fore.magenta}={Fore.dark_goldenrod}{self.per_xparts_mile}",0,x),
        self.static_colorize(f"{Fore.light_cyan}Per Mile{Fore.magenta}={Fore.dark_goldenrod}{self.per_mile}",1,x),
        self.static_colorize(f"{Fore.light_cyan}Flag Drop{Fore.magenta}={Fore.dark_goldenrod}{self.flag_drop}",2,x),
        self.static_colorize(f"{Fore.light_cyan}Airport Surcharge Pickup{Fore.magenta}={Fore.dark_goldenrod}{self.airport_surcharge_pickup}",3,x),
        self.static_colorize(f"{Fore.light_cyan}Airport Surcharge Drop Off{Fore.magenta}={Fore.dark_goldenrod}{self.airport_surcharge_dropoff}",4,x),
        self.static_colorize(f"{Fore.light_cyan}Wait Time Per Hour Cost{Fore.magenta}={Fore.dark_goldenrod}{self.wait_time_per_hour_cost}",5,x),
        self.static_colorize(f"{Fore.light_cyan}Parts of A Mile{Fore.magenta}={Fore.dark_goldenrod}{self.per_xparts_mile_multiplier}",6,x)
        ]
        for line in msf:
            print(line)

    def __init__(self,per_xparts_mile=None,flag_drop=None,per_mile=None, airport_surcharge_pickup=None,airport_surcharge_dropoff=None,wait_time_per_hour_cost=None,per_xparts_mile_multiplier=None):
        if isinstance(per_xparts_mile,float):
            self.per_xparts_mile=per_xparts_mile
        else:
            self.per_xparts_mile=float((detectGetOrSet("per_xparts_mile",0.25,setValue=False,literal=True)))

        if isinstance(flag_drop,float):
            self.flag_drop=flag_drop
        else:
            self.flag_drop=float((detectGetOrSet("flag_drop",3.5,setValue=False,literal=True)))

        if isinstance(per_mile,float):
            self.per_mile=per_mile
        else:
            self.per_mile=float((detectGetOrSet("per_mile",3.5,setValue=False,literal=True)))

        if isinstance(airport_surcharge_pickup,float):
            self.airport_surcharge_pickup=airport_surcharge_pickup
        else:
            self.airport_surcharge_pickup=float((detectGetOrSet("airport_surcharge_pickup",3,setValue=False,literal=True)))

        if isinstance(airport_surcharge_dropoff,float):
            self.airport_surcharge_dropoff=airport_surcharge_dropoff
        else:
            self.airport_surcharge_dropoff=float((detectGetOrSet("airport_surcharge_dropoff",3,setValue=False,literal=True)))

        if isinstance(wait_time_per_hour_cost,float):
            self.wait_time_per_hour_cost=wait_time_per_hour_cost
        else:
            self.wait_time_per_hour_cost=float((detectGetOrSet("wait_time_per_hour_cost",35,setValue=False,literal=True)))

        if isinstance(per_xparts_mile_multiplier,float):
            self.per_xparts_mile_multiplier=per_xparts_mile_multiplier
        else:
            self.per_xparts_mile_multiplier=float((detectGetOrSet("per_xparts_mile_multiplier",14,setValue=False,literal=True)))

        self.ROUNDTO=int(detectGetOrSet("TaxiFare ROUNDTO default",3,setValue=False,literal=True))

        cmds={
        str(uuid1()):{
        'cmds':['set rates','strt'],
        'desc':"Set Taxi Fare Rates if needed!",
        'exec':lambda per_xparts_mile_multiplier=self.per_xparts_mile_multiplier,per_xparts_mile=self.per_xparts_mile,flag_drop=self.flag_drop,per_mile=self.per_mile,airport_surcharge_pickup=self.airport_surcharge_pickup,airport_surcharge_dropoff=self.airport_surcharge_dropoff,wait_time_per_hour_cost=self.wait_time_per_hour_cost,self=self:self.RateData_SalinasYellowCab(per_xparts_mile,flag_drop,per_mile, airport_surcharge_pickup,airport_surcharge_dropoff,wait_time_per_hour_cost,per_xparts_mile_multiplier)
        },
        str(uuid1()):{
        'cmds':['calc fare','clcfr'],
        'desc':"calculate fare estimate using provided values for fare rates set and user values like distance,how_long_may_the_ride_be_hours,airport_surcharge_pickup_bool, and airport_surcharge_dropoff_bool",
        'exec':self.calc_fare
        },
        str(uuid1()):{
        'cmds':['show rates','shw rts','print rates','prt rts','rates'],
        'desc':"calculate fare estimate using provided values for fare rates set and user values like distance,how_long_may_the_ride_be_hours,airport_surcharge_pickup_bool, and airport_surcharge_dropoff_bool",
        'exec':self.print_rates
        }
        
        }       
        helptext=[]
        ct=len(cmds)
        for num,i in enumerate(cmds):
            msg=self.static_colorize(f"{cmds[i]['cmds']} - {cmds[i]['desc']}",num,ct)
            helptext.append(msg)
        helptext='\n'.join(helptext)
        while True:
            try:
                doWhat=Prompt.__init2__(self,func=FormBuilderMkText,ptext=f"{Fore.green_yellow}TaxiFare:{Fore.light_yellow}Do What?:",helpText=helptext,data="string")
                if doWhat is None:
                    print(self.PREVIOUS_MENU)
                    return
                elif doWhat.lower() in ['d',]:
                    print(helptext)
                    continue
                for i in cmds:
                    if doWhat.lower() in [i.lower() for i in cmds[i]['cmds']]:
                        if callable(cmds[i]['exec']):
                            cmds[i]['exec']()
                            break
                        else:
                            print("cmd is not callable()")
            except Exception as e:
                print(e)
    PREVIOUS_MENU=f"{Fore.light_yellow}Going to previous menu!{Style.reset}"
    QUIT_EARLY=f"{Fore.light_red}Nothing was calculated: {Fore.light_steel_blue}User Quit() Early!{Style.reset}"

    def calc_fare(self):        
        total=0

        miles_traveled=10 #user provided
        airport_surcharge_dropoff_bool=False #user provided
        airport_surcharge_pickup_bool=False #user provided
        how_long_may_the_ride_be_hours=0 #user provided

        fare_data={
        'miles_traveled':{
        'type':'float',
        'default':0,
        },
        'airport_surcharge_pickup_bool':{
        'type':'boolean',
        'default':False,
        },
        'airport_surcharge_dropoff_bool':{
        'type':'boolean',
        'default':False,
        },
        'how_long_may_the_ride_be_hours':{
        'type':'float',
        'default':0,
        }
        }
        fd=FormBuilder(data=fare_data)
        if fd is None:
            print(self.QUIT_EARLY)
            return

        miles_traveled=fd['miles_traveled']#user provided
        airport_surcharge_dropoff_bool=fd['airport_surcharge_dropoff_bool'] #user provided
        airport_surcharge_pickup_bool=fd['airport_surcharge_pickup_bool'] #user provided
        how_long_may_the_ride_be_hours=fd['how_long_may_the_ride_be_hours'] #user provided

        cost4miles_traveled=miles_traveled*(self.per_xparts_mile*self.per_xparts_mile_multiplier)
        total+=cost4miles_traveled
        if airport_surcharge_dropoff_bool:
            total+=self.airport_surcharge_dropoff
        if airport_surcharge_pickup_bool:
            total+=self.airport_surcharge_pickup

        total+=(how_long_may_the_ride_be_hours*self.wait_time_per_hour_cost)

        total+=self.flag_drop
        print(self.static_colorize(f"Taxi Fare Estimate: ${round(total,self.ROUNDTO)}",0,1))
        return total

