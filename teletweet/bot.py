#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - bot.py
# 10/22/20 16:25
#

__author__ = "Benny <benny.think@gmail.com>"

import logging
import tempfile

import telebot
from telebot import apihelper

from config import proxy_setup, bot_token, tweet_format
from tweet import send_tweet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')
if proxy_setup:
    apihelper.proxy = {'http': proxy_setup}
bot = telebot.TeleBot(bot_token)

photo_map = {"817262": {"group_id": [""]}
             }


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'Welcome to TeleTweet')


@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'Author: @BennyThink\nGitHub: https://github.com/BennyThink/TeleTweet')


@bot.message_handler()
def tweet_text_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    result = send_tweet(message.text)

    if result.get("error"):
        resp = f"❌ Error: `{result['error']}`"
    else:
        url = tweet_format.format(screen_name=result["user"]["screen_name"], id=result['id'])
        resp = f"✅ Your [tweet]({url}) has been sent.\n"

    bot.reply_to(message, resp, parse_mode="markdown")


@bot.message_handler(content_types=['photo'])
def tweet_photo_handler(message):
    bot.send_chat_action(message.chat.id, 'typing', timeout=100)
    text = message.caption
    if text is None:
        text = ""
    photo_map['message.media_group_id'] = message.photo[0].file_id
    if message.media_group_id:
        bot.send_message(message.chat.id, "I don't support media group yet.")
        return

    fid = bot.get_file(message.photo[0].file_id)
    content = bot.download_file(fid.file_path)

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
