REGION = us-east-1

.PHONY: clean deploy

venv: venv/bin/activate
venv/bin/activate: dev-requirements.txt
	test -d venv || python3 -m venv venv
	venv/bin/pip3 install -U pip
	venv/bin/pip3 install -Ur dev-requirements.txt
	touch venv/bin/activate

clean: cleandist
	rm -rf venv

cleandist:
	rm -rf build

dist: clean build/deploy.zip

build/deploy.zip: imtf.py
	mkdir -p build/
	zip -r build/deploy.zip . \
		-x "*.DS_Store*" \
		"build" \
		"*requirements.txt" \
		".gitignore" \
		"Makefile" \
		"build*" \
		"setup.cfg" \
		"venv*"
	python3 -m venv build/venv
	source build/venv/bin/activate; \
	pip3 install -r requirements.txt; \
	cp -r $$VIRTUAL_ENV/lib/python3.7/site-packages/ build/site-packages
	cd build/site-packages; zip -g -r ../deploy.zip . -x "*__pycache__*"


deploy: dist
	aws lambda update-function-code \
		--region $(REGION) \
		--function-name ismytrainfucked_update_site \
		--zip-file fileb://build/deploy.zip \
		--publish
