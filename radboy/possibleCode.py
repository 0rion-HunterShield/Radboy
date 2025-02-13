import upcean
from barcode import UPCA,EAN13
from colored import Fore,Style,Back
from copy import deepcopy
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base as dbase
from sqlalchemy.ext.automap import automap_base
from radboy.DB.db import *
import radboy.DB.db as DB
from radboy.DB.Prompt import *
def mlen(code):
    if code in [False,None,True]:
        return -1
    elif isinstance(code,float) or isinstance(code,int):
        return len(str(code))
    else:
        return len(str(code))


class PossibleCodesEAN13:
    def mkOption(self,num):
        return f'{Fore.light_green}{num}{Fore.light_red} -> '
    def __init__(self,scanned,skip_retry=True):
        print(f"{Style.bold}{Back.light_slate_blue}{Fore.dark_blue} ::{Fore.red}Code Analsys - EAN13/EAN8{Fore.dark_blue}:: {Fore.dark_green}Start {Style.reset}")
        print(f"EAN13 to Shelf Code Mode! [Start] -- Triggered by -> {Fore.light_magenta}Len(Scanned)>={Fore.light_red}12{Style.reset}")
        if scanned == None:
            return
        while True:
            try:
                print(f"{Fore.light_green}Checking len...{Style.reset}")
                if len(scanned) == 13:
                    print(f"{Fore.light_yellow}Verifing data...{Style.reset}")
                    ean13_verified=EAN13(scanned)
                    ean13_stripped_0=str(ean13_verified)[0:-1]
                    ean13_stripped_1=int(str(ean13_verified)[0:-1])
                    ean13_stripped_2=str(int(str(ean13_verified)))[0:-1]
                    ean8=upcean.convert.convert_barcode_from_ean13_to_ean8(ean13_verified)
                    if ean8:
                        ean8_chped=ean8[:-1]
                    else:
                        ean8_chped=ean8
                    line=1
                    print(f"""
{self.mkOption(1)}{Fore.light_magenta}What You Scanned{Style.reset} -> {scanned}
{self.mkOption(2)}{Fore.cyan}CD_LEN({Fore.orange_red_1}{mlen(ean13_verified)}{Fore.cyan}) - EAN13 is Verified with Checksum{Style.reset} -> {ean13_verified}
{self.mkOption(3.1)}{Fore.light_salmon_1}{Style.bold}{Style.underline}EAN13 Variants that might show on Shelf Tag{Style.reset}
{self.mkOption(3.2)}{Fore.green}CD_LEN({Fore.orange_red_1}{mlen(ean13_stripped_0)}{Fore.green}) - EAN13 Stripped 0 version # 1{Style.reset} -> {ean13_stripped_0}
{self.mkOption(3.3)}{Fore.green_yellow}CD_LEN({Fore.orange_red_1}{mlen(ean13_stripped_1)}{Fore.green_yellow}) - EAN13 Stripped version # 2 {Style.reset} -> {ean13_stripped_1}
{self.mkOption(3.4)}{Fore.yellow}CD_LEN({Fore.orange_red_1}{mlen(ean13_stripped_2)}{Fore.yellow}) - EAN13 Stripped version # 3 {Style.reset} -> {ean13_stripped_2}
{self.mkOption(4.1)}{Fore.light_green}{Style.bold}{Style.underline}EAN8 Variants that might show on the Shelf Tag{Style.reset}
{self.mkOption(4.2)}{Fore.light_salmon_3a}CD_LEN({Fore.orange_red_1}{mlen(ean8)}{Fore.light_salmon_3a}) - EAN8{Style.reset} -> {ean8}
{self.mkOption(4.3)}{Fore.light_salmon_3a}CD_LEN({Fore.orange_red_1}{mlen(ean8_chped)}{Fore.light_salmon_3a}) - EAN8 w/o CKSM{Style.reset} -> {ean8_chped}
                        """)
                    break
                else:
                    print(f"{Fore.light_red}Len is not {Fore.orange_red_1}13{Style.reset}")
                    break
            except Exception as e:
                print(e)
                if skip_retry:
                    break
                print(e)
        print("EAN13 to Shelf Code [Stop]")
        print(f"{Style.bold}{Back.light_steel_blue}{Fore.dark_blue} ::{Fore.red}Code Analsys - EAN13/EAN8{Fore.dark_blue}:: {Fore.dark_green}End {Style.reset}")


class PossibleCodes:
    def mkOption(self,num):
        return f'{Fore.light_green}{num}{Fore.light_red} -> '
    def mkChopped(self,upce,option_number):
        if upce:
            chopped_upce=upce[:-1]
        else:
            chopped_upce=upce
        return f'{Fore.orange_red_1}CD_LEN({Fore.green_yellow}{mlen(chopped_upce)}{Fore.orange_red_1}){Style.reset} - {self.mkOption(option_number)}{Style.underline}UPCE w/o CKSM digit{Style.reset} {Fore.light_magenta}{chopped_upce}{Style.reset}\n{Fore.light_steel_blue}{Style.underline}UPCE Codes should Start with a "0"{Style.reset}'

    def __init__(self,scanned,use_ean13=False,engine=None):
        if scanned == None:
            return
        print(f"{Style.bold}{Back.light_slate_blue}{Fore.dark_blue} ::{Fore.red}Code Analsys - UPCA/UPCE{Fore.dark_blue}:: {Fore.dark_green}Start {Style.reset}")
        upce=False
        try:
            if engine:
                with Session(engine) as session:
                    result=session.query(DB.Entry).filter(DB.Entry.Barcode==scanned).first()
                    if result:
                        msg=f"""{Style.underline}{Fore.light_red}An Entry was found for this Item{Style.reset}
{Fore.light_green}{Style.bold}Entry({Style.reset}
    {Fore.cyan}Name={Fore.light_magenta}{result.Name},{Style.reset}
    {Fore.cyan}Barcode={Fore.orange_red_1}{result.Barcode},{Style.reset}
    {Fore.cyan}Code={Fore.light_yellow}{result.Code},{Style.reset}
    {Fore.cyan}Location={Fore.light_salmon_3a}{result.Location},{Style.reset}
    {Fore.cyan}Price={Fore.grey_50}{result.Price}{Style.reset}
{Fore.light_green}{Style.bold}){Style.reset}
                        """
                        print(msg)
        except Exception as e:
            print(e)
        print(f"--- Start Code=UPC=Barcode ---{scanned}---")
        try:
            if use_ean13:
                scanned_ean13=deepcopy(scanned)
            isUPC=True
            if len(scanned) > 8:
                if len(scanned) < 11:
                    scanned=scanned.zfill(11)
                elif len(scanned) == 13:
                    #scanned=scanned[(11-len(scanned)):len(scanned)]
                    scanned=scanned[len(scanned)-11:len(scanned)]
                 
                upca=UPCA(scanned)
                upcas=str(upca)
                upce=upcean.convert.convert_barcode_from_upca_to_upce(str(upca))
                

                upca_stripped=str(upca)
                upcas=upca_stripped
                upca_ean2=upcean.convert.convert_barcode_from_upca_to_ean13(upcas)
                upca_stripped=str(int(upca_stripped))
                upca_stripped=upca_stripped[:-1]

                print(
            f"""
{Fore.orange_red_1}CD_LEN({Fore.green_yellow}{mlen(upcas[0:-1])}{Fore.orange_red_1}){Style.reset} - {self.mkOption(1)}{Fore.tan}{Style.underline}[{Style.bold}{Fore.light_red}ScanGun{Style.reset}{Fore.tan}{Style.underline}]Telethon Code #:{Style.reset} -> {Fore.pale_green_1b}{Style.bold}{upcas[0:-1]}{Style.reset}
{Fore.orange_red_1}Shelf Tag Variations{Style.reset}
{Fore.orange_red_1}CD_LEN({Fore.green_yellow}{mlen(upca)}{Fore.orange_red_1}){Style.reset} - {self.mkOption(2)}{Fore.cyan}UPCA -> {upca}{Style.reset}
{Fore.orange_red_1}CD_LEN({Fore.green_yellow}{mlen(upca_stripped)}{Fore.orange_red_1}) - {Style.reset}{self.mkOption(3)}{Fore.green}{Style.underline}UPCA Stripped{Style.reset} -> {Fore.magenta}{Style.bold}{upca_stripped}{Style.reset}
{Fore.orange_red_1}CD_LEN({Fore.green_yellow}{mlen(upce)}{Fore.orange_red_1}){Style.reset} - {self.mkOption(4)}{Fore.dark_goldenrod}{Style.underline}UPCE{Style.reset} -> {Fore.magenta}{Style.bold}{upce}{Style.reset}
{self.mkChopped(upce,5)}
                   """)
            else:
                if len(scanned) < 7:
                    print(f"{Fore.light_red}Too Few Digits... at min,{Fore.light_yellow} 7 are needed,{Fore.cyan} {len(scanned)} provided!{Style.reset}")
                    return
                upca=upcean.convert.convert_barcode_from_upce_to_upca(scanned)

                if upca:
                    upca=UPCA(upca)
                    upcas=str(upca)
                    upca_stripped=str(upca) 
                    upca_stripped=str(int(upca_stripped)) 
                    upca_stripped=upca_stripped[:-1]
                    upce=upcean.convert.convert_barcode_from_upce_to_upca(scanned)
                    upce=upcean.convert.convert_barcode_from_upca_to_upce(upce)
                    print(f"""
{Fore.orange_red_1}CD_LEN({Fore.green_yellow}{mlen(upcas[0:-1])}{Fore.orange_red_1}){Style.reset} - {self.mkOption(1.1)}{Fore.tan}{Style.underline}[{Style.bold}{Fore.light_red}ScanGun{Style.reset}{Fore.tan}{Style.underline}]Telethon Code #:{Style.reset} -> {Fore.pale_green_1b}{Style.bold}{upcas[0:-1]}{Style.reset}
{Fore.orange_red_1}Shelf Tag Variations{Style.reset}
{Fore.orange_red_1}CD_LEN({Fore.green_yellow}{mlen(upca)}{Fore.orange_red_1}){Style.reset} - {self.mkOption(1.2)}{Fore.green_yellow}UPCA-Checked -> {upca}{Style.reset}
{Fore.orange_red_1}CD_LEN({Fore.green_yellow}{mlen(upca_stripped)}{Fore.orange_red_1}){Style.reset} - {self.mkOption(1.3)}{Fore.green}{Style.underline}UPCA Stripped{Style.reset} ->{Fore.magenta}{Style.bold}{upca_stripped}{Style.reset}""")
                print(f"""
{Fore.orange_red_1}CD_LEN({Fore.green_yellow}{mlen(upca)}{Fore.orange_red_1}){Style.reset} - {self.mkOption(1)}{Fore.cyan}UPCA -> {upca}{Style.reset}
{Fore.orange_red_1}CD_LEN({Fore.green_yellow}{mlen(upce)}{Fore.orange_red_1}){Style.reset} - {self.mkOption(2)}{Fore.yellow}{Style.underline}UPCE{Style.reset} ->{Fore.magenta}{Style.bold}{upce}{Style.reset}
{self.mkChopped(upce,3)}
                """)
            print(f"{Fore.orange_red_1}CD_LEN({Fore.green_yellow}{mlen(str(str(upca)[:-1]).zfill(13))}{Fore.orange_red_1}){Style.reset} - {self.mkOption(4)}{Fore.yellow}PickList Code -> {str(str(upca)[:-1]).zfill(13)}{Style.reset} - {Style.bold}{Fore.light_red}Only found on picklists, possibly invoices!{Style.reset}")
        except Exception as e:
            print(e)
        print(f"--- End Code=UPC=Barcode ---{scanned}---")
        print(f"{Style.bold}{Back.light_steel_blue}{Fore.dark_blue} ::{Fore.red}Code Analsys - UPCA/UPCE{Fore.dark_blue}:: {Fore.dark_green}End {Style.reset}")

        if use_ean13:
            PossibleCodesEAN13(scanned=scanned_ean13)

if __name__ == "__main__":
    PossibleCodes(scanned=input("code"))


def run(engine=None):
    while True:
        self=PossibleCodes
        def mkString(text,data):
            return text
        ht=f'''
{self.mkOption(PossibleCodes,1)}EAN13/EAN8,UPCA/UPCE break down data; not a db scan, per se.
{self.mkOption(PossibleCodes,2)}EAN13 is the Compressed Form of EAN8; len(EAN13)==13, len(EAN8)==8
{self.mkOption(PossibleCodes,3)}UPCE is the Compressed Form of UPCA; len(UPCA)==8,len(UPCE)==8; UPCE must start with "0"
{self.mkOption(PossibleCodes,4)}UPCE does not have to have a checksum like upca, just make sure all 7 digits are correct
{self.mkOption(PossibleCodes,5)}UPCA codes are don't have to start with their initial "0" if they have one, as they are treated like Integers
{self.mkOption(PossibleCodes,6)}UPCE codes MUST have their starting "0" to be valid
{self.mkOption(PossibleCodes,7.1)}Safeway Store Tags contain the Product CIC, not the product Barcode/UPCA, unless the tag is a ORD/KeHe Tag, which
{self.mkOption(PossibleCodes,7.2)}- In such cases, the shelf label instead stores the product UPC/Barcode.
{self.mkOption(PossibleCodes,8)}Target/Walmart/Grocery Outlet Shelf Tags Carry the UPCA for the product, not the CIC
{self.mkOption(PossibleCodes,9)}The Numbered lines are Possible Codes to Look for, whether it is EAN13 or UPCA, EAN13 is treated differently tho.
{self.mkOption(PossibleCodes,10)}EAN8 input is not supported! Only Ean13 to Ean8 can be used here
{self.mkOption(PossibleCodes,11)}False==No EAN8/UPCE Available for Code Provided
        '''
        code=Prompt.__init2__(None,func=mkString,ptext="UPCA/UPCE/EAN13 Barcodes",helpText=ht,data=None)
        if code in [None,]:
            return
        else:
            try:
                print(f"{Fore.dark_goldenrod}{Style.underline}Scanned Length Info.\n{Style.res_underline}{Style.reset}{Fore.cyan}{code}{Style.reset} is {Fore.green}'{len(code)}'{Style.reset} characters long!")
                PossibleCodes(scanned=code,use_ean13=True,engine=engine)
            except Exception as e:
                print(str(e))
                print(repr(e))
