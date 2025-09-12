import datetime
import pytz
from timetable.models import Timetable

def get_todays_classes(timetable: Timetable):
    tz = pytz.timezone(timetable.timezone)
    today = datetime.datetime.now(tz).date()
    weekday = today.strftime('%a') # Mon, Tue, etc.

    if not (timetable.semester_start <= today <= timetable.semester_end):
        return []

    if today in timetable.holidays:
        return []

    todays_classes = [
        c for c in timetable.classes 
        if weekday in c.days
    ]

    return sorted(todays_classes, key=lambda c: c.start)

def format_message(classes, timezone_str):
    tz = pytz.timezone(timezone_str)
    today = datetime.datetime.now(tz)
    date_str = today.strftime("%Y-%m-%d, %a")

    if not classes:
        return f"No classes today.\n({date_str})"

    title = f"Today's Classes ({date_str})"
    
    class_lines = []
    for c in classes:
        start_time = c.start.strftime("%H:%M")
        end_time = c.end.strftime("%H:%M")
        class_lines.append(
            f"{start_time}–{end_time} | {c.name} | {c.room} | {c.professor}"
        )

    return "\n".join([title] + class_lines)
