import streamlit as st
import pandas as pd

# initialize a session state for the dataframe if it does not exist yet
if 'df' not in st.session_state:
    st.session_state.df = None

if 'geodf' not in st.session_state:
    st.session_state.geodf = None

st.title('OpenJournals Statistics')
csv_file = st.file_uploader("Upload your OJS Articles Report here (Statistics → Articles → Download Report → Download Articles)")

csv_file_geo = st.file_uploader("Upload your OJS Geographic Report here (Statistics → Articles → Download Report → Download Geographic)")

if csv_file is not None:
    #cache the uploaded file so all pages can access it
    st.session_state.df = pd.read_csv(csv_file, skiprows=4)
    st.success("✅ Article Data uploaded and cached successfully!")

if csv_file_geo is not None:
    st.session_state.geodf = pd.read_csv(csv_file_geo, skiprows=4)
    st.success("✅ Geographical Data uploaded and cached successfully!")

st.markdown("""
### How to the necessary files in OJS 3.4

1. **Log in** to your OJS dashboard as a *Journal Manager* or *Editor*.  
2. From the left-hand menu, open **Statistics → Articles**.  
3. Use the **date range selector** in the top-right corner to adjust the reporting period (default: last 30 days).  
4. Click **Download Report**.  
5. Select **Download Articles** to export the article report as a **CSV file**, which you can upload in the first box on this page.
6. Select **Download Geographic** to export the geographical report as a **CSV file**, which you can upload in the second box on this page. 
""")