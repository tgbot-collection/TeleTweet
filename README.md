# TwitterBot
🦉 A telegram Twitter bot that will allow you to send tweets!

# Commands
```
about - What is this bot
start - Start using it today!
timeline - Get newest timeline!
new - Get your tweets
like - Get your likes
help - Help
```
# Features
* send text tweet
* send tweet with one photo(photo and document are supported.)

# General deployment
```shell script
git clone https://github.com/tgbot-collection/TeleTweet/
cd TeleTweet
pip3 install -r requirements.txt
export token="TOKEN" \
-e consumer_key="key"  -e consumer_secret="secret" \
-e access_key="key" -e access_secret="secret" \
-e owner="owner"
python3 teletweet/bot.py
```

# Docker
```shell script
docker run -d --restart=always -e token="TOKEN" \
-e consumer_key="key"  -e consumer_secret="secret" \
-e access_key="key" -e access_secret="secret" \
-e owner="owner" bennythink/teletweet
```

# Plans
- [ ] support multi-user
- [ ] help
- [ ] about
- [ ] start
- [ ] timeline
- [ ] new
- [ ] like

# License
GPL 2.0