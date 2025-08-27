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
You can switch between **File Downloads** (deeper engagement) and **Abstract Views** (initial interest). 
This helps identify which content is generating the most interest and how readers interact with your journal.
""")

# Add detailed explanation of metrics
with st.expander("📖 Understanding These Metrics", expanded=False):
    st.markdown("""
    **Abstract Views** measure **initial interest**:
    - Recorded when someone visits the article's landing page
    - Shows the article title, authors, abstract, and keywords
    - Indicates browsing behavior and topic relevance
    - Higher abstract views suggest good discoverability (SEO, keywords, titles)
    
    **File Downloads** measure **deeper engagement**:
    - Recorded when someone opens the PDF or file viewer
    - Indicates serious intent to read or reference the article
    - Generally represents higher-value interactions
    - Downloads may be accessed directly via Google or bookmarks, bypassing the abstract page
    
    **Interpreting the Comparison**:
    - **Downloads > Abstract Views**: Readers are finding your content directly (good SEO, direct links)
    - **Abstract Views > Downloads**: Normal pattern showing browsing vs. committed reading
    - **High Abstract, Low Downloads**: May indicate titles/abstracts are appealing but content doesn't match expectations
    """)

#check if the df was uploaded
if 'df' in st.session_state and st.session_state.df is not None:
    df = st.session_state.df
    
    st.header('Top 5 Articles by Engagement')
    
    # Add context about the ranking
    st.markdown("""
    **Choose your ranking method:**
    - **Downloads** reflect deeper engagement and serious readership intent
    - **Abstract views** show general curiosity, browsing patterns, and content discoverability
    
    Both metrics are filtered using COUNTER standards to remove bot traffic and provide accurate readership data.
    """)
    
    type = st.radio("Pick one", ["File Downloads", "Abstract views"])
    
    # Add interpretation based on selected metric
    if type == "File Downloads":
        st.info("📄 **File Downloads** - These articles have the highest reader commitment. People are actively opening and likely reading or referencing these papers.")
    else:
        st.info("👀 **Abstract Views** - These articles are attracting the most initial interest. They have strong titles, good SEO, or are being widely browsed.")
    
    top5_df = article_top5_downloads(df, type)
    st.write(top5_df)
    
    # Add insights section
    if not top5_df.empty:
        st.subheader("📊 Quick Insights")
        
        if type == "File Downloads":
            max_downloads = top5_df['PDF'].max()
            min_downloads = top5_df['PDF'].min()
            avg_downloads = top5_df['PDF'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Highest Downloads", f"{max_downloads:,.0f}")
            with col2:
                st.metric("Lowest in Top 5", f"{min_downloads:,.0f}")
            with col3:
                st.metric("Average (Top 5)", f"{avg_downloads:,.0f}")
                
            st.markdown(f"""
            **What this tells you:**
            - Your most downloaded article has been accessed **{max_downloads:,.0f}** times
            - There's a range of **{max_downloads - min_downloads:,.0f}** downloads between your top and 5th-ranked articles
            - High download numbers indicate strong reader engagement and content value
            """)
        
        else:  # Abstract views
            max_views = top5_df['Abstract Views'].max()
            min_views = top5_df['Abstract Views'].min()
            avg_views = top5_df['Abstract Views'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Highest Views", f"{max_views:,.0f}")
            with col2:
                st.metric("Lowest in Top 5", f"{min_views:,.0f}")
            with col3:
                st.metric("Average (Top 5)", f"{avg_views:,.0f}")
                
            st.markdown(f"""
            **What this tells you:**
            - Your most viewed article abstract has been seen **{max_views:,.0f}** times
            - There's a range of **{max_views - min_views:,.0f}** views between your top and 5th-ranked articles
            - High abstract views suggest good discoverability and appealing titles/topics
            """)

    # Add FAQ section
    with st.expander("❓ Frequently Asked Questions", expanded=False):
        st.markdown("""
        **What is an Abstract View?**
    
        An abstract view is recorded when someone looks at the article landing page which gives an overview of the article. 
        This measures initial interest in your content. Note that reloading or refreshing the landing page will also add 
        an abstract view - these are not unique visitors.
        
        **What is a File Download?**
        
        A file download is recorded when someone opens a file by clicking the relevant button to enter the file or PDF viewer. 
        It represents deeper engagement with your content. Note: it doesn't track whether the file is actually saved to 
        someone's computer.            

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
    st.warning("⚠️ No data found. Please upload an article report on the upload page first.")
    if st.button("📂 Go to Upload Page"):
        st.switch_page("Upload.py")