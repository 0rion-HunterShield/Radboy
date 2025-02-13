from barcode import Code128,UPCA,Code39,EAN13
from barcode.writer import ImageWriter
from pathlib import Path
import tkinter as tk
import cv2
from pyzbar import pyzbar as zbar
import pyqrcode
import pyperclip
from colored import Fore,Back,Style
import random,upcean
from tkinter import ttk
from tkinter import scrolledtext
from copy import deepcopy
from PIL import Image,ImageTk,ImageOps
import string
imgfile=Path("code.png")
imgfile_nsfx=str(imgfile).replace(imgfile.suffix,"")
root=tk.Tk()
#entry=tk.Text(root,height=10,width=70)
entry=scrolledtext.ScrolledText(root,wrap=tk.WORD,width=40,height=10,font=("FreeMono",12))
entry.pack()
root.title("renderQR_TK1")
mode=tk.StringVar()
modeW=ttk.Combobox(root,width=30,textvariable=mode)
modeW['values']=(
    'QR',
    'UPCA',
    'Code39',
    'Code128',
    'EAN13',
        )
modeW.current(0)
try:
    f=str(imgfile)
    im=cv2.imread(f)
    cstr=zbar.decode(im)
    print(cstr)
    for code in cstr:
        entry.delete("0.0",tk.END)
        entry.insert("0.0",code.data.decode("utf-8"))
        print(code)

    root.img=ImageTk.PhotoImage(ImageOps.contain(Image.open(f),(400,400)))
    img_label=tk.Label(root,image=root.img)
    img_label.pack()

except Exception as e:
    print(e)

image_file_label=tk.Entry(root)
image_file_label.insert("0",str(imgfile.absolute()))
image_file_label.pack()
image_file_label.configure(state="readonly")
modeW.pack()
warning=tk.Label(root,text='')
warning.pack()
def stripDigits(code):
    code=code
    #remove anything not a digit in 0-9
    for char in string.ascii_letters+string.punctuation+string.whitespace:
        if char in code:
            code=code.replace(char,"")
    return code

def renderFunc(self=None):
    try:
        code=''

        for line in entry.dump("0.0",tk.END,text=True):
            print(line)
            code+=line[1]
        tmp=''
        for char in code:
            if char in string.printable:
                tmp+=char
        code=tmp
        print(code,"entry text")
        if mode.get() == "Code128":
            r=Code128(code,writer=ImageWriter())
            f=r.save(imgfile_nsfx)
            warning.configure(text=f"Code128({code:1.26s})")
        elif mode.get() == "Code39":
            r=Code39(stripDigits(code),writer=ImageWriter(),add_checksum=False)
            f=r.save(imgfile_nsfx)
            warning.configure(text=f"Code39({code:1.26s})")
        elif mode.get() == "EAN13":
            r=EAN13(stripDigits(code),writer=ImageWriter())
            f=r.save(imgfile_nsfx)
            warning.configure(text=f"EAN13({code:1.26s})")

        elif mode.get() == "UPCA":
            try:
                code=stripDigits(code)
                if len(code) <= 8:

                    upce=deepcopy(code)

                    print("code length 8 detected, attempting to convert to upca")
                    c2=upcean.convert.convert_barcode(intype="upce",outtype="upca",upc=code)
                    print(f"{c2} -> {code:1.26s}")
                    if c2 != False:
                        code=c2
                        warning.configure(text=f"UPCE({upce:1.26s}) -> UPCA({code:1.26s})")
                    else:
                        print("print conversion failed!")
                else:
                    warning.configure(text="UPCA")
                    warning.configure(text=f"UPCA({code:1.26s})")

                r=UPCA(code,writer=ImageWriter())
                f=r.save(imgfile_nsfx)
            except Exception as e:
                print(e)
                warning.configure(text=f"Code128({code:1.26s})")
                r=Code128(code,writer=ImageWriter())
                f=r.save(imgfile_nsfx)

        elif mode.get() == "QR":
            warning.configure(text=f"QR({code:1.26s})")
            r=pyqrcode.create(code)
            print(r,"entry qrcode")
            r.png(imgfile,scale=4)
        #im=cv2.imread(str(imgfile))
        #canvas.configure(height=im.shape[0])
        #canvas.configure(width=im.shape[1])
        f=str(imgfile)
        img=Image.open(f)
        img=ImageOps.contain(img,(400,400))
        print(f,Path(f).exists())
        root.img=ImageTk.PhotoImage(img)
        img_label.configure(image=root.img)
    except Exception as e:
        print(e)
root.bind("<End>",renderFunc)
root.bind("<Delete>",lambda x: exit("user quit!"))
#quitbtn=tk.Button(root,text="Quit",command=lambda:exit("user quit!"))
#quitbtn.pack()

render=tk.Button(root,text="Render",command=renderFunc)
render.pack()
def clearEntry(self=None):
    entry.delete("0.0",tk.END)

def fromClipBoard(self):
    clearEntry()
    entry.insert("0.0",pyperclip.paste())
    renderFunc()

def mhelp(self):
    with open("renderQR.py.README","r") as helpfile:
        for num,line in enumerate(helpfile.readlines()):
            red=random.randint(0,256)
            green=random.randint(0,256)
            blue=random.randint(0,256)
            colr=Fore.rgb(red,green,blue)
            print(f"{num}: {colr}{line}{Style.reset}",end="")

root.bind("<Page_Down>",mhelp)
root.bind("<Home>",clearEntry)
root.bind("<Page_Up>",fromClipBoard)
mhelp(None)
root.mainloop()
