all:
	@python madparts.py

size:
	@echo 'python:'
	@wc -l `find . -name '*.py'`
	@echo 'coffee:'
	@wc -l `find . -name '*.coffee'`

.PHONY: all
