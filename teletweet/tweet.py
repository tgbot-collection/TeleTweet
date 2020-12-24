#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - tweet.py
# 10/22/20 16:18
#

__author__ = "Benny <benny.think@gmail.com>"

import traceback
import logging
import re
import tempfile

import twitter
import requests
from twitter.twitter_utils import calc_expected_status_length
from twitter.api import CHARACTER_LIMIT

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
    if not text:
        text = ""
    tweet_id = __get_tweet_id_from_reply(message)
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
        response = f"[{name}](https://twitter.com/{user_id})"
    except Exception as e:
        logging.error(traceback.format_exc())
        response = {"error": str(e)}

    return response


def delete_tweet(message) -> dict:
    logging.info("Deleting tweet for someone...")
    chat_id = message.chat.id
    tweet_id = __get_tweet_id_from_reply(message)
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


def __get_tweet_id_from_reply(message) -> int:
    reply_to = message.reply_to_message
    if reply_to:
        tweet_id = __get_tweet_id_from_url(reply_to.html_text)
    else:
        tweet_id = None
    logging.info("Replying to %s", tweet_id)
    return tweet_id


def __get_tweet_id_from_url(url) -> int:
    try:
        # https://twitter.com/williamwoo7/status/1326147700425809921?s=20
        tweet_id = re.findall(r"https://twitter\.com/.+/status/(\d+)", url)[0]
    except IndexError:
        tweet_id = None
    return tweet_id


def download_video_from_id(chat_id, tweet_id):
    try:
        api = __connect_twitter(decrypt_to_auth(chat_id))

        logging.info("Getting video tweets......")
        status = api.GetStatus(tweet_id)
        url = __get_video_url(status.AsDict())
        response = __download_from_url(url)
    except Exception as e:
        logging.error(traceback.format_exc())
        response = {"error": str(e)}

    return response


def is_video_tweet(chat_id, text) -> str:
    # will return an id
    tweet_id = __get_tweet_id_from_url(text)
    logging.info("tweet id is %s", tweet_id)
    result = ""
    try:
        api = __connect_twitter(decrypt_to_auth(chat_id))
        logging.info("Getting video tweets......")
        status = api.GetStatus(tweet_id)
        url = __get_video_url(status.AsDict())
        if url:
            result = tweet_id
    except Exception:
        logging.error(traceback.format_exc())

    return result


def __get_video_url(json_dict: dict) -> str:
    logging.info("Downloading video...")
    # video/gif is the first one. photo could be four
    media = json_dict.get("media")
    if media:
        media = media[0]
        if media["type"] == "video":
            variants = media["video_info"]["variants"]
            rates = [i.get('bitrate', 0) for i in variants]
            index = rates.index(max(rates))
            url = variants[index]["url"]
            logging.info("Real download url found.")
            return url


def __download_from_url(url) -> dict:
    logging.info("Downloading %s ...", url)
    r = requests.get(url, stream=True)
    logging.info("Download complete")
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as video_file:
        video_file.write(r.content)
    return {"file": video_file, "url": url}


def remain_char(tweet: str) -> str:
    length = calc_expected_status_length(tweet)
    return f"{length}/{CHARACTER_LIMIT}. Click this message to tweet."


if __name__ == '__main__':
    print(__get_tweet_id_from_url("https://twitter.com/williamwoo7/status/1326147700425809921?s=20"))
    print(__get_tweet_id_from_url("https://twitter.com/nixcraft/status/1326077772117078018?s=09"))
