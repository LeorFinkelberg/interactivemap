from typing import Tuple, List, NoReturn
from win32api import GetSystemMetrics # для вычисления размеров экрана
from collections import namedtuple

import sqlite3
import folium
import streamlit as st
from streamlit_folium import folium_static

from css import (
    logo_css,
    annotation_css,
    annotation_normal_css,
    annotation_css_sidebar,
    header_css,
    subheader_css,
)
from database import (
    RowsAlreadyExists,
    MarkerNameError,
    db_conn_cursor,
    db_create_table,
    db_insert_record,
    db_delete_record,
    db_read_table,
)


st.set_page_config(
        layout="wide",
        page_title = ("Интерактивная карта импликации отработанных труб газопроводов"),
        initial_sidebar_state="collapsed"
)

DB_NAME = "gisobjects.sqlite" # файловая база данных 
MARKER_TBL_NAME = "markers"   # таблица маркеров

def main_elements():
    # === Верхняя часть шапки ===
    row1_1, row1_2 = st.beta_columns([1, 1])
    
    with row1_1:
        logo_css("ГАЗСТРОЙПРОМ", clr="black", size=6)
        header_css("<i>Интерактивная карта импликации "
                   "отработанных труб газопроводов</i> (демонстрация)",
                   align = "left", clr="black")
        
    with row1_2:
        annotation_css("Описание")
        
    # === Нижняя часть шапки ===
    row2_1, row2_2 = st.beta_columns([1, 1])
    
    with row2_1:
        uploaded_file = st.file_uploader(
            "Для добавления нескольких маркеров на карту выберите Excel-файл...",
            type = ["xls", "xlsx"],
            accept_multiple_files=True)
        
    with row2_2:
        st.write("test3...")
        
    map_obj = map_creator(zoom_start=15)
    folium.LayerControl().add_to(map_obj)
    
    # width, height = GetSystemMetrics(0), GetSystemMetrics(1)
    # fraction_width = 0.735
    # fraction_height = 0.55
    
    annotation_css("Детали")
    folium_static( # NB! требуется для отображения карты в Streamlit
        map_obj,
        width=1500,
        height=700
    )
        
    
def marker_creator(
        map_obj: folium.Map,
        longitude: float,
        latitude: float,
        marker_name: str = ""
) -> NoReturn:
    folium.Marker(
        location = [longitude, latitude],
        popup = f"<i>{marker_name}</i>"
    ).add_to(map_obj)


def map_creator(
    longitude: float = 54.918808900513945,
    latitude: float = 37.49186810734705,
    zoom_start: int = 5
) -> folium.Map:
    mainMap = folium.Map(
        location = [longitude, latitude],
        #maxZoom=15,
        #minZoom=5,
        zoom_control=True,
        zoom_start=zoom_start,
        scrollWheelZoom=True,
        #maxBounds=[[40, 68],[6, 97]],
        tiles="OpenStreetMap",
        dragging=True
    )
    return mainMap
    

def create_record_in_database(
    longitude: float,
    latitude: float,
    marker_name: str
) -> NoReturn:
    try:
        conn, cur = db_conn_cursor(DB_NAME)
        db_create_table(cur, MARKER_TBL_NAME)
        
        list_records: List[Tuple[int, float, float, str]] = db_read_table(cur, MARKER_TBL_NAME)
        list_records_wo_id = [record[1:] for record in list_records] # список записей таблицы без индекса
        
        record = (longitude, latitude, marker_name.lower()) 
        if record in list_records_wo_id:
            raise RowsAlreadyExists("Такая запись уже существует")
        else:
            db_insert_record(cur, MARKER_TBL_NAME, record)
            
    except sqlite3.DatabaseError as err:
        st.error(f"Ошбика база данных: {err}")
    except RowsAlreadyExists:
        st.error(f"Запись {record} уже существует!")
    else:
        st.success(f"Запись {record} успешно добавлена в базу данных!")
        conn.commit()
    finally:
        cur.close()
        conn.close()


def delete_record_from_database(
    marker_name: str
) -> NoReturn:
    try:
        conn, cur = db_conn_cursor(DB_NAME)
        
        list_records: List[Tuple[int, float, float, str]] = db_read_table(cur, MARKER_TBL_NAME)
        Record = namedtuple("Record", ["id", "longitude", "latitude", "marker_name"])
        list_marker_names = [Record(*elem).marker_name for elem in list_records] # список имен маркеров
        st.write(list_marker_names)
        
        if marker_name in list_marker_names:
            db_delete_record(cur, MARKER_TBL_NAME, marker_name)
        else:
            raise MarkerNameError("Такого маркера нет в базе данных")
    except sqlite3.DatabaseError as err:
        st.error(f"Ошибка базы данных: {err}")
    except MarkerNameError as err:
        st.error(f"{err}")
    else:
        st.success(f"Запись успешно удалена из базы данных!")
        conn.commit()
    finally:
        cur.close()
        conn.close()


def side_bar_elements():
    annotation_css_sidebar("Конструктор маркеров слоя", size=18)
    annotation_css_sidebar("Добавить один маркер слоя", size=15)
    
    longitude = st.sidebar.number_input("Введите долготу", value=54.93295515459673, format="%3f")
    latitude = st.sidebar.number_input("Введите широту", value=37.51391062707511, format="%3f")
    marker_name = st.sidebar.text_input("Введите название маркера", "Серпуховское ЛПУМГ")  
        
    if st.sidebar.button("Добавить маркер в базу данных"):
        create_record_in_database(longitude, latitude, marker_name)
        
    annotation_css_sidebar("Удалить один маркер слоя по имени", size=15)
    marker_name_for_del = st.sidebar.text_input("Введите имя маркера", "Серпуховское ЛПУМГ")  
    
    if st.sidebar.button("Удалить маркер из базы данных"):
        delete_record_from_database(marker_name_for_del.lower())
    

    
    
if __name__ == "__main__":
    main_elements()
    side_bar_elements()