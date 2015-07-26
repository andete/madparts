PYTHON:=python
NOSE:=nosetests
# for OSX:
# PYTHON:=/opt/local/bin/python2.7
# NOSE:=/opt/local/bin/nosetests-2.7

# set DATA_DIR for unit tests
DATA_DIR := .
export DATA_DIR

all:
	@$(PYTHON) madparts

size:
	@echo 'python:'
	@wc -l `find . -name '*.py'`
	@echo 'coffee:'
	@wc -l `find grind examples -name '*.coffee'`
	@echo 'shaders:'
	@wc -l `find . -name '*.vert'` `find . -name '*.frag'`

clean:
	rm -rf build dist madparts.egg-info

sdist:
	$(PYTHON) setup.py sdist

darwin:
	$(PYTHON) setup.py py2app

apprun:
	./dist/madparts.app/Contents/MacOS/madparts

testinstall:
	rm -rf /tmp/bla
	mkdir -p /tmp/bla
	python setup.py install --root /tmp/bla/ --prefix /usr

test:
	@$(NOSE)

testone:
	@$(NOSE) -s test/madparts_test.py:test_kicad_old_export_polygon

list:
	@$(NOSE) --collect-only -v

coverage:
	@$(NOSE) --with-coverage \
	--cover-package=coffee,export,gui,inter,syntax,util

win32:
	@python27 setup.py py2exe

.PHONY: all clean size sdist test
