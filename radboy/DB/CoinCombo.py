#CoinCombo.py
from radboy.DB.db import *
from radboy.FB.FormBuilder import *
from radboy.FB.FBMTXT import *
from radboy.DB.Prompt import *
from radboy.DB.Prompt import prefix_text
import pandas as pd
from datetime import date,datetime
import calendar
import plotext as plt
import numpy as np
from radboy.BNC.BnC import *
import tarfile
import uuid
from radboy.whatIs15 import get_bill_combinations

class CoinCombo4TTL(BASE,Template):
    __tablename__="CoinCombo4TTL"
    cc4ttlid=Column(Integer,primary_key=True)
    Calculated_Total=Column(Float,default=round(0,2))
    TTL=Column(Float,default=round(0,2))
    DTOE=Column(DateTime,default=datetime.now())
    CurrencyName=Column(String,default='')
    CurrencyValue=Column(Float,default=round(0,2))
    CurrencyNeeded4TTL=Column(Integer,default=0)

    group_id=Column(String,default=str(uuid.uuid1()))

    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))

try:
    CoinCombo4TTL.metadata.create_all(ENGINE)
except Exception as e:
    print(e)
    CoinCombo4TTL.metadata.drop(ENGINE)
    CoinCombo4TTL.metadata.create_all(ENGINE)   


#put utilities here
class CoinComboUtil:
    def colorize(self,num,count,msgText):
        msg=f"{Fore.green_yellow}{num}/{Fore.light_salmon_1}{num+1}{Fore.light_yellow} of {Fore.light_red}{count}{Fore.orange_red_1} -> {Fore.cyan}{msgText}{Style.reset}"
        return msg

    def clear_all(self):
        code=''.join([str(random.randint(0,9)) for i in range(10)])
        verification_protection=detectGetOrSet("Protect CoinCombo4TTL's From Delete",code,setValue=False,literal=True)
        while True:
            try:
                h="CoinComboUtil"
                really=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{h}: Really Clear CoinCombo4TTL's?",helpText="yes or no boolean,default is NO",data="boolean")
                if really in [None,]:
                    print(f"{Fore.light_steel_blue}Nothing was {Fore.orange_red_1}{Style.bold}Deleted!{Style.reset}")
                    return True
                elif really in ['d',False]:
                    print(f"{Fore.light_steel_blue}Nothing was {Fore.orange_red_1}{Style.bold}Deleted!{Style.reset}")
                    return True
                else:
                    pass
                really=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"To {Fore.orange_red_1}Delete everything completely,{Fore.light_steel_blue}what is today's date?[{'.'.join([str(int(i)) for i in datetime.now().strftime("%m.%d.%y").split(".")])}]{Style.reset}",helpText="type y/yes for prompt or type as m.d.Y",data="datetime")
                if really in [None,'d']:
                    print(f"{Fore.light_steel_blue}Nothing was {Fore.orange_red_1}{Style.bold}Deleted!{Style.reset}")
                    return True
                today=datetime.today()
                if really.day == today.day and really.month == today.month and really.year == today.year:
                    really=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Please type the verification code {Style.reset}'{Entry.cfmt(None,verification_protection)}'?",helpText=f"type '{Entry.cfmt(None,verification_protection)}' to finalize!",data="string")
                    if really in [None,]:
                        print(f"{Fore.light_steel_blue}Nothing was {Fore.orange_red_1}{Style.bold}Deleted!{Style.reset}")
                        return True
                    elif really in ['d',False]:
                        print(f"{Fore.light_steel_blue}Nothing was {Fore.orange_red_1}{Style.bold}Deleted!{Style.reset}")
                        return True
                    elif really == verification_protection:
                        break
                else:
                    pass
            except Exception as e:
                print(e)
        with Session(ENGINE) as session:
            ct=session.query(CoinCombo4TTL).count()
            done=session.query(CoinCombo4TTL).delete()
            session.commit()
            print(self.colorize(ct,ct,f"Cleared CoinCombo4TTL's - {done}"))

    def list_combos(self):
        with Session(ENGINE) as session:
            ct=session.query(CoinCombo4TTL).count()
            for num,i in enumerate(session.query(CoinCombo4TTL).all()):
                print(self.colorize(num,ct,i))

    def range_generate(self,forwards=True):
        bottom=Prompt.__init2__(None,FormBuilderMkText,ptext="Range Min?",helpText="a value",data="float")
        if bottom in [None,]:
            return
        elif bottom in ['d']:
            bottom=0
        
        top=Prompt.__init2__(None,FormBuilderMkText,ptext="Range Max?",helpText="a value",data="float")
        if top in [None,]:
            return
        elif top in ['d']:
            top=sys.maxsize

        if bottom > top:
            tmp=bottom
            bottom=top
            top=tmp
        rng=np.arange(bottom,top+0.01,0.01)
        ct=len(rng)
        for num,amount in enumerate(rng):
            amount=round(float(amount),2)
            print(f"{self.colorize(num,ct,amount)}")
            self.generate(amount=amount,forwards=forwards)

    def generate(self,amount=None,forwards=True):
        if amount == None or amount < 0:
            amount = Prompt.__init2__(None,FormBuilderMkText,ptext="How much?",helpText="a value",data="float")
        if amount in [None,'d']:
            return
        if amount < 0:
            print("Needs to a positive value")
            return
        combinations_receipt=detectGetOrSet("combinations_receipt","combos.json.csv",setValue=False,literal=True)
        NOW=datetime.now()
        with Session(ENGINE) as session,open(combinations_receipt,"w") as logged:
            currencies=session.query(CashPool).filter(CashPool.Qty>0).order_by(CashPool.Value.desc()).all()
            bills=[]
            for i in currencies:
                bills.append(i.Value)
            bills=sorted(bills)
            combinations = get_bill_combinations(amount, bills,forwards=forwards)

            # Print the combinations
            for num,combo in enumerate(combinations):
                x={}
                ttl=0
                for i in combo:
                    ttl+=(i*1)
                    if str(i) not in x:
                        x[str(i)]=1
                    else:
                        x[str(i)]+=1
                ttl=round(ttl,2)
                msg=f"{x},{ttl},{amount}"

                finalmsg={}
                for k in x:
                    kk=session.query(CashPool).filter(CashPool.Value==float(k)).first()
                    finalmsg[k]={
                    'Calculated Total':ttl,
                    'Line Number':num,
                    'User Provided Amount':amount,
                    'NeededQty':x[k],
                    'DateTime_Of_Location':datetime.now().strftime("%H:%M:%S on %m/%d/%Y"),
                    }
                    if kk:
                        finalmsg[k]['Name']=kk.Name
                        finalmsg[k]['Value']=kk.Value
                        finalmsg[k]['QtyCashPool']=kk.Qty
                        finalmsg[k]['NeededQty']=x[k]
                        
                if 'QtyCashPool' in finalmsg[k].keys() and (finalmsg[k]['NeededQty'] <= finalmsg[k]['QtyCashPool']):
                    print(f"{Fore.light_green}Saving {Fore.light_magenta}{finalmsg}{Fore.light_steel_blue}{Fore.light_green}'{combinations_receipt}'{Style.reset}")
                    logged.write(json.dumps(finalmsg)+",\n")
                    '''
                    __tablename__="CoinCombo4TTL"
                    cc4ttlid=Column(Integer,primary_key=True)
                    Calculated_Total=Column(Float,default=round(0,2))
                    TTL=Column(Float,default=round(0,2))
                    DTOE=Column(DateTime,default=datetime.now())
                    CurrencyName=Column(String,default='')
                    CurrencyValue=Column(Float,default=round(0,2))
                    CurrencyNeeded4TTL=Column(Integer,default=0)

                    group_id=Column(String,default=str(uuid.uuid1()))
                    '''
                    for k in finalmsg:
                        
                        try:
                            if amount == finalmsg[k]['Calculated Total']:
                                gid=f"{combo}={finalmsg[k]['User Provided Amount']}"
                                check=session.query(CoinCombo4TTL).filter(CoinCombo4TTL.group_id==gid).first()
                                if check:
                                    print(self.colorize(0,0,f"User Provided Amount({Fore.light_yellow}{amount}{Fore.cyan}) as group_id({Fore.orange_red_1}{gid}{Fore.cyan}) was Located In Storage -> {Fore.light_red}Refusing to Store!{Fore.cyan}"))
                                    continue

                                coinCombo=CoinCombo4TTL(Calculated_Total=finalmsg[k]['Calculated Total'],TTL=finalmsg[k]['User Provided Amount'],DTOE=NOW,CurrencyName=finalmsg[k]['Name'],CurrencyValue=finalmsg[k]['Value'],CurrencyNeeded4TTL=finalmsg[k]['NeededQty'],group_id=gid)
                                
                                session.add(coinCombo)
                                if (num%self.commit_rate)==0:
                                    try:
                                        session.commit()
                                    except Exception as e:
                                        session.rollback()
                                        print(e)
                            else:
                                print(self.colorize(0,0,f"User Provided Amount({amount}!=Calculated_Total({finalmsg[k]['Calculated Total']})) -> Refusing to Store!"))
                        except Exception as e:
                            print(e,repr(e),'#EXCEPTION')
                else:
                    m=f"{Fore.orange_red_1}Not Saving {Fore.light_magenta}{finalmsg}{Fore.light_steel_blue}{Fore.light_green}'{combinations_receipt}'{Style.reset}".replace(k,f"{Fore.light_yellow}{k}{Fore.orange_red_1}")
            try:
                session.commit()
            except Exception as e:
                session.rollback()
                print(e)

    def seek(self):
        print("Not Yet Implemented")

    def setCommitRate(self):
        self.commit_rate=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What is the commit rate?",helpText="an integer",data="integer")
        if self.commit_rate in [None,'d']:
            self.commit_rate=1

    def __init__(self):
        self.commit_rate=1
        cmds={
            f'{uuid.uuid1()}':{
                'cmds':['lc','list combos','list combinations','lsc'],
                'exec':self.list_combos,
                'desc':"List All Store CoinCombo4TTL Entries",
                },
            f'{uuid.uuid1()}':{
                'cmds':['gen','generate combos','gcc'],
                'exec':self.generate,
                'desc':"Generate Coin Combos for a given amount",
                },
            f'{uuid.uuid1()}':{
                'cmds':['genr','generate combos reversed','gccr'],
                'exec':lambda self=self:self.generate(forwards=False),
                'desc':"Generate Coin Combos for a given amount in reverse",
                },
            f'{uuid.uuid1()}':{
                'cmds':['scr','set commit rate','st cmt rt'],
                'exec':self.setCommitRate,
                'desc':"how fast discoveries are saved (too many too fast=slow,too few too slow=slow);find your balance!",
                },
            f'{uuid.uuid1()}':{
                'cmds':['clear all','clear_all',],
                'exec':self.clear_all,
                'desc':"completely clear your combinations table",
                },
            f'{uuid.uuid1()}':{
                'cmds':['range generate','gen rng','gen range','generate range',',gnrng','gn rng',],
                'exec':self.range_generate,
                'desc':"generate combinations for a range of values [will take a while]",
                },
            f'{uuid.uuid1()}':{
                'cmds':['range generate reverse','gen rng rvs','gen range rvs','generate range reverse',',gnrngr','gn rng r',],
                'exec':self.range_generate,
                'desc':"generate combinations for a range of values [will take a while] in the reverse direction",
                },
            f'{uuid.uuid1()}':{
                'cmds':['skc','scl','seek combo','sk c','search combos',],
                'exec':self.seek,
                'desc':"search for a combination asking questions about currency on hand to provide useful combinations",
                },
            }
        htext=[]
        for i in cmds:
            msg=f"{Fore.cyan}{cmds[i]['cmds']} {Fore.light_red}-{Fore.light_sea_green}{cmds[i]['desc']}"
            htext.append(msg)
        htext='\n'.join(htext)
        while True:
            doWhat=Prompt.__init2__(None,func=FormBuilderMkText,ptext="CoinComboUtil: Do What",helpText=htext,data="string")
            if doWhat in [None,]:
                return
            elif doWhat.lower() in ['d',' ']:
                print(htext)

            for cmd in cmds:
                if doWhat.lower() in [i.lower() for i in cmds[cmd]['cmds']]:
                    if callable(cmds[cmd]['exec']):
                        cmds[cmd]['exec']()
                        break
                    else:
                        print(f"{cmds[cmd]['exec']} -> 4Input('{doWhat}'') is not callable!")
