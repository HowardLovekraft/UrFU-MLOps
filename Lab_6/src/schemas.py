from array import array
from enum import Enum

from pydantic import BaseModel, Field


class WeekDay(str, Enum):
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'


class Period(str, Enum):
    NO_1 = '1st Period'
    NO_2 = '2nd Period'
    NO_3 = '3rd Period'
    NO_4 = '4th Period'
    NO_5 = '5th Period'


class Subject(str, Enum):
    MATH = 'Mathematics'
    PHYS = 'Physics'
    BIO = 'Biology'
    HST = 'History'
    ENG = 'English'


class Grade(str, Enum):
    NO_7 = 'Grade 7'
    NO_8 = 'Grade 8'
    NO_9 = 'Grade 9'
    NO_10 = 'Grade 10'
    NO_11 = 'Grade 11'


class RecordSchema(BaseModel):
    period: Period
    subject: Subject
    co2_ppm: float
    pm25_ugm3: float
    temperature_c: float
    humidity_pct: float
    reaction_time_ms: int
    focus_rating: float
    error_rate: float
    heart_rate_bpm: int
    cognitive_impairment: float
    air_quality: int = Field(ge=0, le=2)


class PredictionSchema(BaseModel):
    performance_index: int = Field(ge=0, le=2)
