FROM frolvlad/alpine-python3

WORKDIR /mdast_cli

COPY ./ /mdast_cli

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "./mdast_cli/mdast_scan.py"]