FROM python:latest

ENV HOME /root
WORKDIR /root

#Copy the files
COPY . .

#Install Flask
RUN pip3 install -r requirements.txt

#We are using port 8080
EXPOSE 8080

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait 
RUN chmod +x /wait

#Run the server!
CMD /wait && python3 -u server.py