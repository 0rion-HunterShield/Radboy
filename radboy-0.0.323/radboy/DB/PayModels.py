from radboy.DB.db import *
from radboy.DB.RandomStringUtil import *
import radboy.Unified.Unified as unified
import radboy.possibleCode as pc
from radboy.DB.Prompt import *
from radboy.DB.Prompt import prefix_text
from radboy.TasksMode.ReFormula import *
from radboy.TasksMode.SetEntryNEU import *
from radboy.FB.FormBuilder import *
from radboy.FB.FBMTXT import *
from radboy.RNE.RNE import *
from radboy.Lookup2.Lookup2 import Lookup as Lookup2
from radboy.DayLog.DayLogger import *
from radboy.DB.masterLookup import *
from radboy.DB.blankDataFile import *
from radboy.GeoTools import *
from radboy.ExportUtility import *
from radboy.Of.of import *
from radboy.AlcoholConsumption.ac import *
from radboy.StopWatchUi.StopWatchUi import *
from radboy.EntryExtras.Extras import *
import platform,sympy
import pathlib
from collections import namedtuple,OrderedDict
import nanoid,qrcode,io
from password_generator import PasswordGenerator
import random
from pint import UnitRegistry
import pandas as pd
import numpy as np
from datetime import *
from colored import Style,Fore
import json,sys,math,re,calendar
from radboy.InListRestore.ILR import *
from radboy.Compare.Compare import *
from radboy.Unified.Unified2 import Unified2
from copy import copy

class SafewayNightCrew_version_6003336(BASE,Template):
    #accumulated variables are the variables to store hour values
    #rate values are charged by the hour as far as i know of
    SWNC_v_6003336_id=Column(Integer,primary_key=True)
    __tablename__="SafewayNightCrew_version_6003336"

    regular_hours_rate=Column(Float,default=27.734)
    regular_hours_accumulated=Column(Float,default=0)

    sunday_regular_hours_rate=Column(Float,default=27.734)
    sunday_regular_hours_accumulated=Column(Float,default=0)

    sunday_premium_rate=Column(Float,default=1)
    sunday_premium_accumulated=Column(Float,default=0)

    sunday_overtime_rate=Column(Float,default=62.409)
    sunday_overtime_accumulated=Column(Float,default=0)

    first_shift_premium_regular_rate=Column(Float,default=0.65)
    first_shift_premium_regular_accumulated=Column(Float,default=0)

    first_shift_premium_sunday_rate=Column(Float,default=0.65)
    first_shift_premium_sunday_accumulated=Column(Float,default=0)

    day6_overtime_rate=Column(Float,default=41.946)
    day6_overtime_accumulated=Column(Float,default=0)

    overtime1x5_rate=Column(Float,default=41.949)
    overtime1x5_accumulated=Column(Float,default=0)

    #datetime(day) that pay is being estimated for
    datetime_for_estimation=Column(DateTime,default=None)
    #estimated taxes to be taken from pay
    estimated_taxes_total=Column(Float,default=24.32942761/100)
    #estimated hours to be worked
    estimated_hours_in=Column(Float)

    #estimated amount to be paid with out taxes
    estimated_paid_out_wo_taxes=Column(Float,default=0)
    #estimated amount to be paid with taxes
    estimated_paid_out_w_taxes=Column(Float,default=0)

    #estimated union dues $10 weekly, spread this over weekly check to, so 10 over 5 days for default
    union_dues=Column(Float,default=10/5)

    def __init__(self,**kwargs):
        for k in kwargs.keys():
            if k in [s.name for s in self.__table__.columns]:
                setattr(self,k,kwargs.get(k))
try:

    SafewayNightCrew_version_6003336.metadata.create_all(ENGINE)
except Exception as e:
    print(e)
    SafewayNightCrew_version_6003336.__table__.drop(ENGINE)
    SafewayNightCrew_version_6003336.metadata.create_all(ENGINE)