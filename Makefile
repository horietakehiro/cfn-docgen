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

test-bdd: develop build-docker-image
	source .env
	sam package \
		--template-file deployments/serverless.yaml \
		--output-template-file deployments/serverless.yaml.packaged \
		--s3-bucket cfn-docgen-artifact-bucket-382098889955-ap-northeast-1 \
		--s3-prefix serverless
	sam deploy \
		--template-file deployments/serverless.yaml.packaged \
        --stack-name cfn-docgen-serverless-bdd \
        --capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset \
		--parameter-overrides ParameterKey=SourceBucketNamePrefix,ParameterValue=cfn-docgen-bdd
	
	behave tests/features/

test-ut:
	pytest -vv src

deploy-serverless:
	sam package \
		--template-file deployments/serverless.yaml \
		--output-template-file deployments/serverless.yaml.packaged \
		--s3-bucket cfn-docgen-artifact-bucket-382098889955-ap-northeast-1 \
		--s3-prefix serverless
	sam deploy \
		--template-file deployments/serverless.yaml.packaged \
        --stack-name cfn-docgen-serverless \
        --capabilities CAPABILITY_IAM

build-docker-image: develop
	docker build -t horietakehiro/cfn-docgen:`python -c "from cfn_docgen import VERSION; print(VERSION)"` ./ -f ./deployments/Dockerfile
deploy-docker-image: build-docker-image
	docker push horietakehiro/cfn-docgen:`python -c "from cfn_docgen import VERSION; print(VERSION)"`

deploy-test-resources:
	sam deploy \
		--template-file ./deployments/test-resources.yaml \
		--stack-name cfn-docgen-test-resources