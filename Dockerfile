FROM python:3.9

WORKDIR /tmp
COPY *.py .
ENTRYPOINT [ "python", "computor.py" ]