import datetime
import os.path
import tkinter as tk
from tkinter import ttk, messagebox
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

class CalendarApp:
    def __init__(self, master):
        self.master = master
        master.title("Googleカレンダー予定取得")

        self.year_label = ttk.Label(master, text="年:")
        self.year_label.grid(row=0, column=0, padx=5, pady=5)
        self.year_entry = ttk.Entry(master, width=10)
        self.year_entry.grid(row=0, column=1, padx=5, pady=5)
        self.year_entry.insert(0, str(datetime.date.today().year))

        self.month_label = ttk.Label(master, text="月:")
        self.month_label.grid(row=1, column=0, padx=5, pady=5)
        self.month_entry = ttk.Entry(master, width=10)
        self.month_entry.grid(row=1, column=1, padx=5, pady=5)
        self.month_entry.insert(0, str(datetime.date.today().month))

        self.day_label = ttk.Label(master, text="日:")
        self.day_label.grid(row=2, column=0, padx=5, pady=5)
        self.day_entry = ttk.Entry(master, width=10)
        self.day_entry.grid(row=2, column=1, padx=5, pady=5)
        self.day_entry.insert(0, str(datetime.date.today().day))

        self.get_events_button = ttk.Button(master, text="予定を取得", command=self.get_events)
        self.get_events_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.output_text = tk.Text(master, height=10, width=50, state='disabled')
        self.output_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        self.service = None
        try:
            creds = get_credentials()
            self.service = build("calendar", "v3", credentials=creds)
        except HttpError as error:
            messagebox.showerror("エラー", f"エラーが発生しました: {error}")

    def get_events(self):
        try:
            year = int(self.year_entry.get())
            month = int(self.month_entry.get())
            day = int(self.day_entry.get())
            target_date = datetime.date(year, month, day)
            events = get_events_for_date(self.service, target_date)

            self.output_text.config(state='normal')
            self.output_text.delete('1.0', tk.END)

            if not events:
                self.output_text.insert(tk.END, "この日の予定はありません。")
            else:
                for event in events:
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    end = event["end"].get("dateTime", event["end"].get("date"))
                    if 'T' in start:
                        start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                        end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
                        start_str = start_dt.strftime("%H:%M")
                        end_str = end_dt.strftime("%H:%M")
                        self.output_text.insert(tk.END, f"{start_str}～{end_str}: {event['summary']}\n")
                    else:
                        self.output_text.insert(tk.END, f"終日: {event['summary']}\n")

            self.output_text.config(state='disabled')
        except ValueError:
            messagebox.showerror("エラー", "無効な日付です。正しい日付を入力してください。")
        except HttpError as error:
            messagebox.showerror("エラー", f"エラーが発生しました: {error}")

def main():
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()