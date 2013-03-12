PYTHON:=/opt/local/bin/python2.7

all:
	@./madparts.py

size:
	@echo 'python:'
	@wc -l `find . -name '*.py'`
	@echo 'coffee:'
	@wc -l `find grind -name '*.coffee'`
	@echo 'shaders:'
	@wc -l `find . -name '*.vert'` `find . -name '*.frag'`

clean:
	rm -rf build dist madparts.egg-info

linux:
	$(PYTHON) setup.py sdist

darwin:
	$(PYTHON) setup.py py2app

apprun::
	./dist/madparts.app/Contents/MacOS/madparts


.PHONY: all clean size linux
