import re

def parse_schedule(schedule_text):
    schedule = []
    for line in schedule_text.split('\n'):
        match = re.match(r'\*\*(\d{2}:\d{2})-(\d{2}:\d{2})\s*(.+)\*\*', line.strip())
        if match:
            start_time, end_time, activity = match.groups()
            schedule.append((start_time, end_time, activity))
    return schedule