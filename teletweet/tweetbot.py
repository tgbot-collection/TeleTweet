#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - bot.py
# 10/22/20 16:25
#

__author__ = "Benny <benny.think@gmail.com>"

import logging
import os
import tempfile
from threading import Lock

import requests
from pyrogram import Client, enums, filters, types
from tgbot_ping import get_runtime

from config import APP_HASH, APP_ID, BOT_TOKEN, tweet_format
from helper import get_auth_data, sign_in, sign_off
from tweet import (
    delete_tweet,
    get_me,
    get_video_download_link,
    is_video_tweet,
    send_tweet,
)

lock = Lock()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(filename)s [%(levelname)s]: %(message)s")
logging.getLogger("apscheduler.executors.default").propagate = False
media_group = {}
bot = Client("teletweet", APP_ID, APP_HASH, bot_token=BOT_TOKEN)

ALLOW_USER = os.getenv("ALLOW_USER", "").split(",")

STEP = {}


@bot.on_message(filters.command(["start"]))
def start_handler(client, message: types.Message):
    message.reply_chat_action(enums.ChatAction.TYPING)
    if get_auth_data(message.chat.id):
        bot.send_message(message.chat.id, "Start by sending me a message?")
        return
    msg = "Welcome to TeleTweet. " "This bot will connect you from Telegram Bot to Twitter. " "Want to get started now? Type /sign_in now!"
    if ALLOW_USER != [""]:
        msg += "\n\nTHIS BOT IS ONLY AVAILABLE TO CERTAIN USERS. Contact creator for help."
    bot.send_message(message.chat.id, msg)


@bot.on_message(filters.command(["sign_in"]))
def sign_in_handler(client, message: types.Message):
    if get_auth_data(message.chat.id):
        bot.send_message(message.chat.id, "You have already signed in, no need to do it again.")
        return
    message.reply_chat_action(enums.ChatAction.TYPING)
    msg = "Click this [link](https://teletweet.app) to login in you twitter." " When your login in is done, send auth code back to me"
    bot.send_message(message.chat.id, msg, enums.ParseMode.MARKDOWN)
    STEP[message.chat.id] = "sign_in"


@bot.on_message(filters.command(["sign_off"]))
def sign_off_handler(client, message: types.Message):
    message.reply_chat_action(enums.ChatAction.TYPING)
    if not get_auth_data(message.chat.id):
        bot.send_message(message.chat.id, "You haven't signed in yet.")
        return

    sign_off(str(message.chat.id))
    msg = (
        "I'm sorry to see you go. I have delete your oauth token." "By the way, you could also check [this link](https://twitter.com/settings/connected_apps)."
    )
    bot.send_message(message.chat.id, msg, enums.ParseMode.MARKDOWN)


@bot.on_message(filters.command(["help"]))
def help_handler(client, message: types.Message):
    message.reply_chat_action(enums.ChatAction.TYPING)
    bot.send_message(message.chat.id, "Author: @BennyThink\nGitHub: https://github.com/tgbot-collection/TeleTweet")


@bot.on_message(filters.command(["ping"]))
def help_handler(client, message: types.Message):
    message.reply_chat_action(enums.ChatAction.TYPING)

    try:
        userinfo = "Hello👋 " + get_me(message.chat.id) + "\n\n"
    except TypeError:
        userinfo = "Hello👋 unknown user! Want to `/sign_in` now?\n\n"

    info = get_runtime("botsrunner_teletweet_1")[:500]
    bot.send_message(message.chat.id, userinfo + info, parse_mode=enums.ParseMode.MARKDOWN, disable_web_page_preview=True)


@bot.on_message(filters.command(["delete"]))
def delete_handler(client, message: types.Message):
    message.reply_chat_action(enums.ChatAction.TYPING)
    if not message.reply_to_message:
        bot.send_message(message.chat.id, "Reply to some message and delete.")
        return
    result = delete_tweet(message)
    if result.get("error"):
        resp = f"❌ Error: `{result['error']}`"
        message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.MARKDOWN)
    else:
        resp = f"🗑 Your tweet has been deleted.\n"
        message.reply_to_message.edit_text(resp, parse_mode=enums.ParseMode.MARKDOWN)


def user_check(func):
    def wrapper(client, message):
        user_id = message.chat.id
        if str(user_id) in ALLOW_USER:
            # check state machien first
            if STEP.get(message.chat.id) == "sign_in":
                try:
                    result = sign_in(message.chat.id, message.text)
                except Exception as e:
                    result = str(e)
                message.reply_text(result, quote=True)
                STEP.pop(message.chat.id)
                return
            elif not get_auth_data(message.chat.id):
                logging.warning("Invalid user %d", message.chat.id)
                message.reply_chat_action(enums.ChatAction.TYPING)
                bot.send_message(message.chat.id, "Sorry, I can't find your auth data. Type /sign_in to try again.")
                return
            return func(client, message)
        else:
            bot.send_message(message.chat.id, "You're not allowed to use this bot.")

    return wrapper


@bot.on_message(filters.incoming & filters.text)
@user_check
def tweet_text_handler(client, message: types.Message):
    message.reply_chat_action(enums.ChatAction.TYPING)
    # first check if the user want to download video, gif
    tweet_id = is_video_tweet(message.chat.id, message.text)
    if tweet_id and message.text.startswith("https://twitter.com"):
        btn1 = types.InlineKeyboardButton("Download", callback_data=tweet_id)
        btn2 = types.InlineKeyboardButton("Tweet", callback_data="tweet")
        markup = types.InlineKeyboardMarkup(
            [
                [btn1, btn2],
            ]
        )
        message.reply_text("Do you want to download video or just tweet this?", quote=True, reply_markup=markup)
        return

    result = send_tweet(message)
    notify_result(result, message)


@bot.on_message(filters.media_group)
@user_check
def tweet_group_photo_handler(client, message: types.Message):
    message.reply_chat_action(enums.ChatAction.UPLOAD_PHOTO)
    # this method will be called multiple times
    # so we need to check if the group has been received
    media_group_id = message.media_group_id
    if STEP.get(media_group_id):
        return
    logging.info("Media group %s received", message.media_group_id)
    STEP[media_group_id] = True
    groups = message.get_media_group()
    files = []
    for group in groups:
        img_data = group.download(in_memory=True)
        setattr(img_data, "mode", "rb")
        caption = group.caption
        if caption:
            setattr(message, "text", caption)
        files.append(img_data)
    result = send_tweet(message, files)
    notify_result(result, message)
    STEP.pop(media_group_id)


@bot.on_message(filters.photo | filters.document | filters.video | filters.sticker)
@user_check
def tweet_single_photo_handler(client, message: types.Message):
    message.reply_chat_action(enums.ChatAction.UPLOAD_PHOTO)
    logging.info("Normal one media message")
    img_data = message.download(in_memory=True)
    setattr(img_data, "mode", "rb")
    result = send_tweet(message, [img_data])
    notify_result(result, message)


def notify_result(result, message: types.Message):
    if result.get("error"):
        resp = f"❌ Error: `{result['error']}`"
    else:
        url = tweet_format.format(screen_name="x", id=result["id"])
        resp = f"✅ Your [tweet]({url}) has been sent.\n"
    message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.MARKDOWN)


@bot.on_callback_query(filters.regex("tweet"))
def tweet_callback(client, call: types.CallbackQuery):
    result = send_tweet(call.message.reply_to_message)
    notify_result(result, call.message)


@bot.on_callback_query()
def video_callback(client, call: types.CallbackQuery):
    chat_id = call.message.chat.id
    message = call.message
    message.reply_chat_action(enums.ChatAction.TYPING)
    bot.answer_callback_query(call.id, "Sure, wait a second.")
    link = get_video_download_link(chat_id, call.data)
    logging.info("Downloading %s ...", link)
    r = requests.get(link, stream=True)
    logging.info("Download complete")
    message.reply_chat_action(enums.ChatAction.UPLOAD_VIDEO)
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as video_file:
        video_file.write(r.content)
        message.reply_video(video_file.name, quote=True)


if __name__ == "__main__":
    banner = """
▀▛▘  ▜     ▀▛▘         ▐
 ▌▞▀▖▐ ▞▀▖  ▌▌  ▌▞▀▖▞▀▖▜▀
 ▌▛▀ ▐ ▛▀   ▌▐▐▐ ▛▀ ▛▀ ▐ ▖
 ▘▝▀▘ ▘▝▀▘  ▘ ▘▘ ▝▀▘▝▀▘ ▀
 by BennyThink
    """
    print(f"\033[1;35m {banner}\033[0m")
    print("\033[1;36mTeletweet is running...\033[0m")
    bot.run()
