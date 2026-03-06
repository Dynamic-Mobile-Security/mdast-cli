FROM python:3.9-slim

WORKDIR /mdast_cli

COPY ./ /mdast_cli

# Make apkeep_linux executable (if it exists)
RUN if [ -f /mdast_cli/apkeep_linux ]; then chmod +x /mdast_cli/apkeep_linux; fi

RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/mdast_cli"

ENTRYPOINT ["python3", "mdast_cli/mdast_scan.py"]