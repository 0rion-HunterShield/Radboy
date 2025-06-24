import pint
import numpy as np
from radboy.DB.db import *
from radboy.DB.Prompt import *
from radboy.FB.FBMTXT import *
from radboy.FB.FormBuilder import *
from colored import Fore,Back,Style

def HoleSize():
    def static_colorize(m,n,c):
        msg=f'{Fore.cyan}{n}/{Fore.light_yellow}{n+1}{Fore.light_red} of {c} {Fore.dark_goldenrod}{m}{Style.reset}'
        return msg
    data={
    'discreetStep':{
    'type':'integer',
    'default':12},
    'discreetFreq':{
    'type':'float',
    'default':500e9},
    'percentBuffer':{
    'type':'float',
    'default':0.09091},
    'roundTo':{
    'type':'integer',
    'default':4,
    }
    }
    fd=FormBuilder(data=data)
    if fd == None:
        return 
    roundTo=fd['roundTo']
    discreetStep=fd['discreetStep']
    discreetFreq=fd['discreetFreq']
    speedoflight=299792458
    #add 10% to accomodate for accuracies
    percentBuffer=fd['percentBuffer']
    #add buffer and 1 step to ensure end of frequency range is calculated
    frequency_max=discreetFreq+((discreetFreq/discreetStep)+((discreetFreq/discreetStep)*percentBuffer)) #5ghz
    step=frequency_max/discreetStep
    converter=pint.UnitRegistry()
    numerable=np.arange(0,frequency_max,step)
    ct=len(numerable)
    numerable=enumerate(numerable)
    for num,frequency in numerable:
     try:
         frequency=round(float(frequency),roundTo)
         formula_result=round(float(speedoflight/frequency),roundTo)
         as_mm=round(float(converter.convert(formula_result,'meter','millimeter')),roundTo)
         frequency_human=round(float(converter.convert(frequency,'hertz','gigahertz')),roundTo)
         print(static_colorize(f'{Fore.green_yellow}hole diameter/Gap Width/Wavelength{Fore.orange_red_1} (mm)/{Fore.magenta}(in){Fore.light_steel_blue} for frequency (ghz)',num,ct))
         print(static_colorize(f"{Fore.orange_red_1}{as_mm}/{Fore.magenta}{round(converter.convert(as_mm,'mm','in'),roundTo)}{Fore.light_steel_blue} for {frequency_human}(ghz){Style.reset}",num,ct))
     except Exception as e:
        print(e)
