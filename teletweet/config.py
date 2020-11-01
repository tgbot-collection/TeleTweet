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
