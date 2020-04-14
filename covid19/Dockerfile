FROM python:3.7-slim-buster
ADD . /covid19
WORKDIR /covid19
RUN apt-get update && apt-get install -y \
    librdkafka-dev openssl libssl-dev ssl-cert \
    iputils-ping python-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "covid_capture.py", "&"]
