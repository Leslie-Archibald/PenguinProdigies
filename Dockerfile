FROM python:3.8
RUN apt-get update

# set home directory to /root
ENV HOME /root 

#cd directory
WORKDIR /root 

# install extra software (not needed for the homework)

# copy all files into image
COPY . .


# download dependencies
RUN pip3 install -r requirements.txt


# allow port to be accessed
EXPOSE 8080

# run the app 
CMD python3 -u server.py