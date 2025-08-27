import streamlit as st
import pandas as pd

#function that counts the top 5 downloads
def article_top5_downloads(df, button):
    if button == 'File Downloads':
        type = 'PDF'
    elif button == 'Abstract views':
        type = 'Abstract Views'
    return df.sort_values(by=type, ascending=False, na_position='last').head(5)

st.title('OpenJournals Statistics')

#check if the df was uploaded
if 'df' in st.session_state and st.session_state.df is not None:
    df = st.session_state.df
    st.header('Top 5 articles')
    type = st.radio("Pick one", ["File Downloads", "Abstract views"])
    st.write(article_top5_downloads(df, type))

else:
    st.warning("⚠️ No data found. Please upload an article report on the upload page first.")
    if st.button("📂 Go to Upload Page"):
        st.switch_page("pages/Upload.py")  # Adjust the page name as needed