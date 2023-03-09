"""
Use a Google Sheet as a read-only data source for keeping track of baby's most recent
feeding, diaper, etc.

Depends on 2 environment variables:
    - GOOGLE_SHEET_NAME: the name of the Google Sheet
    - GOOGLE_CREDENTIALS: json blob of your service workers google credentials, typically
    found in google-credentials.json or client-credentials.json
"""
import json
import os
from datetime import datetime, timedelta
from typing import NamedTuple, Optional

import gspread

SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")


class BabyEvent(NamedTuple):
    """One record parsed from baby-tracking Google Sheet"""

    created_at: datetime
    diaper_type: str
    formula_amount: float | None
    people: list[str]


def to_pretty_time(dt: datetime) -> str:
    return dt.strftime("%-I:%M %p (%a)")


class BabyUpdate(NamedTuple):
    """Holds the state of the app"""

    most_recent_feed: datetime
    next_feed: datetime
    most_recent_dirty_diaper: datetime
    most_recent_feed_amount: float | None

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
    credentials = json.loads(GOOGLE_CREDENTIALS)  # type:ignore

    gc = gspread.service_account_from_dict(credentials)
    return gc.open(SHEET_NAME).sheet1


def parse_baby_event_from_record(record: list[str]) -> BabyEvent:
    """Turn a record (row) from the Google Sheet into a BabyEvent

    A record is a list of string, each representing a cell.
    The cells are:
        - Timestamp: in the form of e.g. "10/15/2022 14:31:02"
        - Diaper: "Poop" or "Pee"
        - Formula amount in mL: number
        - Person: who fed/changed baby (single person or comma-sep list of people)

    """
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


def get_most_recent_feed_event(events: list[BabyEvent]) -> BabyEvent:
    most_recent = [e for e in events if e.formula_amount is not None][-1]
    return most_recent


def get_most_recent_dirty_diaper_from_events(events: list[BabyEvent]) -> datetime:
    most_recent = [e for e in events if "Poop" in e.diaper_type][-1]
    return most_recent.created_at


def get_next_feeding_time_from_events(
    events: list[BabyEvent], delta: float = 3.0
) -> datetime:
    most_recent_event = get_most_recent_feed_event(events)
    return most_recent_event.created_at + timedelta(hours=delta)


def get_baby_update() -> BabyUpdate:
    """Get most recent state of baby feeding/diapers from Google Sheet"""
    sheet = get_sheet()
    events = get_baby_events_from_sheet(sheet)
    most_recent_feed = get_most_recent_feed_event(events)
    most_recent_feed_amount = most_recent_feed.formula_amount
    next_feed = get_next_feeding_time_from_events(events, delta=3.0)
    most_recent_dirty_diaper = get_most_recent_dirty_diaper_from_events(events)
    return BabyUpdate(
        most_recent_feed=most_recent_feed.created_at,
        next_feed=next_feed,
        most_recent_dirty_diaper=most_recent_dirty_diaper,
        most_recent_feed_amount=most_recent_feed_amount,
    )
