FROM python:alpine

RUN apk update && apk add git --no-cache&& \
git clone https://github.com/tgbot-collection/TeleTweet && \
pip3 install --no-cache-dir -r /TeleTweet/requirements.txt

WORKDIR /TeleTweet/teletweet

CMD python3 bot.py
