import json
import csv
from pathlib import Path
from typing import List
from .models import Timetable, ClassItem
import datetime

def load_from_json(file_path: str) -> Timetable:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return Timetable(**data)

def load_from_csv(file_path: str) -> Timetable:
    classes = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['days'] = row['days'].split('|')
            classes.append(ClassItem(**row))
    # CSV doesn't contain metadata, so we use defaults or placeholders.
    # This part might need to be adjusted based on how metadata is provided for CSVs.
    return Timetable(
        semester_start=datetime.date(2025, 1, 1),
        semester_end=datetime.date(2025, 12, 31),
        classes=classes
    )
