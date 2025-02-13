from PIL import Image,ImageDraw,ImageFont,ImageOps
from datetime import datetime
from pathlib import Path




class renderImageFromText:
    def setWidthFromLongestLine(self,text):
        lines=text.split("\n")
        old=0
        for line in lines:
            if len(line) > old:
                old=len(line)
        return int(old*(self.fontsize*1.0))

    def setHeightFromLines(self,text):
        #set self.size
        lines=text.split("\n")
        print(len(lines))
        f=(self.fontsize*1.75)
        ff=f*len(lines)
        return int(ff)


    def __init__(self,filename,text,barcode_file=None,code_file=None,img_file=None):
        self.barcode_file=barcode_file
        self.barcode_file_name=barcode_file
        self.code_file=code_file
        self.code_file_name=code_file
        self.img_file_name=img_file
        self.fontsize=16
        self.width=self.setWidthFromLongestLine(text) 
        self.widthOrig=self.width
        self.height=self.setHeightFromLines(text)
        self.heightOrig=self.height
        self.size=(self.width,self.height)
        self.widthBarcodeImg=0

        if self.barcode_file not in [True,False,None]:
            try:
                self.barcode_file=Image.open(self.barcode_file)
                self.width=self.barcode_file.size[0]+self.width
                print(self.width)
                if self.barcode_file.size[1] > self.height:
                    self.height=self.barcode_file.size[1]
                self.size=(self.width,self.height)
            except Exception as e:
                print(e,f"unable to open barcode_file '{barcode_file}'")
        if self.code_file not in [True,False,None]:
            try:
                self.code_file=Image.open(self.code_file)
                self.width=self.code_file.size[0]+self.width
                print(self.width)
                if self.code_file.size[1] > self.height:
                    self.height=self.code_file.size[1]
                self.size=(self.width,self.height)
            except Exception as e:
                print(e,f"unable to open code_file '{code_file}'")

        self.img_file=img_file
        print(self.img_file,"img_file")
        try:
            x=Path(self.img_file)
            print(x,"img_file_1",x.exists(),x.is_file())
            ex=x.exists()
            if not ex:
                self.img_file=None
            else:
                if not x.is_file():
                    self.img_file=None
        except Exception as e:
            self.img_file=None
            
        if self.img_file not in [True,False,None]:

            try:
                self.img_file=Image.open(self.img_file)
                self.img_file=ImageOps.contain(self.img_file.copy(),(300,300))
                #self.img_file=self.img_file.resize((200,200))
                self.width=self.img_file.size[0]+self.width
                print(self.width)
                if self.img_file.size[1] > self.height:
                    self.height=self.img_file.size[1]
                self.size=(self.width,self.height)
            except Exception as e:
                print(e,f"unable to open img_file '{self.img_file}'")


        self.dt=datetime.strftime(datetime.now(),"%m%d%Y")
        self.filename=filename
        self.white=(255,255,255)
        self.black=(0,0,0)
        self.padded=(20,20)
        
        self.text=text
        self.font_name=Path(__file__).parent.parent/Path("Default.TTF")

        self.font=ImageFont.truetype(str(self.font_name),16)
        self.image=Image.new("RGB",self.size,self.white)
        self.draw=ImageDraw.Draw(self.image)
        
        print(self.font_name)
        
        '''
        try:
            raise Exception("e")
            self.font=ImageFont.load_default(size=16)
            print()
        except Exception as e:
            try:
                self.font=ImageFont.truetype("/system/fonts/DroidSansMono.ttf",16)
            except Exception as e:
                print(e)
                self.font=ImageFont.load_default() 
        '''
        self.save()

    def save(self):
        try:
            self.draw.text(self.padded,self.text,self.black,font=self.font)
            if self.barcode_file not in [True,False,None]:
                w=self.width-self.barcode_file.size[0]
                self.image.paste(self.barcode_file.copy(),(w,0))
                Path(self.barcode_file_name).unlink()
            if self.code_file not in [True,False,None]:
                w=self.width-self.code_file.size[0]
                if self.barcode_file not in [True,False,None]:
                    w=w-self.barcode_file.size[0]
                self.image.paste(self.code_file.copy(),(w,0))
                Path(self.code_file_name).unlink()
            if self.img_file not in [True,False,None]:
                w=self.width-int(self.img_file.size[0])
                if self.code_file not in [True,False,None]:
                    w=w-self.code_file.size[0]
                if self.barcode_file not in [True,False,None]:
                    w=w-self.barcode_file.size[0]

                self.image.paste(self.img_file.copy(),(w,0))
                #Path(self.img_file_name).unlink()
            fname=f"{self.filename}_{self.dt}.jpg"
            print(fname)
            self.image.save(fname)

        except Exception as e:
            exit(e)
            print(e,repr(e),str(e))

if __name__ == "__main__":
    t='''image = Image.new("RGBA", (288,432), (255,255,255))
usr_font = ImageFont.truetype("resources/HelveticaNeueLight.ttf", 25)
d_usr = ImageDraw.Draw(image)
d_usr = d_usr.text((105,280), "Travis L.",(0,0,0), font=usr_font)'''
    renderImageFromText("test",t)

