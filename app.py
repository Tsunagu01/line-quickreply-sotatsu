from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction
)
# パスを扱うためのOSモジュールをインポート
import os

app = Flask(__name__)

# ★★★ ここにあなたのアクセス情報を設定してください (必須) ★★★
YOUR_CHANNEL_ACCESS_TOKEN = "wz76WqyigigdALZ/ryJ6pee8AkRtZGupRLMET4E6/FbYjykULYyA8MFbIUYuLq15BvpTlGnV94NwEJRtjz/UFyzxFxYv/gWpILIL/bfSfbl9lKYScjXnJtCw1bIS3pX8B7Kxa6mfm/8pfqFreSU8OgdB04t89/1O/w1cDnyilFU=" 
YOUR_CHANNEL_SECRET = "d0937484949a957ea5c1565fed548ef7" 

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# ★★★ 修正箇所: ファイルの絶対パスを自動で定義する ★★★
# app.pyが存在するディレクトリと、ファイル名 'saisoku.txt' を結合して、
# 実行環境に依存しない絶対パスを自動で生成します。
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, 'saisoku.txt')
# ----------------------------------------------------

# WebhookからのPOSTリクエストを受け付けるルート
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Check your channel access token/secret.")
        abort(400)
    return 'OK'

# メッセージイベントの処理（Botにメッセージが送られたとき）
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    # --- saisoku.txt から返信メッセージの内容を読み込む ---
    try:
        # 'utf-8-sig'は、メモ帳で保存されがちなBOM付きUTF-8でも安全に読み込めます。
        with open(FILE_PATH, 'r', encoding='utf-8-sig') as f:
            reply_text = f.read()
            # 読み込みが成功した場合、コンソールに確認メッセージを出力
            print("--- ファイル読み込み成功（自動パス）---")
            print(f"読み込んだパス: {FILE_PATH}")
            print(f"読み込んだテキストの最初の20文字: {reply_text[:20].replace('\n', ' ')}")
            print("----------------------------------")
    except FileNotFoundError:
        # ファイルが見つからない場合のエラーメッセージ
        # ユーザーに表示されるメッセージは固定
        reply_text = "【システムエラー】自動送信文ファイルが絶対パスでも見つかりません。開発者にご連絡ください。"
        # コンソールにはより詳細なエラー情報を表示
        print(f"重大エラー: ファイルが定義されたパス ({FILE_PATH}) に見つかりません。app.pyと同じフォルダにsaisoku.txtがあるか確認してください。")
    except Exception as e:
        # その他のエラーが発生した場合
        reply_text = f"【システムエラー】メッセージの準備中に予期せぬエラーが発生しました: {e}"
        print(f"ファイル読み込み中に予期せぬエラーが発生しました: {e}")

    # --- クイックリプライボタンの定義 ---
    quick_reply_items = [
        # ①ボタン: タップで「①の日程を希望します」というメッセージをBotに送る
        QuickReplyButton(action=MessageAction(label="①", text="①の日程を希望します")), 
        # ②ボタン: タップで「②の日程を希望します」というメッセージをBotに送る
        QuickReplyButton(action=MessageAction(label="②", text="②の日程を希望します")),
        # ③ボタン: タップで「③の日程を希望します」というメッセージをBotに送る
        QuickReplyButton(action=MessageAction(label="③", text="③の日程を希望します"))
    ]

    # --- クイックリプライ付きメッセージの作成 ---
    message_with_quick_reply = TextSendMessage(
        text=reply_text,  # 読み込んだファイルの内容を設定
        quick_reply=QuickReply(items=quick_reply_items)
    )

    # ユーザーにメッセージを返信
    line_bot_api.reply_message(
        event.reply_token,
        message_with_quick_reply
    )

if __name__ == "__main__":
    # Flaskサーバーを起動
    app.run(host='0.0.0.0', port=5000)
