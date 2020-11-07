#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - tweet.py
# 10/22/20 16:18
#

__author__ = "Benny <benny.think@gmail.com>"

import traceback
import logging
import re

import twitter

from config import CONSUMER_KEY, CONSUMER_SECRET
from helper import decrypt_to_auth

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')


def __connect_twitter(auth_data: dict):
    logging.info("Connecting to twitter api...")
    return twitter.Api(consumer_key=CONSUMER_KEY,
                       consumer_secret=CONSUMER_SECRET,
                       access_token_key=auth_data['ACCESS_KEY'],
                       access_token_secret=auth_data['ACCESS_SECRET'],
                       sleep_on_rate_limit=True)


def send_tweet(message, pic=None) -> dict:
    logging.info("Preparing tweet for someone...")
    chat_id = message.chat.id
    text = message.text or message.caption

    tweet_id = __get_tweet_id(message)
    try:
        api = __connect_twitter(decrypt_to_auth(chat_id))
        logging.info("Tweeting...")
        status = api.PostUpdate(text, media=pic, in_reply_to_status_id=tweet_id)
        logging.info("Tweeted")
        response = status.AsDict()
    except Exception as e:
        logging.error(traceback.format_exc())
        response = {"error": str(e)}

    return response


def get_me(chat_id) -> str:
    logging.info("Get me!")
    try:
        api = __connect_twitter(decrypt_to_auth(chat_id))
        name = api.VerifyCredentials().name
        user_id = api.VerifyCredentials().screen_name
        response = f"Hello👋 [{name}](https://twitter.com/{user_id})"
    except Exception as e:
        logging.error(traceback.format_exc())
        response = {"error": str(e)}

    return response


def delete_tweet(message) -> dict:
    logging.info("Deleting tweet for someone...")
    chat_id = message.chat.id
    tweet_id = __get_tweet_id(message)
    if not tweet_id:
        return {"error": "Which tweet do you want to delete? This does not seem like a valid tweet message."}

    try:
        api = __connect_twitter(decrypt_to_auth(chat_id))
        logging.info("Deleting......")
        status = api.DestroyStatus(tweet_id)
        response = status.AsDict()
    except Exception as e:
        logging.error(traceback.format_exc())
        response = {"error": str(e)}

    return response


def __get_tweet_id(message) -> int:
    reply_to = message.reply_to_message
    if reply_to:
        tweet_id = re.findall(r"\d+", reply_to.html_text)
    else:
        tweet_id = None
    if tweet_id:
        tweet_id = int(tweet_id[0])
    logging.info("Replying to %s", tweet_id)
    return tweet_id


if __name__ == '__main__':
    get_me("260260121")
