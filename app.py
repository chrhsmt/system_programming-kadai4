# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import urllib
import urllib2
import json
import os
import sys
import logging

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)

BOT_NAME = "harahe"
HOTPAPPER_API_PATH = "http://webservice.recruit.co.jp/hotpepper/gourmet/v1/"

cache = {}

class Message(object):
    """Slackのメッセージクラス"""
    token = ""
    team_id = ""
    channel_id = ""  # 投稿されたチャンネルID
    channel_name = ""  # チャンネル名
    timestamp = 0
    user_id = ""  
    user_name = ""  # 投稿ユーザー名
    text = ""  # 投稿内容
    service_id = ""
    team_domain = ""
    trigger_word = ""  # OutgoingWebhooksに設定したトリガー

    def __init__(self, params):
        if (params.has_key("token")):
            self.token = params["token"]
        if (params.has_key("team_id")):
            self.team_id = params["team_id"]
        if (params.has_key("channel_id")):
            self.channel_id = params["channel_id"]
        if (params.has_key("channel_name")):
            self.channel_name = params["channel_name"]
        if (params.has_key("timestamp")):
            self.timestamp = params["timestamp"]
        if (params.has_key("user_id")):
            self.user_id = params["user_id"]
        if (params.has_key("user_name")):
            self.user_name = params["user_name"]
        if (params.has_key("text")):
            self.text = params["text"]
        if (params.has_key("team_domain")):
            self.team_domain = params["team_domain"]
        if (params.has_key("service_id")):
            self.service_id = params["service_id"]
        if (params.has_key("trigger_word")):
            self.trigger_word = params["trigger_word"]

    def __str__(self):
        res = self.__class__.__name__
        res += "@{0.token}[channel={0.channel_name}, user={0.user_name}, text={0.text}]".format(self)
        return res

@app.route('/', methods=["POST"])
def index():
    app.logger.debug(request.form)
    msg = Message(request.form)
    app.logger.debug(msg)
    if msg.user_name == BOT_NAME:
        # BOT自身の投稿に反応させてしまうと無限ループになることもあるので反応させない
        return ""
    if BOT_NAME in msg.text:
        return say(recommend(" ".join(msg.text.split()[1:])), msg.user_name)
    else:
        return ""

def recommend(keyword):
    app.logger.debug("recommend start: [keyword=%s]" % keyword)
    if cache.has_key(keyword):
        return cache[keyword]

    keyword = urllib.quote(keyword.strip().encode("UTF-8"))
    request = urllib2.Request("%s?keyword=%s&format=json&is_open_time=now&key=%s" % (HOTPAPPER_API_PATH, keyword, os.environ['API_KEY']))
    response = urllib2.urlopen(request)
    json_obj = json.loads(response.read())
    app.logger.debug("-- response --")
    app.logger.debug(json_obj)
    app.logger.debug("-- /response --")
    if (len(json_obj["results"]["shop"]) > 0):
        shop = json_obj["results"]["shop"][0]
        text = "%s [at] %s\n%s" % (shop["name"], shop["address"], shop["urls"]["pc"])
        cache[keyword] = text
        return text
    else:
        return "Oops... not found."

def say(text, to_user):
    """Slackの形式でJSONを返す"""
    app.logger.debug("say start")
    return jsonify({
        "text": "@%s %s" % (to_user, text), # 投稿する内容
        "username": BOT_NAME, # bot名
        "icon_emoji": "", # botのiconを絵文字の中から指定
    })

if __name__ == '__main__':
  app.run(debug = True)
