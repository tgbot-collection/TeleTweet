#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - bot.py
# 10/22/20 16:25
#

__author__ = "Benny <benny.think@gmail.com>"

import logging
import tempfile
import json

from base64 import b64decode
import telebot
from telebot import apihelper

from config import proxy_setup, bot_token, tweet_format
from helper import can_use
from tweet import send_tweet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')
if proxy_setup:
    apihelper.proxy = {'http': proxy_setup}
bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    msg = 'Welcome to TeleTweet. ' \
          'This bot will connect you from Telegram Bot to Twitter.' \
          'Wanna get started now? Type /auth now!'
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['auth'])
def auth_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    msg = 'Click this [link](https://teletweet.app) to auth you twitter.' \
          ' When your auth is done, send auth code back to me'
    bot.send_message(message.chat.id, msg, parse_mode='markdown')

    bot.register_next_step_handler(message, add_auth)


def add_auth(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        twitter_auth = b64decode(message.text)
    except ValueError as e:
        logging.error("Base64 decode failed %s", e)
        bot.send_message(message.chat.id, f"Your token appears to be invalid.\n`{e}`", parse_mode='markdown')
        return

        # read json file, update it, write back
    with open("database.json") as f:
        data: dict = json.load(f)
        data[message.chat.id] = json.loads(twitter_auth)
    with open("database.json", "w") as f:
        json.dump(data, f, indent="\t")

    bot.send_message(message.chat.id, f"Auth success!")


@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'Author: @BennyThink\nGitHub: https://github.com/tgbot-collection/TeleTweet')


@bot.message_handler()
def tweet_text_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not can_use(message.chat.id):
        bot.send_message(message.chat.id, "Sorry, I can't find your auth data. Type /auth to auth.")
        return

    result = send_tweet(message.chat.id, message.text)

    if result.get("error"):
        resp = f"❌ Error: `{result['error']}`"
    else:
        url = tweet_format.format(screen_name=result["user"]["screen_name"], id=result['id'])
        resp = f"✅ Your [tweet]({url}) has been sent.\n"

    bot.reply_to(message, resp, parse_mode="markdown")


@bot.message_handler(content_types=['photo', 'document'])
def tweet_photo_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not can_use(message.chat.id):
        bot.send_message(message.chat.id, "Sorry, I can't find your auth data. Type /auth to auth.")
        return

    text = message.caption
    if text is None:
        text = ""
    if message.media_group_id:
        bot.send_message(message.chat.id, "I don't support media group yet.")
        return

    if message.photo:
        file_id = message.photo[-1].file_id
    else:
        file_id = message.document.file_id
    file_info = bot.get_file(file_id)
    content = bot.download_file(file_info.file_path)

    with tempfile.NamedTemporaryFile() as temp:
        temp.write(content)

        result = send_tweet(text, [temp])

    if result.get("error"):
        resp = f"❌ Error: `{result['error']}`"
    else:
        url = tweet_format.format(screen_name=result["user"]["screen_name"], id=result['id'])
        resp = f"✅ Your [tweet]({url}) has been sent.\n"
    bot.reply_to(message, resp, parse_mode="markdown")


if __name__ == '__main__':
    logging.info('TeleTweet bot is running...')
    bot.polling(none_stop=True)
