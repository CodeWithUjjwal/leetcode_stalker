__title__ = "leetcode_stalker"
__author__ = "Ujjwal Gupta"
__license__ = "MIT"
__version__ = "1.0.0"
__url__ = "https://github.com/CodeWithUjjwal/leetcode_stalker"

from ._data_scraper import store_by_name, store_by_leetcode_id
from ._data_viewer import get_data, print_data, format_data
from .db.sql.query_loader import StudentData, StudentStats, InfoData

__all__ = [
    "store_by_name",
    "store_by_leetcode_id",
    "get_data",
    "print_data",
    "format_data",
    "StudentData",
    "StudentStats",
    "InfoData",
]