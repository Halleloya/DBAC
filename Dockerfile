FROM python:3.8.5
ENV LEVEL level1
COPY ./ /droit
WORKDIR /droit
RUN pip3 install -r requirements.txt
