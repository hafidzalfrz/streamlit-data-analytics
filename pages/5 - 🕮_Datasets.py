import streamlit as st
import time
import numpy as np
import pandas as pd


st.set_page_config(page_title="About Datasets", page_icon="🕮")

st.title("About Datasets")
st.subheader("1. Superstore Sale Datasets, didapat dari Kaggle [disini](https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting)")

superstore_data = pd.read_csv('data/superstore.csv')

st.write('preview:')
st.write(superstore_data.head())

columns_length=len(superstore_data.columns)
rows_length=len(superstore_data)

st.write('Jumlah kolom:', columns_length)
st.write('Jumlah baris:', rows_length)


st.write('#### Cek Nilai null')
st.write(superstore_data.isnull().sum(), 'Terdapat nilai null pada kolom Postal Code sebanyak 11 baris. Dikarenakan field/kolom postal code tidak digunakan pada analisis dan juga sulit untuk mengisinya karena kekurangan informasi, maka nilai null tersebut diabaikan')
# null = superstore_data[superstore_data.isnull().any(axis=1)]
# st.write(null)
st.write('#### Cek Data Duplikat')
st.write('terdapat', superstore_data.duplicated().sum(), 'data duplikat')
st.write('#### Descriptive Statistics')
df = superstore_data.describe(include='all').fillna("").astype("str")
st.write(df)
'''
Terdapat beberapa informasi penting yang didapat disini diantaranya adalah:  
1. Terdapat 793 Customer berbeda
2. Customer berasal dari 529 kota dari 49 negara bagian berbeda
3. Terdapat 1861 produk yang berbeda dari 3 kategori dan  17 sub kategori
4. Staple Envelope menjadi produk dengan penjualan paling banyak dengan jumlah penjualan sebanyak 47 kali
5. Produk paling banyak terjual di kota New York dengan total penjualan 891
6. William Brown merupakan customer paling banyak membeli produk dengan jumlah pembelian 35
'''
