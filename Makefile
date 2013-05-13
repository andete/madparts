# set DATA_DIR for unit tests
DATA_DIR := .
export DATA_DIR

all:
	@./madparts

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
	python setup.py sdist

testinstall:
	rm -rf /tmp/bla
	mkdir -p /tmp/bla
	python setup.py install --root /tmp/bla/ --prefix /usr

test:
	@nosetests

testone:
	@nosetests test/madparts_test.py:test_eagle_export_empty

coverage:
	@nosetests --with-coverage \
	--cover-package=coffee,export,gui,inter,syntax,util

.PHONY: all clean size sdist test
