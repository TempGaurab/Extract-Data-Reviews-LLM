import streamlit as st
import pandas as pd
from google_play_scraper import reviews, Sort
import time

# --- Page Config ---
st.set_page_config(page_title="Play Store Scraper", page_icon="📱")

st.title("📱 Google Play Reviews Scraper")
st.markdown("Drag and drop a CSV file with `app_name` and `package_name` columns to start.")

# --- 1. The Drag & Drop Area ---
uploaded_file = st.file_uploader("Upload Apps CSV", type=["csv"])

# User settings
target_count = st.number_input("Reviews per App", min_value=100, max_value=100000, value=1000, step=100)

if uploaded_file is not None:
    try:
        # Read the uploaded CSV
        apps_df = pd.read_csv(uploaded_file)
        
        # specific check to ensure columns exist
        if 'app_name' not in apps_df.columns or 'package_name' not in apps_df.columns:
            st.error("CSV must contain columns: `app_name` and `package_name`")
        else:
            if st.button("Start Scraping"):
                all_reviews = []
                
                # Create a progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                total_apps = len(apps_df)
                
                # --- 2. Scraping Loop ---
                for index, row in apps_df.iterrows():
                    app_name = row['app_name']
                    package_id = row['package_name']
                    
                    status_text.text(f"Scraping {app_name} ({package_id})...")
                    
                    try:
                        # We use the library's internal pagination by setting count
                        # Note: For very large counts (>10k), this might take a while per app
                        result, _ = reviews(
                            package_id,
                            lang='en',
                            country='us',
                            sort=Sort.NEWEST,
                            count=target_count
                        )
                        
                        # Add metadata
                        for r in result:
                            r['app_name'] = app_name
                            
                        all_reviews.extend(result)
                        
                    except Exception as e:
                        st.warning(f"Could not scrape {app_name}: {e}")
                    
                    # Update progress
                    progress_bar.progress((index + 1) / total_apps)

                status_text.text("Scraping Complete!")
                
                # --- 3. Display & Download ---
                if all_reviews:
                    result_df = pd.read_json(pd.DataFrame(all_reviews).to_json()) # Clean format
                    
                    # Select useful columns
                    cols_to_keep = ['at', 'app_name', 'score', 'content', 'thumbsUpCount']
                    # Only keep columns that actually exist in the result
                    final_cols = [c for c in cols_to_keep if c in result_df.columns]
                    result_df = result_df[final_cols]

                    st.success(f"Successfully scraped {len(result_df)} reviews!")
                    st.dataframe(result_df.head())

                    # CSV Download Button
                    csv = result_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Reviews CSV",
                        data=csv,
                        file_name='scraped_reviews.csv',
                        mime='text/csv',
                    )
                else:
                    st.warning("No reviews found.")
                    
    except Exception as e:
        st.error(f"Error reading file: {e}")

st.markdown("---")
st.caption("Instructions: Create a CSV with headers `app_name,package_name` and drag it above.")