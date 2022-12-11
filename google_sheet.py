import json
import os
from datetime import datetime, timedelta
from typing import NamedTuple, Optional

import gspread

SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")


class BabyEvent(NamedTuple):
    created_at: datetime
    diaper_type: str
    formula_amount: Optional[float]
    people: list[str]


def to_pretty_time(dt: datetime) -> str:
    return dt.strftime("%-I:%M %p (%a)")


class BabyUpdate(NamedTuple):
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


def get_sheet():
    raw_creds = os.getenv("GOOGLE_CREDENTIALS")
    credentials = json.loads(raw_creds)

    gc = gspread.service_account_from_dict(credentials)
    return gc.open(SHEET_NAME).sheet1


def parse_val_into_event(val: list[str]) -> BabyEvent:
    created_at = datetime.strptime(val[0], "%m/%d/%Y %H:%M:%S")
    try:
        formula_amount = float(val[2])
    except:
        formula_amount = None
    return BabyEvent(
        created_at=created_at,
        diaper_type=val[1],
        formula_amount=formula_amount,
        people=val[3].split(", "),
    )


def get_baby_events_from_sheet(sheet) -> list[BabyEvent]:
    vals = sheet.get_all_values()
    return [parse_val_into_event(v) for v in vals[1:]]


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


def get_next_feeding_time() -> datetime:
    sheet = get_sheet()
    baby_events = get_baby_events_from_sheet(sheet)
    return get_next_feeding_time_from_events(baby_events, delta=3.0)


def get_baby_update() -> BabyUpdate:
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
