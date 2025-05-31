from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from datetime import datetime

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = 'UTgP0Vqiv+5fiF2BwAgol4aiNqq8GkGzrj1nfvbcctdeEEy0zs9r9czhsQdWZDZLhlpzL36JXlfWybO/NDVk59LlCnvo/kL8L5luw/fY5HAMf3OTZQE95VCih9WrLB7E24bpx3Xkb5IzwOiUBncHtAdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'fc09bbd6a7b5904836b8832795e27c7c'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

user_sessions = {}

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
    user_id = event.source.user_id
    text = event.message.text
    now = datetime.now()

    if text == "勉強始める":
        user_sessions[user_id] = now
        reply = f"勉強を開始しました！（{now.strftime('%H:%M')}）"
    elif text == "終わった":
        if user_id in user_sessions:
            start = user_sessions.pop(user_id)
            minutes = (now - start).seconds // 60
            reply = f"おつかれさま！勉強時間は {minutes} 分でした。"
        else:
            reply = "勉強開始が記録されていません。「勉強始める」と送ってください。"
    else:
        reply = "「勉強始める」または「終わった」と送ってください。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run()
