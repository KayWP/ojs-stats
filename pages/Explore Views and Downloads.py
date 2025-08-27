import streamlit as st
import pandas as pd

#function that counts the top 5 downloads
def article_top5_downloads(df, button):
    if button == 'File Downloads':
        type = 'PDF'
    elif button == 'Abstract views':
        type = 'Abstract Views'
    return df.sort_values(by=type, ascending=False, na_position='last').head(5)

st.title('Views and Downloads')
st.markdown("""
This section highlights the most popular articles based on the selected metric. 
            You can switch between **File Downloads** (how many times an article’s PDF was downloaded) and **Abstract Views** (how many times its abstract page was opened). 
            This helps identify which content is generating the most interest.
""")

#check if the df was uploaded
if 'df' in st.session_state and st.session_state.df is not None:
    df = st.session_state.df
    st.header('Top 5 articles')
    st.markdown("Choose how you’d like to rank articles. Downloads reflect deeper engagement, while abstract views show general curiosity or browsing.")
    type = st.radio("Pick one", ["File Downloads", "Abstract views"])
    
    st.write(article_top5_downloads(df, type))

else:
    st.warning("⚠️ No data found. Please upload an article report on the upload page first.")
    if st.button("📂 Go to Upload Page"):
        st.switch_page("Upload.py")  # Adjust the page name as needed