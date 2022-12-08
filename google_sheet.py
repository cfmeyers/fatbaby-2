from datetime import datetime, timedelta
from typing import NamedTuple, Optional

import gspread
from oauth2client.service_account import ServiceAccountCredentials


class BabyEvent(NamedTuple):
    created_at: Optional[datetime]
    diaper_type: str
    formula_amount: Optional[float]
    people: list[str]


def get_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "client_secret.json", scope
    )
    client = gspread.authorize(creds)
    return client.open("Arthur's App (Responses)").sheet1


def parse_val_into_event(val: list[str]) -> BabyEvent:
    try:
        created_at = datetime.strptime(val[0], "%m/%d/%Y %H:%M:%S")
    except:
        created_at = None
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


def get_sheet_values(sheet) -> list[BabyEvent]:
    vals = sheet.get_all_values()
    return [parse_val_into_event(v) for v in vals[1:]]


def get_next_feeding_time(events: list[BabyEvent], delta: float = 3.0) -> datetime:
    most_recent = [e for e in events if e.formula_amount is not None][-1]
    last_feeding_time = most_recent.created_at
    return last_feeding_time + timedelta(hours=delta)
