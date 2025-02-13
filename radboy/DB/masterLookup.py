from radboy.RNE.RNE import *
from radboy.DB.db import *
from radboy.DB.RandomStringUtil import *
import radboy.Unified.Unified as unified
import radboy.possibleCode as pc
from radboy.DB.Prompt import *
from radboy.DB.Prompt import prefix_text
from radboy.TasksMode.ReFormula import *
from radboy.TasksMode.SetEntryNEU import *
from radboy.FB.FormBuilder import *
from radboy.FB.FBMTXT import *
from radboy.RNE.RNE import *
from radboy.DB.glossary_db import *
from radboy.EntryRating.ER import *

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
from radboy.DB.config import *
def getRandomColorFore():
    excludes=['black',]
    colors=[getattr(Fore,i) for i in Fore._COLORS if i.lower() not in excludes]
    c=colors[random.randint(0,len(colors)-1)]
    return c

def pager(self,l=[1,2,3,4,5,6,7,8,9],what=None):
    count=len(l)
    current=0
    while True:
        #print(current)
        if current >= count:
            current=0
        elif current <= -1:
            current=count
        try:
            print(l[current])
        except Exception as e:
            pass
        htext=f'''
{Fore.dark_slate_gray_1}'n',' ','next'{Fore.light_steel_blue} - advance forwards through list{Style.reset}
{Fore.dark_slate_gray_1}'p','prev'{Fore.light_steel_blue} - go backwards through list{Style.reset}
{Fore.dark_slate_gray_1}'nt','next_table','next table','nxt tbl','m'{Fore.light_steel_blue} - advance to the next table{Style.reset}
        '''
        do=Prompt.__init2__(self,func=FormBuilderMkText,ptext=f"Searched({what})({current}/{count})[N|n]ext/[P|p]rev/[Q|q]uit/[B|b]ack/[m]Next Table:",helpText=htext,data="string")
        if do in [None,]:
            return
        elif do.lower() in ["n","d","next"]:
            if current < count:
                current+=1
            else:
                current=0
        elif do.lower() in ["p","prev"]:
            if current >= 0:
                current-=1
            else:
                current=count
        elif do.lower() in ['nt','next_table','next table','nxt tbl','m']:
            return
    
class MasterLookup:
    def __init__(self):
        self.pager=lambda l,what,self=self:pager(self=self,l=l,what=what)
        modules={i:globals().get(i) for i in SEARCH_TABLES}
        with Session(ENGINE) as session:
            while True:
                try:
                    what=Prompt.__init2__(self,func=FormBuilderMkText,ptext="What are you looking for[you may get result spammed]?",helpText="what are you looking for?",data="string")
                    if what in [None,]:
                        return
                    elif what.lower() in ['d',]:
                        continue
                    else:
                        for num,i in enumerate(modules):
                            #print(i,modules[i])
                            m=modules[i]
                            text_fields=[ii for ii in m.__table__.columns if str(ii.type).lower() in ["varchar","text","string"]]
                            query=session.query(m)
                            logic=[]
                            for ii in text_fields:
                                logic.append(ii.icontains(what))
                            query=query.filter(or_(*logic))
                            results=query.all()
                            ct=len(results)
                            ct_num=getRandomColorFore()
                            if ct >= 1:
                                msg1=f"{Fore.light_green}Total Results[{ct_num}{i}{Fore.light_green}]: {Fore.dark_slate_gray_1}{ct}{Style.reset}"
                                print(msg1)
                                displayResults=Prompt.__init2__(self,func=FormBuilderMkText,ptext="Display Results?",helpText="yes or no",data="boolean")
                                if displayResults in [None,'d']:
                                    continue
                                elif displayResults:
                                    self.pager(l=results,what=what)
                                else:
                                    pass
                                #yes or no
                                #yes displays them
                                #no goes to next set of results
                except Exception as e:
                    print(e) 
                            