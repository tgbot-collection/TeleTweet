#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - config.py
# 10/22/20 16:20
#

__author__ = "Benny <benny.think@gmail.com>"

import os

bot_token = os.environ.get("token") or ""
consumer_key = os.environ.get("consumer_key") or ""
consumer_secret = os.environ.get("consumer_secret") or ""
access_token_key = os.environ.get("access_key") or ""
access_token_secret = os.environ.get("access_secret") or ""
proxy_setup = os.environ.get("proxy")
owner = os.environ.get("owner") or ""

tweet_format = "https://twitter.com/{screen_name}/status/{id}"
