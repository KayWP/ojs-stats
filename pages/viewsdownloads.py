import streamlit as st
import pandas as pd
#from streamlit-extras import stoggle

def article_top5_downloads(df, button):
    if button == 'File Downloads':
        type = 'PDF'
    elif button == 'Abstract views':
        type = 'Abstract Views'
    return df.sort_values(by=type, ascending=False, na_position='last').head(5)

def geo_overview(df):
    result = df.groupby('Country')['Unique'].sum().reset_index()

    sorted_result = result.sort_values(by='Unique', ascending=False, na_position='last')
    
    return sorted_result.head(10)

df = pd.read_csv('sample_stats.csv', skiprows=4)
geo_df = pd.read_csv('geo_stats.csv', skiprows=4)
total_articles = len(df)

st.title('OpenJournals Statistics')
st.header('Top 5 articles')
type = st.radio("Pick one", ["File Downloads", "Abstract views"])
st.write(article_top5_downloads(df, type))