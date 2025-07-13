from fastapi import FastAPI, Request, Header
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import re
from datetime import datetime
from urllib.parse import quote

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
            date_str = dt.strftime('%Y%m%d')

            # 日曜日の判定（祝日は今後拡張可）
            if dt.weekday() == 6:
                reply = f"{dt.strftime('%Y年%m月%d日')} は日曜のため利用できません"
            else:
                # URL生成
                goten_url = f"https://www.undoukai-reserve.com/facility/reserve/goten/daytable.php?yearmonthday={date_str}&place=gymnasium"
                arakawa_url = "https://www.arakawa-sposen.com/category/info/"
                minato_url = "https://minatoku-sports.com/schedule/"

                # 文京区：PDFファイルURL（エンコード付き）
                year = dt.strftime('%Y')
                yymm = dt.strftime('%y%m')
                month = dt.month
                dir_month = f"{month - 1:02d}" if month > 1 else "12"
                dir_year = year if month > 1 else str(int(year) - 1)

                filename = f"一般公開　予定表{yymm}-.pdf"
                filename_encoded = quote(filename)
                bunkyo_url = f"https://www.shisetsu-tds.jp/tokyo-bunkyo-sogotaiikukan/wp-content/uploads/sites/93/{dir_year}/{dir_month}/{filename_encoded}"

                reply = "\n\n".join([
                    f"御殿下体育館：\n{goten_url}",
                    f"荒川総合スポーツセンター：\n{arakawa_url}",
                    f"港区スポーツセンター：\n{minato_url}",
                    f"文京区総合体育館：\n{bunkyo_url}"
                ])

        except ValueError:
            reply = "日付の形式が正しくありません（例：20250722）"
    else:
        reply = "日付を8桁（例：20250722）または yyyy-mm-dd 形式で入力してください。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )