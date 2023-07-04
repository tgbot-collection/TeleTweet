#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - config.py
# 10/22/20 16:20
#

__author__ = "Benny <benny.think@gmail.com>"

import os

BOT_TOKEN = os.getenv("TOKEN", "fghjk789")
APP_ID = os.getenv("APP_ID", "456fgh78")
APP_HASH = os.getenv("APP_HASH", "456gfhj78")

CONSUMER_KEY = os.getenv("CONSUMER_KEY", "456fghj78")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET", "45678fghj")

tweet_format = "https://twitter.com/{screen_name}/status/{id}"
