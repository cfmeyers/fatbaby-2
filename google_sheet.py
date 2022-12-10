import json
import os
from datetime import datetime, timedelta
from typing import NamedTuple, Optional

import gspread

# SHEET_NAME = "Arthur's App (Responses)"
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")


class BabyEvent(NamedTuple):
    created_at: datetime
    diaper_type: str
    formula_amount: Optional[float]
    people: list[str]


def get_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "google-credentials.json", scope  # type: ignore
    )
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1


def get_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    raw_creds = os.getenv("GOOGLE_CREDENTIALS")
    credentials = json.loads(raw_creds)

    gc = gspread.service_account_from_dict(credentials)
    return gc.open("Arthur's App (Responses)").sheet1


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


def get_next_feeding_time_from_sheet(
    events: list[BabyEvent], delta: float = 3.0
) -> datetime:
    most_recent = [e for e in events if e.formula_amount is not None][-1]
    last_feeding_time = most_recent.created_at
    return last_feeding_time + timedelta(hours=delta)


def get_next_feeding_time() -> datetime:
    sheet = get_sheet()
    baby_events = get_baby_events_from_sheet(sheet)
    return get_next_feeding_time_from_sheet(baby_events, delta=3.0)
