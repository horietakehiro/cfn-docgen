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

deploy-cicd:
	sam deploy \
		--template-file deployments/cicd.yaml \
		--stack-name cfn-docgen-cicd \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
			ParameterKey=ApiTokenParamName,ParameterValue=/pypi/api-token \
			ParameterKey=GithubTokenParamName,ParameterValue=/GitHub/MyToken \
			ParameterKey=DockerHubPasswordParamName,ParameterValue=/DockerHub/Password \
			ParameterKey=ServerlessTestBucketName,ParameterValue=cfn-docgen-bdd-382098889955-ap-northeast-1 \
			ParameterKey=GitHubConnectionArn,ParameterValue=arn:aws:codestar-connections:ap-northeast-1:382098889955:connection/6f899bca-b98f-4fe3-ab68-ce57f8d600e4


build-docker-image: develop
	docker build -t horietakehiro/cfn-docgen:`python -c "from cfn_docgen import __version__; print(__version__)"` ./ -f ./deployments/Dockerfile
deploy-docker-image: build-docker-image
	docker push horietakehiro/cfn-docgen:`python -c "from cfn_docgen import __version__; print(__version__)"`

deploy-test-resources:
	sam deploy \
		--template-file ./deployments/test-resources.yaml \
		--stack-name cfn-docgen-test-resources

deploy-local-build:
	./deployments/codebuild_build.sh \
		-i aws/codebuild/standard:6.0 \
		-b deployments/buildspec.yaml \
		-s ./ -a ./artifacts \
		-e .codebuild_local.env \
		-c 

synth-cdk:
	cdk synth -o cdk.out
	cfn-docgen docgen -s cdk.out -d cdk.doc