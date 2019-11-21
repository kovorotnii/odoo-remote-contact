FROM python:3.7-slim

MAINTAINER Igor Kovorotniy "i.kovorotniy@rightech.io"

RUN useradd -ms /bin/bash odoo-user

WORKDIR /home/odoo-user

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY app app

COPY boot.sh config.py ./

RUN chmod +x boot.sh

RUN chown -R odoo-user:odoo-user ./

EXPOSE 5000