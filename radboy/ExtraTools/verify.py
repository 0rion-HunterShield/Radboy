import csv,string
from colored import Fore,Style,Back
from pathlib import Path

class VerifyCSV:
    def __init__(self):
        c={
        1:Fore.light_green,
        2:Fore.light_yellow,
        3:Fore.light_red,
        4:Fore.light_magenta,
        5:Fore.orange_red_1,
        6:Fore.light_steel_blue,
        7:Fore.light_sea_green,
        8:Fore.dark_goldenrod,
        9:Fore.yellow,
        10:Fore.magenta,
        }
        last=None
        if Path('last.txt').exists():
            last=Path('last.txt').open('r').read()
            if not Path(last).exists():
                Path('last.txt').unlink()

        if last in ['',None]:
            ifile=input("file: ")
        else:
            ifile=last

        with open(ifile,"r") as o:
         reader=csv.reader(o,delimiter=',')
         print("Line Len,Line No., - # -Line Text")
         for num,line in enumerate(reader):
          print(f'{c[len(line)]}{len(line)}{Style.reset}',num+1,f'{Fore.magenta}- #-{Fore.light_sea_green}{line}{Style.reset}')
          if len(line[0]) != 8 and num > 0:
              print(f"{Fore.orange_red_1}Code Len is not 8{Style.reset}")
          if num == 0:
           header=["Code","Facings","Name","CaseCount","Barcode"]
           if line != header:
            print(f"{Fore.orange_red_1}Header is missing: {header}{Style.reset}")
          if num > 0:
           for char in line[0]:
            if char in string.ascii_letters+string.punctuation+string.whitespace:
             print(f"{Fore.orange_red_1}Invalid Character '{char}' found in Code Column")
           for char in line[-1]:
            if char in string.ascii_letters+string.punctuation+string.whitespace:
             print(f"{Fore.orange_red_1}Invalid Character '{char}' found in Barcode Column")


        Path('last.txt').open('w').write(ifile)
if __name__ == "__main__":
    VerifyCSV()
