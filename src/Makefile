# HACK: Vendor my fork of py-trello until https://github.com/sarumont/py-trello/pull/297 is merged
.PHONY: trello
trello:
	rm -Rf trello
	pip install -t . --no-deps --no-compile git+https://github.com/bhrutledge/py-trello.git@develop
	rm -Rf test *.dist-info *.egg-info
	curl https://raw.githubusercontent.com/bhrutledge/py-trello/develop/LICENSE > trello/LICENSE
	@echo "\nIMPORTANT: Copy 'install_requires' from https://github.com/bhrutledge/py-trello/blob/master/setup.py to setup.cfg"
