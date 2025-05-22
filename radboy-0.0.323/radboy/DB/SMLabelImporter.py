from bs4 import BeautifulSoup as bs
import sys
from barcode import UPCA
from upcean import convert
import csv
from pathlib import Path
import time
from radboy.DB.Prompt import *
from radboy.DB.db import *
from colored import Fore,Style

def ScrapeLocalSmartLabelList(engine=None):
    pgurl="https://us.pg.com/brands/\nwww.colgatepalmolive.com/en-us/\nsmartlabel.henkel-northamerica.com"
    smurl="https://smartlabel.pg.com/en-us\nhttps://www.colgatepalmolive.com/en-us/smartlabel\nsmartlabel.henkel-northamerica.com"
    print(f"{Fore.light_yellow}manufacturer",pgurl)
    print(f"{Fore.light_green}smartlabel",smurl)
    print(Style.reset)
    time.sleep(1)
    def mkPath(text,self):
        print(text)
        try:
            p=Path(text)
            if p.exists() and p.is_file():
                return p
            else:
                return
        except Exception as e:
            print(e)

    filename=Prompt.__init2__(None,func=mkPath,ptext="Smartlabel file",helpText="from right-click save-page-as in chrome/firefox",data={})
    if filename in [None,]:
        return

    with open(filename,"r") as file,open("export.csv","w") as exported:
        writer=csv.writer(exported,delimiter=';')
        html=''
        html=file.read()
        soup=bs(html)
        tables=soup.find_all('table')
        csvd=[]
        csvd.append(['Barcode','Code','Name','ALT_Barcode'])
        for r in tables:
            links=r.find_all('a')
            for link in links:
                link_is_pg='smartlabel.pg.com/en-us' in link['href']
                link_is_po='www.colgatepalmolive.com/en-us/' in link['href']
                link_is_henkel='smartlabel.henkel-northamerica.com' in link['href']
                if link_is_pg:
                    name,upc=link.text,str(link['href'].split('/')[-1])[2:]
                elif link_is_po:
                    name,upc=link.text,str(UPCA(str(link['href'].split('/')[-1])))
                elif link_is_henkel:
                    name,upc=link.text,str(link['href'].split('/')[-1])[2:]
                else:
                    continue
                print(str(link['href']))
                if name != '':
                    if upc != '':
                        try:
                            print(upc)
                            if len(upc) > 8:
                                upca=UPCA(upc)
                                upce=convert.convert_barcode_from_upca_to_upce(upc)
                            else:
                                if len(upc) < 8:
                                    print(f"invalid barcode '{upc}'")
                                    continue
                                upce=upc
                                upca=convert.convert_barcode_from_upce_to_upca(upc)
                            if upce == False:
                                upce=''
                            csvd.append([upca,'',name.replace('\n','$newline$').replace(';','$semicolon$'),upce])
                            print(name,upca,upce,'added',sep=';')
                        except Exception as e:
                            print(name,upc,e,'Exception')
        if engine != None:
            with Session(engine) as session:
                for num,(upc,code,name,alt) in enumerate(csvd):
                    print((upc,code,name,alt))
                    check=session.query(Entry).filter(Entry.Barcode==str(upc)).first()
                    if not check:
                        print(f"adding {upc} -> {name}")
                        ne=Entry(Barcode=str(upc),Code=str(code),Name=name,ALT_Barcode=str(alt),Price=0,CaseCount=1)
                        session.add(ne)
                        if num % 30 == 0:
                            session.commit()
                    else:
                        print(check.seeShort())
                session.commit()
                session.flush()


        writer.writerows(csvd)
        #print(links)
if __name__ == "__main__":
    ScrapeLocalSmartLabelList(engine=ENGINE)
