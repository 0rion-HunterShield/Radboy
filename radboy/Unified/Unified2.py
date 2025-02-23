import pandas as pd
import csv
from datetime import datetime
from pathlib import Path
from colored import Fore,Style,Back
from barcode import Code39,UPCA,EAN8,EAN13
import barcode,qrcode,os,sys,argparse
from datetime import datetime,timedelta
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
from radboy.DB.Prompt import *
from radboy.DB.SMLabelImporter import *
from radboy.DB.ResetTools import *

from radboy.ConvertCode.ConvertCode import *
from radboy.setCode.setCode import *
from radboy.Locator.Locator import *
from radboy.ListMode2.ListMode2 import *
from radboy.TasksMode.Tasks import *
from radboy.ExportList.ExportListCurrent import *
from radboy.TouchStampC.TouchStampC import *
from radboy.EntryExtras.Extras import *
from radboy import VERSION
import radboy.possibleCode as pc
from radboy.Unified.clearalll import *
def format_bytes(size):
            """
            Auto-convert bytes to a human-readable format.

            this was generated by Google's AI Console.
            """
            power = 2**10
            n = 0
            power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
            while size > power:
                size /= power
                n += 1
            return f"{size:.2f} {power_labels[n]}B"
class Unified2:
    cmds={}
    def __init__(self,*args,**kwargs):
        '''Add Commands like:

        self.options["compare product"]={
                    'cmds':["#"+str(count),f"compare product","p1==p2?"],
                    'desc':f'compare two products qty and price',
                    'exec':lambda self=self: CompareUI(),
                    }
        count+=1
        '''
        count=0
        self.options["remove entry"]={
                    'cmds':["#"+str(count),f"remove entry","remove","rm",'del','delete'],
                    'desc':f'remove an entry via EntryId',
                    'exec':lambda self=self: self.rmEntry(),
                    }
        count+=1
        self.options["smle-no-arg"]={
                    'cmds':["#"+str(count),f"smle-no-arg","smle-narg","smle-0a"],
                    'desc':f'{Fore.cyan}show list items if no argument, or show list items summary for item with Code or Barcode{Style.reset}',
                    'exec':lambda self=self: self.smle(args=[]),
                    }
        count+=1
        self.options["smle-w-arg"]={
                    'cmds':["#"+str(count),f"smle-with-arg","smle-arg","smle-1a","smle-w-arg"],
                    'desc':f'{Fore.cyan}show list items if no argument, or show list items summary for item with Code or Barcode{Style.reset}',
                    'exec':lambda self=self: self.argSMLE(),
                    }
        count+=1
        '''image options'''
        self.options["img"]={
                    'cmds':["#"+str(count),'img','im','Image'],
                    'desc':f'''{Fore.green}ls{Style.reset}-{Fore.cyan}Display Image Path for EntryId{Style.reset}
                {Fore.green}set{Style.reset}-{Fore.cyan}set Image for $EntryId with $value{Style.reset}''',
                    'exec':lambda self=self: self.img(),
                    }
        count+=1

        self.options["rm_img"]={
                    'cmds':["#"+str(count),'rm_img','rm_im','del_img'],
                    'desc':f'{Fore.cyan}remove Image from $EntryId{Style.reset}',
                    'exec':lambda self=self: self.rm_img(),
                    }
        count+=1

        self.options["showEntryId"]={
                    'cmds':["#"+str(count),'show','entryid','see'],
                    'desc':f'{Fore.cyan}display Entry from $EntryId{Style.reset}',
                    'exec':lambda self=self: self.showEntryId(),
                    }
        count+=1

        self.options["upce2upca"]={
                    'cmds':["#"+str(count),'upce2upca','u2u','e2a'],
                    'desc':f'{Fore.cyan}display or set upce2upca field{Style.reset}',
                    'exec':lambda self=self: self.upce2upca(),
                    }
        count+=1

        self.options["modify list qty"]={
                    'cmds':["#"+str(count),'-lq','+lq','=lq'],
                    'desc':f'{Fore.cyan}modify ListQty +/-/= using first of Barcode==CODE or Code==CODE; does not fuzz!!!{Style.reset}',
                    'exec':lambda self=self: self.modify_listQty(),
                    }
        count+=1

        self.options["list all"]={
                    'cmds':["#"+str(count),"list_all","la"],
                    'desc':f'{Fore.cyan}show all Entry to screen{Style.reset}',
                    'exec':lambda self=self: self.showAll(),
                    }
        count+=1

        self.options["show list"]={
                    'cmds':["#"+str(count),"show_list","sl"],
                    'desc':f'{Fore.cyan}show everything with InList==True{Style.reset}',
                    'exec':lambda self=self: self.show_list(),
                    }
        count+=1

        self.options["clear list"]={
                    'cmds':["#"+str(count),"clear_list","cl","clrl"],
                    'desc':f'{Fore.cyan}set ALL with InList==True to update with InList==False and ListQty==0{Style.reset}',
                    'exec':lambda self=self: self.clear_list(),
                    }
        count+=1


    def argSMLE(self):
        arg=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Barcode,Code: ",helpText="a barcode or code",data="list")
        if arg in [None,'d']:
            return
        else:
            return self.smle(args=args)

    def smle(self,args=[]):
        if len(args) == 0:
            with Session(self.engine) as session:
                results=session.query(Entry).filter(Entry.InList==True).all()
                if len(results) < 1:
                    print(f"{Fore.dark_goldenrod}No Items in List!{Style.reset}")
                for num,result in enumerate(results):
                    result.listdisplay_extended(num=num)
        elif len(args) >= 2:
            if args[1].lower() in ['?','s','search','lu']:
                while True:
                    def search(text,self):
                        code=text.lower()
                        with Session(self.engine) as session:
                            result=session.query(Entry).filter(or_(Entry.Barcode==code,Entry.Code==code),Entry.InList==True).first()
                            if result:
                                result.listdisplay_extended(num=0)  
                            else:
                                print(f"{Style.bold+Style.underline+Fore.orange_red_1}No Such Item by {Style.underline}{code}{Style.reset}")
                    return Prompt(func=search,ptext="code|barcode|q/quit|b/back",helpText=self.help(print_no=True),data=self).state
            else:
                with Session(self.engine) as session:
                    result=session.query(Entry).filter(or_(Entry.Barcode==args[1],Entry.Code==args[1]),Entry.InList==True).first()
                    if result:
                        result.listdisplay_extended(num=0)
                    else:
                        print(f"{Style.bold+Style.underline+Fore.orange_red_1}No Such Item by {Style.underline}{args[1]}{Style.reset}")             
        return True


    def rmEntry(self):
        while True:
            try:
                EntryId=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Entry Id to Remove: ",helpText="an integer representing the Entry==Entry.EntryId to be deleted",data="integer")
                if EntryId is None or EntryId in [None,'d']:
                    return True
                else:
                    with Session(ENGINE) as session:
                        result=session.query(Entry).filter(Entry.EntryId==int(EntryId)).first()
                        if result:
                            daylog_exist=session.query(DayLog).filter(DayLog.EntryId==result.EntryId).all()
                            if len(daylog_exist) < 1:
                                extras=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==result.EntryId).all()
                                for num,i in enumerate(extras):
                                    session.delete(i)
                                    if (num%100) == 0:
                                        session.commit()
                                        session.flush()
                                session.commit()
                            print(result)
                            result.before_entry_delete()
                            session.delete(result)
                        session.commit()
                        session.flush()
            except Exception as e:
                print(e)
        return True


    def img(self):
        '''['img','im','Image']'''
        args=Prompt.__init2__(None,func=FormBuilderMkText,ptext="ls/set",helpText="type ls or set",data="string")
                if args in [None,'d']:
                    return
        entryId=Prompt.__init2__(None,func=FormBuilderMkText,ptext="EntryId",helpText="EntryId integer",data="integer")
                if entryId in [None,'d']:
                    return
        if args.lower() == "ls":
            with Session(ENGINE) as session:
                    result=session.query(Entry).filter(Entry.EntryId==int(entryId)).first()
                    if result:
                        print(result.Image)
                    else:
                        print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
        elif args.lower() == "set":
            with Session(ENGINE) as session:
                result=session.query(Entry).filter(Entry.EntryId==int(entryId)).first()
                try:
                    imtext=str(args[2])
                    f=importImage(image_dir=img_dir,src_path=imtext,nname=f'{result.EntryId}.png',ow=True)
                    setattr(result,'Image',f)
                    
                    session.commit()
                    session.flush()
                    session.refresh(result)
                    print(result.Image)
                except Exception as e:
                    print("No Such EntryId!")
        return True

    def rm_img(self):
        '''['rm_img','rm_im','del_img']'''
        try:
            with Session(self.engine) as session:
                entryId=Prompt.__init2__(None,func=FormBuilderMkText,ptext="EntryId",helpText="EntryId integer",data="integer")
                if entryId in [None,'d']:
                    return
                result=session.query(Entry).filter(Entry.EntryId==int(entryId)).first()
                try:
                    imtext=result.Image
                    removeImage(image_dir=img_dir,img_name=imtext)
                    setattr(result,'Image','')
                    
                    session.commit()
                    session.flush()
                    session.refresh(result)
                    print(result.Image)
                except Exception as e:
                    print(e)
                    print("No Such EntryId!")
        except Exception as e:
            print(e)
        return True

    def upce2upca(self):
        '''['upce2upca','u2u','e2a']:'''
        args=Prompt.__init2__(None,func=FormBuilderMkText,ptext="ls/setd",helpText="type ls or set",data="string")
                if args in [None,'d']:
                    return
        entryId=Prompt.__init2__(None,func=FormBuilderMkText,ptext="EntryId",helpText="EntryId integer",data="integer")
        if entryId in [None,'d']:
            return
        code=Prompt.__init2__(None,func=FormBuilderMkText,ptext="UPCA from UPCE",helpText="UPCA from UPCE; does not convert; directly saves code",data="string")
        if code in [None,'d']:
            return
        if args.lower() == "ls":
            with Session(ENGINE) as session:
                    result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
                    if result:
                        print(result.upce2upca)
                    else:
                        print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
        elif args.lower() in ["set"]:
            with Session(ENGINE) as session:
                result=session.query(Entry).filter(Entry.EntryId==int(args[1])).first()
                setattr(result,'upce2upca',code)
                
                session.commit()
                session.flush()
                session.refresh(result)
                print(result.upce2upca)   
        return True

    def modify_listQty(self):
        '''['+','-','=']'''
        args=Prompt.__init2__(None,func=FormBuilderMkText,ptext="+/-/=",helpText="type + or - or =",data="string")
                if args in [None,'d']:
                    return
        qty=Prompt.__init2__(None,func=FormBuilderMkText,ptext="EntryId",helpText="EntryId integer",data="float")
        if entryId in [None,'d']:
            return
        code=Prompt.__init2__(None,func=FormBuilderMkText,ptext="UPCA from UPCE",helpText="UPCA from UPCE; does not convert; directly saves code",data="string")
        if code in [None,'d']:
            return
        if args.lower() in ["+","-","="]:
            with Session(self.engine) as session:
                result=session.query(Entry).filter(or_(Entry.Barcode==code,Entry.Code==code)).first()
                if result:
                    if args == '-':
                        result.ListQty=result.ListQty-float(qty)
                    elif args == '+':
                        result.ListQty=result.ListQty+float(qty)
                    elif args == '=':
                        result.ListQty=float(qty)
                    result.InList=True
                    session.commit()
                    session.flush()
                    session.refresh(result)
                    print(result)       
                else:
                    print(f"{Fore.yellow}{Style.blink}{Style.bold}Nothing by that EntryId{Style.reset}")
        else:
            print(f"{Style.bold+Style.underline+Fore.orange_red_1}[+,-,=]{Style.reset},{Fore.yellow}QTY{Style.reset},{Fore.green}Code/Barcode{Style.reset}")
        return True

    def showEntryId(self):
        """show"""
        entryId=Prompt.__init2__(None,func=FormBuilderMkText,ptext="EntryId",helpText="EntryId integer",data="integer")
        if entryId in [None,'d']:
            return
        with Session(ENGINE) as session:
                result=session.query(Entry).filter(Entry.EntryId==entryId).all()
                for num,e in enumerate(result):
                    print(num,e)
        return True

    def search_all(self):
        args=','.split(",")
        fields='\n'.join([f"{num}/{num+1} of {len(Entry.__table__.columns)} -> {f.name}:{str(f.type)}" for num,f in enumerate(Entry.__table__.columns)])
        fields_l=[f'{f.name}' for f in Entry.__table__.columns]
        field_arg_1=None
        while True:
            try:
                field_arg_1=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Field Name index: ",helpText=fields,data="integer")
                if field_arg_1 in ['d',None]:
                    return
                else:
                    print(field_arg_1)
                    if 0 > field_arg_1 < len(fields_l)-1:
                        field_arg_1=fields_l[field_arg_1]
                    break
            except Exception as e:
                print(e)

        while True:
            try:
                field_arg_2=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Value to Search: ",helpText="a string or textual data",data="string")
                if field_arg_2 in ['d',None]:
                    return
                else:
                    print(field_arg_2)
                    if 0 > field_arg_2 < len(fields_l)-1:
                        field_arg_2=fields_l[field_arg_2]
                    break
            except Exception as e:
                print(e)
        args=f",{field_arg_1},{field_arg_2}"

        print("Search Mod")
        with Session(ENGINE) as session:
            #session.query(Entries).filter
            for field in Entry.__table__.columns:
                if field.name.lower() == args[1].lower():
                    print(field)
                    if str(field.type) in ['FLOAT','INTEGER']:
                        term=0
                        if str(field.type) == 'FLOAT':
                            term=float(args[2])
                        elif str(field.type) == 'INTEGER':
                            term=int(args[2])
                        operators=['==','!=','<','<=','>','>=','q','b']
                        print(f"""
{Fore.yellow}=={Style.reset} -> equal to
{Fore.yellow}=!{Style.reset} -> not equal to
{Fore.yellow}<{Style.reset} -> less than
{Fore.yellow}<={Style.reset} -> less than, or equal to
{Fore.yellow}>{Style.reset} -> greater than
{Fore.yellow}>={Style.reset} -> greater than, or equal to
{Style.bold+Style.underline+Fore.orange_red_1}q{Style.reset} -> quit
{Style.bold+Style.underline+Fore.orange_red_1}b{Style.reset} -> back
                            """)
                        while True:
                            operator=input(f"operator {operators}:").lower()
                            if operator not in operators:
                                continue
                            if operator == 'q':
                                exit('user quit')
                            elif operator == 'b':
                                break
                            elif operator == '==':
                                query=session.query(Entry).filter(field==term)
                                save_results(query)
                                results=query.all()
                                for num,e in enumerate(results):
                                    print(f"{Style.bold+Style.underline+Fore.orange_red_1}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
                                print(f"Number of Results: {len(results)}")
                                break
                            elif operator == '!=':
                                query=session.query(Entry).filter(field!=term)
                                save_results(query)
                                results=query.all()
                                for num,e in enumerate(results):
                                    print(f"{Style.bold+Style.underline+Fore.orange_red_1}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
                                print(f"Number of Results: {len(results)}")
                                break
                            elif operator == '<':
                                query=session.query(Entry).filter(field<term)
                                save_results(query)
                                results=query.all()
                                for num,e in enumerate(results):
                                    print(f"{Style.bold+Style.underline+Fore.orange_red_1}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
                                print(f"Number of Results: {len(results)}")
                                break
                            elif operator == '<=':
                                query=session.query(Entry).filter(field<=term)
                                save_results(query)
                                results=query.all()
                                for num,e in enumerate(results):
                                    print(f"{Style.bold+Style.underline+Fore.orange_red_1}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
                                print(f"Number of Results: {len(results)}")
                                break
                            elif operator == '>':
                                query=session.query(Entry).filter(field>term)
                                save_results(query)
                                results=query.all()
                                for num,e in enumerate(results):
                                    print(f"{Style.bold+Style.underline+Fore.orange_red_1}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
                                print(f"Number of Results: {len(results)}")
                                break
                            elif operator == '>=':
                                query=session.query(Entry).filter(field>=term)
                                save_results(query)
                                results=query.all()
                                for num,e in enumerate(results):
                                    print(f"{Style.bold+Style.underline+Fore.orange_red_1}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
                                print(f"Number of Results: {len(results)}")
                                break
                        break
                    elif str(field.type) == 'VARCHAR':
                        operators=['=','%','q','b','!%','!=']
                        print(f"""
{Fore.yellow}={Style.reset} -> entry in Field is exactly
{Fore.yellow}!={Style.reset} -> entry is not equal to
{Fore.yellow}%{Style.reset} -> entry is contained within field but is NOT exact to the total of the field
{Fore.yellow}!%{Style.reset} -> entry is not contained within field but is NOT exact to the total of the field
{Style.bold+Style.underline+Fore.orange_red_1}q{Style.reset} -> quit
{Style.bold+Style.underline+Fore.orange_red_1}b{Style.reset} -> back
                            """)
                        while True:
                            operator=input(f"operator {operators}:").lower()
                            if operator not in operators:
                                continue
                            if operator == 'q':
                                exit('user quit')
                            elif operator == 'b':
                                break
                            elif operator == '=':
                                query=session.query(Entry).filter(field==args[2])
                                save_results(query)
                                results=query.all()
                                for num,e in enumerate(results):
                                    print(f"{Style.bold+Style.underline+Fore.orange_red_1}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
                                print(f"Number of Results: {len(results)}")
                                break
                            elif operator == '!=':
                                query=session.query(Entry).filter(field!=args[2])
                                save_results(query)
                                results=query.all()
                                for num,e in enumerate(results):
                                    print(f"{Style.bold+Style.underline+Fore.orange_red_1}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
                                print(f"Number of Results: {len(results)}")
                                break
                            elif operator == '%':
                                query=session.query(Entry).filter(field.icontains(args[2]))
                                save_results(query)
                                results=query.all()
                                for num,e in enumerate(results):
                                    print(f"{Style.bold+Style.underline+Fore.orange_red_1}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
                                print(f"Number of Results: {len(results)}")
                                break
                            elif operator == '!%':
                                query=session.query(Entry).filter(field.icontains(args[2])==False)
                                save_results(query)
                                results=query.all()
                                for num,e in enumerate(results):
                                    print(f"{Style.bold+Style.underline+Fore.orange_red_1}{Style.bold}{Style.underline}{num}{Style.reset}->{e}")
                                print(f"Number of Results: {len(results)}")
                                break

                        break
                    else:
                        print(field.type)
        return True

    def showAll(self):
    """["list_all","la"]"""
        print("-"*10)
        with Session(ENGINE) as session:
                result=session.query(Entry).all()
                for num,e in enumerate(result):
                    print(num,e)
        print("-"*10)
        return True

    def show_list(self):
    """["show_list","sl",]"""
        print("-"*10)
        with Session(ENGINE) as session:
                result=session.query(Entry).filter(Entry.InList==True).all()
                for num,e in enumerate(result):
                    print(num,e)
        print("-"*10)
        return True

    def clear_list(self):      
    """["clear_list","cl","clrl"]"""
        print("-"*10)
        with Session(ENGINE) as session:
                result=session.query(Entry).filter(Entry.InList==True).update({'InList':False,'ListQty':0})
                session.commit()
                session.flush()
                print(result)
        print("-"*10)
        return True


    '''Stopped at 349.''''