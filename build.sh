
#vim ./setup.py 
#vim radboy/__init__.py
#vim pyproject.toml 
python replaceLine.py
if ! test -e ./setup.py.back ; then
	cp ./setup.py ./setup.py.back
fi
if ! test -e radboy/__init__.py.back; then 
	cp radboy/__init__.py radboy/__init__.py.back
fi
if ! test -e pyproject.toml.back ; then 
	cp pyproject.toml pyproject.toml.back
fi
mv pyproject.toml.tmp pyproject.toml
mv ./setup.py.tmp ./setup.py
mv radboy/__init__.py.tmp radboy/__init__.py

rm dist/* 
python3 -m build 
twine upload dist/* 

while test 1 -eq 1 ; do
pip install --user --break-system-packages radboy==`cat radboy/__init__.py| grep VERSION | head -n1 | cut -f2 -d"=" | sed s/"'"/''/g`
	if test 0 -eq $?; then
		break
	fi
done
#pip install --user --break-system-packages radboy==`cat setup.py| grep version | head -n1 | cut -f2 -d"=" | sed s/"'"/''/g`
