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

clitest:
	@./madparts.py \
		-f examples/7db0a6816f5a4a5581e92cecab7d7e08.coffee \
		-l /tmp/empty.lbr export

.PHONY: all clean size linux
