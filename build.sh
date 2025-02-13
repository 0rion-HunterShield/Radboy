rm dist/*
python setup.py sdist
twine upload -u __token__ -p "pypi-AgEIcHlwaS5vcmcCJGQ2ZjcyZjM4LTE1ZTItNGVjMy1hNzdhLTlkMDkwY2YwZWMwNQACKlszLCIwOWJiODFhYy1jZDVjLTQ5OGQtYTc5Yi01NWI5NjRmYmIyZjQiXQAABiA3JmZ7UfYPVANs0jnjBsVSYUqEuvEwnpP7ms_Cdxxctw" dist/* 
pip install radboy==`cat setup.py| grep version | head -n1 | cut -f2 -d"=" | sed s/"'"/''/g`
pip install radboy==`cat setup.py| grep version | head -n1 | cut -f2 -d"=" | sed s/"'"/''/g`
