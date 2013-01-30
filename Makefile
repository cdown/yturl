.PHONY: man clean

man:
	PAGER=cat MANWIDTH=80 man ./yturl.1 > README

clean:
	rm README
