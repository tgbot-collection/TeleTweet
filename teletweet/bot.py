#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - bot.py
# 10/22/20 16:25
#

__author__ = "Benny <benny.think@gmail.com>"

import tempfile

import telebot

from config import BOT_TOKEN, tweet_format
from helper import can_use, sign_in, init_enc, sign_off, is_sign_in
from tweet import send_tweet

bot = telebot.TeleBot(BOT_TOKEN)
init_enc()


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    msg = 'Welcome to TeleTweet. ' \
          'This bot will connect you from Telegram Bot to Twitter.' \
          'Wanna get started now? Type /sign_in now!'
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['sign_in'])
def sign_in_handler(message):
    if is_sign_in(message.chat.id):
        bot.send_message(message.chat.id, "You have already signed in, no need to do it again.")
        return

    bot.send_chat_action(message.chat.id, 'typing')
    msg = 'Click this [link](https://teletweet.app) to login in you twitter.' \
          ' When your login in is done, send auth code back to me'
    bot.send_message(message.chat.id, msg, parse_mode='markdown')
    bot.register_next_step_handler(message, add_auth)


def add_auth(message):
    bot.send_chat_action(message.chat.id, 'typing')
    msg = sign_in(str(message.chat.id), message.text)
    bot.send_message(message.chat.id, msg, parse_mode='markdown')


@bot.message_handler(commands=['sign_off'])
def sign_off_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not is_sign_in(str(message.chat.id)):
        bot.send_message(message.chat.id, "Lazarus came back from the dead.\nYou haven't signed in yet.")
        return

    sign_off(str(message.chat.id))
    msg = "I'm sorry to see you go. I have delete your oauth token." \
          "By the way, you could also check [this link](https://twitter.com/settings/connected_apps)."
    bot.send_message(message.chat.id, msg, parse_mode='markdown')


@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'Author: @BennyThink\nGitHub: https://github.com/tgbot-collection/TeleTweet')


@bot.message_handler()
def tweet_text_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not can_use(message.chat.id):
        bot.send_message(message.chat.id, "Sorry, I can't find your auth data. Type /sign_in to try again.")
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
        bot.send_message(message.chat.id, "Sorry, I can't find your auth data. Type /sign_in to try again.")
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

        result = send_tweet(message.chat.id, text, [temp])

    if result.get("error"):
        resp = f"❌ Error: `{result['error']}`"
    else:
        url = tweet_format.format(screen_name=result["user"]["screen_name"], id=result['id'])
        resp = f"✅ Your [tweet]({url}) has been sent.\n"
    bot.reply_to(message, resp, parse_mode="markdown")


if __name__ == '__main__':
    banner = """
▀▛▘  ▜     ▀▛▘         ▐
 ▌▞▀▖▐ ▞▀▖  ▌▌  ▌▞▀▖▞▀▖▜▀
 ▌▛▀ ▐ ▛▀   ▌▐▐▐ ▛▀ ▛▀ ▐ ▖
 ▘▝▀▘ ▘▝▀▘  ▘ ▘▘ ▝▀▘▝▀▘ ▀
 by BennyThink
    """
    print(f"\033[1;35m {banner}\033[0m")
    print("\033[1;36mTeletweet is running...\033[0m")
    bot.polling(none_stop=True)
