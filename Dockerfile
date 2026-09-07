FROM golang:1.27.1-bookworm AS go-toolchain
FROM python:3.12-slim-bookworm AS sap-builder
COPY --from=go-toolchain /usr/local/go /usr/local/go
ENV PATH="/usr/local/go/bin:${PATH}"
WORKDIR /src
COPY tools/sap tools/sap
RUN mkdir -p mdast_cli/distribution_systems/appstore_client/bin \
    && python tools/sap/build.py --target host

FROM python:3.12-slim-bookworm
WORKDIR /mdast_cli
COPY ./ /mdast_cli
COPY --from=sap-builder /src/mdast_cli/distribution_systems/appstore_client/bin/ \
    /mdast_cli/mdast_cli/distribution_systems/appstore_client/bin/
COPY --from=sap-builder /src/mdast_cli/distribution_systems/appstore_client/IPATOOL-LICENSE \
    /mdast_cli/mdast_cli/distribution_systems/appstore_client/IPATOOL-LICENSE
RUN if [ -f /mdast_cli/apkeep_linux ]; then chmod +x /mdast_cli/apkeep_linux; fi
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH="/mdast_cli"
ENTRYPOINT ["python3", "mdast_cli/mdast_scan.py"]
