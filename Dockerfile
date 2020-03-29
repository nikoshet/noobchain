FROM python:3.7.7-slim-stretch
#FROM python:3.7.7-stretch

MAINTAINER Noobcash Blockchain

# Environment Variables
ENV IP                   0.0.0.0
ENV PORT                 1000
ENV BOOTSTRAP            True
ENV IP_BOOTSTRAP	 0.0.0.0 
ENV PORT_BOOTSTRAP	 1000
ENV NODES		 5
ENV CAPACITY		 2
ENV DIFFICuLTY		 4

# Copy files
COPY ./requirements.txt /app/requirements.txt
COPY . /app

# Set working directory
WORKDIR /app

RUN apt-get update && apt-get install gcc -y && \
	pip install -r requirements.txt

# Final command
#ENTRYPOINT ["python3","-u","noobchain/main_het.py","-ip ${IP} -p ${PORT} -bootstrap ${BOOTSTRAP} -ip_bootstrap ${IP_BOOTSTRAP} -port_bootstrap ${PORT_BOOTSTRAP} -nodes ${NODES} -cap ${CAPACITY} -dif ${DIFFICuLTY}"]

#ENTRYPOINT ["python3","-u","noobchain/main_het.py"]
