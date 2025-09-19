import streamlit as st
import pandas as pd

def validate_csv(df, column_lists):
    """
    Validate CSV against multiple possible column configurations
    column_lists should be a list of lists, where each inner list represents
    a valid column configuration
    """
    actual_columns = list(df.columns)
    
    for valid_columns in column_lists:
        if actual_columns == valid_columns:
            return True
    return False

def generate_temporal_span(csv_file):
    ...

# initialize a session state for the dataframe if it does not exist yet
if 'df' not in st.session_state:
    st.session_state.df = None

if 'df_valid' not in st.session_state:
    st.session_state.df_valid = False

if 'geodf' not in st.session_state:
    st.session_state.geodf = None

if 'geodf_valid' not in st.session_state:
    st.session_state.geodf_valid = False

st.title('OpenJournals Statistics')

st.markdown("""
Welcome to **OpenJournals Statistics** 👋  

This dashboard helps you explore how readers engage with your journal articles.  
- 📊 See which articles are most popular by downloads and abstract views.  
- 🌍 Discover where your readers are located around the world.  

To get started, please upload your **Articles Report** and **Geographic Report** exported from OJS (Open Journal Systems).  
            
Once uploaded, you'll be able to navigate between pages to analyze your readership in detail using the sidebar on the left.
""")

st.subheader("Upload files here")

csv_file = st.file_uploader("Upload your OJS Articles Report here (Statistics → Articles → Download Report → Download Articles)")

if csv_file is not None:
    # Check if the uploaded file is a CSV
    if not csv_file.name.lower().endswith('.csv'):
        st.error("❌ Please upload a CSV file (.csv extension required)")
    else:
        try:
            # Cache the uploaded file so all pages can access it
            st.session_state.df = pd.read_csv(csv_file, skiprows=4)
            
            try:
                # Define valid column configurations for articles (English and Dutch)
                articles_column_configs = [
                    ['ID', 'Title', 'Total', 'Abstract Views', 'File Views', 'PDF', 'HTML', 'Other'],  # English
                    ['ID', 'Titel', 'Total', 'Samenvatting bekeken', 'File Views', 'PDF', 'HTML', 'Overig']  # Dutch
                ]
                
                if validate_csv(st.session_state.df, articles_column_configs):
                    st.session_state.df_valid = True
                    st.success("✅ Article Data uploaded and cached successfully!")
                else:
                    st.warning("The CSV you uploaded does not appear to be an OJS Article Report.")
                    with st.expander("Show detected columns"):
                        st.write("Detected columns:", list(st.session_state.df.columns))
                        st.write("Expected columns (English):", articles_column_configs[0])
                        st.write("Expected columns (Dutch):", articles_column_configs[1])
            except Exception as validation_error:
                st.warning("The CSV you uploaded does not appear to be an OJS Article Report.")
                # Optionally show the technical error for debugging
                with st.expander("Technical details (for debugging)"):
                    st.error(f"Validation error: {str(validation_error)}")
                    
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")

csv_file_geo = st.file_uploader("Upload your OJS Geographic Report here (Statistics → Articles → Download Report → Download Geographic)")

if csv_file_geo is not None:
    #check if the uploaded file is a CSV
    if not csv_file_geo.name.lower().endswith('.csv'):
        st.error("❌ Please upload a CSV file (.csv extension required)")
    else:
        try:
            #cache the uploaded file so all pages can access it
            st.session_state.geodf = pd.read_csv(csv_file_geo, skiprows=4)
            
            try:
                # Define valid column configurations for geographic data (English and Dutch)
                geo_column_configs = [
                    ['City', 'Region', 'Country', 'Total', 'Unique'],  # English
                    ['Stad', 'Regio', 'Land', 'Total', 'Unique']  # Dutch
                ]
                
                if validate_csv(st.session_state.geodf, geo_column_configs):
                    st.session_state.geodf_valid = True
                    st.success("✅ Geographical Data uploaded and cached successfully!")
                else:
                    st.warning("The CSV you uploaded does not appear to be an OJS Geographic Report.")
                    with st.expander("Show detected columns"):
                        st.write("Detected columns:", list(st.session_state.geodf.columns))
                        st.write("Expected columns (English):", geo_column_configs[0])
                        st.write("Expected columns (Dutch):", geo_column_configs[1])
            except Exception as validation_error:
                st.warning('The CSV you uploaded does not appear to be a valid OJS Geographic Report.')
                with st.expander("Technical details (for debugging)"):
                    st.error(f"Validation error: {str(validation_error)}")

        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
    
    

st.markdown("""
### How to the necessary files in OJS 3.4

1. **Log in** to your OJS dashboard as a *Journal Manager* or *Editor*.  
2. From the left-hand menu, open **Statistics → Articles**.  
3. Use the **date range selector** in the top-right corner to adjust the reporting period (default: last 30 days).  
4. Click **Download Report**.  
5. Select **Download Articles** to export the article report as a **CSV file**, which you can upload in the first box on this page.
6. Select **Download Geographic** to export the geographical report as a **CSV file**, which you can upload in the second box on this page. 
""")