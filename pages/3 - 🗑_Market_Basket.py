import streamlit as st
import pandas as pd
from pyECLAT import ECLAT
from pyECLAT import Example1, Example2

st.set_page_config(page_title="Market Basket", page_icon="🧑")

@st.cache
def load_data(data):
    superstore_data = pd.read_csv(data)
    return superstore_data

superstore_data = load_data('data/superstore.csv')


st.header('Market Basket Analytics')
'''
Market Basket Analytics merupakan salah satu teknik yang digunakan Superstore untuk meningkatkan penjualan produk.
Teknik ini bertujuan untuk mendapatkan informasi mengenai asosiasi antar produk. Hal tersebut dilakukan dengan melihat kombinasi antar produk yang sering muncul pada transaksi
Sehingga Superstore dapat menjadikan informasi tersebut untuk kebutuhan seperti rekomendasi produk, dan tata letak produk dalam katalog/etalase untuk meningkatkan penjualan produk. 
'''

st.subheader('1. Dataset Pembelian Produk')
ex2 = Example2().get()
st.write(' Berikut merupakan dataset pembelian produk. Tiap baris merepresentasikan 1 pemesanan')
ex2
st.write('Terdapat',len(ex2), 'jumlah pembelian')

st.subheader('2. Algoritma Eclat')
st.write('Selanjutnya akan dicari produk mana yang sering muncul bersama dalam pembelian menggunakan algoritma Eclat.')
eclat_instance = ECLAT(data=ex2, verbose=True)
get_ECLAT_indexes, get_ECLAT_supports = eclat_instance.fit(min_support=0.04,
                                                           min_combination=2,
                                                           max_combination=3,
                                                           separator=' & ',
                                                           verbose=True)

result = pd.DataFrame(get_ECLAT_supports.items(),columns=['Item', 'Support'])
result.sort_values(by=['Support'], ascending=True)
result
st.write("Produk dengan asosiasi paling sering muncul merupakan mineral water & spaghetti")

