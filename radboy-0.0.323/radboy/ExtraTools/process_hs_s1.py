import re,csv
from colored import Fore,Style
from pathlib import Path

errors={'too many':[],'too few':[]}
rows=[['Term','Definition']]
s1_file=Path("dictionary.txt")

with open(s1_file,"r") as f:
    for num,line in enumerate(f.readlines()):
        p=re.findall(r"PAGE \d* START",line)
        if len(p) > 0:
            continue
        elif line in ['','\n']:
            continue
        else:
            if '#' in line:
                print(line.replace('#',f'{Fore.light_red}#{Style.reset}'))
                if len(line.split('#')) > 2:
                    print(f"{Fore.orange_red_1}Too many '#' {line}{Style.reset}")
                    errors['too many'].append({'line no.':num+1,'count':len(line.split('#')),'line text':line})
            else:
                print(f"{Fore.orange_red_1}Missing '#'{line}{Style.reset}")
                errors['too few'].append({'line no.':num+1,'count':len(line.split('#')),'line text':line})

            rows.append(line.split("#"))



final_file=Path("result.hsv")
if errors == {'too many': [], 'too few': []}:
    with open(final_file,"w") as ofile:
        writer=csv.writer(ofile,delimiter="#")
        writer.writerows(rows)
        print(f"'{Fore.light_green}{final_file.absolute()}{Style.reset}' -> Written")
else:
    for num,k in enumerate(errors):
        for numnum,kk in enumerate(errors[k]):
            print(f'{Fore.light_red}{k} - {Fore.light_yellow}{numnum}{Style.reset}',kk)
    #print(rows)
    


