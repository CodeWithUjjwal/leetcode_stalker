from typing import Any
from tabulate import tabulate
from collections.abc import Iterable

import psycopg2

from .config import DB_CONFIG
from .db.sql.query_loader import StudentData, StudentStats, InfoData, load_db_query

class QueryResult(list):
    def __init__(self, data: list[tuple[Any, ...]], headers: list[str]):
        super().__init__(data)
        self.headers = headers

def _validate_placeholders(placeholder_count: int, param: tuple, query: StudentData | StudentStats | InfoData) -> None:
    provided_count = len(param)
    if placeholder_count != provided_count:
        arg = "argument" if placeholder_count == 1 else "arguments"
        raise TypeError(
            f"{query.name} requires {placeholder_count} {arg} but {provided_count} were provided"
        )


def _run_single(cur, sql: str, placeholder_count: int, query: StudentData | StudentStats | InfoData) -> list[tuple]:
    _validate_placeholders(placeholder_count, (), query)
    cur.execute(sql)
    return cur.fetchall()


def _run_multi(cur, sql: str, param_list: list, placeholder_count: int, query: StudentData | StudentStats | InfoData) -> list[tuple]:
    all_rows = []
    for param in param_list:
        bound = param if isinstance(param, tuple) else (param,)
        _validate_placeholders(placeholder_count, bound, query)
        cur.execute(sql, bound)
        all_rows.extend(cur.fetchall())
    return all_rows


def get_data(query: StudentData | StudentStats | InfoData, params: Iterable[Any] | str = ()) -> QueryResult:
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                param_list = [params] if isinstance(params, str) else list(params)
                sql = load_db_query(query, query.table)
                placeholder_count = sql.count("%s")

                rows = (
                    _run_single(cur, sql, placeholder_count, query)
                    if not param_list
                    else _run_multi(cur, sql, param_list, placeholder_count, query)
                )

                headers = [desc[0].title() for desc in cur.description]
                return QueryResult(rows, headers)
    finally:
        conn.close()

def format_data(data: QueryResult, table_style: str = "fancy_grid", show_index: bool = True) -> str:
    if show_index:
        return tabulate(data, headers = ['#'] + data.headers, tablefmt = table_style, showindex = range(1, len(data) + 1))
    return tabulate(data, headers = data.headers, tablefmt = table_style)

def print_data(query: StudentData | StudentStats | InfoData, params: Iterable[Any] | str = (), table_style: str = "fancy_grid", show_index: bool = True) -> None:
    print(format_data(get_data(query, params), table_style, show_index))