from flask import Flask, request, abort
import json
import requests
from pyquery import PyQuery as pq
import regex

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('i74nB4XNbr0LeXp8Dxce7A47/VYWjHEOzcAlYXsduEVnbL/7GBHRD/6o3RQZnMtBG0W8EzaSbCTf2XtJftDZZXmTp5+fRLpcwr+s70X9J7lRbwO3FH4gOqWoT5u4QTrI0KRnop8IY8prxNWrkcvnSQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('2129e122903ec7666aaf9ecfce19e3f0')

zodiac=[
    '牡羊','金牛','雙子','巨蟹','獅子','處女','天秤','天蠍','射手','魔羯','水瓶','雙魚',
    'Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'
]

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    if text.lower()=='hello':
        message = json.load(open('introduction.json','r',encoding='utf-8'))
        line_bot_api.reply_message(event.reply_token, FlexSendMessage('hello',message))
    elif text.lower() in zodiac:
        matchObj=regex.match(r'[a-z]+',text.lower()) # whether text is English or not
        if matchObj: # English
            res = requests.get("https://askastrology.com/zodiac-compatibility/taurus-compatibility/taurus-"+text.lower()+"/")
            doc = pq(res.text)
            match_score = doc("div > div.score").text()
            message = json.load(open('matchResult.json','r',encoding='utf-8'))
            message['body']['contents'][3]['text'] = "Your zodiac sign is: " + zodiac[zodiac.index(text)-12] + "/ " + text
            message['body']['contents'][5]['text'] = match_score + "%"
            message['body']['contents'][6]['action']['uri'] = "https://askastrology.com/zodiac-compatibility/taurus-compatibility/taurus-"+text.lower()+"/"
            line_bot_api.reply_message(event.reply_token, FlexSendMessage('match',message))
        else:
            eng_text = zodiac[zodiac.index(text)+12]
            res = requests.get("https://askastrology.com/zodiac-compatibility/taurus-compatibility/taurus-"+eng_text.lower()+"/")
            doc = pq(res.text)
            match_score = doc("div > div.score").text()
            message = json.load(open('matchResult.json','r',encoding='utf-8'))
            message['body']['contents'][3]['text'] = "Your zodiac sign is: " + text + "/ " + eng_text
            message['body']['contents'][5]['text'] = match_score + "%"
            message['body']['contents'][6]['action']['uri'] = "https://askastrology.com/zodiac-compatibility/taurus-compatibility/taurus-"+eng_text.lower()+"/"
            line_bot_api.reply_message(event.reply_token, FlexSendMessage('match',message))
    

@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'project':
        message = json.load(open('project.json','r',encoding='utf-8'))
        line_bot_api.reply_message(event.reply_token, FlexSendMessage('project',message))
    elif event.postback.data == 'about_me':
        message = json.load(open('aboutMe.json','r',encoding='utf-8'))
        line_bot_api.reply_message(event.reply_token, FlexSendMessage('about_me',message))
    elif event.postback.data == 'character':
        message = json.load(open('character.json','r',encoding='utf-8'))
        line_bot_api.reply_message(event.reply_token, FlexSendMessage('character',message))
    elif event.postback.data == 'match':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="你的星座是？\nEx: 牡羊\nWhat's your zodiac sign？\nEx: Aries")
        )
    elif event.postback.data == 'api_introduction':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Tweet C.A.R.D. API 是一款「信用卡推薦API」，APP的開發者、銀行端與TSP業者都能串接此API，讓使用者能獲得更個人化的推薦結果。\n此推薦API會將使用者依據其基本資訊、優惠偏好和消費金額找尋相似用戶，並根據消費者的定位地點與當下的環境因素（例如：時間、移動速度），來推薦最符合消費者當下需求的信用卡。")
        )
    elif event.postback.data == 'ptt_introduction':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Group Buying Trend Prediction for PTT 能預測PTT團購版下一個時間點團購量的趨勢！\n會將PTT團購資訊依據蝦皮類別來分類，再根據彼此間的相關性與個別的PageRank score，找出對PTT團購總量有預測能力的類別們！")
        )

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
