#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - config.py
# 10/22/20 16:20
#

__author__ = "Benny <benny.think@gmail.com>"

import os

BOT_TOKEN = os.environ.get("TOKEN") or "37"
CONSUMER_KEY = os.environ.get("CONSUMER_KEY") or "2222222"
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET") or "111111111"
tweet_format = "https://twitter.com/{screen_name}/status/{id}"
reply_json = r'{"message_id":1,"from":{"id":108929734,"first_name":"Frank","last_name":"Wang","username":"eternnoir","is_bot":true},"chat":{"id":1734,"first_name":"F","type":"private","last_name":"Wa","username":"oir"},"date":1435296025,"text":"%s"}'
