from typing import Any
from datetime import date, datetime
from collections.abc import Iterable, Mapping

import requests
import psycopg2

from .config import DB_CONFIG, STUDENT_TABLE, STORAGE_TABLE
from ._data_viewer import print_data
from .db.sql.query_loader import load_db_query, StudentStats
from .graphql.query_loader import load_graphql_query

def get_session_progress(username: str) -> Mapping[str, Any]:
    return {
        "operationName" : "userSessionProgress",
        "query" : load_graphql_query("user_session_progress"),
        "variables" : {
            "username" : username
        }
    }

def get_recent_ac_submissions(username: str, limit: int = 1) -> Mapping[str, Any]:
    return {
        "operationName" : "recentAcSubmissions",
        "query" : load_graphql_query("recent_ac_submissions"),
        "variables" : {
            "username" : username,
            "limit" : limit
        }
    }

def store_by_name(names: Iterable[str], display_msg: bool = True) -> None:
    mp = {}

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                for name in names:
                    cur.execute(load_db_query("get_leetid_by_name", STUDENT_TABLE), (name.title(),))

                    row = cur.fetchone()

                    if row is not None:
                        mp[name] = row[0]
                    else:
                        mp[name] = ""
    finally:
        conn.close()

    store_by_leetcode_id(mp, display_msg)

_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (compatible; leetcode-stalker/1.0)",
    "Referer": "https://leetcode.com",
}
_TIMEOUT = 10

def _fetch_leetcode(uid: str) -> tuple | None:
    try:
        progress_res = requests.post(
            "https://leetcode.com/graphql/",
            json=get_session_progress(uid),
            headers=_HEADERS,
            timeout=_TIMEOUT,
        ).json()

        submissions_res = requests.post(
            "https://leetcode.com/graphql/",
            json=get_recent_ac_submissions(uid),
            headers=_HEADERS,
            timeout=_TIMEOUT,
        ).json()

        matched_user = progress_res["data"]["matchedUser"]
        if matched_user is None:
            print(f"User '{uid}' not found on leetcode")
            return None

        submission_list = submissions_res["data"]["recentAcSubmissionList"]
        if not submission_list:
            print(f"User '{uid}' has no submissions yet")
            return None

        return matched_user, submission_list[0]

    except requests.RequestException as e:
        print(f"Network error for '{uid}': {e}")
        return None
    except requests.exceptions.JSONDecodeError as e:
        print(f"Invalid response (not JSON) for '{uid}': {e}")
        return None
    except (KeyError, TypeError) as e:
        print(f"Unexpected response structure for '{uid}': {e}")
        return None

def store_by_leetcode_id(name_to_id: Mapping[str, str], display_msg: bool = True) -> None:
    student_data = []

    for name, uid in name_to_id.items():
        if not uid:
            continue

        result = _fetch_leetcode(uid)
        if result is None:
            continue

        matched_user, last_submission = result

        stats = {
            item["difficulty"]: item["count"]
            for item in matched_user["submitStats"]["acSubmissionNum"]
        }

        student_data.append((
            date.today(),
            name,
            stats["All"],
            stats["Easy"],
            stats["Medium"],
            stats["Hard"],
            datetime.fromtimestamp(int(last_submission["timestamp"]))
        ))

    if student_data:
        _store(student_data, display_msg)

def _store(params: list[tuple[Any, ...]], display_msg: bool = True) -> None:
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.executemany(load_db_query("update_storage", STORAGE_TABLE), params)
    finally:
        conn.close()

    if display_msg:
        _successful_msg()

def _successful_msg() -> None:
    print_data(StudentStats.GET_STATS_BY_DATE, str(date.today()))