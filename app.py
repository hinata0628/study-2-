from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from datetime import datetime
import pytz

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

daily_totals = {}  # 勉強時間を記録する辞書（簡易例）

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

    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst).strftime('%Y/%m/%d %H:%M:%S')
    date_str = datetime.now(jst).strftime('%Y-%m-%d')

    if user_message == '開始':
        response = f'🟢 勉強を開始しました！\n🕒 記録時刻：{now}'
    elif user_message == '終了':
        response = f'🔴 勉強を終了しました！\n🕒 記録時刻：{now}'
    elif user_message == '今日':
        total_seconds = daily_totals.get(user_id, {}).get(date_str, 0)
        mins = int(total_seconds // 60)
        hrs = mins // 60
        m = mins % 60
        response = f'🟢 今日（{date_str}）の勉強時間：{hrs}時間{m}分'
    elif user_message == 'いままで':
        total_seconds = sum(daily_totals.get(user_id, {}).values())
        mins = int(total_seconds // 60)
        hrs = mins // 60
        m = mins % 60
        response = f'📚 これまでの勉強時間：{hrs}時間{m}分'
    else:
        response = '「勉強始める」または「勉強終わる」と送ってください。'

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )

print("LINE_CHANNEL_SECRET:", LINE_CHANNEL_SECRET)
print("LINE_CHANNEL_ACCESS_TOKEN:", LINE_CHANNEL_ACCESS_TOKEN)
