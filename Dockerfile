FROM python:3.9-slim

WORKDIR /mdast_cli

COPY ./ /mdast_cli

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "./mdast_cli/mdast_scan.py"]