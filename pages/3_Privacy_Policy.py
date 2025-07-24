import streamlit as st


with open("./docs/privacy_policy.txt") as f:
    text = f.read()

st.markdown(text)