all:
	@./madparts.py

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
	@nosetests
	#@nosetests test/madparts_test.py:test_eagle_import_one

.PHONY: all clean size sdist test
