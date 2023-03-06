import streamlit as st
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
import altair as alt
import json
import geopandas as gpd
from vega_datasets import data

from geopy.geocoders import Nominatim
import requests
import folium
from streamlit_folium import folium_static



st.set_page_config(page_title="Plotting Demo", page_icon="📊")


dicts = {"First Class": 'ship_first', "Same Day": 'ship_same', "Second Class": 'ship_second', "Standard Class": 'ship_standard',
"Sales": 'sales', "Sales Consumer": 'sales_consumer', "Sales Corporate": 'sales_corporate', "Sales Homeoffice": 'sales_homeoffice',
"Sales Category Furniture": 'sales_furniture', "Sales Category Office": 'sales_office', "Sales Category Technology": 'sales_tech'}

data_all = pd.read_csv('states/world_country_and_usa_states_latitude_and_longitude_values.csv')
data_all = data_all.dropna()
data_all = data_all.drop(['country_code', 'latitude', 'longitude', 'country', 'usa_state_code'], axis=1)
data_all = data_all[data_all["usa_state"].str.contains("Puerto Rico") == False]
data_geo = json.load(open('states/states.geojson'))

@st.cache
def load_data(data):
    superstore_data = pd.read_csv(data)
    return superstore_data

@st.cache
def center():
   address = 'United States'
   geolocator = Nominatim(user_agent="id_explorer")
   location = geolocator.geocode(address)
   latitude = location.latitude
   longitude = location.longitude
   return latitude, longitude


def threshold(data):
   threshold_scale = np.linspace(data_all[dicts[data]].min(),
                              data_all[dicts[data]].max(),
                              10, dtype=float)
   # change the numpy array to a list
   threshold_scale = threshold_scale.tolist() 
   threshold_scale[-1] = threshold_scale[-1]
   return threshold_scale

def show_maps(data, threshold_scale):
    map_us = folium.Map(tiles="OpenStreetMap", location=[centers[0], centers[1]], zoom_start=4)
    maps= folium.Choropleth(geo_data = data_geo,
                           data = data_all,
                           columns=['usa_state',dicts[data]],
                           key_on='feature.properties.NAME',
                           threshold_scale=threshold_scale,
                           fill_color='YlOrRd',
                           fill_opacity=0.7,
                           line_opacity=0.2,    
                           legend_name=dicts[data],
                           highlight=True,
                           reset=True).add_to(map_us)

    folium.LayerControl().add_to(map_us)
    maps.geojson.add_child(folium.features.GeoJsonTooltip(fields=['NAME',dicts[data]],
                                                        aliases=['State: ', data],
                                                        labels=True)) 
    
    folium_static(map_us)

centers = center()

st.header('Data Analytics')
'''
Superstore memiliki data yang besar mengenai penjualannya. Data ini dapat membantu toko untuk meningkatkan penjualan.
Menggunakan metode analisis data, kita dapat memperoleh informasi berguna untuk memutuskan strategi bisnis yang harus
diambil kedepannya.
'''

st.subheader('1. Best Selling Category')
superstore_data = load_data('data/superstore.csv')

freq_category = pd.DataFrame(superstore_data.groupby(by=['Category'])['Category'].value_counts())
freq_category.rename(columns={'Category':'Quantity'}, inplace=True)
freq = pd.DataFrame(freq_category.Quantity.droplevel(0))
category_analysis = pd.DataFrame(superstore_data.groupby(by=['Category'])['Sales'].sum())

# Set for grouped plots - figure with a 2x2 grid of Axes
# sns.set_theme(style="whitegrid")
figure, axis = plt.subplots(1, 2, figsize=(8, 5))
# Plot barplots
cat1 = sns.barplot(x = category_analysis.index, y = category_analysis.Sales, ax=axis[0])
cat2 = sns.barplot(x = freq.index, y = freq.Quantity, ax=axis[1])
cat1.set(title = 'Sales of each Category $')
cat2.set(title = 'Quantity')
# Rotate axis for x-axis
plt.setp(cat2.get_xticklabels(), rotation = 'horizontal', size = 9)
plt.setp(cat1.get_xticklabels(), rotation = 'horizontal', size = 9)

# plt.show()
figure.tight_layout()
st.pyplot(figure)

select_time = st.selectbox(
    "Choose Year :",
    (2015, 2016, 2017, 2018)
)
time_sales = pd.DataFrame(superstore_data.groupby(by=['Order Date', 'Category'], as_index=False)['Sales'].sum())
time_sales['Month'] = pd.DatetimeIndex(time_sales['Order Date']).month
time_sales['Year'] = pd.DatetimeIndex(time_sales['Order Date']).year
time_sales = pd.DataFrame(time_sales.groupby(by=['Year', 'Month', 'Category'], as_index=False)['Sales'].sum())

dfs = dict(tuple(time_sales.groupby('Year')))
source = pd.DataFrame(dfs.get(select_time))
base = alt.Chart(source)
line = base.mark_line().encode(
    x='Month',
    y='Sales',
    color='Category:N'
)

nearest = alt.selection_single(nearest=True, on='mouseover',
                        fields=['Month'], empty='none')

selectors = alt.Chart(source).mark_point().encode(
    x='Month:Q',
    opacity=alt.value(0),
).add_selection(
    nearest
)

# Draw points on the line, and highlight based on selection
points = line.mark_point().encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
)

# Draw text labels near the points, and highlight based on selection
text = line.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.condition(nearest, 'Sales:Q', alt.value(' '))
)

# Draw a rule at the location of the selection
rules = alt.Chart(source).mark_rule(color='gray').encode(
    x='Month:Q',
).transform_filter(
    nearest
)

line_chart = alt.layer(
    line, selectors, points, rules, text
)

st.altair_chart(line_chart, use_container_width=True)

'''
###### Analisis:  
1. Seluruh kategori (Furniture, Office Supplies, Technology) memiliki hasil keuntungan penjualan yang hampir serupa
2. Kategori Office Supplies merupakan kategori dengan kuantitas penjualan terbanyak, namun dalam sisi keuntungan menjadi yang paling kecil diantara kategori lainnya
3. Meskipun kategori Technology memiliki keuntungan penjualan tertinggi, kuantitas produk yang terjual merupakan yang terendah diantara kategori lainnya

###### Keputusan:
1. Membuat diskon atau penawaran yang menarik pada produk kategori Technology dan Furniture untuk meningkatkan kuantitas penjualan yang dapat meningkatkan keuntungan penjualan
2. Menaikkan sedikit harga dari produk Office Supplies dan mengobservasi dampak kuantitas yang terjual, jika kuantitas penjualan masih di angka yang sama maka akan meningkatkan keuntungan penjualan
3. Membuat paket/bundle antara Office Supplies dengan Furniture/Technology untuk menaikkan kuantitas penjualan Furniture dan Technology
'''
 
st.subheader('2. Best Customer Segment')
col1, col2= st.columns(2)
customer_segment = pd.DataFrame(superstore_data.groupby(by=['Segment'])['Sales'].sum())
customer_segment_2 = pd.DataFrame(superstore_data.groupby(by=['Segment','Category'], as_index=False)['Sales'].sum())
with col1:
    st.bar_chart(customer_segment, width=300, height=400, use_container_width=False)
with col2:
    c = alt.Chart(customer_segment_2).mark_bar().encode(
        x=alt.X('Category:N', axis=alt.Axis(labelAngle=-45)),
        y='Sales:Q',
        color='Category:N',
        column='Segment:N'
    )
    st.altair_chart(c, use_container_width=False)



'''
###### Analisis:  
1. Customer dengan pembelian terbanyak merupakan Consumer diikuti Corporate, dan yang terendah Home Office
2. Jumlah pembelian produk(Furniture, Office Supplies, Technology) juga mengikuti urutan pada nomor 1 yaitu dengan Customer Consumer, Corporate, dan yang terakhir Home Office

###### Keputusan:
1. Membuat produk baru yang kemungkinan akan dibutuhkan oleh customer Corporate, dan Home Office
'''

st.subheader('3. Preferred Ship Mode')
c2 = alt.Chart(superstore_data).mark_bar().encode(
    x='count(Ship Mode):Q',
    y='Ship Mode:N',
    color='Ship Mode:N',

).properties(height=200)
st.altair_chart(c2, use_container_width=False)

## Extract Jumlah Ship Mode yang di grup berdasarkan State
shipmode_state = pd.DataFrame(superstore_data.groupby(by=['State','Ship Mode'])['Ship Mode'].value_counts())
shipmode_state.rename(columns={'Ship Mode':'Quantity'}, inplace=True)
shipmode_state = pd.DataFrame(shipmode_state.Quantity.droplevel(1))
shipmode_state = shipmode_state.reset_index()

## First Class Shipment
first_class = shipmode_state.loc[shipmode_state['Ship Mode'] == "First Class"] ## Extract First Class dari shipmode yang di grup berdasarkan State
first_class = first_class.drop(['Ship Mode'], axis=1)
first_class = first_class.set_index('State').T.to_dict('index') 
data_all['ship_first'] = data_all['usa_state'].map(first_class['Quantity'], na_action=None) ## Memasukkan kolom first class ke data_all
data_all['ship_first'] = data_all['ship_first'].fillna(0)

# Same Day Shipment
same_day = shipmode_state.loc[shipmode_state['Ship Mode'] == "Same Day"] ## Extract Same Class dari shipmode yang di grup berdasarkan State
same_day = same_day.drop(['Ship Mode'], axis=1)
same_day = same_day.set_index('State').T.to_dict('index') 
data_all['ship_same'] = data_all['usa_state'].map(same_day['Quantity'], na_action=None) ## Memasukkan kolom first class ke data_all
data_all['ship_same'] = data_all['ship_same'].fillna(0)
# Second Class Shipment
second_class = shipmode_state.loc[shipmode_state['Ship Mode'] == "Second Class"] ## Extract Same Class dari shipmode yang di grup berdasarkan State
second_class = second_class.drop(['Ship Mode'], axis=1)
second_class = second_class.set_index('State').T.to_dict('index') 
data_all['ship_second'] = data_all['usa_state'].map(second_class['Quantity'], na_action=None) ## Memasukkan kolom first class ke data_all
data_all['ship_second'] = data_all['ship_second'].fillna(0)
# Standard Class Shipmet
standard_class = shipmode_state.loc[shipmode_state['Ship Mode'] == "Standard Class"] ## Extract Same Class dari shipmode yang di grup berdasarkan State
standard_class = standard_class.drop(['Ship Mode'], axis=1)
standard_class = standard_class.set_index('State').T.to_dict('index') 
data_all['ship_standard'] = data_all['usa_state'].map(standard_class['Quantity'], na_action=None) ## Memasukkan kolom first class ke data_all
data_all['ship_standard'] = data_all['ship_standard'].fillna(0)

st.write('Preferred Shipmode in United States')

select_shipmode = st.selectbox(
    "Choose Ship Mode :",
    ("First Class", "Same Day","Second Class",'Standard Class')
)
for index, row in data_all.iterrows():
   for x in range(51):
      if data_geo['features'][x]['properties']['NAME'] == row['usa_state']:
        data_geo['features'][x]['properties']['ship_first'] = row['ship_first']
        data_geo['features'][x]['properties']['ship_standard'] = row['ship_standard']
        data_geo['features'][x]['properties']['ship_same'] = row['ship_same']
        data_geo['features'][x]['properties']['ship_second'] = row['ship_second']
      else:
        continue

show_maps(select_shipmode, threshold(select_shipmode))


'''
###### Analisis:  
1. Customer jauh lebih banyak memilih pengiriman kelas standar, hal ini mungkin dikarenakan murahnya harga pengiriman standar, dan juga customer yang tidak terlalu membutuhkan pesanan dengan waktu yang cepat


''' 
# st.subheader('4. Sales per Region')

sales_state = pd.DataFrame(superstore_data.groupby(by=['State'])['Sales'].sum())
sales_category_state = pd.DataFrame(superstore_data.groupby(by=['State','Category'], as_index=False)['Sales'].sum())
# sales_state
# quantity_state = pd.DataFrame(superstore_data.groupby(by=['State'])['State'].value_counts())
# quantity_state.rename(columns={'State':'Quantity'}, inplace=True)

# quantity_category_state = pd.DataFrame(superstore_data.groupby(by=['State', 'Category'])['State'].value_counts())
# quantity_category_state.rename(columns={'State':'Quantity'}, inplace=True)
# quantity_category_state = pd.DataFrame(quantity_category_state.Quantity.droplevel(0))

customer_segment_state = pd.DataFrame(superstore_data.groupby(by=['State','Segment'])['Sales'].sum())
# customer_segment_state
# sales_category_state






