FROM python:alpine as builder

RUN apk update && apk add  --no-cache  alpine-sdk tzdata libressl-dev libffi-dev cargo
ADD requirements.txt /tmp/
RUN pip3 install --user -r /tmp/requirements.txt && rm /tmp/requirements.txt



FROM python:alpine

COPY --from=builder /root/.local /usr/local
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo
COPY . /TeleTweet
RUN apk update && apk add --no-cache libressl && cd /TeleTweet && rm -rf assets .git

ENV TZ=Asia/Shanghai
WORKDIR /TeleTweet/teletweet
CMD ["python", "bot.py"]
