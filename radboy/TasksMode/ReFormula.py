import re
from copy import deepcopy
from colored import Style,Fore
import math
import pandas as pd
import numpy as np
import pint
CVT=pint.UnitRegistry().convert

class ReParseFormula:
    def NumDotCase(self,formula='1+2-2/3*1**5//%3.c-1.3.case',suffixes=["case","c"],casecount=1):
        for suffix in suffixes:
            search=r'\d+\.?\d*\.{suffix}'.format(suffix=suffix)
            search2=r"\d+\.?\d*"
            pattern=re.compile(search)
            results_list=[[m.start(),m.end()] for m in re.finditer(pattern,formula)]
            rs=[formula[s:e] for s,e in results_list]
            rs.sort(key=len,reverse=True)
            for u in rs:
                qty=re.findall(search2,u)
                if len(qty) == 1:
                    qty=float(qty[0])
                    formula=formula.replace(u,f'({qty}*{casecount})')
        return formula

    def CaseDotNum(self,formula='1+2-2/3*1**5//%3-case.1.3',suffixes=["case","c"],casecount=1):
        for suffix in suffixes:
            search=r'{suffix}\.\d+\.?\d*'.format(suffix=suffix)
            search2=r"\d+\.?\d*"
            pattern=re.compile(search)
            results_list=[[m.start(),m.end()] for m in re.finditer(pattern,formula)]
            rs=[formula[s:e] for s,e in results_list]
            rs.sort(key=len,reverse=True)
            for u in rs:
                qty=re.findall(search2,u)
                if len(qty) == 1:
                    qty=float(qty[0])
                    formula=formula.replace(u,f'({qty}*{casecount})')
        return formula

    def __init__(self,formula,casecount=1,suffixes=['c','case'],solve=False):
        suffixes.sort(key=len,reverse=True)
        f=self.CaseDotNum(formula=formula,casecount=casecount,suffixes=suffixes)
        f=self.NumDotCase(formula=f,casecount=casecount,suffixes=suffixes)
        self.formula=f
        print(f"{Fore.light_red}Processing Suffixes/Prefixes: {Fore.light_green}{suffixes}{Fore.dark_goldenrod} -> {f}{Style.reset}")
        if solve:
            self.value=float(eval(f))
        else:
            self.value=None

    def __str__(self):
        return self.formula
if __name__ == "__main__":
    f="1.c"
    formulaObj=ReParseFormula(formula=f)
    print(formulaObj.formula,formulaObj.value)
