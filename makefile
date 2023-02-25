testpath='tests'

b:
	rm -rf dist; \
	rm -rf src/*.egg-info; \
	python3 -m build
bp:
	rm -rf dist; \
	rm -rf src/*.egg-info; \
	python3 -m build; \
	twine upload dist/* $(options)
install:
	pip install -r requirements.txt
install-prod:
	pip install -r prod-requirements.txt
n:
	jupyter notebook
p:
	twine upload dist/* $(options)
t:
	black ./
	flake8 ./
	pytest --capture=no --verbose $(testpath)