FROM python:alpine

RUN apk update && apk add git && \
git clone https://github.com/tgbot-collection/TeleTweet && \
pip3 install -r /TeleTweet/requirements.txt

WORKDIR /TeleTweet

CMD python3 teletweet/bot.py

# docker run -d --restart=always -e token="TOKEN" \
  #-e consumer_key="key"  -e consumer_secret="secret" \
  #-e access_key="key" -e access_secret="secret" \
  #-e owner="owner" teletweet
