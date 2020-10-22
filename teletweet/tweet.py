#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - tweet.py
# 10/22/20 16:18
#

__author__ = "Benny <benny.think@gmail.com>"

import sys
import twitter
import os
import re
import random
import time
import logging
from config import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')

api = twitter.Api(consumer_key=consumer_key,
                  consumer_secret=consumer_secret,
                  access_token_key=access_token_key,
                  access_token_secret=access_token_secret)

# api.PostUpdate("", media=file)
