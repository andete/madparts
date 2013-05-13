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

test:
	@#nosetests
	@nosetests test/madparts_test.py:test_eagle_export_empty

coverage:
	@nosetests --with-coverage \
	--cover-package=coffee,export,gui,inter,syntax,util

.PHONY: all clean size sdist test
