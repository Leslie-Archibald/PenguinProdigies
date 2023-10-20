FROM python:3.8
RUN apt-get update

# set home directory to /root
ENV HOME /root 

#cd directory
WORKDIR /root 
#Copy the files
COPY . .

#Install Flask
RUN pip3 install -r requirements.txt

# install extra software (not needed for the homework)

# copy all files into image
COPY . .


# download dependencies
RUN pip3 install -r requirements.txt


# allow port to be accessed
EXPOSE 8080

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait 
RUN chmod +x /wait

#Run the server!
CMD /wait && python3 -u server.py
