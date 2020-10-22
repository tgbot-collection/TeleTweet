#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - bot.py
# 10/22/20 16:25
#

__author__ = "Benny <benny.think@gmail.com>"

import time
import re
import os
import logging

import telebot
from telebot import types, apihelper

from config import proxy_setup, bot_token

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')
if proxy_setup:
    apihelper.proxy = {'https': proxy_setup}

bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'Welcome to TeleTweet')


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'Author: @BennyThink\nGitHub: https://github.com/BennyThink/TeleTweet')


if __name__ == '__main__':
    logging.info('YYeTs bot is running...')
    bot.polling(none_stop=True)
