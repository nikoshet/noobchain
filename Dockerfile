#FROM frolvlad/alpine-python3:latest
FROM python:3.7.7-slim-stretch
#FROM python:3.7.7-stretch

MAINTAINER Noobcash Blockchain

RUN apt-get update && apt-get install gcc -y

#RUN apk update  && apk add --no-cache gcc 
#-y && \
    #apk install -y python-pip python-dev
  #apk add --no-cache gcc 

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

#ENTRYPOINT ["python3","noobchain/rest.py"]

#CMD python3 noobchain/main.py

CMD python3 noobchain/main.py 0.0.0.0 1000 TRUE 0.0.0.0 1000 3 5 2
