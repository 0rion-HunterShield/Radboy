from . import *


class InListRestoreUI:
    def sf2l(self):
        with Session(ENGINE) as session:
            results=session.query(Entry).filter(Entry.InList==True).all()
            Comments=Prompt.__init2__(None,func=FormBuilderMkText,ptext="what Comments need to be said about this Restore List?",helpText="Comments",data="string")
            if Comments in ['d',]:
                Comments=''
            elif Comments in [None,]:
                return
            Note=Prompt.__init2__(None,func=FormBuilderMkText,ptext="what is the Note for this Restore List?",helpText="Note",data="string")
            if Note in ['d',]:
                Note=''
            elif Note in [None,]:
                return
            Description=Prompt.__init2__(None,func=FormBuilderMkText,ptext="what is the Description of this Restore List?",helpText="Description",data="string")
            if Description in ['d',]:
                Description=''
            elif Description in [None,]:
                return
            Name=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What Name Do you want to call this Restore List?",helpText="Name",data="string")
            if Name in [None,'d']:
                print("Name cannot be empty, or user cancelled!")
                return
            InList=True
            if len(results) < 1:
                print("No results were found to use!")
                return
            EntryFieldsJson={}
            EntryFieldsJson['Note']=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What Notes do you wish to save for restore on Entry.Note",helpText=f"a random string, use {Fore.light_cyan}#ml#{Fore.light_yellow}{Fore.light_cyan}#ml#{Fore.light_yellow} for multi-line input",data="string")
            if EntryFieldsJson['Note'] is None or EntryFieldsJson['Note'] in [None,]:
                return
            elif EntryFieldsJson['Note'] in ['d',]:
                EntryFieldsJson['Note']=''
            EntryFieldsJson=json.dumps(EntryFieldsJson)
            for num,entry in enumerate(results):
                
                ilr=InListRestore(Name=Name,InList=InList,Description=Description,Note=Note,Comments=Comments,EntryId=entry.EntryId,EntryFieldsJson=EntryFieldsJson)
                #ilr=InListRestore(Name=Name,InList=InList,Description=Description,Note=Note,Comments=Comments,EntryId=entry.EntryId)
                session.add(ilr)
                if num % 10 == 0:
                    session.commit()
            session.commit()


    '''Not Currently in use was just a something to make.'''
    def TagSelector(self):
        with Session(ENGINE) as session:
            daylogs=session.query(DayLog).group_by(DayLog.Tags).all()
            entrys=session.query(Entry).group_by(Entry.Tags).all()
            tags=[]
            for i in daylogs:
                try:
                    tagsSub=json.loads(i.Tags)
                    for ii in tagsSub:
                        if ii not in tags:
                            tags.append(ii)
                except Exception as e:
                    print(f"no tags to append to list tags={tags}")
            for i in entrys:
                try:
                    tagsSub=json.loads(i.Tags)
                    for ii in tagsSub:
                        if ii not in tags:
                            tags.append(ii)
                except Exception as e:
                    print(f"no tags to append to list tags={tags}")
            ct=len(tags)
            if ct < 1:
                print("there are no tags in the system!!!")
                return '[]'
            tagHelp=[]
            for num,i in enumerate(tags):
                msg=f"{Fore.light_cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct}{Fore.light_steel_blue} -> {i}{Style.reset}"
                tagHelp.append(msg)
            tagHelp='\n'.join(tagHelp)
            print(tagHelp)
            while True:
                selector=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Which indexes (comma seperated {Fore.light_cyan}#'s{Fore.light_yellow}')",helpText=f"a comma seperated list or just a number\n{tagHelp}",data="list")
                if selector is None or selector in [None,[]]:
                    print("User cancelled")
                    return '[]'
                else:
                    try:
                        tsub=[]
                        for i in selector:
                            try:
                                i=int(i)
                                if tags[i] not in tsub:
                                    tsub.append(tags[i])
                            except Exception as ee:
                                print(ee,"Processing will continue")
                        return json.dumps(tsub)
                    except Exception as e:
                        print(e)
                        return '[]'

    def sf2llf(self):
        with Session(ENGINE) as session:
            results=session.query(Entry).filter(Entry.InList==True).all()
            Comments=Prompt.__init2__(None,func=FormBuilderMkText,ptext="what Comments need to be said about this Restore List?",helpText="Comments",data="string")
            if Comments in ['d',]:
                Comments=''
            elif Comments in [None,]:
                return
            Note=Prompt.__init2__(None,func=FormBuilderMkText,ptext="what is the Note for this Restore List?",helpText="Note",data="string")
            if Note in ['d',]:
                Note=''
            elif Note in [None,]:
                return
            Description=Prompt.__init2__(None,func=FormBuilderMkText,ptext="what is the Description of this Restore List?",helpText="Description",data="string")
            if Description in ['d',]:
                Description=''
            elif Description in [None,]:
                return
            Name=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What Name Do you want to call this Restore List?",helpText="Name",data="string")
            if Name in [None,'d']:
                print("Name cannot be empty, or user cancelled!")
                return
            InList=True
            if len(results) < 1:
                print("No results were found to use!")
                return
            EntryFieldsJson_z=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What Notes do you wish to save for restore on Entry.Note",helpText=f"a random string, use {Fore.light_cyan}#ml#{Fore.light_yellow}{Fore.light_cyan}#ml#{Fore.light_yellow} for multi-line input",data="string")
            if EntryFieldsJson_z is None or EntryFieldsJson_z in [None,]:
                return
            elif EntryFieldsJson_z in ['d',]:
                EntryFieldsJson_z=''
            for num,entry in enumerate(results):
                locationFields=['Shelf',
                                'BackRoom',
                                'Display_1',
                                'Display_2',
                                'Display_3',
                                'Display_4',
                                'Display_5',
                                'Display_6',
                                'SBX_WTR_DSPLY',
                                'SBX_CHP_DSPLY',
                                'SBX_WTR_KLR',
                                'FLRL_CHP_DSPLY',
                                'FLRL_WTR_DSPLY',
                                'WD_DSPLY',
                                'CHKSTND_SPLY',
                                'Distress',
                                'ListQty']
                EntryFieldsJson={}
                for i in locationFields:
                    EntryFieldsJson[i]=getattr(entry,i)
                EntryFieldsJson['Note']=EntryFieldsJson_z
                EntryFieldsJson=json.dumps(EntryFieldsJson)
                ilr=InListRestore(Name=Name,InList=InList,Description=Description,Note=Note,Comments=Comments,EntryId=entry.EntryId,EntryFieldsJson=EntryFieldsJson)
                session.add(ilr)
                if num % 10 == 0:
                    session.commit()
            session.commit()

    def listRestoreNames(self,ALL=False):
        Name=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What Do you want look for by Name?",helpText="Name",data="string")
        if Name in [None,]:
            print("Name cannot be empty, or user cancelled!")
            return
        elif Name in ['d',]:
            Name=''
        with Session(ENGINE) as session:
            results=session.query(InListRestore).filter(InListRestore.Name.icontains(Name)).group_by(InListRestore.Name).all()
            ct=len(results)
            mtext=[]
            for num, i in enumerate(results):
                if not ALL:
                    msg=f"""{Fore.light_cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct} -> {Fore.grey_70}Name: {Fore.light_steel_blue}{i.Name}{Style.reset}"""
                else:
                    msg=f"""{Fore.light_cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct} -> {i}"""
                mtext.append(msg)
            mtext='\n'.join(mtext)
            print(mtext)
            print(f"{Fore.light_steel_blue}{ct}{Fore.orange_red_1} Total Results{Style.reset}")

    def RestoreFromName(self,values=False):
        Name=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What Do you want look for by Name?",helpText="Name",data="string")
        if Name in [None,]:
            print("Name cannot be empty, or user cancelled!")
            return
        elif Name in ['d',]:
            Name=''
        with Session(ENGINE) as session:
            results=session.query(InListRestore).filter(InListRestore.Name.icontains(Name)).group_by(InListRestore.Name).all()
            ct=len(results)
            mtext=[]
            for num, i in enumerate(results):
                msg=f"{Fore.light_cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct} -> {Fore.grey_70}Name: {Fore.light_steel_blue}{i.Name}{Style.reset}"
                mtext.append(msg)
            mtext='\n'.join(mtext)
            while True:
                try:
                    print(mtext)
                    print(f"{Fore.light_steel_blue}{ct}{Fore.orange_red_1} Total Results{Style.reset}")
                    if ct < 1:
                        print("No results")
                        break
                    which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Which index?",helpText="an integer",data="integer")
                    if which in [None,'d']:
                        return
                    if which >= 0 and which < ct:
                        zerod=session.query(Entry).update({'InList':False})
                        session.commit()
                        restore=session.query(InListRestore).filter(InListRestore.Name==results[which].Name).all()
                        for num,i in enumerate(restore):
                            try:
                                j=json.loads(i.EntryFieldsJson)
                                note=j.get("Note")
                            except Exception as e:
                                print(e)
                                note=''
                            x=session.query(Entry).filter(Entry.EntryId==i.EntryId).update({'InList':i.InList,'Note':note})
                            if values:
                                try:
                                    z=json.loads(i.EntryFieldsJson)
                                    if 'Tags' in z.keys():
                                        tags=z.pop('Tags')
                                    x=session.query(Entry).filter(Entry.EntryId==i.EntryId).update(z)
                                    #xtra tag processing goes here time to start sleeping!!!#
                                except Exception as e:
                                    print(e)
                            if num % 10 == 0:
                                session.commit()
                        session.commit()
                        break
                except Exception as e:
                    print(e)

    def DeleteFromName(self):
        Name=Prompt.__init2__(None,func=FormBuilderMkText,ptext="What Do you want look for by Name?",helpText="Name",data="string")
        if Name in [None,]:
            print("Name cannot be empty, or user cancelled!")
            return
        elif Name in ['d',]:
            Name=''
        with Session(ENGINE) as session:
            results=session.query(InListRestore).filter(InListRestore.Name.icontains(Name)).group_by(InListRestore.Name).all()
            ct=len(results)
            mtext=[]
            for num, i in enumerate(results):
                msg=f"{Fore.light_cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{ct} -> {Fore.grey_70}Name: {Fore.light_steel_blue}{i.Name}{Style.reset}"
                mtext.append(msg)
            mtext='\n'.join(mtext)
            while True:
                try:
                    print(mtext)
                    print(f"{Fore.light_steel_blue}{ct}{Fore.orange_red_1} Total Results{Style.reset}")
                    which=Prompt.__init2__(None,func=FormBuilderMkText,ptext="Which index?",helpText="an integer",data="integer")
                    if which in [None,'d']:
                        return
                    if which >= 0 and which < ct:
                        restore=session.query(InListRestore).filter(InListRestore.Name==results[which].Name).delete()
                        session.commit()
                        break
                except Exception as e:
                    print(e)
    def FixTable(self):
        InListRestore.__table__.drop(ENGINE)
        InListRestore.metadata.create_all(ENGINE)
        test=InListRestore()
        print(test)
        print(f"{Fore.light_green}Done!!!{Style.reset}")

    def __init__(self):
        '''Store A List of EntryId's whose InList==True being set to True will allow for speedier on-the-floor use of the List Maker.'''
        cmds={
            'save2list':{
            'cmds':['save2list','s2l',],
            'exec':self.sf2l,
            'desc':"save all current Entries with InList=True to InListRestore"
            },
            'list tags test':{
            'cmds':['ltt','list tags test',],
            'exec':lambda self=self:print(self.TagSelector()),
            'desc':"test list tags"
            },
            'save2list lf':{
            'cmds':['save2list lf','s2llf','s2l lf'],
            'exec':self.sf2llf,
            'desc':"save all current Entries with InList=True to InListRestore and Stores Location Fields values in EntryFieldsJson as a dictionary"
            },
            'list names':{
            'cmds':['lrn','list restore names'],
            'exec':self.listRestoreNames,
            'desc':"List Restore Names",
            },
            'list all names':{
            'cmds':['sarn','show all restore names'],
            'exec':lambda self=self:self.listRestoreNames(ALL=True),
            'desc':"List Restore Names, but show everything",
            },
            'restore list':{
            'cmds':['restore','restore list','rl','lr'],
            'exec':self.RestoreFromName,
            'desc':"Restore Entry's to InList==True by Restore Name",
            },
            'restore list lf':{
            'cmds':['restore lf','restore list lf','rl lf','lr lf'],
            'exec':lambda self=self:self.RestoreFromName(values=True),
            'desc':"Restore Entry's to InList==True by Restore Name and restore location fields values",
            },
            'delete list':{
            'cmds':['del','delete','remove','rem','rm',],
            'exec':self.DeleteFromName,
            'desc':"Delete a Restore list by Name",
            },
            'fixtable':{
            'cmds':['fixtable','fxtbl','fix table','fx tbl',],
            'exec':self.FixTable,
            'desc':"Drop and Recreate table; in case new fields are added",
            },
        }
        helpText=[]
        for m in cmds:
            helpText.append(f"{Fore.light_cyan}{cmds[m]['cmds']}{Fore.orange_red_1} - {Fore.light_steel_blue}{cmds[m]['desc']}{Style.reset}")
        helpText='\n'.join(helpText)
        while True:
            doWhat=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"InListRestore@{Fore.light_green}Menu{Fore.light_yellow}",helpText=helpText,data="string")
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