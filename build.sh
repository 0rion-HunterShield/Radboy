vim ./setup.py
rm dist/*
python setup.py sdist
twine upload dist/* 
pip install --user --break-system-packages radboy==`cat setup.py| grep version | head -n1 | cut -f2 -d"=" | sed s/"'"/''/g`
pip install --user --break-system-packages radboy==`cat setup.py| grep version | head -n1 | cut -f2 -d"=" | sed s/"'"/''/g`
