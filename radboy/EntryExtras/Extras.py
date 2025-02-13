#MobileInventoryCLI is now radboy
from . import *
from radboy.DB.db import ENGINE
def get_bool(text):
    if text in (None,'',False,'n','N','NO','No','nO','False','false',0,'0'):
        return False
    elif text in (True,'y','yes',1,'1','True','true','YES','Yes','Y'):
        return True
    else:
        try:
            return eval(text)
        except Exception as e:
            print(e)
            return False
DateTimeFormats=(
'%m/%d/%Y@%H:%M:%S',
'%H:%M:%S on %m/%d/%Y',
'%m/%d/%Y@%H:%M',
'%H:%M on %m/%d/%Y',
)
'''
 bytes are stored as base64 string
 under neu
  af2e add field to Entry
  sf2e select a field name from searched/listed and add field to entry
   these searched/listed fieldnames would be collected from already created fields
   results=search by name or use '*' to show all
   name=select index from results and get name of object
   apply name to new extra
   apply type from result
   get value
   apply entry id
   commit result
 under esu
  when a product is searched the Extras Table for corresponding
  EntryId and display that info as well before printing next Entry
'''       
TYPES_FromText={
"string":{
'cmds':['str','text',],
"exec":str,
"desc":'anything that is meant to be text'
},
"integer":{
'cmds':['integer','int'],
'exec':int,
'desc':"numbers without decimal"
},
"float":{
'cmds':['float','decimal'],
'exec':float,
'desc':"numbers with a decimal"
},
"boolean":{
'cmds':['boolean','bool'],
'exec':get_bool,
'desc':"True or False,"
},
"DateTime":{
'cmds':['datetime'],
'exec':lambda x,format:datetime.datetime.strptime(format,x),
'desc':"date values from format and string"
},
"bytes":{
'cmds':['byte','bytes','base64bytes'],
'exec':lambda x: base64.b64decode(x.encode()),
'desc':"byte values stored as a base64 string"
},
}



class EntryDataExtrasMenu:
    '''
    Add,remove,list fields,create fields EntryDataExtras
    '''
    def rm_ede_id(self):
        with Session(ENGINE) as session:
            ede_id=Prompt.__init2__(None,func=FormBuilderMkText,ptext="ExtryDataExtras.ede_id to delete?",helpText="the id value for the EntryDataExtras that you wish to delete.",data="integer")
            if ede_id in [None,]:
                return
            ede=session.query(EntryDataExtras).filter(EntryDataExtras.ede_id==ede_id).first()
            if ede:
                session.delete(ede)
                session.commit()
                results=session.query(EntryDataExtras).all()
                for i in results:
                    check=session.query(Entry).filter(Entry.EntryId==i.EntryId).first()
                    check2=session.query(DayLog).filter(DayLog.EntryId==i.EntryId).first()
                    if not check and not check2:
                        session.delete(i)
                        session.commit()

    def af2e(self,barcode=None):
        with Session(ENGINE) as session:
            if barcode != None:
                search=barcode
            else:
                search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search? [Barcode,Code,Name]",helpText="searches Barcode,Code,Name",data="string")
                if search in [None]:
                    return
            results=session.query(Entry).filter(or_(Entry.Barcode==search,Entry.Code==search,Entry.Barcode.icontains(search),Entry.Code.icontains(search),Entry.Name.icontains(search))).all()
            ct=len(results)
            if ct == 0:
                print("No Results were Found!")
                return
            msg=[]
            for num,i in enumerate(results):
                msg.append(f"{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct}{Fore.grey_50} -> {i.seeShort()}")
            msg='\n'.join(msg)
            product=None
            while True:
                print(msg)
                index=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which index do you wish to use?",helpText=msg,data="integer")
                if index in [None,]:
                    return
                try:
                    product=results[index]
                    break
                except Exception as e:
                    print(e)
            if product in [None,]:
                return
            print("af2e()")
            field_name=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Field Name",helpText="make a field name",data="string")
            if field_name in [None,]:
                return
            msg=[]
            ct=len(TYPES_FromText)
            '''make a list of field types to refer to by index instead of key.'''
            ftypes=[i for i in TYPES_FromText]
            for num,i in enumerate(TYPES_FromText):
                msg.append(f'{num}/{num+1} of {ct} -> {TYPES_FromText[i]["cmds"]} - {TYPES_FromText[i]["desc"]}')
            msg='\n'.join(msg)
            print(msg)
            field_type=None
            while True:
                field_type=Prompt.__init2__(self,func=FormBuilderMkText,ptext="please select a type by index.",helpText=msg,data="integer")
                if field_type in [None,]:
                    return
                try:
                    field_type=ftypes[field_type]
                    break
                except Exception as e:
                    print(e)
            field_value=Prompt.__init2__(self,func=FormBuilderMkText,ptext="What do you wish to store as the value?",helpText=field_type,data=field_type)
            if field_value in [None,]:
                return

            print(field_name,field_type,field_value)
            extra=EntryDataExtras(field_name=field_name,field_type=field_type,field_value=field_value,EntryId=product.EntryId)
            session.add(extra)
            session.commit()
            session.refresh(extra)
            print(extra)


    def sf2e(self,barcode=None):
        with Session(ENGINE) as session:
            if barcode != None:
                search=barcode
            else:
                search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search? [Barcode,Code,Name]",helpText="searches Barcode,Code,Name",data="string")
                if search in [None]:
                    return
            results=session.query(Entry).filter(or_(Entry.Barcode==search,Entry.Code==search,Entry.Barcode.icontains(search),Entry.Code.icontains(search),Entry.Name.icontains(search))).all()
            ct=len(results)
            if ct == 0:
                print("No Results were Found!")
                return
            msg=[]
            for num,i in enumerate(results):
                msg.append(f"{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct}{Fore.grey_50} -> {i.seeShort()}")
            msg='\n'.join(msg)
            product=None
            while True:
                print(msg)
                index=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which index do you wish to use?",helpText=msg,data="integer")
                if index in [None,]:
                    return
                try:
                    product=results[index]
                    break
                except Exception as e:
                    print(e)
            if product in [None,]:
                return
            print("sf2e()")
            query=session.query(EntryDataExtras)
            results_ede=query.group_by(EntryDataExtras.field_name,EntryDataExtras.field_type).all()
            field=None
            msg_ede=[]
            for num,i in enumerate(results_ede):
                if num%2==0:
                    color=Fore.cyan
                elif num%3==0:
                    color=Fore.light_cyan
                elif num%4==0:
                    color=Fore.light_steel_blue
                elif num%5==0:
                    color=Fore.light_green
                elif num%6==0:
                    color=Fore.turquoise_4
                elif num%7==0:
                    color=Fore.deep_sky_blue_3a
                elif num%8==0:
                    color=Fore.spring_green_3a
                elif num%9==0:
                    color=Fore.dark_cyan
                else:
                    color=Fore.light_blue
                msg_ede.append(f"{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct}{Fore.grey_50} -> {color}{i.field_name}{Style.reset}:{i.field_type} ede_id={i.ede_id} doe={i.doe}")
            msg_ede='\n'.join(msg_ede)
            while True:
                try:
                    print(msg_ede)
                    index=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which index do you wish to use?",helpText=msg_ede,data="integer")
                    if index in [None,]:
                        return
                    try:
                        print(index)
                        if index <= len(results_ede)-1:
                            field=results_ede[index]
                        else:
                            print(f"index is not within 0-{len(results_ede)-1}")
                            continue
                        break
                    except Exception as e:
                        print(e)
                        break
                except Exception as e:
                    print(e)
            if field == None:
                return
            field_name=field.field_name
            field_type=field.field_type
            field_value=Prompt.__init2__(self,func=FormBuilderMkText,ptext="What do you wish to store as the value?",helpText=field_type,data=field_type)
            if field_value in [None,]:
                return
            
            print(field_name,field_type,field_value)
            extra=EntryDataExtras(field_name=field_name,field_type=field_type,field_value=field_value,EntryId=product.EntryId)
            session.add(extra)
            session.commit()
            session.refresh(extra)
            print(extra)
    
    def sch_f2e(self,barcode=None):
        with Session(ENGINE) as session:
            if barcode != None:
                search=barcode
            else:
                search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search? [Barcode,Code,Name]",helpText="searches Barcode,Code,Name",data="string")
                if search in [None]:
                    return

            results=session.query(Entry).filter(or_(Entry.Barcode==search,Entry.Code==search,Entry.Barcode.icontains(search),Entry.Code.icontains(search),Entry.Name.icontains(search))).all()
            ct=len(results)
            if ct == 0:
                print("No Results were Found!")
                return
            msg=[]
            for num,i in enumerate(results):
                msg.append(f"{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct}{Fore.grey_50} -> {i.seeShort()}")
            msg='\n'.join(msg)
            product=None
            while True:
                print(msg)
                index=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which index do you wish to use?",helpText=msg,data="integer")
                if index in [None,]:
                    return
                try:
                    product=results[index]
                    break
                except Exception as e:
                    print(e)
            if product in [None,]:
                return
            print("sf2e()")
            while True:
                try:
                    fs=[]
                    fse=session.query(EntryDataExtras).group_by(EntryDataExtras.field_name,EntryDataExtras.field_type).all()
                    ct_fse=len(fse)
                    for nunm,i in enumerate(fse):
                        fs.append(f"{Fore.light_yellow}{num}/{Fore.light_cyan}{num+1} of {Fore.light_red}{ct_fse} -> {Fore.light_magenta}{i.field_name}{Style.reset}")
                    fs='\n'.join(fs)
                    field_search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search field?",helpText=f"searches EntryDataExtras field_names:\n{fs}",data="string")
                    if field_search in [None]:
                        return
                    elif field_search in ['d',]:
                        field_search=''
                    query=session.query(EntryDataExtras).filter(EntryDataExtras.field_name.icontains(field_search))
                    results_ede=query.group_by(EntryDataExtras.field_name,EntryDataExtras.field_type).all()
                    if len(results_ede) < 1:
                        continue
                    break
                except Exception as e:
                    print(e)
            field=None
            msg_ede=[]
            for num,i in enumerate(results_ede):
                if num%2==0:
                    color=Fore.cyan
                elif num%3==0:
                    color=Fore.light_cyan
                elif num%4==0:
                    color=Fore.light_steel_blue
                elif num%5==0:
                    color=Fore.light_green
                elif num%6==0:
                    color=Fore.turquoise_4
                elif num%7==0:
                    color=Fore.deep_sky_blue_3a
                elif num%8==0:
                    color=Fore.spring_green_3a
                elif num%9==0:
                    color=Fore.dark_cyan
                else:
                    color=Fore.light_blue
                msg_ede.append(f"{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct}{Fore.grey_50} -> {color}{i.field_name}{Style.reset}:{i.field_type} ede_id={i.ede_id} doe={i.doe}")
            msg_ede='\n'.join(msg_ede)
            while True:
                try:
                    print(msg_ede)
                    index=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which index do you wish to use?",helpText=msg_ede,data="integer")
                    if index in [None,]:
                        return
                    try:
                        print(index)
                        if index <= len(results_ede)-1:
                            field=results_ede[index]
                        else:
                            print(f"index is not within 0-{len(results_ede)-1}")
                            continue
                        break
                    except Exception as e:
                        print(e)
                        break
                except Exception as e:
                    print(e)
            if field == None:
                return
            field_name=field.field_name
            field_type=field.field_type
            field_value=Prompt.__init2__(self,func=FormBuilderMkText,ptext="What do you wish to store as the value?",helpText=field_type,data=field_type)
            if field_value in [None,]:
                return
            
            print(field_name,field_type,field_value)
            extra=EntryDataExtras(field_name=field_name,field_type=field_type,field_value=field_value,EntryId=product.EntryId)
            session.add(extra)
            session.commit()
            session.refresh(extra)
            print(extra)

    def sch_c2e(self,barcode=None):
        with Session(ENGINE) as session:
            if barcode != None:
                search=barcode
            else:
                search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search? [Barcode,Code,Name]",helpText="searches Barcode,Code,Name",data="string")
                if search in [None]:
                    return

            results=session.query(Entry).filter(or_(Entry.Barcode==search,Entry.Code==search,Entry.Barcode.icontains(search),Entry.Code.icontains(search),Entry.Name.icontains(search))).all()
            ct=len(results)
            if ct == 0:
                print("No Results were Found!")
                return
            msg=[]
            for num,i in enumerate(results):
                msg.append(f"{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct}{Fore.grey_50} -> {i.seeShort()}")
            msg='\n'.join(msg)
            product=None
            while True:
                print(msg)
                index=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which index do you wish to use?",helpText=msg,data="integer")
                if index in [None,]:
                    return
                try:
                    product=results[index]
                    break
                except Exception as e:
                    print(e)
            if product in [None,]:
                return
            print("sch_c2e()")
            while True:
                try:
                    fs=[]
                    fse=session.query(EntryDataExtras).group_by(EntryDataExtras.field_name,EntryDataExtras.field_type).all()
                    ct_fse=len(fse)
                    for nunm,i in enumerate(fse):
                        fs.append(f"{Fore.light_yellow}{num}/{Fore.light_cyan}{num+1} of {Fore.light_red}{ct_fse} -> {Fore.light_magenta}{i.field_name}{Style.reset}")
                    fs='\n'.join(fs)
                    field_search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search field?",helpText=f"searches EntryDataExtras field_names:\n{fs}",data="string")
                    if field_search in [None]:
                        return
                    elif field_search in ['d',]:
                        field_search=''
                    query=session.query(EntryDataExtras).filter(EntryDataExtras.field_name.icontains(field_search))
                    results_ede=query.group_by(EntryDataExtras.field_name,EntryDataExtras.field_type,EntryDataExtras.field_value).all()
                    if len(results_ede) < 1:
                        continue
                    break
                except Exception as e:
                    print(e)
            field=None
            msg_ede=[]
            for num,i in enumerate(results_ede):
                if num%2==0:
                    color=Fore.cyan
                elif num%3==0:
                    color=Fore.light_cyan
                elif num%4==0:
                    color=Fore.light_steel_blue
                elif num%5==0:
                    color=Fore.light_green
                elif num%6==0:
                    color=Fore.turquoise_4
                elif num%7==0:
                    color=Fore.deep_sky_blue_3a
                elif num%8==0:
                    color=Fore.spring_green_3a
                elif num%9==0:
                    color=Fore.dark_cyan
                else:
                    color=Fore.light_blue
                msg_ede.append(f"{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct}{Fore.grey_50} -> {color}{i.field_name}{Style.reset}:{i.field_type}={Fore.light_yellow}{i.field_value}{Style.reset} ede_id={i.ede_id} doe={i.doe}")
            msg_ede='\n'.join(msg_ede)
            while True:
                try:
                    print(msg_ede)
                    index=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which index do you wish to use?",helpText=msg_ede,data="integer")
                    if index in [None,]:
                        return
                    try:
                        print(index)
                        if index <= len(results_ede)-1:
                            field=results_ede[index]
                        else:
                            print(f"index is not within 0-{len(results_ede)-1}")
                            continue
                        break
                    except Exception as e:
                        print(e)
                        break
                except Exception as e:
                    print(e)
            if field == None:
                return
            field_name=field.field_name
            field_type=field.field_type
            field_value=field.field_value
            
            print(field_name,field_type,field_value)
            extra=EntryDataExtras(field_name=field_name,field_type=field_type,field_value=field_value,EntryId=product.EntryId)
            session.add(extra)
            session.commit()
            session.refresh(extra)
            print(extra)


    def massEntry(self):
        while True:
            cmds=[
            'n,nf - New Field',
            's,sf - Select Field',
            '1s,bsf - 1 Barcode Select Fields Loop',
            '1n,bnf - 1 Barcode New Fields Loop',
            'sch f2e,ssf2e - search select field',
            '1sch f2e,1ssf2e - search select field loop',
            "'cf2e','copy searched field to entry' - search select copy field to entry",
            ]
            cmds='\n'.join(cmds)
            print(cmds)
            doWhat=Prompt.__init2__(None,func=FormBuilderMkText,ptext="ExtrasMenu:MassEntry[n=New Field,s=Select Field]",helpText=cmds,data="string")
            if doWhat in [None,'d']:
                return
            elif doWhat.lower() in "sch f2e,ssf2e".split(","):
                self.sch_f2e()
            elif doWhat.lower() in "1sch f2e,1ssf2e".split(","):
                barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search? [Barcode,Code,Name]",helpText="searches Barcode,Code,Name",data="string")
                if barcode in [None]:
                    return
                while True:
                    self.sch_f2e(barcode)
                    another=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Another?[Y/n]",helpText="boolean value for yes and no, default is yes",data="boolean")
                    if another in [None,]:
                        return
                    elif another in ['d',True]:
                        continue
                    else:
                        break
            elif doWhat.lower() in ['cf2e','copy searched field to entry']:
                self.sch_c2e()
            elif doWhat.lower() in ['n','nf','New Field'.lower()]:
                self.af2e()
            elif doWhat.lower() in ['s','sf','Select Field'.lower()]:
                self.sf2e()
            elif doWhat.lower() in ['1s','bsf','Barcode Select Fields Loop'.lower()]:
                barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search? [Barcode,Code,Name]",helpText="searches Barcode,Code,Name",data="string")
                if barcode in [None]:
                    return
                while True:
                    self.sf2e(barcode)
                    another=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Another?[Y/n]",helpText="boolean value for yes and no, default is yes",data="boolean")
                    if another in [None,]:
                        return
                    elif another in ['d',True]:
                        continue
                    else:
                        break
            elif doWhat.lower() in ['1n','bnf','Barcode New Fields Loop'.lower()]:
                barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search? [Barcode,Code,Name]",helpText="searches Barcode,Code,Name",data="string")
                if barcode in [None]:
                    return
                while True:
                    self.af2e(barcode)
                    another=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Another?[Y/n]",helpText="boolean value for yes and no, default is yes",data="boolean")
                    if another in [None,]:
                        return
                    elif another in ['d',True]:
                        continue
                    else:
                        break

    def lookup(self):
        with Session(ENGINE) as session:
            search=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search? [Barcode,Code,Name]",helpText="searches Barcode,Code,Name",data="string")
            if search in [None]:
                return
            results=session.query(Entry).filter(or_(Entry.Barcode==search,Entry.Code==search,Entry.Barcode.icontains(search),Entry.Code.icontains(search),Entry.Name.icontains(search))).all()
            ct=len(results)
            if ct == 0:
                print("No Results were Found!")
                return
            msg=[]
            for num,i in enumerate(results):
                msg.append(f"{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct}{Fore.grey_50} -> {i.seeShort()}")
            msg='\n'.join(msg)
            product=None
            while True:
                print(msg)
                index=Prompt.__init2__(None,func=FormBuilderMkText,ptext="which index do you wish to use?",helpText=msg,data="integer")
                if index in [None,]:
                    return
                try:
                    product=results[index]
                    break
                except Exception as e:
                    print(e)
            if product in [None,]:
                return
            extras=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==product.EntryId).all()
            extras_ct=len(extras)
            if extras_ct == 0:
                print("No Extras Found For that Item")
                return
            mtext=[]
            for n,e in enumerate(extras):
                mtext.append(f"\t- {Fore.orange_red_1}{e.field_name}:{Fore.light_steel_blue}{e.field_type}={Fore.light_yellow}{e.field_value} {Fore.cyan}ede_id={e.ede_id} {Fore.light_magenta}doe={e.doe}{Style.reset}")
            mtext='\n'.join(mtext)
            print(product.seeShort())
            print(mtext)


    def __init__(self):
        cmds={
            'af2e':{
            'cmds':['af2e','add field to entry','add field 2 entry'],
            'exec':self.af2e,
            'desc':"add field to Entry"
            },
            'sf2e':{
            'cmds':['sf2e','select field to entry','select field 2 entry'],
            'exec':self.sf2e,
            'desc':"select a stored field and add field to Entry"
            },
            'rm':{
            'cmds':['rm','delete','del','remove'],
            'exec':self.rm_ede_id,
            'desc':"delete an EntryDataExtras item"
            },
            'lookup':{
            'cmds':['s','search','lu','lookup'],
            'exec':self.lookup,
            'desc':"lookup an EntryDataExtras from Entry Data"
            },
            'massEntry':{
            'cmds':['m','massEntry','me',],
            'exec':self.massEntry,
            'desc':"Add Multiple Extras Menu"
            },
            'search select':{
                'cmds':"sch f2e,ssf2e".split(","),
                'exec':self.sch_f2e,
                'desc':'search for field, select field, set value'
            },
            'search select copy':{
                'cmds':"sch c2e,cf2e,sscf2e".split(","),
                'exec':self.sch_c2e,
                'desc':'search for field, select field, copy to entry'
            },
        }
        '''
elif doWhat.lower() in "sch f2e,ssf2e".split(","):
                self.sch_f2e()
            elif doWhat.lower() in "1sch f2e,1ssf2e".split(","):
                barcode=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Search? [Barcode,Code,Name]",helpText="searches Barcode,Code,Name",data="string")
                if barcode in [None]:
                    return
                while True:
                    self.sch_f2e(barcode)
                    another=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Another?[Y/n]",helpText="boolean value for yes and no, default is yes",data="boolean")
                    if another in [None,]:
                        return
                    elif another in ['d',True]:
                        continue
                    else:
                        break
        '''
        helpText=[]
        for m in cmds:
            helpText.append(f"{cmds[m]['cmds']} - {cmds[m]['desc']}")
        helpText='\n'.join(helpText)
        while True:
            doWhat=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"EntryDataExtras@{Fore.light_green}Menu{Fore.light_yellow}",helpText=helpText,data="string")
            if doWhat in [None,]:
                return
            elif doWhat in ['d',]:
                print(helpText)
                continue
            for cmd in cmds:
                check=[i.lower() for i in cmds[cmd]['cmds']]
                if doWhat.lower() in check:
                    try:
                        cmds[cmd]['exec']()
                        break
                    except Exception as e:
                        print(e)