import sqlite3
from collections import namedtuple
from typing import NoReturn

import folium
import numpy as np
import pandas as pd

# import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import folium_static

from css import annotation_css, annotation_css_sidebar, header_css, logo_css
from database import (
    EmptyDatabase,
    MarkerNameError,
    RowsAlreadyExists,
    db_conn_cursor,
    db_create_table,
    db_delete_record,
    db_insert_record,
    db_read_table,
)

st.set_page_config(
    layout="wide",
    page_title=(
        "Интерактивная карта импликации отработанных труб газопроводов"
    ),
    initial_sidebar_state="expanded",
)

DB_NAME = "gisobjects.sqlite"  # файловая база данных
MARKER_TBL_NAME = "markers"  # таблица маркеров
Record = namedtuple(
    "Record",
    [
        "id",
        "longitude",
        "latitude",
        "marker_name",
        "descr_pattern",
        "marker_value",
        "marker_clr",
    ],
)
Record_wo_id = namedtuple(
    "Record_wo_id",
    [
        "longitude",
        "latitude",
        "marker_name",
        "descr_pattern",
        "marker_value",
        "marker_clr",
    ],
)
colors_for_marker = {
    "красный": "red",
    "темно-красный": "darkred",
    "зеленый": "green",
    "темно-зеленый": "darkgreen",
    "синий": "blue",
    "темно-синий": "darkblue",
    "оранжевый": "orange",
    "фиолетовый": "purple",
    "черный": "black",
}


def init_db():
    try:
        conn, cur = db_conn_cursor(DB_NAME)
        db_create_table(cur, MARKER_TBL_NAME)
    except sqlite3.DatabaseError as err:
        st.error(f"Ошбика база данных: {err}")
    finally:
        cur.close()
        conn.close()


def main_elements():
    """
    Создает шапку страницы
    """
    # === Верхняя часть шапки ===
    row1_1, row1_2 = st.beta_columns([2, 1])

    with row1_1:
        logo_css("АО ГАЗСТРОЙПРОМ", align="left", clr="#1E2022", size=33)
        logo_css(
            "<i>Департамент по восстановлению и утилизации<br>трубной продукции</i>",
            align="left",
            clr="#52616B",
            size=20,
        )

    with row1_2:
        pass

    header_css(
        "<i>Интерактивная карта импликации отработанных труб газопроводов</i>",
        align="left",
        clr="#52616B",
        size=26,
    )

    row1, row2 = st.beta_columns([2, 1])
    with row1:
        st.markdown(
            "_Ниже приводится упрощенное представление карты. Коммерческий вариант "
            "приложения на усмотрение Заказчика может быть "
            "построен с помощью [MapBox](https://www.mapbox.com/maps)_"
        )

    with row2:
        pass

    # === Нижняя часть шапки ===
    row2_1, row2_2 = st.beta_columns([2, 1])

    with row2_1:
        uploaded_file = st.file_uploader(
            "Для добавления нескольких маркеров на карту выберите Excel-файл...",
            type=["xls", "xlsx"],
            accept_multiple_files=False,
        )

    if uploaded_file is not None:
        create_markers_from_excel(uploaded_file)

    with row2_2:
        pass

    try:
        conn, cur = db_conn_cursor(DB_NAME)
        list_records = db_read_table(cur, MARKER_TBL_NAME)

        # список записей таблицы без индекса
        list_records_wo_id = [record[1:] for record in list_records]
    except sqlite3.DatabaseError as err:
        st.error(f"Ошбика база данных: {err}")
    finally:
        cur.close()
        conn.close()

    st.markdown("_База данных маркеров_")

    st.dataframe(  # отображает базу данных маркеров
        pd.DataFrame(
            list_records_wo_id,
            columns=[
                "Долгота",
                "Широта",
                "Имя маркера",
                "Категория",
                "Значение показателя",
                "Цвет маркера",
            ],
        )
    )

    folium.LayerControl().add_to(main_map)

    # width, height = GetSystemMetrics(0), GetSystemMetrics(1)
    # fraction_width = 0.735
    # fraction_height = 0.55


def create_markers_from_excel(excel_file_name):
    excel_file = pd.read_excel(
        excel_file_name,
        names=[
            "longitude",
            "latitude",
            "marker_name",
            "descr",
            "marker_value",
            "marker_clr",
        ],
    )
    list_tuples_from_excel = [
        tuple(record)[1:] for record in list(excel_file.to_records())
    ]
    list_tuples_from_excel = [
        (
            Record_wo_id(*record).longitude,
            Record_wo_id(*record).latitude,
            Record_wo_id(*record).marker_name.upper(),
            Record_wo_id(*record).descr_pattern,
            float(f"{Record_wo_id(*record).marker_value:.1f}"),
            Record_wo_id(*record).marker_clr,
        )
        for record in list_tuples_from_excel
    ]

    try:
        conn, cur = db_conn_cursor(DB_NAME)
        list_records = db_read_table(cur, MARKER_TBL_NAME)
        list_records = [record[1:] for record in list_records]

        for record in list_tuples_from_excel:
            if record not in list_records:
                db_insert_record(cur, MARKER_TBL_NAME, record)
            else:
                continue
    except sqlite3.DatabaseError as err:
        st.error(f"Ошибка базы данных: {err}")
    else:
        st.success("Маркеры успешны добавлены!")
        conn.commit()
    finally:
        cur.close()
        conn.close()


def render_folium_map():
    annotation_css(
        "Для навигации по карте можно использовать "
        "компоненты ZoomIn (+), ZoomOut (-) и Drag",
        clr="#C9D6DF",
    )
    folium_static(  # NB! требуется для отображения карты в Streamlit
        main_map, width=1050, height=550
    )


def plotly_pie() -> NoReturn:
    df = pd.DataFrame(
        {
            "values": np.random.randint(1000, 5000, size=8),
            "markers": [
                "Югорск",
                "Надым",
                "Ухта",
                "Тюмень",
                "Томск",
                "Уфа",
                "Тимашевск",
                "Москва",
            ],
        }
    )
    # fig = px.pie(df, values="values", names="markers", title="Распределение",
    #              color_discrete_sequence=px.colors.sequential.Bluyl_r)
    fig = go.Figure(
        data=[
            go.Pie(
                labels=df["markers"],
                values=df["values"],
                scalegroup="one",
                hole=0.3,
            )
        ]
    )
    fig.update_traces(
        hoverinfo="label+percent",
        textinfo="label+value",
        textfont_size=15,
    )
    st.sidebar.plotly_chart(fig, use_container_width=False)


def plotly_lines() -> NoReturn:
    df = pd.DataFrame(
        {
            "lom": np.random.randint(1000, 5000, size=8),
            "bu": np.random.randint(10000, 50000, size=8),
            "markers": [
                "Югорск",
                "Надым",
                "Ухта",
                "Тюмень",
                "Томск",
                "Уфа",
                "Тимашевск",
                "Москва",
            ],
        }
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["markers"], y=df["lom"], mode="lines+markers", name=None
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["markers"], y=df["bu"], mode="lines+markers", name=None
        )
    )
    st.sidebar.plotly_chart(fig, use_container_width=True)


def marker_creator(
    # map_obj: folium.Map,
    longitude: float,
    latitude: float,
    marker_name: str,
    descr: str,
    marker_value: float,
    marker_clr: str,
) -> NoReturn:
    popup = f"""
        <table rules="rows" col=2 width="255">
          <tr><td><i>Имя маркера</i></td><td><i><b>{marker_name}</b></i></td></tr>
          <tr><td><i>Категория</i></td><td>{descr}</td></tr>
          <tr><td><i>Значение показателя</i></td><td>{marker_value:.1f}, [т]</td></tr>
        </table>
        """
    marker_clr = colors_for_marker[marker_clr]
    folium.Marker(
        location=[longitude, latitude],
        popup=popup,
        parse_html=True,
        icon=folium.Icon(color=marker_clr, icon="fa-cogs", prefix="fa"),
    ).add_to(main_map)


def map_creator(
    longitude: float = 55.6787825,
    latitude: float = 37.79647853,
    zoom_start: int = 14,
) -> folium.Map:
    main_map = folium.Map(
        location=[longitude, latitude],
        # maxZoom=15,
        # minZoom=5,
        zoom_control=True,
        zoom_start=zoom_start,
        scrollWheelZoom=True,
        # maxBounds=[[40, 68],[6, 97]],
        tiles="OpenStreetMap",
        dragging=True,
    )
    return main_map


def create_record_in_database(
    longitude: float,
    latitude: float,
    marker_name: str,
    descr_pattern: str,
    marker_value: float,
    marker_clr: str,
) -> NoReturn:
    try:
        conn, cur = db_conn_cursor(DB_NAME)
        # db_create_table(cur, MARKER_TBL_NAME)

        list_records = db_read_table(cur, MARKER_TBL_NAME)
        # список записей таблицы без индекса
        list_records_wo_id = [record[1:] for record in list_records]

        record = (
            longitude,
            latitude,
            marker_name.upper(),
            descr_pattern,
            float(f"{marker_value:.1f}"),
            marker_clr,
        )
        if record not in list_records_wo_id:
            db_insert_record(cur, MARKER_TBL_NAME, record)
        else:
            raise RowsAlreadyExists("Такая запись уже существует")

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


def delete_record_from_database(marker_name: str) -> NoReturn:
    try:
        conn, cur = db_conn_cursor(DB_NAME)
        list_records = db_read_table(cur, MARKER_TBL_NAME)

        # список имен маркеров
        list_marker_names = [
            Record(*elem).marker_name for elem in list_records
        ]
        if marker_name in list_marker_names:
            db_delete_record(cur, MARKER_TBL_NAME, marker_name)
        else:
            raise MarkerNameError(
                f"Маркера '{marker_name.upper()}' нет в базе данных!"
            )
    except sqlite3.DatabaseError as err:
        st.error(f"Ошибка базы данных: {err}")
    except MarkerNameError as err:
        st.error(err)
    else:
        st.success("Запись успешно удалена из базы данных!")
        conn.commit()
        put_markers_on_map()
    finally:
        cur.close()
        conn.close()


def sidebar_elements():
    annotation_css_sidebar(
        "Сводные отчеты",
        align="left",
        size=18,
        clr="#1E2022",
    )
    selected_type_report = st.sidebar.radio(
        "Выберите формат отчета",
        ("Excel (табличное представление)", "LaTeX (аналитика)"),
    )

    if st.sidebar.button("Подготовить отчет"):
        pass

    annotation_css_sidebar(
        "Работа с базой данных маркеров слоя",
        align="left",
        size=18,
        clr="#1E2022",
    )

    if st.sidebar.button("Выгрузить базу данных маркеров"):
        # st.warning("База данных успешно выгружена в текущую директорию")
        pass

    if st.sidebar.button("Обновить базу данных маркеров"):
        put_markers_on_map()

    if st.sidebar.button("Открепить базу данных маркеров"):
        pass

    annotation_css_sidebar(
        "Конструктор маркеров слоя", align="left", size=18, clr="#1E2022"
    )
    annotation_css_sidebar(
        "Добавить один маркер слоя", align="left", size=15, clr="#52616B"
    )

    longitude = st.sidebar.number_input(
        "Введите долготу", value=54.93295515459673, format="%3f"
    )
    latitude = st.sidebar.number_input(
        "Введите широту", value=37.51391062707511, format="%3f"
    )
    marker_name = st.sidebar.text_input(
        "Введите имя маркера", "Серпуховское ЛПУМГ"
    )
    clr_icon_for_descr_pattern = {
        "Отходы трансгазы": ("blue"),
        "Отходы добыча": ("black"),
        "Лом": ("orange"),
        "Труба б/у": ("green"),
        "Труба категории А3": ("blue"),
        "Площадки по отходам": ("yellow"),
    }
    descr_pattern = st.sidebar.selectbox(
        "Выберите категорию маркера",
        list(clr_icon_for_descr_pattern.keys()),
    )

    marker_clr = st.sidebar.selectbox(
        "Выберите цвет маркера", list(colors_for_marker.keys())
    )

    marker_value = st.sidebar.number_input(
        "Введите значение показателя, [т]", value=6530.324, format="%3f"
    )

    if st.sidebar.button("Добавить маркер в базу данных"):
        create_record_in_database(
            longitude,
            latitude,
            marker_name,
            descr_pattern,
            marker_value,
            marker_clr,
        )

    annotation_css_sidebar(
        "Удалить один маркер слоя по имени",
        align="left",
        size=15,
        clr="#52616B",
    )

    try:
        conn, cur = db_conn_cursor(DB_NAME)
        list_records = db_read_table(cur, MARKER_TBL_NAME)

        # список записей таблицы без индекса
        list_avaible_marker_name = [
            Record(*record).marker_name for record in list_records
        ]
        marker_name_for_del = st.sidebar.selectbox(
            "Выберите имя маркера для удаления",
            options=list_avaible_marker_name,
        )
    except sqlite3.DatabaseError as err:
        st.error(f"Ошбика база данных: {err}")
    else:
        put_markers_on_map()
    finally:
        cur.close()
        conn.close()

    if st.sidebar.button("Удалить маркер из базы данных"):
        if marker_name_for_del is not None:
            delete_record_from_database(marker_name_for_del.upper())


def put_markers_on_map():
    """
    Наносит марекры на карту
    """
    try:
        conn, cur = db_conn_cursor(DB_NAME)
        list_records = db_read_table(cur, MARKER_TBL_NAME)

        if list_records:
            for record in list_records:
                from_record2_nt = Record(*record)
                lon = from_record2_nt.longitude
                lat = from_record2_nt.latitude
                marker_name = from_record2_nt.marker_name
                descr_pattern = from_record2_nt.descr_pattern
                marker_value = from_record2_nt.marker_value
                marker_clr = from_record2_nt.marker_clr

                marker_creator(
                    lon,
                    lat,
                    marker_name,
                    descr_pattern,
                    marker_value,
                    marker_clr,
                )
        else:
            raise EmptyDatabase("Пока в базе нет ни одного маркера...")

    except sqlite3.DatabaseError as err:
        st.error(f"Ошбика база данных: {err}")
    except EmptyDatabase as err:
        # st.warning(err)
        pass
    finally:
        cur.close()
        conn.close()


def start_load_markers():
    create_markers_from_excel("./additional_files/added_markers.xlsx")


if __name__ == "__main__":
    init_db()  # инициализация базы данных
    main_map = map_creator()
    main_elements()
    sidebar_elements()
    put_markers_on_map()
    render_folium_map()
