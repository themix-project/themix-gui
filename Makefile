SASS=sass
SCSS_DIR=gtk-3.0/scss
DIST_DIR=gtk-3.0/dist

css:
	$(SASS) --sourcemap=none --update $(SCSS_DIR):$(DIST_DIR)

all: css

clean:
	rm -rf $(DIST_DIR)

.PHONY: css
# vim: set ts=4 sw=4 tw=0 noet :
