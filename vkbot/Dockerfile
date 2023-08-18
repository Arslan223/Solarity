FROM python:3.9

RUN mkdir /base
WORKDIR /base

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT python3 -m src.vk_bot
