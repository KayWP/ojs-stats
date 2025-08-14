import streamlit as st
import pandas as pd
#from streamlit-extras import stoggle

def geo_overview(df):
    result = df.groupby('Country')['Unique'].sum().reset_index()

    sorted_result = result.sort_values(by='Unique', ascending=False, na_position='last')
    
    return sorted_result.head(10)

def total_visitor_count(df):
    return sum(df['Total'])

geo_df = pd.read_csv('geo_stats.csv', skiprows=4)

st.title('OpenJournals Statistics')
st.header('Total Unique Users')
st.write(str(total_visitor_count(geo_df)))

st.header('Geographical overview')
st.write(geo_overview(geo_df))