.PHONY: test bundle clean

test:
	python3 -m unittest discover -s tests -v

bundle:
	mkdir -p dist
	rm -f dist/freenet-headless-deploy.zip
	zip -r dist/freenet-headless-deploy.zip README.md LICENSE CONTRIBUTING.md CODE_OF_CONDUCT.md SKILL.md scripts/ tests/ Makefile -x "*/__pycache__/*" "*.pyc" "*.pyo" "*/.DS_Store" ".DS_Store"

clean:
	rm -rf dist freenet_staging __pycache__ tests/__pycache__ scripts/__pycache__
