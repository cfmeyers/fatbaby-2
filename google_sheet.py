import json
import os
from datetime import datetime, timedelta
from typing import NamedTuple, Optional

import gspread

SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")


class BabyEvent(NamedTuple):
    """One record parsed from baby-tracking Google Sheet"""

    created_at: datetime
    diaper_type: str
    formula_amount: Optional[float]
    people: list[str]


def to_pretty_time(dt: datetime) -> str:
    return dt.strftime("%-I:%M %p (%a)")


class BabyUpdate(NamedTuple):
    """Holds the state of the app"""

    most_recent_feed: datetime
    next_feed: datetime
    most_recent_dirty_diaper: datetime

    @property
    def pretty_most_recent_feed(self) -> str:
        return to_pretty_time(self.most_recent_feed)

    @property
    def pretty_next_feed(self) -> str:
        return to_pretty_time(self.next_feed)

    @property
    def pretty_most_recent_dirty_diaper(self) -> str:
        return to_pretty_time(self.most_recent_dirty_diaper)


def get_sheet() -> gspread.worksheet.Worksheet:
    """Get the Google Sheet that holds the raw baby event data"""
    raw_creds = os.getenv("GOOGLE_CREDENTIALS")
    credentials = json.loads(raw_creds)

    gc = gspread.service_account_from_dict(credentials)
    return gc.open(SHEET_NAME).sheet1


def parse_baby_event_from_record(record: list[str]) -> BabyEvent:
    """Turn a record (row) from the Google Sheet into a BabyEvent"""
    created_at = datetime.strptime(record[0], "%m/%d/%Y %H:%M:%S")
    try:
        formula_amount = float(record[2])
    except:
        formula_amount = None
    return BabyEvent(
        created_at=created_at,
        diaper_type=record[1],
        formula_amount=formula_amount,
        people=record[3].split(", "),
    )


def get_baby_events_from_sheet(sheet: gspread.worksheet.Worksheet) -> list[BabyEvent]:
    """Convert all records in sheet (apart from header row) to BabyEvents"""
    vals = sheet.get_all_values()
    return [parse_baby_event_from_record(v) for v in vals[1:]]


def get_most_recent_feeding_time_from_events(events: list[BabyEvent]) -> datetime:
    most_recent = [e for e in events if e.formula_amount is not None][-1]
    return most_recent.created_at


def get_most_recent_dirty_diaper_from_events(events: list[BabyEvent]) -> datetime:
    most_recent = [e for e in events if "Poop" in e.diaper_type][-1]
    return most_recent.created_at


def get_next_feeding_time_from_events(
    events: list[BabyEvent], delta: float = 3.0
) -> datetime:
    last_feeding_time = get_most_recent_feeding_time_from_events(events)
    return last_feeding_time + timedelta(hours=delta)


def get_baby_update() -> BabyUpdate:
    """Get most recent state of baby feeding/diapers from Google Sheet"""
    sheet = get_sheet()
    events = get_baby_events_from_sheet(sheet)
    most_recent_feed = get_most_recent_feeding_time_from_events(events)
    next_feed = get_next_feeding_time_from_events(events, delta=3.0)
    most_recent_dirty_diaper = get_most_recent_dirty_diaper_from_events(events)
    return BabyUpdate(
        most_recent_feed=most_recent_feed,
        next_feed=next_feed,
        most_recent_dirty_diaper=most_recent_dirty_diaper,
    )
