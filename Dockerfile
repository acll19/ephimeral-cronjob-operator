FROM python:3.10.12
RUN pip install kopf
RUN pip install kubernetes
RUN pip install croniter
ADD . /src
CMD kopf run /src/ephimeralcronjob.py --verbose