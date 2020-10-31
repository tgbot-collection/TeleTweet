#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - config.py
# 10/22/20 16:20
#

__author__ = "Benny <benny.think@gmail.com>"

import os

bot_token = os.environ.get("TOKEN") or ""
consumer_key = os.environ.get("CONSUMER_KEY") or ""
consumer_secret = os.environ.get("CONSUMER_SECRET") or ""

tweet_format = "https://twitter.com/{screen_name}/status/{id}"
