SHELL = /bin/bash
.PHONY: deploy-test-resources build develop

develop:
	. .venv/bin/activate
	python setup.py develop
	cfn-docgen --version

build:
	. .venv/bin/activate
	pip install -r requirements-dev.txt
	pip install -r requirements.txt
	python setup.py sdist bdist_wheel 

test-bdd:
	export TEST_BUCKET_NAME=cfn-docgen-test-bucket-382098889955-ap-northeast-1 && \
	cd tests && behave

deploy-cicd:
	

deploy-test-resources:
	sam deploy \
		--template-file ./deployments/test-resources.yaml \
		--stack-name cfn-docgen-test-resources