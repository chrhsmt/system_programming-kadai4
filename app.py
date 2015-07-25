# -*- coding: utf-8 -*-
from flask import Flask, url_for, request
import urllib
import urllib2
import json
import os

BOT_NAME = "harahe"

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
    trigger_word = ""  # OutgoingWebhooksに設定したトリガー

    def __init__(self, params):
        self.team_id = params["team_id"]
        self.channel_id = params["channel_id"]
        self.channel_name = params["channel_name"]
        self.timestamp = params["timestamp"]
        self.user_id = params["user_id"]
        self.user_name = params["user_name"]
        self.text = params["text"]
        self.trigger_word = params["trigger_word"]

    def __str__(self):
        res = self.__class__.__name__
        res += "@{0.token}[channel={0.channel_name}, user={0.user_name}, text={0.text}]".format(self)
        return res

app = Flask(__name__)

@app.route('/', methods=["POST"])
def index():
    app.logger(request.form)
    msg = Message(request.form)
    app.logger.debug(msg)
    if msg.user_name == BOT_NAME:
        return ""
    if BOT_NAME in msg.text:
        return say(recommend(msg.text.split()[-1]))

def recommend(keyword):
    keyword = urllib.quote(keyword)
    request = urllib2.Request("http://webservice.recruit.co.jp/hotpepper/gourmet/v1/", data="keyword=%s&format=json&is_open_time=now&key=%s" % (keyword, os.environ['API_KEY']))
    response = urllib2.urlopen(request)
    return json.loads(response.read())["results"]["shop"][0]["name"]

def say(str):
    """Slackの形式でJSONを返す"""
    return jsonify({
        "text": text, # 投稿する内容
        "username": "mybot", # bot名
        "icon_emoji": "", # botのiconを絵文字の中から指定
    })

if __name__ == '__main__':
  app.run(debug = True)
