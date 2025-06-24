from radboy.DB.db import *
from radboy.DB.RandomStringUtil import *
import radboy.Unified.Unified as unified
import radboy.possibleCode as pc
import radboy.DB.db as db
from radboy.DB.Prompt import *
from radboy.DB.Prompt import prefix_text
from radboy.TasksMode.ReFormula import *
from radboy.FB.FormBuilder import *
from radboy.FB.FBMTXT import *
from radboy.RNE.RNE import *
from radboy.Lookup2.Lookup2 import Lookup as Lookup2
from collections import namedtuple,OrderedDict
import nanoid
from password_generator import PasswordGenerator
import random
from pint import UnitRegistry
import pandas as pd
import numpy as np
from datetime import *
from colored import Style,Fore
import json,sys,math,re,calendar
def today():
    dt=datetime.now()
    return date(dt.year,dt.month,dt.day)


class NEUSetter:
    def next_barcode(self):
        with Session(ENGINE) as session:
            next_barcode=session.query(SystemPreference).filter(SystemPreference.name=="next_barcode").first()
            
            state=False
            
            if next_barcode:
                    try:
                        state=json.loads(next_barcode.value_4_Json2DictString).get("next_barcode")
                    except Exception as e:
                        print(e)
                        next_barcode.value_4_Json2DictString=json.dumps({'next_barcode':False})
                        session.commit()
                        session.refresh(next_barcode)
                        state=json.loads(next_barcode.value_4_Json2DictString).get("next_barcode")
            else:
                next_barcode=db.SystemPreference(name="next_barcode",value_4_Json2DictString=json.dumps({'next_barcode':False}))
                session.add(next_barcode)
                session.commit()
                session.refresh(next_barcode)
                state=json.loads(next_barcode.value_4_Json2DictString).get("next_barcode")
            f=deepcopy(state)
            print(f,"NEXT BARCODE")
            next_barcode.value_4_Json2DictString=json.dumps({'next_barcode':False})
            session.commit()
            return f

    def __init__(self,code=None):
        self.code=code

    def newCodesFromExpireds(self):
        print(f"{Fore.light_green}Expiry{Style.reset}")
        with Session(ENGINE) as session:
            exps=session.query(Expiry).group_by(Expiry.Barcode).all()
            exps_ct=len(exps)
            if exps_ct == 0:
                print(f"{exps_ct} Expiry to Check!")
                return
            for num,exp in enumerate(exps):
                entry_result=session.query(Entry).filter(Entry.Barcode==exp.Barcode).first()
                if entry_result == None:
                    ptext=f"{Fore.light_green}{num}/{Fore.light_yellow}{num+1}/{Fore.light_red}{exps_ct} - {Fore.light_magenta}No Entry found to match {exp.Barcode}|{exp.Name} [[c]reate] Entry/[[s]kip]|[[i]gnore]|<Enter|Return>/d[[r]elete] Expiry"
                    helpText=ptext
                    while True:
                        doWhat=Prompt.__init2__(None,func=FormBuilderMkText,ptext=ptext,helpText=helpText,data="string")
                        nb=self.next_barcode()
                        if doWhat in [None,] and nb == False:
                            continue
                        elif doWhat in [None,] and nb == True:
                            return
                        elif doWhat.lower() in ['s','skip','i','ignore','d']:
                            break
                        elif doWhat.lower() in ['delete','r','rm','del',]:
                            session.delete(exp)
                            session.commit()
                            print(f"Deleted {exp}")
                        elif doWhat.lower() in ['create','new','n']:
                            data={
                            'Barcode':{
                                    'type':'String',
                                    'default':exp.Barcode,
                                },
                            'Code':{
                                    'type':'String',
                                    'default':'',
                                },
                            'Name':{
                                    'type':'String',
                                    'default':'',
                                },
                            'CaseCount':{
                                    'type':'integer',
                                    'default':'1',
                                },
                            'Price':{
                                    'type':'String',
                                    'default':0.0,
                                }
                            }
                            neu=FormBuilder(data)
                            if neu in [None,]:
                                continue
                            new_entry=Entry(**neu)
                            session.add(new_entry)
                            session.commit()
                            session.refresh(new_entry)
                            print(new_entry)
                            break
                else:
                    print(f"{num}/{num+1}/{exps_ct} - {Expiry.Barcode} - checking...")
                    toRM=session.query(Expiry).filter(Expiry.Barcode==entry_result.Barcode).all()
                    toRM_ct=len(toRM)
                    if toRM_ct == 0:
                        print("Nothing to Update!")
                        continue
                    else:
                        for num0,rmt in enumerate(toRM):
                            print(f"{num0}/{num0+1}/{toRM_ct} Updating Located Expiry.Barcode -> Entry.Barcode - {rmt.Barcode} - {entry_result.Name}!")
                            rmt.Name=entry_result.Name
                            if num0%10==0:
                                session.commit()
                        session.commit()
        print(f"{Fore.light_sea_green}Done{Fore.light_yellow} Cleaning Expiry's{Style.reset}")
        pass
        #scan through expireds table and check each barcode for an entry in Entry and update info from first result, or if not exists, prompt to create it/skip it/delete it, perform said action

    def newCodesFromPCs(self):
        print(f"{Fore.light_green}Cleaning PairCollection's{Style.reset}")
        with Session(ENGINE) as session:
            pcs=session.query(PairCollection).group_by(PairCollection.Barcode).all()
            pcs_ct=len(pcs)
            if pcs_ct == 0:
                print(f"{pcs_ct} PairCollection to Check!")
                return
            for num,pc in enumerate(pcs):
                entry_result=session.query(Entry).filter(Entry.Barcode==pc.Barcode).first()
                if entry_result == None:
                    ptext=f"{Fore.light_green}{num}/{Fore.light_yellow}{num+1}/{Fore.light_red}{pcs_ct} - {Fore.light_magenta}No Entry found to match {pc.Barcode}|{pc.Code} [[c]reate] Entry/[[s]kip]|[[i]gnore]|<Enter|Return>/d[[r]elete] PC"
                    helpText=ptext
                    while True:
                        doWhat=Prompt.__init2__(None,func=FormBuilderMkText,ptext=ptext,helpText=helpText,data="string")
                        nb=self.next_barcode()
                        if doWhat in [None,] and nb == False:
                            continue
                        elif doWhat in [None,] and nb == True:
                            return
                        elif doWhat.lower() in ['s','skip','i','ignore','d']:
                            break
                        elif doWhat.lower() in ['delete','r','rm','del',]:
                            session.delete(pc)
                            session.commit()
                            print(f"Deleted {pc}")
                        elif doWhat.lower() in ['create','new','n']:
                            data={
                            'Barcode':{
                                    'type':'String',
                                    'default':pc.Barcode,
                                },
                            'Code':{
                                    'type':'String',
                                    'default':'',
                                },
                            'Name':{
                                    'type':'String',
                                    'default':'',
                                },
                            'CaseCount':{
                                    'type':'integer',
                                    'default':'1',
                                },
                            'Price':{
                                    'type':'String',
                                    'default':0.0,
                                }
                            }
                            neu=FormBuilder(data)
                            if neu in [None,]:
                                continue
                            new_entry=Entry(**neu)
                            session.add(new_entry)
                            session.commit()
                            session.refresh(new_entry)
                            print(new_entry)
                            break
                else:
                    print(f"{num}/{num+1}/{pcs_ct} - {pc.Barcode} - checking...")
                    toRM=session.query(PairCollection).filter(PairCollection.Barcode==entry_result.Barcode).all()
                    toRM_ct=len(toRM)
                    if toRM_ct == 0:
                        print("Nothing to delete!")
                        continue
                    else:
                        for num0,rmt in enumerate(toRM):
                            print(f"{num0}/{num0+1}/{toRM_ct} Deleting Located PC.Barcode -> E.Barcode - {rmt.Barcode} - {entry_result.Name}!")
                            session.delete(rmt)
                            if num0%10==0:
                                session.commit()
                        session.commit()
        print(f"{Fore.light_sea_green}Done{Fore.light_yellow} Cleaning PairCollection's{Style.reset}")

        #scan through PairCollection table and check each barcode for an entry in Entry and if not exists, prompt to create it/skip it/delete it, perform said action, and remove PairCollection with corresponding Barcode
                

    def setFieldByName(self,fname):
        fnames=[]
        if isinstance(fname,str):
            fnames=[fname,]
        elif isinstance(fname,list):
            fnames=fname
        elif fname == None:
            try:
                fields=[
                    'Barcode',
                    'Code',
                    'Price',
                    'Description',
                    'Facings',
                    'UnitsDeep',
                    'UnitsHigh',
                    'Size',
                    'Tax',
                    'TaxNote',
                    'CRV',
                    'Name',
                    'Location',
                    'ALT_Barcode',
                    'DUP_Barcode',
                    'CaseID_BR',
                    'CaseID_LD',
                    'CaseID_6W',
                    'LoadCount',
                    'PalletCount',
                    'ShelfCount',
                    'CaseCount',]
                fct=len(fields)
                for num,f in enumerate(fields):
                    msg=f'{Fore.light_green}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{fct} -> {Fore.turquoise_4}{f}{Style.reset}'
                    print(msg)
                fnames=[]
                which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"which {Fore.light_green}index{Fore.light_red}({Fore.light_green}es{Fore.light_red}){Fore.light_yellow}?: ",helpText=f"which {Fore.light_green}index{Fore.light_red}({Fore.light_green}es{Fore.light_red}){Fore.light_yellow}, use comma to separate multiple fields{Style.reset}",data="list")
                if which in [None,]:
                    return
                elif which in ['d',]:
                    which=[0,]
                for i in which:
                    try:
                        fnames.append(fields[int(i)])
                    except Exception as e:
                        print(e)
                        try:
                            fnames.append(fields[fields.index(str(i))])
                        except Exception as e:
                            print(e)

            except Exception as e:
                print(e)
                return

        while True:
            try:
                if self.code in [None,]:
                    barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"[{fnames}] {Fore.light_green}Barcode|{Fore.turquoise_4}Code|{Fore.light_magenta}Name{Fore.light_yellow}:",helpText="what are you looking for?",data="string")
                    if barcode in ['d',None]:
                        return
                else:
                    barcode=self.code
                with Session(ENGINE) as session:
                    query=session.query(Entry).filter(or_(
                        Entry.Barcode==barcode,
                        Entry.Code==barcode,
                        Entry.Barcode.icontains(barcode),
                        Entry.Code.icontains(barcode),
                        Entry.Name.icontains(barcode)
                        ))
                    results=query.all()
                    ct=len(results)
                    if ct == 0:
                        print("Nothing Found")
                        if self.code in [None,]:
                            continue
                        else:
                            return

                    for num,entry in enumerate(results):
                        msg=f'{Fore.light_green}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct} -> {entry.seeShort()}'
                        print(msg)
                    which=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"[{fnames}]which {Fore.light_green}index{Fore.light_yellow}?: ",helpText=f"{Fore.light_steel_blue}which index {Fore.light_yellow}number in light yellow{Style.reset}",data="integer")
                    if which in [None,]:
                        if not self.code:
                            continue
                        else:
                            break
                    elif which in ['d',]:
                        which=0
                    selected=results[which]
                    tax_adjusted=False
                    for fname in fnames:
                        column=getattr(Entry,fname)
                        newValue=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"[{Fore.medium_violet_red}old{Fore.light_yellow}] {Fore.light_magenta}{fname} = {Fore.light_red}{getattr(selected,fname)}{Fore.orange_red_1} to: {Style.reset}",helpText="new value",data=str(column.type))
                        if newValue in [None,'d']:
                            continue
                        if fname.lower() == 'tax':
                            if not tax_adjusted:
                                setattr(selected,fname,newValue)
                        else:
                            setattr(selected,fname,newValue)

                        if fname.lower() == 'price':
                            session.commit()
                            session.refresh(selected)
                            adjust_tax=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Adjust Tax using Price({newValue}),CRV({selected.CRV}), and the Tax Rate",helpText="yes/no/boolean",data="boolean")
                            if adjust_tax in ['d',True]:
                                tax_adjusted=True
                                ROUNDTO=int(db.detectGetOrSet("lsbld ROUNDTO default",3,setValue=False,literal=True))
                                default_taxrate=round(float(db.detectGetOrSet("Tax Rate",0.0925,setValue=False,literal=True)),4)
                                tax_rate=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Tax({default_taxrate}): ",helpText=f"What is the tax rate, default is {default_taxrate}.",data="float")
                                if tax_rate is None:
                                    return tax,crv
                                elif tax_rate in ['d',]:
                                    tax_rate=default_taxrate

                                tax=round(selected.Price+selected.CRV,ROUNDTO)*tax_rate
                                tax=round(tax,ROUNDTO)
                                selected.Tax=tax
                                session.commit()
                                session.refresh(selected)
                                if self.code in [None,]:
                                    continue
                                else:
                                    return
                            elif adjust_tax in [None,False]:
                                if self.code in [None,]:
                                    continue
                                else:
                                    return

                    session.commit()
                    session.flush()
                    session.refresh(selected)
                    print(selected)
            except Exception as e:
                print(e)
                break