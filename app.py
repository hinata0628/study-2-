from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from datetime import datetime
import pytz  # ← 追加（日本時間にするために必要）

app = Flask(__name__)

# 環境変数からLINEチャネル情報を取得（Renderなどに安全に保存する方法）
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    user_id = event.source.user_id

    # 日本時間にする
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst).strftime('%Y/%m/%d %H:%M:%S')

    if user_message == '開始':
        response = f'🟢 勉強を開始しました！\n🕒 記録時刻：{now}'
    elif user_message == '終了':
        response = f'🔴 勉強を終了しました！\n🕒 記録時刻：{now}'
    else:
        response = '「勉強始める」または「勉強終わる」と送ってください。'

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )
