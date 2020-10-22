#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - config.py
# 10/22/20 16:20
#

__author__ = "Benny <benny.think@gmail.com>"

import os

bot_token = os.environ.get("token")
consumer_key = os.environ.get("consumer_key")
consumer_secret = os.environ.get("consumer_secret")
access_token_key = os.environ.get("access_key")
access_token_secret = os.environ.get("access_secret")
proxy_setup = os.environ.get("proxy")
