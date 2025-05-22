from bs4 import BeautifulSoup
import requests
import json,sys
from colored import Fore,Style
headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
url = 'https://www.walmart.com/search?query=030772047675'

r = requests.get(url,headers=headers)
soup = BeautifulSoup(r.text, 'lxml')
z=[{f'{Fore.light_red}{str(num)}{Style.reset}':i} for num,i in enumerate(soup.findAll('script'))]
for i in z:
    for k in i:
        if sys.argv[1] in str(i[k]):
            disp=str(i[k]).replace(sys.argv[1],f"{Fore.light_green}{sys.argv[1]}{Style.reset}")
            disp=disp.replace("Results ",f'{Fore.light_magenta}Results {Style.reset}')
            disp=disp.replace('"items"',f'{Fore.light_red}"items"{Style.reset}')
            print(k,disp)
    
#s = str(soup.find('script', {'id': 'searchContent'}))
#print(s)
#s = s.strip('<script id="searchContent" type="application/json"></script>')
#j = json.loads(s)
#print(s)
#x = j['searchContent']['preso']['items']
