#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - tweet.py
# 10/22/20 16:18
#

__author__ = "Benny <benny.think@gmail.com>"

import traceback
import logging

import twitter

from config import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')


def connect_twitter():
    api = twitter.Api(consumer_key=consumer_key,
                      consumer_secret=consumer_secret,
                      access_token_key=access_token_key,
                      access_token_secret=access_token_secret,
                      sleep_on_rate_limit=True)
    return api


def send_tweet(text: str, pic=None):
    if pic is None:
        pic = ""
    logging.info("Preparing tweet... %s with %s picture(s)", text, len(pic))

    logging.info("Connecting to twitter api")
    try:
        api = connect_twitter()
        logging.info("Tweeting...")
        status = api.PostUpdate(text, media=pic)
        logging.info("Tweeted")
        response = status.AsDict()
    except Exception as e:
        logging.error(traceback.format_exc())
        response = {"error": str(e)}

    return response
