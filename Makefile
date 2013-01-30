# This isn't actually needed to install the program, it contains developer
# actions.

.PHONY: man clean lint

man:
	PAGER=cat MANWIDTH=80 man ./yturl.1 > README

lint:
	pylint yturl

clean:
	rm README
