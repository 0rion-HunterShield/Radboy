#Prompt.py
from colored import Fore,Style,Back
import random
import re,os,sys
from radboy.DB.db import *
from radboy.DB.Prompt import *
from radboy.DB.DatePicker import *
from radboy import VERSION
import inspect,string
import json
from pathlib import Path
from datetime import date,time,datetime
from radboy.FB.FBMTXT import *


def FormBuilder(data,extra_tooling=False,passThruText=None):
    if passThruText != None:
        passThruText=f"{Fore.light_green}{passThruText}: {Fore.light_yellow}"
    GOTOK=None
    def keys_index(data):
        for num,k in enumerate(data.keys()):
            msg=f"{Fore.light_cyan}{num}/{Fore.light_magenta}{num+1}{Fore.light_steel_blue} of {Fore.light_red}{len(data.keys())}{Fore.medium_violet_red} as {Fore.light_green}{k}:{Fore.cyan}{data[k]['type']}={Fore.magenta}{data[k]['default']}{Style.reset}"
            print(msg)

    def setGOTOK(GOTOK):
        gotoi=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What index do you wish to goto?",helpText=f"please type an integer between 0 to {len(data.keys())-1}",data="integer")
        if gotoi in [None,]:
            return
        elif gotoi in ['d',]:
            pass
        else:
            try:
                keys=data.keys()
                GOTOK=list(keys)[gotoi]
                print(GOTOK)
                return GOTOK
            except Exception as e:
                print(e)
                print(f"Index {gotoi} not found in {data} in its keys-list indexes: {data.keys()}")
                
    def setGOTOK_str(data):
        while True:
            gotoi=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What key do you wish to goto?",helpText=f"please type the key you want to goto",data="string")
            if gotoi in [None,]:
                return
            elif gotoi in ['d',]:
                pass
            else:
                try:
                    test=data[gotoi]
                    return gotoi
                except Exception as e:
                    print(e)
                    print(f"Key {gotoi} not found in {data} in its keys {data.keys()}")
    index=None
    item={}
    for num,k in enumerate(data.keys()):
        item[k]=data[k]['default']
    review=False
    finalize=False
    while True:
        if finalize:
            break
        while True:
            if finalize:
                break
            for num,k in enumerate(data.keys()):
                if GOTOK != None:
                    print(k,GOTOK)
                    if k != GOTOK:
                        continue
                    else:
                        GOTOK=None
                if isinstance(index,int):
                    if num < index:
                        continue
                    else:
                        index=None
                ht=''
                if data[k]['type'].lower() in ['date','datetime','time']:
                    ht="type 'y' or 'n' to start"
                elif data[k]['type'].lower() in ['list']:
                    ht="type your $DELIMITED list, the you will be asked for $DELIMITED character to use!"
                elif data[k]['type'].lower() in ['bool','boolean']:
                    ht="type y|yes|t|true|1 for yes/True, and n|no|0|false|f for no/False"
                ht2=f"""{Style.bold}{Fore.dark_blue}{Back.grey_70} FormBuilder {Fore.dark_red_1}Options {Style.reset}
{Fore.light_yellow}#b{Fore.light_green} will restart {Fore.light_red}[If it is wired to, might be reverse of 'b']{Style.reset}
{Fore.light_yellow}b{Fore.light_green} will return to previous menu{Fore.light_red}[If it is wired to, might be reverse of '#b']{Style.reset}
{Fore.light_yellow}f{Fore.light_green} will proceeds to review, where 'f' finishes,'y/yes/1' will review,'<Enter>/<Return>/n/f/0' will act as finish{Style.reset}
{Fore.light_yellow}p{Fore.light_green} at field filling lines goes to previous field{Style.reset}
{Fore.light_yellow}d{Fore.light_green} use default{Style.reset}
{Fore.light_yellow}m{Fore.light_green} use manually entered data present under m key option{Style.reset}
{Fore.light_yellow}#done#{Fore.light_green} to finish a str+(MultiLine) Input{Style.reset}
{Fore.grey_70}*{Fore.light_cyan}{num}/{Fore.light_magenta}{num+1}{Fore.light_steel_blue} of {Fore.light_red}{len(data.keys())}{Fore.medium_violet_red} as {Fore.light_green}{k}:{Fore.cyan}{data[k]['type']}={Fore.magenta}{data[k]['default']}{Style.reset}
{Fore.grey_70}*{Fore.light_yellow}goto {Fore.light_cyan}i{Fore.light_yellow}/goto{Fore.light_cyan}i{Fore.light_green} - go to {Fore.light_cyan}index{Style.reset}
{Fore.grey_70}*{Fore.light_yellow}goto{Fore.light_cyan}k{Fore.light_yellow},goto {Fore.light_cyan}k{Fore.light_green} goto {Fore.light_cyan}key{Fore.light_green} for field in Form {Style.reset}
{Fore.grey_70}*{Fore.light_yellow}showkeys{Fore.light_green} to see indexes refering to form keys{Style.reset}
{Fore.grey_70}* {Fore.grey_50}These cmds only work with fields that return str/VARCHAR/TEXT/str+/list of str's, i.e. [str,]{Style.reset}"""
                print(ht2)
                FormBuilderHelpText()
                cmd=None
                if data[k]['type']=='str+':
                    done=False
                    while not done:
                        lines=[]
                        skip_review=False
                        while True:
                            line=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{passThruText}You(m):{item.get(k)}|Default(d):{data[k]['default']} Field:{str(k)}",helpText=f'{ht}\nuse {Fore.light_red}{Style.bold}{Back.grey_50}#done#{Style.reset} to stop.',data=data[k]['type'][:-1])
                            if line in [None,]:
                                return
                            elif line.lower() in ['#done#',]:
                                break
                            elif isinstance(line,list) and [i.lower() for i in line] in [['gotoi',],['goto i']]:
                                GOTOK=setGOTOK(data)
                                while GOTOK not in list(data.keys()):
                                    GOTOK=setGOTOK(data)
                                    if GOTOK in [None,]:
                                        return  
                                done=True
                                finalize=True
                                skip_review=True
                                break
                            elif isinstance(line,list) and [i.lower() for i in line] in [['gotok',],['goto k']]:
                                GOTOK=setGOTOK_str(data)
                                while GOTOK not in list(data.keys()):
                                    GOTOK=setGOTOK_str(data)
                                    if GOTOK in [None,]:
                                        return
                                done=True
                                finalize=True
                                skip_review=True
                                break
                            elif isinstance(line,str) and line.lower() in ['gotoi','goto i']:
                                GOTOK=setGOTOK(GOTOK)
                                while GOTOK not in list(data.keys()):
                                    GOTOK=setGOTOK(GOTOK)
                                    if GOTOK in [None,]:
                                        return
                                done=True
                                finalize=True
                                skip_review=True
                                break
                            elif isinstance(line,str) and line.lower() in ['gotok','goto k']:
                                GOTOK=setGOTOK_str(data)
                                while GOTOK not in list(data.keys()):
                                    GOTOK=setGOTOK(GOTOK)
                                    if GOTOK in [None,]:
                                        return
                                done=True
                                finalize=True
                                skip_review=True
                                break
                            elif isinstance(line,str) and line.lower() in ['showkeys','show keys']:
                                keys_index(data)
                                done=True
                                finalize=True
                                skip_review=True
                                break
                            elif line.lower() == 'd':
                                line='\n'
                            else:
                                if len(line) in [i for i in range(7,14)]:
                                    with Session(ENGINE) as session:
                                        possible=session.query(Entry).filter(or_(Entry.Barcode==line,Entry.Barcode.icontains(line),Entry.Code==line,Entry.Code.icontains(line))).all()
                                        if len(possible) > 0:
                                            line+="\nBarcode/Code Matches found Below\n"+f"{'-'*len('Barcode/Code Matches found Below')}\n"
                                            for num,i in enumerate(possible):
                                                line+=i.seeShortRaw()+"\n"

                            lines.append(line)
                        cmd='\n'.join(lines)
                        if not skip_review:
                            use=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{passThruText}{cmd}\nUse? [y/n]",helpText="type something that can be represented as a boolean, this includes boolean formulas used in if/if-then statements(True=y/1/t/true/yes/1==1,False=n/no/0/f/false/1==0)",data="boolean")
                            if use in [None,]:
                                return
                            elif use:
                                done=True
                                finalize=True
                                break
                            else:
                                continue
                else:
                    passThru=['gotoi','goto i','gotok','goto k','showkeys','show keys']
                    cmd=Prompt.__init2__(None,func=lambda text,data:FormBuilderMkText(text,data,passThru=passThru),ptext=f"{passThruText} You(m):{item.get(k)}|Default(d):{data[k]['default']} Field:{str(k)}",helpText=f'{ht}',data=data[k]['type'])
                    if cmd in [None,]:
                        return
                    elif isinstance(cmd,list) and [i.lower() for i in cmd] in [['gotoi',],['goto i']]:
                        GOTOK=setGOTOK(data)
                        while GOTOK not in list(data.keys()):
                            GOTOK=setGOTOK(data)
                        continue
                    elif isinstance(cmd,list) and [i.lower() for i in cmd] in [['gotok',],['goto k']]:
                        GOTOK=setGOTOK_str(data)
                        while GOTOK not in list(data.keys()):
                            GOTOK=setGOTOK_str(data)
                        continue
                    elif isinstance(cmd,str) and cmd.lower() in ['gotoi','goto i']:
                        GOTOK=setGOTOK(GOTOK)
                        while GOTOK not in list(data.keys()):
                            GOTOK=setGOTOK(GOTOK)
                        continue
                    elif isinstance(cmd,str) and cmd.lower() in ['gotok','goto k']:
                        GOTOK=setGOTOK_str(data)
                        while GOTOK not in list(data.keys()):
                            GOTOK=setGOTOK_str(data)
                        continue
                    elif isinstance(cmd,str) and cmd.lower() in ['showkeys','show keys']:
                        keys_index(data)
                        continue
                if cmd in [None,]:
                    return
                elif isinstance(cmd,str):
                    if cmd.lower() in ['p',]:
                        if num == 0:
                            index=len(data.keys())-1
                        else:
                            index=num-1
                        break
                    elif cmd.lower() in ['d',]:
                        item[k]=data[k]['default']
                    elif cmd.lower() in ['f','finalize']:
                        finalize=True
                        break
                    elif cmd.lower() in ['m',]:
                        print(f"Not changing User set value '{k}':'{item.get(k)}'")
                        pass
                    else:
                        item[k]=cmd
                else:
                    item[k]=cmd
        review=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{passThruText}review?",helpText="",data="bool")
        #print(review)
        if review in ['f',]:
            review=False
        if review in [None,]:
            return 
        elif review in [True,'d']:
            finalize=False
            continue
        else:
            break
    if extra_tooling == True:
        tmp_item={str(num):item[i] for num,i in enumerate(item)}
        #ask if extra data is needed
        count=len(tmp_item)
        while True:
            nkv=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{passThruText}New Key:Value Pair",helpText="yes or no",data="boolean")
            if nkv in ['d',True]:
                key=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{passThruText}default[{count}] Key",helpText="yes or no",data="string")
                if key in [None,]:
                    continue
                elif key in ['d',]:
                    key=str(count)
                value=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{passThruText}Value",helpText="data text",data="string")
                if value in [None,]:
                    continue
                tmp_item[key]=value
                count+=1
            else:
                break
        #loop through lines for removal
        final_result={}
        for k in tmp_item:
            keep=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"{passThruText}['{tmp_item[k]}'] keep?",helpText="yes or no",data="boolean")
            if keep in ['d',True]:    
                final_result[k]=tmp_item[k]
        return final_result
    return item            

'''
form=FormBuilder(data=fm_data)
print(form)
'''