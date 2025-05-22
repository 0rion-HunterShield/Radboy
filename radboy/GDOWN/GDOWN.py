from . import *
from radboy.DB.db import ENGINE
import gdown
import tarfile

class RestoreFromGDrive:
	def __init__(self):
		output_file="./radboy-backup.tgz"
		url=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Link to File For Download({Fore.light_red}Make sure the {Fore.light_steel_blue}File is Accessible to Anyone with a Link{Fore.light_yellow})",helpText="a public google drive link",data="string")
		if url in [None,]:
			print("User Cancelled!")
			return
		try:
			gdown.download(url=url,output=output_file,fuzzy=True)
			output_file=Path(output_file)
			if output_file.exists():
				with tarfile.open(output_file) as tf:
					tf.extractall()
					exit(f"{Fore.light_yellow}You now need to restart! {Fore.light_green}Quitting Now!{Style.reset}")
		except Exception as e:
			print(e)