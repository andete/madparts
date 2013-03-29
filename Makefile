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

linux:
	python setup.py sdist

.PHONY: all clean size linux
