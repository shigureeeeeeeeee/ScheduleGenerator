import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def get_events_for_date(service, date):
    start_of_day = datetime.datetime.combine(date, datetime.time.min).isoformat() + 'Z'
    end_of_day = datetime.datetime.combine(date, datetime.time.max).isoformat() + 'Z'

    print(f"{date.strftime('%Y年%m月%d日')}の予定を取得しています...")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return events_result.get("items", [])

def print_events(events):
    if not events:
        print("この日の予定はありません。")
        return
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))
        
        # 日付のみの場合と時間も含む場合で処理を分ける
        if 'T' in start:  # 時間が含まれている場合
            start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
            start_str = start_dt.strftime("%H:%M")
            end_str = end_dt.strftime("%H:%M")
            print(f"{start_str}～{end_str}: {event['summary']}")
        else:  # 終日イベントの場合
            print(f"終日: {event['summary']}")

def get_date_from_user():
    today = datetime.date.today()
    year = today.year
    month = today.month

    year_input = input(f"年を入力してください（デフォルト: {year}）: ")
    if year_input:
        try:
            year = int(year_input)
        except ValueError:
            print("無効な年です。現在の年を使用します。")

    month_input = input(f"月を入力してください（デフォルト: {month}）: ")
    if month_input:
        try:
            month = int(month_input)
            if month < 1 or month > 12:
                raise ValueError
        except ValueError:
            print("無効な月です。現在の月を使用します。")

    while True:
        day_input = input("日を入力してください: ")
        try:
            day = int(day_input)
            return datetime.date(year, month, day)
        except ValueError:
            print("無効な日付です。もう一度入力してください。")

def main():
    try:
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)

        target_date = get_date_from_user()
        events = get_events_for_date(service, target_date)
        print_events(events)
    except HttpError as error:
        print(f"エラーが発生しました: {error}")

if __name__ == "__main__":
    main()