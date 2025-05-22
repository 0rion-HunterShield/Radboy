#! /usr/bin/python3
import upcean
import os
import sys,json,base64
import barcode,qrcode
from barcode.writer import ImageWriter
from colored import Fore,Back,Style
from pathlib import Path

class ConvertCode:
    def __init__(self):
        cmds={
                '1':{
                        'cmds':['q','quit','1'],
                        'exec':lambda self=self:exit("user quit!"),
                        'desc':"quit the program",
                    },
                '2':{
                        'cmds':['b','back','2'],
                        'exec':None,
                        'desc':"Go back a menu, if any"
                    },
                '3':{
                        'cmds':['converta2e','ca2e','3','cnvrt_a2e','cnvt_a2e'],
                        'exec':self.convert_a2e,
                        'desc':"convert upca to upce ; if it can't False is displayed.",
                    },
                '4':{
                        'cmds':['converte2a','ce2a','4','cnvrt_e2a','cnvt_e2a'],
                        'exec':self.convert_e2a,
                        'desc':"convert upce to upca ; if it can't False is displayed.",
                    },
            }
        while True:
            for cmd in cmds:
                print(f"{Fore.yellow}{cmds[cmd]['cmds']}{Style.reset} - {Fore.cyan}{cmds[cmd]['desc']}{Style.reset}")
            action=input(f"{Fore.green_yellow}Do What{Style.blink}:{Style.reset}")
            action=action.lower()
            for cmd in cmds:
                if action in cmds[cmd]['cmds']:
                    if cmds[cmd]['exec']!=None:
                        cmds[cmd]['exec']()
                    elif cmds[cmd]['exec']==None:
                        return

    def display(self,code):
        if code == False:
            print(f"{Fore.red}Code could not be converted{Style.reset}: {code}")
        else:
            print(f"{Fore.magenta}{code}{Style.reset}")

    def convert_a2e(self):
        upca=input(f"{Fore.light_sky_blue_1}UPCA{Style.blink}:{Style.reset} ")
        #upce=input(f"{Fore.gold_3a}UPCE{Style.blink}:{Style.reset} ")
        result=upcean.convert.convert_barcode(intype="upca",outtype="upce",upc=upca)
        self.display(result)

    def convert_e2a(self):
        upce=input(f"{Fore.gold_3a}UPCE{Style.blink}:{Style.reset} ")
        result=upcean.convert.convert_barcode(intype="upce",outtype="upca",upc=upce)
        while True:
            save_img=input("save [path/q/b/n]: ")
            if save_img.lower() in ["q",'quit']:
                exit("user quit")
            elif save_img.lower() in ['b','back']:
                return
            elif save_img.lower() in ['n','no','next','skip']:
                break
            else:
                try:
                    p=Path(save_img)
                    pp=Path(str(p)+".png")
                    if pp.exists():
                        ovrWrte=input("Overwrite Existing File!: ")
                        if ovrWrte.lower() in ['y','yes']:
                            code=barcode.UPCA(result,writer=ImageWriter())
                            code.save(p)
                            break
                        else:
                            raise Exception("A File Already Exists! Refusing To Write!")
                    elif p.parent.exists():
                        code=barcode.UPCA(result,writer=ImageWriter())
                        code.save(p)
                        break
                    else:
                        raise Exception("Directory for saving to does not exist!")

                except Exception as e:
                    print(e)

        self.display(result)

if __name__ == "__main__":
    ConvertCode()
