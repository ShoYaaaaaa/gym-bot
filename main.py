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

    # yyyy-mm-dd / yyyymmdd / yyyy/mm/dd 対応
    match = re.search(r'(\d{4})[-/]?(\d{2})[-/]?(\d{2})', user_text)
    
    if match:
        y, m, d = match.groups()
        try:
            dt = datetime.strptime(f"{y}{m}{d}", "%Y%m%d")

            if dt.weekday() == 6:
                reply = f"{dt.strftime('%Y年%m月%d日')} は日曜のため利用できません"
            else:
                date_str = dt.strftime('%Y%m%d')
                reply = (
                    f"御殿下体育館（1/5）：https://www.undoukai-reserve.com/facility/reserve/goten/daytable.php?yearmonthday={date_str}&place=gymnasium"
                )
        except ValueError:
            reply = "日付の形式が正しくありません"
    else:
        # 日付が含まれない場合はリンク一覧を案内
        reply = "\n".join([
            "御殿下体育館（1/5）：https://www.undoukai-reserve.com/facility/reserve/goten/calendar.php",
            "荒川総合スポーツセンター（2/5）：https://example.com/aragawa",
            "港区スポーツセンター（3/5）：https://example.com/minato",
            "文京区総合体育館（4/5）：https://example.com/bunkyo",
            "江戸川スポーツセンター（5/5）：https://example.com/edogawa"
        ])

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )