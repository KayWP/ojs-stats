import streamlit as st
import pandas as pd

df = pd.read_csv('sample_stats.csv', skiprows=4)
total_articles = len(df)

st.title('OpenJournals Statistics')
st.write(f"Total amount of published articles: {total_articles}")