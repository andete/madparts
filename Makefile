all:
	@./madparts.py

size:
	@echo 'python:'
	@wc -l madparts `find . -name '*.py'`
	@echo 'coffee:'
	@wc -l `find grind -name '*.coffee'`
	@echo 'shaders:'
	@wc -l `find . -name '*.vert'` `find . -name '*.frag'`

clean:
	rm -rf build dist

linux:
	python setup.py sdist

.PHONY: all clean size linux
