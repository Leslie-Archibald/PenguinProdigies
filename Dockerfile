# install mongodb: https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/
FROM python:latest

ENV HOME /root
WORKDIR /root

#Install Flask
RUN pip install -r requirements.txt

#Run Mongodb
RUN systemctl start mongod

#We are using port 8080
EXPOSE 8080

#Copy the files
COPY server.py CSE312/
COPY pyvenv.cfg CSE312/
COPY public CSE312/public
COPY Lib CSE312/Lib/
COPY Scripts CSE312/Scripts

#Run the server!
CMD python3 CSE312/server.py
