from time import time
from turtle import width
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import json
import geopandas as gpd

from geopy.geocoders import Nominatim
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Superstore Dashboard",
    page_icon="📋",
    layout="wide"
)

dicts = {"First Class": 'ship_first', "Same Day": 'ship_same', "Second Class": 'ship_second', "Standard Class": 'ship_standard',
"Sales": 'sales', "Sales Consumer": 'sales_consumer', "Sales Corporate": 'sales_corporate', "Sales Homeoffice": 'sales_homeoffice',
"Sales Category Furniture": 'sales_furniture', "Sales Category Office": 'sales_office', "Sales Category Technology": 'sales_tech'}
data_all = pd.read_csv('states/world_country_and_usa_states_latitude_and_longitude_values.csv')
data_all = data_all.dropna()
data_all = data_all.drop(['country_code', 'latitude', 'longitude', 'country', 'usa_state_code'], axis=1)
data_all = data_all[data_all["usa_state"].str.contains("Puerto Rico") == False]
data_geo = json.load(open('states/states.geojson'))

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
    
    st_folium(map_us, width='100%')

centers = center()

st.markdown("<h2 style='text-align: center; color: black;'>SUPERSTORE DATA ANALYTICS DASHBOARD</h2>", unsafe_allow_html=True)
st.write(" ")
col1, col2, col3 = st.columns(3)

@st.cache
def load_data(data):
    superstore_data = pd.read_csv(data)
    return superstore_data

superstore_data = load_data('data/superstore.csv')
array_of_year = []
year = pd.DataFrame(superstore_data['Order Date'])
year['Year'] = pd.DatetimeIndex(superstore_data['Order Date']).year
array_of_year = year.Year.unique()
array_of_year = np.sort(array_of_year)

def product_quantity(data):
    quantity = pd.DataFrame(superstore_data.groupby(by=['Category'], as_index=False)['Order Date'].value_counts())
    quantity['Year'] = pd.DatetimeIndex(quantity['Order Date']).year
    quantity_dict = dict(tuple(quantity.groupby('Year')))
    yearly_quantity = pd.DataFrame(quantity_dict.get(data))
    return yearly_quantity

@st.cache
def time_sales_data(data):
    time_sales = pd.DataFrame(superstore_data.groupby(by=['Order Date', 'Category'], as_index=False)['Sales'].sum())
    time_sales['Month'] = pd.DatetimeIndex(time_sales['Order Date']).month
    time_sales['Year'] = pd.DatetimeIndex(time_sales['Order Date']).year
    time_sales = pd.DataFrame(time_sales.groupby(by=['Year', 'Month', 'Category'], as_index=False)['Sales'].sum())
    dfs = dict(tuple(time_sales.groupby('Year')))
    source = pd.DataFrame(dfs.get(data))
    return source
    
def line_chart(data):
    source = time_sales_data(data)
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
    ).properties(width=700)

    st.altair_chart(line_chart, use_container_width=True)

column1, column2= st.columns(2)
with column1:
    st.markdown("#### Sales Line Chart")
    select_time = st.selectbox(
        "Choose Year :",
        array_of_year
    )
with column1:
    line_chart(select_time)

with column2:
    st.markdown("#### Customer Segment Bar Chart")
    customer_segment_2 = pd.DataFrame(superstore_data.groupby(by=['Order Date','Segment','Category'], as_index=False)['Sales'].sum())
    customer_segment_2['Year'] = pd.DatetimeIndex(customer_segment_2['Order Date']).year
    customer_segment_2 = pd.DataFrame(customer_segment_2.groupby(by=['Year', 'Segment', 'Category'], as_index=False)['Sales'].sum())
    dfs_customer = dict(tuple(customer_segment_2.groupby('Year')))
    customer_segment_3 = pd.DataFrame(dfs_customer.get(select_time))

    c = alt.Chart(customer_segment_3).mark_bar().encode(
        x=alt.X('Category:N', axis=alt.Axis(labelAngle=-45)),
        y='Sales:Q',
        color='Category:N',
        column='Segment:N'
    )
    st.altair_chart(c, use_container_width=False)

st.markdown("#### Sales by Region")
sales_state = pd.DataFrame(superstore_data.groupby(by=['Order Date', 'State'], as_index=False)['Sales'].sum())
sales_state['Year'] = pd.DatetimeIndex(sales_state['Order Date']).year
sales_state = pd.DataFrame(sales_state.groupby(by=['Year', 'State'], as_index=False)['Sales'].sum())
dfs_sales = dict(tuple(sales_state.groupby('Year')))
sales_state_2 = pd.DataFrame(dfs_sales.get(select_time))
sales_state_2 = sales_state_2.set_index('State')
data_all['sales'] = data_all['usa_state'].map(sales_state_2['Sales'], na_action=None) ## Memasukkan kolom first class ke data_all
data_all['sales'] = data_all['sales'].fillna(0)

for index, row in data_all.iterrows():
   for x in range(51):
      if data_geo['features'][x]['properties']['NAME'] == row['usa_state']:
        data_geo['features'][x]['properties']['sales'] = row['sales']
      else:
        continue

show_maps("Sales", threshold("Sales"))

for x in array_of_year:
    if x == select_time:
        yearly_sales = time_sales_data(select_time)
        yearly_sales = yearly_sales['Sales'].sum()
        product_sold = product_quantity(select_time)
        product_sold = product_sold['count'].sum()
        delta_sales=0
        delta_product=0
        break
    elif x < select_time:
        time_before = select_time - 1
        
        yearly_sales = time_sales_data(select_time)
        yearly_sales = yearly_sales['Sales'].sum()
        sales_before = time_sales_data(time_before)
        sales_before = sales_before['Sales'].sum()
        
        product_sold = product_quantity(select_time)
        product_sold = product_sold['count'].sum()
        product_before = product_quantity(time_before)
        product_before = product_before['count'].sum()
        
        delta_sales = yearly_sales - sales_before
        delta_product = product_sold - product_before
        delta_product = delta_product.item()
        break


col1.metric(
    label="Sales 💲",
    value=yearly_sales,
    delta=delta_sales,
)
col3.metric(
    label="Product Sold 📦",
    value=product_sold,
    delta=delta_product,
)