import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🌏"
)

st.title("Welcome to my small Project! 👋")
st.write("Berikut merupakan beberapa project kecil pribadi yang saya buat di waktu luang ")

'''
1. Superstore Data Dashboard
2. Superstore Data Analytics
3. Superstore Demand Forecasting (Machine Learning)
'''
st.write("Anda dapat melihatnya di sidebar! !")
st.sidebar.success("Select a demo above.")