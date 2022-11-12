FROM python:3.8.15-slim-bullseye

ENV CFN_DOCGEN_AWS_REGION  ap-northeast-1
RUN pip install --no-cache-dir cfn-docgen

ENTRYPOINT [ "cfn-docgen" ]