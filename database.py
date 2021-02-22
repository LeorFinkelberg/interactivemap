import sqlite3
from typing import List, Tuple


class RowsAlreadyExists(Exception):
    """
    Пользовательское исключение. Возбуждается при попытке добавления
    в базу данных неуникальной записи
    """

class MarkerNameError(Exception):
    """
    Пользовательское исключение. Возбуждается при попытке удалить запись по
    отсутствующему в базе данных имени маркера
    """

class EmptyDatabase(Exception):
    """
    Пользовательское исключение. Возбуждается если при старте сессии
    база данных пуста
    """
    

def db_conn_cursor(db_name: str):
    """
    Возвращает объект-соединения и
    объект-курсора
    """
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    return conn, cur


def db_create_table(cur, tbl_name: str):
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {tbl_name}(
          `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
          `longitude` REAL NOT NULL,
          `latitude` REAL NOT NULL,
          `marker_name` TEXT NOT NULL,
          `descr_pattern` TEXT NOT NULL,
          `marker_value` REAL NOT NULL,
          `marker_clr` TEXT NOT NULL
        );
        """
    )


def db_insert_record(cur, tbl_name: str, record: Tuple):
    """
    Вставляет одну запись в таблицу базы данных
    """
    cur.execute(
        f"""
        INSERT INTO {tbl_name}(longitude, latitude, marker_name, descr_pattern, marker_value, marker_clr)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        record,
    )


def db_insert_record_many(cur, tbl_name: str, records: List[Tuple]):
    """
    Вставляет несколько записей в таблицу базы данных
    """
    cur.executemany(
        f"""
        INSERT INTO {tbl_name}(longitude, latitude, marker_name, descr_pattern, marker_value, marker_clr)
        VALUES (?, ?, ?, ?, ?);
        """,
        records,
    )


def db_delete_record(cur, tbl_name: str, marker_name: str):
    """
    Удаляет одну запись из таблицы базы данных
    """
    cur.execute(
        f"""
        DELETE FROM {tbl_name} WHERE marker_name = ?
        """,
        (marker_name,),
    )


def db_read_table(cur, tbl_name: str) -> List[Tuple[int, float, float, str]]:
    """
    Читает таблицу базы данных в список кортежей
    """
    cur.execute(
        f"""
        SELECT * FROM {tbl_name};
        """
    )
    return cur.fetchall()
