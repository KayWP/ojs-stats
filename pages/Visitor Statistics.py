import streamlit as st
import pandas as pd

def geo_overview(df):
    result = df.groupby('Country')['Unique'].sum().reset_index()

    sorted_result = result.sort_values(by='Unique', ascending=False, na_position='last')
    
    return sorted_result.head(10)

def total_visitor_count(df):
    return sum(df['Total'])

def filter_visitors(df, country):
    filtered_df = df[df['Country'] == country]
    return sum(filtered_df['Unique'])

st.title('Visitor statistics')

#check if the df was uploaded
if 'geodf' in st.session_state and st.session_state.geodf is not None:
    geo_df = st.session_state.geodf

    total_unique = total_visitor_count(geo_df)

    st.subheader('Total Unique Users')
    
    st.markdown("""
    This is the total number of distinct visitors recorded in your dataset. Each unique visitor is only counted once, no matter how many times they visited.
    """)
    
    st.write(str(f"Unique visitor count: {total_unique}"))

    st.subheader('Users per country')
    unique_countries = list(set(geo_df['Country']))
    unique_countries = sorted(unique_countries)
    st.markdown("Here you can explore what share of your audience comes from each country. Select a country to see both the raw number of unique visitors and what percentage they represent out of all visitors.")

    option = st.selectbox(
        "What percentage of my users is from this country?",
        unique_countries,
        index=92 #default is the Netherlands
    )

    
    number = filter_visitors(geo_df, option)
    percentage = round((number/total_unique)*100, 2)

    st.write(f"{number} unique visitors are from {option}. This is {percentage}% of your total unique visitors.")

    st.subheader("Top 10 Countries")
    st.markdown('This table lists the top 10 countries where your journal is accessed most frequently. It helps you quickly identify your strongest international audiences')
    st.write(geo_overview(geo_df))

else:
    st.warning("⚠️ No geographical data found. Please upload a geographical report on the upload page first.")
    if st.button("📂 Go to Upload Page"):
        st.switch_page("Upload.py")  # Adjust the page name as needed
