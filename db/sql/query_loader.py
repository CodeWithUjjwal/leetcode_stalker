from pathlib import Path
from enum import StrEnum

from ...config import STUDENT_TABLE, STORAGE_TABLE

_QUERIES_DIR = Path(__file__).resolve().parent / "queries"

class StudentData(StrEnum):
    GET_LEETCODE_ID = "get_leetcode_id"

    @property
    def table(self) -> str:
        return STUDENT_TABLE

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self._name_}>"

class StudentStats(StrEnum):
    GET_ALL_STATS = "get_all_stats"
    GET_LATEST_SAVED = "get_latest_saved"
    GET_RECENT_PROGRESS = "get_recent_progress"
    GET_OVERALL_PROGRESS = "get_overall_progress"
    GET_STATS_BY_DATE = "get_stats_by_date"

    @property
    def table(self) -> str:
        return STORAGE_TABLE

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self._name_}>"

class InfoData(StrEnum):
    GET_STORED_STUDENTS = "get_stored_students"
    GET_DATE_RANGE = "get_date_range"

    @property
    def table(self) -> str:
        return STORAGE_TABLE

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self._name_}>"

def load_db_query(file_name: StudentStats | StudentData | str, table_name: str) -> str:
    return (_QUERIES_DIR / f"{file_name}.sql").read_text(encoding = "utf-8").format(table_name = table_name)