import pyperclip
from colored import Fore,Style
final='Term#Definition\n'

with open("snippet.txt") as f:
    lines=f.readlines()
    for line in lines:
        #print(line.encode())
        if line == '\n':
            continue
        de=line.replace("\n"," ").replace("—","#")+"\n "
        if len(de.split("#")) > 2:
            print(Fore.grey_30+de.replace("\n",f"{Fore.light_red}{Style.bold}\n\\n{Style.reset}").replace("#",f"{Fore.light_green}#{Style.reset}{Fore.grey_30}")+Style.reset)
            fix=input("fixed line: ")
            if fix != '':
                de=fix

        final+=de
            
    with open("result.hsv","w") as out:
        out.write(final)
