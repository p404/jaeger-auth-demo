FROM python:3.8.5
ADD requirements.txt /requirements.txt
WORKDIR /
RUN apt-get update
RUN apt-get install python3-psycopg2 -y
RUN pip3 install psycopg2
RUN pip3 install -r requirements.txt
COPY . /
CMD [ "python3", "main.py" ]
