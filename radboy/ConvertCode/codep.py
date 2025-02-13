import barcode
from barcode.writer import ImageWriter
import os
if __name__ == "__main__":
    while True:
        code=input("code: ")
        if code.lower() in ['q','quit']:
            exit()
        else:
            try:
                barcode.UPCA(code,writer=ImageWriter()).save('code')
                os.system("viewnior code.png")
            except Exception as e:
                print(e)
else:
    raise Exception("Not An Importable Module! Made For Linux only! ; requires viewoir!")
