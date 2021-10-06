FROM ubuntu:latest
WORKDIR /app

RUN apt update && apt upgrade -y
RUN apt install python3 python3-pip -y

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .
COPY .env .env

CMD ["python3", "src/bot.py"]
