# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from flask import Flask, request, jsonify
import urllib
import urllib2
import json
import os

app = Flask(__name__)

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
    service_id = ""
    team_domain = ""
    trigger_word = ""  # OutgoingWebhooksに設定したトリガー

    def __init__(self, params):
        # self.token = params["token"]
        # self.team_id = params["team_id"]
        # self.channel_id = params["channel_id"]
        # self.channel_name = params["channel_name"]
        # self.timestamp = params["timestamp"]
        # self.user_id = params["user_id"]
        # self.user_name = params["user_name"]
        self.text = params["text"]
        # self.team_domain = params["team_domain"]
        # self.service_id = params["service_id"]
        if (params.has_key("trigger_word")):
            self.trigger_word = params["trigger_word"]

    def __str__(self):
        res = self.__class__.__name__
        res += "@{0.token}[channel={0.channel_name}, user={0.user_name}, text={0.text}]".format(self)
        return res

@app.route('/', methods=["POST", "GET"])
def index():
    print (request.form)
    app.logger.info("----------")
    app.logger.debug(request.form)
    try:
        if (request.method == "POST"):
            msg = Message(request.form)
            app.logger.debug(msg)
        if msg.user_name == BOT_NAME:
            return ""
        if BOT_NAME in msg.text:
            return say(recommend(msg.text.split()[-1]))
        else:
            return ""
    except Exception, e:
        print (e)
        return e
    else:
        pass
    finally:
        pass

def recommend(keyword):
    print ("recommend start")
    keyword = urllib.quote(keyword.encode("UTF-8"))
    print ("keyword %s" % keyword)
    request = urllib2.Request("http://webservice.recruit.co.jp/hotpepper/gourmet/v1/?keyword=%s&format=json&is_open_time=now&key=%s" % (keyword, os.environ['API_KEY']))
    print (request.get_full_url())
    response = urllib2.urlopen(request)
    json_obj = json.loads(response.read())
    if (len(json_obj["results"]["shop"]) > 0):
        return json_obj["results"]["shop"][0]["name"]
    else:
        return "Oops... none"

def say(text):
    """Slackの形式でJSONを返す"""
    print ("say start")
    return jsonify({
        "text": text, # 投稿する内容
        "username": BOT_NAME, # bot名
        "icon_emoji": "", # botのiconを絵文字の中から指定
    })

if __name__ == '__main__':
  app.run(debug = True)
