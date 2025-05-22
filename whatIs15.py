import sys
from colored import Fore,Back,Style
from datetime import datetime
currency={}
currency['1$']=1
currency['2$']=2
currency['5$']=5
currency['10$']=10
currency['20$']=20
currency['50$']=50
currency['100$']=100
currency['penny']=0.01
currency['nickel']=0.05
currency['dime']=0.1
currency['quarter']=0.25

max_dollars=15
max_unit_range=int(max_dollars/currency['penny'])
now=datetime.now()
def all_of_one_type():
    for i in currency:
        for num in range(0,max_unit_range):
            if round(currency[i]*num,2) > max_dollars:
                yield currency[i],i,round(currency[i]*num,2)

def brute_force():
    possibilities=0
    ttl_found=0
    last=0
    for d100 in range(0,max_unit_range):
        if d100*100 > max_dollars:
            break
        for d50 in range(0,max_unit_range):
            if d50*50 > max_dollars:
                break
            for d20 in range(0,max_unit_range):
                if d20*20 > max_dollars:
                    break
                for d10 in range(0,max_unit_range):
                    if d10*10 > max_dollars:
                        break
                    for d5 in range(0,max_unit_range):
                        if d5*5 > max_dollars:
                            break
                        for d2 in range(0,max_unit_range):
                            if d2*2 > max_dollars:
                                break
                            for d1 in range(0,max_unit_range):
                                if d1*1 > max_dollars:
                                    break
                                for c025 in range(0,max_unit_range):
                                    if c025*0.25 > max_dollars:
                                        break
                                    for c010 in range(0,max_unit_range):
                                        if c010*0.1 > max_dollars:
                                            break
                                        for c005 in range(0,max_unit_range):
                                            if c005*0.05 > max_dollars:
                                                break
                                            for c001 in range(0,max_unit_range):
                                                if c001*0.01 > max_dollars:
                                                    break
                                                formula_string=f"""({currency['1$']}*{d1})+({currency['2$']}*{d2})+({currency['5$']}*{d5})+({currency['10$']}*{d10})+({currency['20$']}*{d20})+({currency['50$']}*{d50})+({currency['100$']}*{d100})+({currency['penny']}*{c001})+({currency['nickel']}*{c005})+({currency['dime']}*{c010})+({currency['quarter']}*{c025})"""
                                                test=eval(formula_string)
                                                taken=datetime.now()-now
                                                if round(test,2) == round(max_dollars,2):
                                                    msg=f'{"\b"*last}'+f'{Fore.light_green}Found {ttl_found} out of {possibilities} Iterations @ {now}, taking {taken} to find!{Style.reset}'
                                                    last=len(msg)
                                                    sys.stdout.write(msg)
                                                    ttl_found+=1
                                                    yield formula_string,round(test,2)
                                                else:
                                                    if (possibilities%(100))==0:
                                                        msg=f'{"\b"*last}'+f'{Fore.light_yellow}Searched {possibilities}{Style.reset}'
                                                        last=len(msg)
                                                        sys.stdout.write(msg)
                                                possibilities+=1
for formula,result in brute_force():
    print(formula,result)



