#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - helper.py
# 10/31/20 21:57
#

__author__ = "Benny <benny.think@gmail.com>"

import json
import os
import base64
import logging

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from config import CONSUMER_KEY, CONSUMER_SECRET

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')


def can_use(chat_id) -> bool:
    plaintext: dict = json.loads(decrypt(read_file()))
    return plaintext.get(str(chat_id))


def read_file() -> bytes:
    with open("database.enc", "rb") as f:
        data = f.read()
    return data


def write_file(data: bytes):
    with open("database.enc", "wb") as f:
        f.write(data)


def get_fernet():
    logging.info("Initializing cryptography system...")

    password = CONSUMER_SECRET.encode('u8')
    salt = CONSUMER_KEY[0:16].encode('u8')
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000, backend=default_backend())
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    return f


def encrypt(data: [str, bytes]) -> bytes:
    logging.info("Encrypting now...")
    f = get_fernet()
    if isinstance(data, str):
        data = data.encode('u8')
    return f.encrypt(data)


def decrypt(data: [str, bytes]) -> bytes:
    logging.info("Decrypting now...")
    f = get_fernet()
    if isinstance(data, str):
        data = data.encode('u8')
    return f.decrypt(data)


def sign_off(chat_id: str):
    logging.info("Deleting user oauth token...")
    data: dict = json.loads(decrypt(read_file()))
    del data[chat_id]
    write_file(encrypt(json.dumps(data)))


def sign_in(chat_id: str, user_text: str) -> str:
    try:
        twitter_auth = base64.b64decode(user_text)
    except ValueError as e:
        logging.error("Base64 decode failed %s", e)
        msg = f"Your token appears to be invalid.\n`{e}`"
        return msg

    # add auth here
    logging.info("Adding user oauth token...")
    plaintext: dict = json.loads(decrypt(read_file()))
    plaintext[chat_id] = json.loads(twitter_auth)
    ciphertext = encrypt(json.dumps(plaintext))
    write_file(ciphertext)
    return "Login success"


def is_sign_in(chat_id: str) -> bool:
    return can_use(chat_id)


def init_enc():
    if os.path.getsize("database.enc") == 0:
        logging.info("Init the encryption database now...")
        ct = encrypt("{}")
        write_file(ct)
