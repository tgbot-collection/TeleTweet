#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - tweet.py
# 10/22/20 16:18
#

__author__ = "Benny <benny.think@gmail.com>"

import traceback
import logging
import json

import twitter

from config import CONSUMER_KEY, CONSUMER_SECRET
from helper import read_file, decrypt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')


def connect_twitter(auth_data: dict):
    api = twitter.Api(consumer_key=CONSUMER_KEY,
                      consumer_secret=CONSUMER_SECRET,
                      access_token_key=auth_data['ACCESS_KEY'],
                      access_token_secret=auth_data['ACCESS_SECRET'],
                      sleep_on_rate_limit=True)
    return api


def send_tweet(chat_id: int, text: str, pic=None):
    data: dict = json.loads(decrypt(read_file()))

    if pic is None:
        pic = ""
    logging.info("Preparing tweet for someone...")

    logging.info("Connecting to twitter api")
    try:
        api = connect_twitter(data[str(chat_id)])
        logging.info("Tweeting...")
        status = api.PostUpdate(text, media=pic)
        logging.info("Tweeted")
        response = status.AsDict()
    except Exception as e:
        logging.error(traceback.format_exc())
        response = {"error": str(e)}

    return response
