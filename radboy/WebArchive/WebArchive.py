from . import *

import requests

wa_filepath=detectGetOrSet("WebArchiveDownloadsFilePath","WebArchiveDownloads",literal=True)
class WebArchiveStore(BASE,Template):
	'''Store web data from url in filename at filepath on dtoe with user provided name,description,notes,comment where default filepath="WebArchiveDownloads".

	default filepath can be changed and stored in SystemPreference
	'''
	__tablename__="WebArchiveStore"
	filepath=Column(String,default=wa_filepath)
	filename=Column(String,default=None)
	waid=Column(Integer,primary_key=True)
	src_url=Column(String,default=None)
	checksum=Column(String,default=None)
	dtoe=Column(DateTime,default=datetime.now())
	name=Column(String)
	description=Column(String)
	notes=Column(String)
	comment=Column(String)

	def __init__(self,**kwargs):
		for k in kwargs.keys():
			if k in [s.name for s in self.__table__.columns]:
				setattr(self,k,kwargs.get(k))


wa_filepath=Path(wa_filepath)
if not wa_filepath.exists():
	wa_filepath.mkdir()
print(f"{Fore.light_green}{wa_filepath}.exist()->{wa_filepath.exists()}")

WebArchiveStore.metadata.create_all(ENGINE)

class WebArchiver:
	def __init__(self):
		pass


	def downloadWebFile(self):
		was=WebArchiveStore()
		excludes=["waid","dtoe","checksum","filepath","filename"]
		fields=[i for i in was.columns if i.name not in excludes]
		fields_str=[str(i.name) for i in fields]

		'''
		from google gemini
		try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        with open(local_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded {url} to {local_filename}")
	    except requests.exceptions.RequestException as e:
	         print(f"Error downloading {url}: {e}")


		'''