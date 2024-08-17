import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からAPIキーを取得
api_key = os.getenv('GOOGLE_API_KEY')

# APIキーが取得できたか確認
if not api_key:
    raise ValueError("GOOGLE_API_KEYが設定されていません。.envファイルを確認してください。")

genai.configure(api_key=api_key)

model_id = "gemini-1.5-flash-001"  # input 0.35/MTokens - output 1.05/MTokens

# モデル情報の初期化
model = genai.GenerativeModel(model_id)

# 生成AIのパラメータ設定
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0.7,
}
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
}

def generate_schedule(date, events):
    prompt = f"""
    {date.strftime('%Y年%m月%d日')}の予定は以下の通りです：

    {chr(10).join(events)}

    これらの予定を考慮して、以下の点に注意しながら1日のスケジュールを立ててください：
    1. 予定の間に適切な休憩時間を入れてください。
    2. 朝食、昼食、夕食の時間を確保してください。
    3. バイト先に行くのに1時間、帰るのに1時間かかるので、その時間を確保してください。
    4. 予定で指定された時間以外はバイトをいれることができません。
    5. 睡眠時間を8時間確保してください。
    6. スケジュールは必ず「**HH:MM-HH:MM 活動内容**」の形式で記述してください。例: **07:00-08:00 朝食**
    7. 備考を出力しないでください。
    8. バイトの予定がないとき、移動時間を入れないでください。
    9. 移動時間は、バイトの時間に含まれません。

    スケジュール：
    """

    response = model.generate_content(prompt)
    return response.text