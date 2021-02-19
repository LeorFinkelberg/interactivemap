import streamlit as st
from typing import NoReturn


def logo_css(
        text: str = "",
        align: str = "center",
        clr: str = "black",
        size: int = 15
) -> NoReturn:
    st.markdown(
        f"<h1 style='font-family: Helvetica, sans-serif;"
        "line-height: 1.2; margin-top: 0px; font-size: {size}px;"
        "text-align: {align};"
        f"color: {clr}'>{text}",
        unsafe_allow_html=True,
    )


def header_css(
        text: str = "",
        align: str = "center",
        clr: str = "black"
) -> NoReturn:
    st.markdown(
        f"<h1 style='font-family: Helvetica, sans-serif;"
        "line-height: 1.2; margin-top: 3px; font-size: 18px;"
        "text-align: {align};"
        f"color: {clr}'>{text}",
        unsafe_allow_html=True,
    )


def subheader_css(
        text: str = "",
        clr: str = "black"
) -> NoReturn:
    st.markdown(
        f"<h2 style='font-family: Helvetica, sans-serif;"
        "line-height: 1.2; text-align: justify; font-size: 20px;"
        f"color: {clr}'>{text}",
        unsafe_allow_html=True,
    )


def annotation_css(
        text: str = "",
        clr: str = "black",
        size: int = 15
) -> NoReturn:
    st.markdown(
        f"<h2 style='font-family: Helvetica, sans-serif;"
        f"line-height: 1.2; text-align: justify; font-size: {size}px;"
        f"color: {clr}'><i>{text}</i>",
        unsafe_allow_html=True,
    )
    
    
def annotation_css_sidebar(
        text: str = "",
        clr: str = "black",
        size: int = 15
) -> NoReturn:
    st.sidebar.markdown(
        f"<h2 style='font-family: Helvetica, sans-serif;"
        f"line-height: 1.2; text-align: justify; font-size: {size}px;"
        f"color: {clr}'><i>{text}</i>",
        unsafe_allow_html=True,
    )


def annotation_normal_css(
        text: str = "",
        clr: str = "black",
        size: int = 15
) -> NoReturn:
    st.markdown(
        f"<h2 style='font-family: Helvetica, sans-serif;"
        f"line-height: 1.2; text-align: justify; font-size: {size}px;"
        f"color: {clr}'>{text}",
        unsafe_allow_html=True,
    )
