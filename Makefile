README: yturl.1
	PAGER=cat MANWIDTH=80 man ./$^ > $@

clean:
	rm README
