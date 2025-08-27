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

st.title('Visitor Statistics')

st.markdown("""
Understanding where your readers come from helps you identify your journal's global reach and can inform decisions about 
language, topics, marketing efforts, and international collaborations.

**Note**: These statistics represent unique visitors filtered using COUNTER standards to remove bot traffic and provide 
accurate geographic readership data.
""")

#check if the df was uploaded
if 'geodf' in st.session_state and st.session_state.get("geodf_valid", True):
    geo_df = st.session_state.geodf

    total_unique = total_visitor_count(geo_df)

    st.subheader('📊 Total Unique Visitors')
    
    st.markdown("""
    This represents the total number of **distinct individuals** who visited your journal during the selected time period. 
    Each unique visitor is counted only once, regardless of how many articles they viewed or how often they returned.
    
    This metric helps you understand your journal's overall reach and audience size.
    """)
    
    # Display total with better formatting
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Total Unique Visitors", f"{total_unique:,}")
    with col2:
        st.markdown("""
        **What this means:**
        - Real people who accessed your journal
        - Bot traffic has been filtered out
        - Each person counted only once per time period
        """)

    st.subheader('🌍 Visitor Distribution by Country')
    
    # Add explanatory context
    st.markdown("""
    Geographic data reveals your journal's international impact and can help you understand:
    - Which regions find your content most relevant
    - Potential collaboration opportunities
    - Language and cultural considerations for future content
    - Time zone considerations for announcements or events
    """)

    unique_countries = list(set(geo_df['Country']))
    unique_countries = sorted(unique_countries)

    option = st.selectbox(
        "Select a country to see detailed statistics:",
        unique_countries,
        index=92 if len(unique_countries) > 92 else 0  # default is the Netherlands if available
    )

    number = filter_visitors(geo_df, option)
    percentage = round((number/total_unique)*100, 2)

    # Display country-specific data with better formatting
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Unique Visitors", f"{number:,}")
    with col2:
        st.metric("Percentage of Total", f"{percentage}%")
    with col3:
        if total_unique > 0:
            rank_df = geo_overview(geo_df)
            if option in rank_df['Country'].values:
                # Find the position in the sorted list (1-based ranking)
                country_rank = rank_df.reset_index(drop=True)
                country_rank = country_rank[country_rank['Country'] == option].index[0] + 1
                st.metric("Country Rank", f"#{country_rank}")
            else:
                st.metric("Country Rank", "Not in Top 10")

    st.markdown(f"""
    **{number:,} unique visitors** are from **{option}**, representing **{percentage}%** of your total readership.
    
    This tells you how important this market is for your journal's reach and impact.
    """)

    st.subheader("🏆 Top 10 Countries by Readership")
    
    st.markdown("""
    This ranking shows your journal's strongest international audiences. Understanding these patterns can help with:
    - **Content strategy**: Topics that resonate globally vs. regionally
    - **Author outreach**: Identifying regions with engaged readers who might contribute
    - **Marketing focus**: Where to concentrate promotional efforts
    - **Partnership opportunities**: Academic institutions in high-readership countries
    """)
    
    top_countries = geo_overview(geo_df)
    
    # Enhanced display with percentages
    top_countries['Percentage'] = round((top_countries['Unique'] / total_unique) * 100, 2)
    top_countries['Rank'] = range(1, len(top_countries) + 1)
    
    # Reorder columns for better display
    display_df = top_countries[['Rank', 'Country', 'Unique', 'Percentage']].copy()
    display_df.columns = ['Rank', 'Country', 'Unique Visitors', 'Percentage of Total (%)']
    
    st.dataframe(display_df, hide_index=True)
    
    # Add insights section
    st.subheader("📈 Geographic Insights")
    
    if len(top_countries) > 0:
        top_country = top_countries.iloc[0]
        top_3_percentage = round(top_countries.head(3)['Percentage'].sum(), 1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **Concentration Analysis:**
            - **{top_country['Country']}** is your largest audience ({top_country['Percentage']}%)
            - Your **top 3 countries** represent **{top_3_percentage}%** of all visitors
            - You have readers from **{len(unique_countries)}** different countries
            """)
        
        with col2:
            if top_3_percentage < 50:
                st.success("🌐 **Globally Distributed**: Your readership is well-spread internationally")
            elif top_3_percentage < 75:
                st.info("🎯 **Moderately Concentrated**: Strong in key regions with international reach")
            else:
                st.warning("📍 **Highly Concentrated**: Most readers from few countries - consider international outreach")


    # Add FAQ section
    with st.expander("❓ Frequently Asked Questions", expanded=False):
        st.markdown("""
        **Do Bots influence these statistics?**
    
        OJS uses COUNTER-recommended methods to filter out automated activity:
        - Known bot and crawler filtering using COUNTER lists
        - Consolidating multiple views from the same user within 30 seconds into a single view
        - This means your statistics may be lower than raw server logs, but more accurate for real readership
                          
        **Do deleted submissions affect my statistics?**
        
        OJS does not count properly deleted submissions in statistics. However, if your numbers seem off, check for:
        - Duplicate submissions where only one version was published
        - Submissions that were rejected but not properly deleted
        - Multiple versions of the same manuscript
        """)

else:
    st.warning("⚠️ No geographical data found. Please upload a geographical report on the upload page first.")
    if st.button("📂 Go to Upload Page"):
        st.switch_page("Upload.py")