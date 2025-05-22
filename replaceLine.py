from radboy.DB.db import *
from radboy.DB.Prompt import *
from radboy.FB.FBMTXT import *
from radboy.FB.FormBuilder import *

while True:
    version=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"version in x.x.x({VERSION}) format",helpText=f"was {VERSION}",data="string")
    if version in [None,'d']:
        exit(1)
    if len(version.split(".")) == len(VERSION.split(".")):
        break
    else:
        print(f"Invalid Version({version})")

files=['./setup.py','radboy/__init__.py','pyproject.toml']
line_to_replace={}
line_to_replace[0]={'search':'VERSION=','replace':f'VERSION="{version}"\n'}
line_to_replace[1]={'search':'VERSION=','replace':f'VERSION="{version}"\n'}
line_to_replace[2]={'search':'version = ','replace':f'version = "{version}"\n'}

for file in files:
    f=Path(file)
    if f.exists():
        with open(f,"r") as x,open(file+'.tmp',"w") as o:
            for line in x.readlines():
                if line_to_replace[files.index(file)]['search'] in line:
                    if line.startswith("V") or line.startswith("v"):
                        o.write(line_to_replace[files.index(file)]['replace'])
                    else:
                        o.write(line)
                else:
                    o.write(line)

