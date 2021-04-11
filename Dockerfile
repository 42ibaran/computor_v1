FROM python:3.9-slim

WORKDIR /tmp
COPY *.py .
ENTRYPOINT [ "python", "computor.py" ]