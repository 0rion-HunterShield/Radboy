#! /usr/bin/env bash
Personal\ Access\ Token.py at2cb
git config --global credential.helper store
git add .
#msg=`python -c "m=input('message: '); print(m,end=\" \");"`
msg="updates as of `date`"
git commit -am "$msg"
git push --set-upstream origin main
#git push
