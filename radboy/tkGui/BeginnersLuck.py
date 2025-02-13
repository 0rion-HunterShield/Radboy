import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk

root=tk.Tk()
try:
        display_width=root.winfo_screenwidth()
        display_height=root.winfo_screenheight()
except:
        display_width=600
        display_height=800
div=1
root.geometry(f"{int(display_width/div)}x{int(display_height/div)}")
print(f"display set to {display_width}x{display_height}!")

master_frame=Frame(root)
master_frame.pack(fill=BOTH,expand=1)

master_canvas=Canvas(master_frame)
master_canvas.pack(side=LEFT,fill=BOTH,expand=1)

master_scrollbar=Scrollbar(master_frame,orient=VERTICAL,command=master_canvas.yview)
master_scrollbar.pack(side=RIGHT,fill=Y)
master_canvas.configure(yscrollcommand=master_scrollbar.set)
master_canvas.bind(
        '<Configure>',
        lambda e:master_canvas.configure(scrollregion=master_canvas.bbox("all"))
        )



child0_frame=Frame(master_canvas,width=display_width-50,height=display_height-50)
#widgets go after here


#tabWidget
tabControl=ttk.Notebook(child0_frame)
tab1=ttk.Frame(tabControl)
tab2=ttk.Frame(tabControl)

#exit app
btn_exit=Button(tab1,text="Exit",command=lambda: exit("user quit!"))
btn_exit.grid(column=0,row=0)



tabControl.add(tab1,text="Ctrl")
tabControl.add(tab2,text="Tab2")
tabControl.grid(column=0,row=1)



#stop widgets
master_canvas.create_window((0,0),window=child0_frame,anchor="nw")
root.mainloop()
