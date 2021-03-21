#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - bot.py
# 10/22/20 16:25
#

__author__ = "Benny <benny.think@gmail.com>"

import os
import tempfile
import logging
import copy
import re
from threading import Lock

import telebot
from telebot import types
from tgbot_ping import get_runtime
from apscheduler.schedulers.background import BackgroundScheduler
from twitter.twitter_utils import calc_expected_status_length
from twitter.api import CHARACTER_LIMIT

from config import BOT_TOKEN, tweet_format, reply_json
from crypto import has_auth_data, sign_in, init_enc, sign_off, is_sign_in
from tweet import get_me, delete_tweet, download_video_from_id, is_video_tweet, remain_char, send_tweet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')
logging.getLogger('apscheduler.executors.default').propagate = False
media_group = {}
bot = telebot.TeleBot(BOT_TOKEN)
init_enc()
lock = Lock()


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if is_sign_in(message.chat.id):
        bot.send_message(message.chat.id, "Start by sending me a message?")
        return
    msg = 'Welcome to TeleTweet. ' \
          'This bot will connect you from Telegram Bot to Twitter. ' \
          'Want to get started now? Type /sign_in now!'
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
    bot.register_next_step_handler(message, next_step_add_auth)


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


@bot.message_handler(commands=['ping'])
def help_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        userinfo = "Hello👋 " + get_me(message.chat.id) + "\n\n"
    except TypeError:
        userinfo = "Hello👋 unknown user! Want to `/sign_in` now?\n\n"

    info = get_runtime("botsrunner_teletweet_1")
    bot.send_message(message.chat.id, userinfo + info, parse_mode="markdown", disable_web_page_preview=True)


@bot.message_handler(commands=['delete'])
def delete_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not message.reply_to_message:
        bot.send_message(message.chat.id, "Reply to some message and delete.")
        return
    result = delete_tweet(message)
    if result.get("error"):
        resp = f"❌ Error: `{result['error']}`"
        bot.reply_to(message, resp, parse_mode="markdown")
    else:
        resp = f"🗑 Your tweet `{result['text']}` has been deleted.\n"
        bot.edit_message_text(resp, message.chat.id, message.reply_to_message.message_id, parse_mode='markdown')
        # bot.delete_message(message.chat.id,message.reply_to_message.message_id)


def group_permission_check(message):
    allow = False
    if message.chat.type in ("supergroup", "group"):
        admin_ids = [i.user.id for i in bot.get_chat_administrators(message.chat.id)]
        bot_id = bot.get_me().id
        from_id = message.from_user.id
        if (bot_id in admin_ids) or (from_id in admin_ids):
            allow = True
    else:
        allow = True
    return allow


@bot.message_handler()
def tweet_text_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not has_auth_data(message.chat.id):
        bot.send_message(message.chat.id, "Sorry, I can't find your auth data. Type /sign_in to try again.")
        return

    if not group_permission_check(message):
        bot.send_message(message.chat.id, "Sorry, you don't have the permission to send tweets.")
        return
    # first check if the user want to download video, gif
    tweet_id = is_video_tweet(message.chat.id, message.text)
    if tweet_id and message.text.startswith("https://twitter.com") and (not getattr(message, "force", False)):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Download?', callback_data=tweet_id)
        btn2 = types.InlineKeyboardButton('Tweet?', callback_data='tweet')
        markup.add(btn1, btn2)
        bot.reply_to(message, "Do you want to download video or just tweet this?", reply_markup=markup)
        return

    send_tweet_entrance(message)


@bot.message_handler(content_types=['photo', 'document', 'video'])
def tweet_photo_handler(message):
    if not has_auth_data(message.chat.id):
        logging.warning("Invalid user %d", message.chat.id)
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, "Sorry, I can't find your auth data. Type /sign_in to try again.")
        return

    bot.send_chat_action(message.chat.id, 'upload_photo')
    if message.media_group_id:
        logging.info("Media group %s received", message.media_group_id)
        with lock:
            # we need a background to periodically check this structure
            # shouldn't download here because download is slow and it will exceeds 5 seconds
            fid = get_file_id(message)
            key = f"{message.chat.id}/{message.media_group_id}"
            pre_value = media_group.get(key)
            if pre_value:
                pre_value["file_id_list"].append(fid)
                if message.caption:
                    pre_value["caption"] = message.caption
                    pre_value['timeout'] += 1
            else:
                # bot.send_message(message.chat.id, "Hang on, this might take a few seconds")
                cur_value = {
                    "message": message,
                    "caption": message.caption,
                    "file_id_list": [fid],
                    "timeout": 6
                }
                media_group[key] = cur_value
    else:
        # for one photo/video/document
        logging.info("Normal one media message")

        file_obj = download_file_from_msg(message)
        send_tweet_entrance(message, file_obj)
        file_obj.close()
        os.remove(file_obj.name)


@bot.callback_query_handler(func=lambda call: True)
def video_callback(call):
    # why we use send document instead of video url?
    # Telegram will download and send the file.
    # 5 MB max size for photos and 20 MB max for other types of content.
    if call.data == "tweet":
        setattr(call.message.reply_to_message, "force", True)
        # call.message - > current bot message?
        tweet_text_handler(call.message.reply_to_message)
    else:
        chat_id = call.message.chat.id
        message = call.message
        bot.send_chat_action(call.message.chat.id, 'typing')
        bot.answer_callback_query(call.id, "Sure, wait a second.")
        file_info = download_video_from_id(chat_id, call.data)
        if file_info.get("error"):
            # resp, message.chat.id, message.reply_to_message.message_id
            bot.edit_message_text(f"❌ Error: `{file_info['error']}`", chat_id, message.message_id,
                                  parse_mode="markdown")
            return

        file = file_info.get("file")
        url = file_info.get("url")
        if os.path.getsize(file.name) > 1 * 1024 * 1024 * 50:
            bot.edit_message_text(f"The video file is too big. I'll send you url instead\n{url}", chat_id,
                                  message.message_id)
        else:
            bot.send_chat_action(chat_id, 'upload_document')
            with open(file.name, "rb") as f:
                bot.send_document(chat_id, f)
            bot.delete_message(message.chat.id, message.message_id)

        file.close()
        os.remove(file.name)


@bot.inline_handler(lambda query: True)
def query_text(inline_query):
    try:
        usage = remain_char(inline_query.query)
        r = types.InlineQueryResultArticle('1', usage, types.InputTextMessageContent(inline_query.query))
        bot.answer_inline_query(inline_query.id, [r])
    except Exception as e:
        logging.error(e)


def next_step_add_auth(message):
    bot.send_chat_action(message.chat.id, 'typing')
    msg = sign_in(str(message.chat.id), message.text)
    bot.send_message(message.chat.id, msg, parse_mode='markdown')


def send_tweet_entrance(message, file=None):
    if file is None:
        # normal text tweet, could be too long
        text = message.text
        if calc_expected_status_length(text) > CHARACTER_LIMIT:
            # pre calculation
            is_long = False
            for part in re.split(r"\n+", message.text):
                if calc_expected_status_length(part) > CHARACTER_LIMIT:
                    logging.warning("%s chars for thread tweet!", calc_expected_status_length(part))
                    bot.reply_to(message, f"`{part}` is too long", parse_mode="markdown")
                    is_long = True
            if is_long:
                return
            # normal process
            url = ""
            first_thread = []
            for part in re.split(r"\n+", message.text):
                new_message = copy.copy(message)
                if url:
                    replied = types.Message.de_json(reply_json % url)
                    setattr(new_message, "reply_to_message", replied)

                new_message.text = part
                result = send_tweet(new_message)
                first_thread.append(result)
                url = tweet_format.format(screen_name="abc", id=result["id"])
            # send response
            send_tweet_message(first_thread[0], message)
            return
        else:
            result = send_tweet(message)
    elif isinstance(file, list):
        result = send_tweet(message, file)
        [f.close() for f in file]
    else:
        # one image message, file object
        result = send_tweet(message, [file])
        file.close()

    send_tweet_message(result, message)


def send_tweet_message(result, message):
    if result.get("error"):
        resp = f"❌ Error: `{result['error']}`"
    else:
        url = tweet_format.format(screen_name=result["user"]["screen_name"], id=result['id'])
        resp = f"✅ Your [tweet]({url}) has been sent.\n"
    bot.reply_to(message, resp, parse_mode="markdown")


def download_file_from_msg(message):
    file_id = get_file_id(message)
    return download_file_from_id(file_id)


def download_file_from_id(file_id):
    file_info = bot.get_file(file_id)
    content = bot.download_file(file_info.file_path)

    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(content)
    return temp


def get_file_id(message) -> str:
    if message.photo:
        object_type = "photo"
    elif message.video:
        object_type = "video"
    elif message.document:
        object_type = "document"
    else:
        object_type = ""

    try:
        file_id = getattr(message, object_type)[-1].file_id
    except Exception:
        file_id = getattr(message, object_type).file_id
    return file_id


def multi_photo_checker():
    # full with 4 or timeout is 0
    logging.debug("Multi photo checker started with %d job(s)", len(media_group))
    for unique, data in list(media_group.items()):
        if data['timeout'] <= 0 or len(data["file_id_list"]) >= 4:
            logging.info("Set %s is ready, sending now...", unique)
            data['message'].text = data['caption']
            f_obj_list = [download_file_from_id(fid) for fid in data["file_id_list"][:4]]
            send_tweet_entrance(data['message'], f_obj_list)
            # delete media_group
            media_group.pop(unique)
        else:
            logging.info("Set %s with %d photo(s) is losing time %d", unique, len(data["file_id_list"]),
                         data['timeout'])
            data['timeout'] -= 5


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(multi_photo_checker, 'interval', seconds=5)
    scheduler.start()

    banner = """
▀▛▘  ▜     ▀▛▘         ▐
 ▌▞▀▖▐ ▞▀▖  ▌▌  ▌▞▀▖▞▀▖▜▀
 ▌▛▀ ▐ ▛▀   ▌▐▐▐ ▛▀ ▛▀ ▐ ▖
 ▘▝▀▘ ▘▝▀▘  ▘ ▘▘ ▝▀▘▝▀▘ ▀
 by BennyThink
    """
    print(f"\033[1;35m {banner}\033[0m")
    print("\033[1;36mTeletweet is running...\033[0m")
    bot.polling()
