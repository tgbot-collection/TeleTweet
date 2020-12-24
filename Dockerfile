FROM python:alpine

RUN apk update && apk add  --no-cache alpine-sdk tzdata libressl-dev libffi-dev
ADD requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt
COPY . /TeleTweet

ENV TZ=Asia/Shanghai

WORKDIR /TeleTweet/teletweet

CMD ["python", "bot.py"]
