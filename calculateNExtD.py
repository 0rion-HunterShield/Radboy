from datetime import datetime,date,time,timedelta


def odays(self,offDays=['monday','sunday','wednesday','friday']):
    now=datetime.now()
    tdy=datetime(now.year,now.month,24)
    count=0
    limit=7
    while True:
        count+=1
        name=tdy.strftime("%A").lower()
        if name not in offDays:
            yield name,tdy,tdy.ctime()
        
        tdy=tdy+timedelta(days=1)
        if count >= 7:
            break
def gap(self):
    nextD=[i for i in odays(None)][0]
    now=datetime.now()
    tdy=datetime(now.year,now.month,24)
    gap=nextD[1]-tdy
    if gap <= timedelta(0):
        nextD=[i for i in odays(None)][1]
        now=datetime.now()
        tdy=datetime(now.year,now.month,24)
        gap=nextD[1]-tdy

print(gap)
