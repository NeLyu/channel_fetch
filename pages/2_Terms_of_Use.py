import streamlit as st


with open("./docs/terms_of_use.txt") as f:
    text = f.read()

st.markdown(text)