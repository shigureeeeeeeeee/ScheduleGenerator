import matplotlib.pyplot as plt
import japanize_matplotlib
from matplotlib.patches import Rectangle
from datetime import datetime
import numpy as np

def visualize_schedule(schedule, date):
    print("視覚化するスケジュール:")
    print(schedule)
    if not schedule:
        print("スケジュールが空です。視覚化をスキップします。")
        return None

    fig, ax = plt.subplots(figsize=(8, 12))  # グラフのサイズを調整
    ax.set_ylim(0, 24)
    ax.set_yticks(range(0, 25))
    ax.set_yticklabels([f'{h:02d}:00' for h in range(0, 25)])
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.invert_yaxis()  # 時間軸を上から下に

    ax.set_title(f'{date.strftime("%Y年%m月%d日")}のスケジュール', fontsize=16)
    ax.set_xlabel('活動', fontsize=12)

    colors = plt.cm.Set3(np.linspace(0, 1, len(schedule)))  # カラーパレットの設定

    for (start, end, activity), color in zip(schedule, colors):
        start_time = datetime.strptime(start, "%H:%M")
        end_time = datetime.strptime(end, "%H:%M")
        
        start_hour = start_time.hour + start_time.minute / 60
        end_hour = end_time.hour + end_time.minute / 60
        
        if end_hour < start_hour:  # 日をまたぐ場合
            # 日をまたぐ部分を2つに分けて描画
            rect1 = Rectangle((0, start_hour), 1, 24 - start_hour, facecolor=color, alpha=0.7)
            rect2 = Rectangle((0, 0), 1, end_hour, facecolor=color, alpha=0.7)
            ax.add_patch(rect1)
            ax.add_patch(rect2)
            
            # テキストは真ん中に配置
            text_y = (start_hour + 24 + end_hour) / 2
            if text_y > 24:
                text_y -= 24
            ax.text(0.5, text_y, activity, ha='center', va='center', fontsize=10, fontweight='bold', wrap=True)
        else:
            duration = end_hour - start_hour
            rect = Rectangle((0, start_hour), 1, duration, facecolor=color, alpha=0.7)
            ax.add_patch(rect)
            ax.text(0.5, start_hour + duration/2, activity, 
                    ha='center', va='center', fontsize=10, fontweight='bold', wrap=True)
        
        ax.axhline(y=start_hour, color='gray', linestyle='--', linewidth=0.5)

    # 現在時刻を示す赤い線を追加
    now = datetime.now()
    current_hour = now.hour + now.minute / 60
    ax.axhline(y=current_hour, color='red', linestyle='-', linewidth=2)
    ax.text(1.01, current_hour, '現在', color='red', va='center', fontsize=10)

    plt.tight_layout()
    return fig