#!/usr/local/bin/python3
# coding: utf-8

# TeleTweet - twauth.py
# 10/31/20 18:32
#

__author__ = "Benny <benny.think@gmail.com>"

import logging
import os
import json

from base64 import b64encode

import oauth2 as oauth
import urllib.request
import urllib.parse
import urllib.error

from tornado import web, ioloop, httpserver, options

request_token_url = 'https://api.twitter.com/oauth/request_token'
access_token_url = 'https://api.twitter.com/oauth/access_token'
authorize_url = 'https://api.twitter.com/oauth/authorize'
show_user_url = 'https://api.twitter.com/1.1/users/show.json'

APP_CONSUMER_KEY = os.environ.get("CONSUMER_KEY") or '1'
APP_CONSUMER_SECRET = os.environ.get("APP_CONSUMER_SECRET") or '2'
callback_url = os.environ.get("CALLBACK_URL") or "http://127.0.0.1:8888/callback"

oauth_store = {}


class BaseHandler(web.RequestHandler):
    def data_received(self, chunk):
        pass


class IndexHandler(BaseHandler):
    async def get(self):
        await self.render("index.html")


class Step1Handler(BaseHandler):
    async def get(self):
        await self.render('step1.html')


class Step2Handler(BaseHandler):
    async def get(self):
        # Generate the OAuth request tokens, then display them
        consumer = oauth.Consumer(APP_CONSUMER_KEY, APP_CONSUMER_SECRET)
        client = oauth.Client(consumer)

        resp, content = client.request(request_token_url, "POST", body=urllib.parse.urlencode({
            "oauth_callback": callback_url}))

        if resp['status'] != '200':
            error_message = 'Invalid response, status {status}, {message}'.format(
                status=resp['status'], message=content.decode('utf-8'))
            await self.render('error.html', error_message=error_message)

        request_token = dict(urllib.parse.parse_qsl(content))
        oauth_token = request_token[b'oauth_token'].decode('utf-8')
        oauth_token_secret = request_token[b'oauth_token_secret'].decode('utf-8')

        oauth_store[oauth_token] = oauth_token_secret
        await self.render('step2.html', authorize_url=authorize_url, oauth_token=oauth_token,
                          request_token_url=request_token_url)


class CallbackHandler(BaseHandler):
    async def get(self):
        # Accept the callback params, get the token and call the API to
        # display the logged-in user's name and handle
        oauth_token = self.get_query_argument("oauth_token")
        oauth_verifier = self.get_query_argument('oauth_verifier')
        oauth_denied = self.get_query_argument('denied', '')

        # if the OAuth request was denied, delete our local token
        # and show an error message
        if oauth_denied:
            if oauth_denied in oauth_store:
                del oauth_store[oauth_denied]
            await self.render('error.html', error_message="the OAuth request was denied by this user")

        if not oauth_token or not oauth_verifier:
            await self.render('error.html', error_message="callback param(s) missing")

        # unless oauth_token is still stored locally, return error
        if oauth_token not in oauth_store:
            await self.render('error.html', error_message="oauth_token not found locally")

        oauth_token_secret = oauth_store[oauth_token]

        # if we got this far, we have both callback params and we have
        # found this token locally

        consumer = oauth.Consumer(APP_CONSUMER_KEY, APP_CONSUMER_SECRET)
        token = oauth.Token(oauth_token, oauth_token_secret)
        token.set_verifier(oauth_verifier)
        client = oauth.Client(consumer, token)

        resp, content = client.request(access_token_url, "POST")
        access_token = dict(urllib.parse.parse_qsl(content))

        screen_name = access_token[b'screen_name'].decode('utf-8')
        user_id = access_token[b'user_id'].decode('utf-8')

        # These are the tokens you would store long term, someplace safe
        real_oauth_token = access_token[b'oauth_token'].decode('utf-8')
        real_oauth_token_secret = access_token[b'oauth_token_secret'].decode(
            'utf-8')
        __secret = {"ACCESS_KEY": real_oauth_token, "ACCESS_SECRET": real_oauth_token_secret}
        bot_paste = b64encode(json.dumps(__secret).encode('u8')).decode('u8')

        # Call api.twitter.com/1.1/users/show.json?user_id={user_id}
        real_token = oauth.Token(real_oauth_token, real_oauth_token_secret)
        real_client = oauth.Client(consumer, real_token)
        real_resp, real_content = real_client.request(
            show_user_url + '?user_id=' + user_id, "GET")

        if real_resp['status'] != '200':
            error_message = "Invalid response from Twitter API GET users/show: {status}".format(
                status=real_resp['status'])
            await self.render('error.html', error_message=error_message)

        response = json.loads(real_content.decode('utf-8'))

        name = response['name']

        # don't keep this token and secret in memory any longer
        del oauth_store[oauth_token]

        await self.render('callback.html', screen_name=screen_name, user_id=user_id, name=name,
                          bot_paste=bot_paste)


class RunServer:
    root_path = os.path.dirname(__file__)
    handlers = [
        (r'/', IndexHandler),
        (r'/step1', Step1Handler),
        (r'/step2', Step2Handler),
        (r'/callback', CallbackHandler),
        (r'/(favicon.ico)', web.StaticFileHandler, {"path": "."}),
    ]
    settings = {
        "cookie_secret": "5Li05DtnQewDZq1mDVB3HAAhFqUu2vD2USnqezkeu+M=",
        "xsrf_cookies": False,
        "autoreload": True,
        'template_path': os.path.join(root_path, "templates"),
    }

    application = web.Application(handlers, **settings)

    @staticmethod
    def run_server(port, host, **kwargs):
        tornado_server = httpserver.HTTPServer(RunServer.application, **kwargs)
        tornado_server.bind(port, host)

        tornado_server.start()

        try:
            print('Server is running on http://{host}:{port}'.format(host=host, port=port))
            ioloop.IOLoop.instance().current().start()
        except KeyboardInterrupt:
            ioloop.IOLoop.instance().stop()
            print('"Ctrl+C" received, exiting.\n')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    options.define("p", default=8888, help="running port", type=int)
    options.define("h", default='127.0.0.1', help="listen address", type=str)
    options.parse_command_line()
    p = options.options.p
    h = options.options.h
    RunServer.run_server(port=p, host=h)
