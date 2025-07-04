from setuptools import setup,find_packages
from datetime import datetime
from pathlib import Path
VERSION="0.0.445"
long_description=Path('README.md')
if long_description.exists():
  long_description=long_description.open("r").read()
else:
  long_description=''
name='radboy'
setup(name=name,
      long_description=long_description,
      long_description_content_type='text/markdown',
      version=VERSION,
      author="Carl Joseph Hirner III",
      author_email="k.j.hirner.wisdom@gmail.com",
      description="A Command-Line Style Scanner designed to be used on cellular devices as a list maker, note taker, look up system, and custom calculator.",
      classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Operating System :: Android',
        'Environment :: Console',
        'Programming Language :: SQL',
          ],
      packages=find_packages(),
      python_requires='>=3.6',
      install_requires=['gdown','biip','sympy','scipy','plotext','haversine','holidays','odfpy','qrcode[pil]','chardet','nanoid','random-password-generator','cython','pint','pyupc-ean','openpyxl','plyer','colored','numpy','pandas','Pillow','python-barcode','qrcode','requests','sqlalchemy','argparse','geocoder','beautifulsoup4','pycryptodome','forecast_weather','boozelib','inputimeout'],
      extras_require={'Terminal Readline Support':["readline"]},
      package_data={
        '':["*.config","*.txt","*.README","*.TTF",],
        }
      )
with open(f"{name}/__init__.py","w") as c:
    c.write(f"VERSION='{VERSION}'")
