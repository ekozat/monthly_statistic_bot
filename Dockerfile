FROM python:3.8

WORKDIR /app

COPY . .
RUN pip3 install -r requirements.txt

#CMD ["/bin/bash"]
ENTRYPOINT ["python", "api.py"]

#CMD ["-e", "URLSLACK=urlSlack", "-e", "xAuthKey=xAuthKey", "-e", "xAuthEmail=xAuthEmail"]
#secrets/vault implementation

