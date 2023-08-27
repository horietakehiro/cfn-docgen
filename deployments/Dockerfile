FROM python:3.10.13-slim-bookworm

ENV PYTHONPATH=${PYTHONPATH}:/cfn-docgen:/cfn-docgen/src

RUN mkdir /cfn-docgen
COPY ./ /cfn-docgen/
WORKDIR /cfn-docgen
RUN pip install --no-cache-dir -r requirements.txt
RUN python setup.py install
ENTRYPOINT [ "cfn-docgen" ]