.PHONY: build publish localbuild
build:
	. .venv/bin/activate
	pip install -r requirements.txt
	python setup.py sdist bdist_wheel 


publish:
	aws codeartifact login --tool twine --repository horie-t --domain ht-burdock --domain-owner 382098889955
	twine upload --repository codeartifact dist/*

localbuild:
	./codebuild_build.sh -i public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:3.0 -a ./out -e .env -c