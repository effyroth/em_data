FROM python:3.9


RUN apt update && apt install -y git psmisc zip gcc g++
RUN mkdir -p /investment_data


RUN  pip install numpy==1.23.5 && pip install --upgrade cython \
   && cd / && git clone https://github.com/effyroth/em_data.git \
   && cd /em_data/ && pip install -r requirements.txt 
   
COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

WORKDIR /em_data/
