import os
from fastapi import FastAPI, Request, Header
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.post("/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    try:
        handler.handle(body.decode(), x_line_signature)
    except InvalidSignatureError:
        return {"message": "invalid signature"}
    return {"message": "ok"}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    reply_text = "\n".join([
        "御殿下体育館（1/5）：https://www.undoukai-reserve.com/facility/reserve/goten/calendar.php",
        "荒川総合スポーツセンター（2/5）：https://example.com/aragawa",  # 仮リンク
        "港区スポーツセンター（3/5）：https://example.com/minato",      # 仮リンク
        "文京区総合体育館（4/5）：https://example.com/bunkyo",         # 仮リンク
        "江戸川スポーツセンター（5/5）：https://example.com/edogawa"   # 仮リンク
    ])
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )