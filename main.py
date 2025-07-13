from fastapi import FastAPI, Request, Header
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import re
from datetime import datetime

app = FastAPI()

# LINE認証
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.post("/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    handler.handle(body.decode(), x_line_signature)
    return {"message": "ok"}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text.strip()

    # 20250722 のような日付8桁形式を探す
    m = re.search(r"\b(20\d{6})\b", user_text)
    if not m:
        reply = "日付を8桁 (例: 20250722) で送ってください"
    else:
        date_str = m.group(1)
        try:
            dt = datetime.strptime(date_str, "%Y%m%d")
            # 祝日判定：文字に (祝) が含まれる場合だけの仕様を仮定するのでスキップ
            if dt.weekday() == 6:  # Sunday
                reply = f"{dt.strftime('%Y年%m月%d日')} は日曜のため利用できません"
            else:
                url = f"https://www.undoukai-reserve.com/facility/reserve/goten/daytable.php?yearmonthday={date_str}&place=gymnasium"
                reply = f"こちらをご確認ください：\n{url}"
        except ValueError:
            reply = "日付の形式が正しくありません"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )