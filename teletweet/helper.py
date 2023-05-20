#!/usr/bin/env python3
# coding: utf-8

# TeleTweet - helper.py
# 2023-05-20  22:32

import json
import logging
from base64 import b64decode


def get_auth_data(chat_id: str) -> dict:
    data = json.load(open("auth.json", "r"))
    return data.get(str(chat_id), {})


def sign_in(chat_id: str, auth_string):
    logging.info("Adding user oauth token...")
    auth_dict = b64decode(auth_string.encode("u8")).decode("u8")
    data = json.load(open("auth.json", "r"))
    data[str(chat_id)] = json.loads(auth_dict)
    json.dump(data, open("auth.json", "w"))
    return "Login success"


def sign_off(chat_id: str):
    logging.info("Deleting user oauth token...")
    data = json.load(open("auth.json", "r"))
    data.pop(str(chat_id), None)
    json.dump(data, open("auth.json", "w"))
