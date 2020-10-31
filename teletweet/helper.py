#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - helper.py
# 10/31/20 21:57
#

__author__ = "Benny <benny.think@gmail.com>"

import json


def can_use(chat_id) -> bool:
    with open("database.json") as f:
        data: dict = json.load(f)
    return data.get(str(chat_id))
