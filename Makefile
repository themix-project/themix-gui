SASS=sass

css: 
	$(SASS) --update gtk-3.0/scss:gtk-3.0/gen

all: css

    
.PHONY: css
# vim: set ts=4 sw=4 tw=0 noet :
