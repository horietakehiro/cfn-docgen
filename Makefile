.PHONY: build publish localbuild
build:
	. .venv/bin/activate
	pip install -r requirements.txt
	python setup.py sdist bdist_wheel 


publish: build
	twine upload --repository pypi dist/*

localbuild:
	./codebuild_build.sh -i public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:3.0 -a ./out -e .env -c