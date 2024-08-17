import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from google_calendar_api import get_events_for_date, get_credentials
from schedule_parser import parse_schedule
from schedule_visualizer import visualize_schedule
from gemini_integration import generate_schedule
import json
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re

class CalendarApp:
    def __init__(self, master):
        self.master = master
        master.title("Googleカレンダー予定取得")
        master.geometry("1000x800")  # ウィンドウサイズを拡大

        # 入力フィールドとラベルを配置するフレーム
        input_frame = ttk.Frame(master)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        self.year_label = ttk.Label(input_frame, text="年:")
        self.year_label.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="e")
        self.year_entry = ttk.Entry(input_frame, width=10)
        self.year_entry.grid(row=0, column=1, padx=5, pady=5)
        self.year_entry.insert(0, str(date.today().year))

        self.month_label = ttk.Label(input_frame, text="月:")
        self.month_label.grid(row=1, column=0, padx=(0, 5), pady=5, sticky="e")
        self.month_entry = ttk.Entry(input_frame, width=10)
        self.month_entry.grid(row=1, column=1, padx=5, pady=5)
        self.month_entry.insert(0, str(date.today().month))

        self.day_label = ttk.Label(input_frame, text="日:")
        self.day_label.grid(row=2, column=0, padx=(0, 5), pady=5, sticky="e")
        self.day_entry = ttk.Entry(input_frame, width=10)
        self.day_entry.grid(row=2, column=1, padx=5, pady=5)
        self.day_entry.insert(0, str(date.today().day))

        self.get_events_button = ttk.Button(input_frame, text="予定を取得", command=self.get_events)
        self.get_events_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        # スケジュール表示用のテキストウィジェット
        self.output_text = tk.Text(master, height=15, width=80, state='disabled')
        self.output_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # グラフ表示用のキャンバス
        self.canvas_frame = ttk.Frame(master)
        self.canvas_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # グリッドの設定
        master.grid_columnconfigure(1, weight=1)
        master.grid_rowconfigure(1, weight=1)

        # canvasを初期化
        self.canvas = None

        self.service = None
        try:
            creds = get_credentials()
            self.service = build("calendar", "v3", credentials=creds)
        except HttpError as error:
            messagebox.showerror("エラー", f"エラーが発生しました: {error}")

        self.data_file = "calendar_data.json"
        self.data = {}  # データを格納するディクショナリを初期化
        self.load_data()  # アプリケーション起動時にデータを読み込む
        self.display_saved_data()  # 保存されたデータを表示

        # ウィンドウが閉じられる際にデータを保存するイベントを設定
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def save_schedule(self, target_date, schedule_text, schedule):
        """スケジュールデータを保存する"""
        date_str = target_date.strftime("%Y-%m-%d")
        self.data = {  # 既存のデータを上書きする
            date_str: {
                "schedule_text": schedule_text,
                "schedule": schedule
            }
        }
        self.save_data()
        print(f"データを保存しました: {self.data}")  # デバッグ用

    def save_data(self):
        """データをJSONファイルに保存する"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """保存されたデータを読み込む"""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            print(f"データを読み込みました: {self.data}")  # デバッグ用
        except FileNotFoundError:
            print("データファイルが見つかりません。新しいファイルを作成します。")
            self.data = {}
        except json.JSONDecodeError:
            print("JSONファイルの解析に失敗しました。新しいデータファイルを作成します。")
            self.data = {}

    def display_saved_data(self):
        """保存されたデータを表示する"""
        if self.data:
            print("保存されたデータ:", self.data)  # デバッグ用
            # 最新の日付のデータを探す
            latest_date = None
            for key in self.data.keys():
                if key.startswith('20') and len(key) == 10:  # 日付形式のキーを探す
                    if latest_date is None or key > latest_date:
                        latest_date = key

            if latest_date:
                date = datetime.strptime(latest_date, "%Y-%m-%d").date()
                saved_data = self.data[latest_date]

                self.year_entry.delete(0, tk.END)
                self.year_entry.insert(0, str(date.year))
                self.month_entry.delete(0, tk.END)
                self.month_entry.insert(0, str(date.month))
                self.day_entry.delete(0, tk.END)
                self.day_entry.insert(0, str(date.day))

                self.output_text.config(state='normal')
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, saved_data["schedule_text"])
                self.output_text.config(state='disabled')

                schedule = saved_data["schedule"]
                fig = visualize_schedule(schedule, date)
                if fig:
                    if self.canvas:
                        self.canvas.get_tk_widget().destroy()
                    self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
                    self.canvas.draw()
                    self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
                    self.canvas_frame.grid_columnconfigure(0, weight=1)
                    self.canvas_frame.grid_rowconfigure(0, weight=1)
                else:
                    self.output_text.insert(tk.END, "\nスケジュールを視覚化できませんでした。")
            else:
                print("有効な日付のデータが見つかりません。")
        else:
            print("保存されたデータがありません。")

    def get_events(self):
        try:
            year = int(self.year_entry.get())
            month = int(self.month_entry.get())
            day = int(self.day_entry.get())
            target_date = date(year, month, day)
            events = get_events_for_date(self.service, target_date)

            self.output_text.config(state='normal')
            self.output_text.delete('1.0', tk.END)

            if not events:
                self.output_text.insert(tk.END, "この日の予定はありません。")
            else:
                events_list = []
                for event in events:
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    end = event["end"].get("dateTime", event["end"].get("date"))
                    if 'T' in start:
                        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                        start_str = start_dt.strftime("%H:%M")
                        end_str = end_dt.strftime("%H:%M")
                        event_str = f"{start_str}～{end_str}: {event['summary']}"
                    else:
                        event_str = f"終日: {event['summary']}"
                    
                    self.output_text.insert(tk.END, event_str + "\n")
                    events_list.append(event_str)

                # Geminiを使用してスケジュールを立てる
                schedule_text = generate_schedule(target_date, events_list)
                self.output_text.insert(tk.END, "\n--- Geminiによるスケジュール提案 ---\n" + schedule_text)
                print("Geminiが生成したスケジュール:")
                print(schedule_text)

                # スケジュールを解析して視覚化
                schedule = parse_schedule(schedule_text)
                print("解析されたスケジュール:")
                print(schedule)

                if schedule:
                    fig = visualize_schedule(schedule, target_date)
                    if fig:
                        # 既存のキャンバスを削除
                        if self.canvas:
                            self.canvas.get_tk_widget().destroy()

                        # 新しいキャンバスを作成
                        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
                        self.canvas.draw()
                        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
                        self.canvas_frame.grid_columnconfigure(0, weight=1)
                        self.canvas_frame.grid_rowconfigure(0, weight=1)
                    else:
                        self.output_text.insert(tk.END, "\nスケジュールを視覚化できませんでした。")
                else:
                    self.output_text.insert(tk.END, "\nスケジュールを解析できませんでした。")

                # スケジュールデータを保存
                self.save_schedule(target_date, schedule_text, schedule)

            self.output_text.config(state='disabled')
        except ValueError:
            messagebox.showerror("エラー", "無効な日付です。正しい日付を入力してください。")
        except HttpError as error:
            messagebox.showerror("エラー", f"エラーが発生しました: {error}")

    def on_closing(self):
        """ウィンドウが閉じられる際の処理"""
        self.save_data()
        self.master.destroy()

def parse_schedule(schedule_text):
    schedule = []
    print("解析するスケジュールテキスト:")
    print(schedule_text)
    for line in schedule_text.split('\n'):
        print(f"処理中の行: {line}")
        # 修正された正規表現パターン
        match = re.match(r'\*\*(\d{2}:\d{2})-(\d{2}:\d{2})\s*(.+)\*\*', line.strip())
        if not match:
            match = re.match(r'(\d{2}:\d{2})-(\d{2}:\d{2})\s*(.+)', line.strip())
        if match:
            start_time, end_time, activity = match.groups()
            schedule.append((start_time, end_time, activity))
            print(f"マッチした行: {start_time} - {end_time}: {activity}")
        else:
            print(f"マッチしなかった行: {line}")
    print(f"解析されたスケジュール: {schedule}")
    return schedule