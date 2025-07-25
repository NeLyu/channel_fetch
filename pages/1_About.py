import streamlit as st


with open("./docs/about.md") as f:
    text = f.read()

st.markdown(text)