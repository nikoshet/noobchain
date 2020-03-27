FROM python:3.7.7-slim-stretch

MAINTAINER Noobcash Blockchain

RUN apt-get update && apt-get install gcc -y

#RUN apk update  && apk add --no-cache gcc 

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

#ENTRYPOINT ["python3","noobchain/main.py"]
#CMD python3 noobchain/main_het.py 

ENTRYPOINT ["python3","-u","noobchain/main_het.py","-ip 0.0.0.0 -p 1000 -bootstrap True -ip_bootstrap 0.0.0.0 -port_bootstrap 1000 -nodes 5 -cap 2 -dif 4"]
