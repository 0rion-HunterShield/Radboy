vim ./setup.py 
vim radboy/__init__.py
vim pyproject.toml 
rm dist/* 
python3 -m build 
twine upload dist/* 
pip install --user --break-system-packages radboy==`cat setup.py| grep version | head -n1 | cut -f2 -d"=" | sed s/"'"/''/g`
pip install --user --break-system-packages radboy==`cat setup.py| grep version | head -n1 | cut -f2 -d"=" | sed s/"'"/''/g`
