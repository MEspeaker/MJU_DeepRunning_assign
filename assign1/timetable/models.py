from pydantic import BaseModel, Field, validator
from typing import List
import datetime

class ClassItem(BaseModel):
    name: str
    professor: str
    room: str
    days: List[str]
    start: datetime.time
    end: datetime.time

    @validator('days', each_item=True)
    def validate_days(cls, v):
        if v not in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            raise ValueError('Invalid day string')
        return v

class Timetable(BaseModel):
    timezone: str = "Asia/Seoul"
    semester_start: datetime.date
    semester_end: datetime.date
    holidays: List[datetime.date] = []
    classes: List[ClassItem]
