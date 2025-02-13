import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import json
from radboy.DB.db import *


root=tk.Tk()
#root.geometry("500x600")



scanner_frame=tk.Frame(root)
scanner_entry=tk.Entry(scanner_frame)
scanner_entry.grid(column=0,row=0)

results_frame=tk.Frame(root)
results_label=tk.Text(results_frame,width=550)

results_scrollbar=tk.Scrollbar(results_frame,orient='vertical')
results_scrollbar.pack(fill=tk.Y,side='right')
results_scrollbar.config(command=results_label.yview)

results_label.configure(yscrollcommand=results_scrollbar.set)



results_label.pack(fill=tk.BOTH)
results_frame.pack(fill=tk.BOTH)
results_option=tk.Entry(root,text='0')
results_option.pack(fill=tk.BOTH)
results_options=tk.Label(root,text='0/0')
results_options.pack(fill=tk.X)
def search():
	results_label.delete("1.0",tk.END)
	with Session(ENGINE) as session:
		query=session.query(Entry).filter(or_(Entry.Barcode==scanner_entry.get(),Entry.Code==scanner_entry.get()))
		results=query.all()
		if len(results) < 1:
			print("No Results!")
		elif len(results) >= 1:
			
				selection=results_option.get()
				if selection == '':
					selection=0
				else:
					selection=int(selection)
				
				select=results[selection]
				results_options.configure(text=f'{selection}/{len(results)-1}')
				for num,column in enumerate(Entry.__table__.columns):
					text=''
					value=select.__dict__[column.name]
					text+=f"{column.name}={value}\n"
					results_label.insert(tk.END,text)
			
				


scanner_submit=tk.Button(scanner_frame,text="Submit",command=search)
scanner_submit.grid(column=1,row=0)






scanner_frame.pack(fill=tk.BOTH)
root.mainloop()
