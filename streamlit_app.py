import streamlit as st
import pandas as pd
from google_play_scraper import reviews, Sort, search
import time

# --- Page Config ---
st.set_page_config(page_title="Play Store Scraper", page_icon="📱")

st.title("📱 Google Play Reviews Scraper")
st.markdown("Enter the name of an app to automatically find and scrape its reviews.")

# --- 1. Input Area (Search instead of Drag & Drop) ---
app_name_input = st.text_input("Enter App Name (e.g., ChatGPT, Claude, Gemini)")

# User settings
target_count = st.number_input("Reviews to Scrape", min_value=100, max_value=100000, value=1000, step=100)

if st.button("Find & Scrape"):
    if not app_name_input:
        st.error("Please enter an app name first.")
    else:
        try:
            # --- 2. Search for the App ---
            status_text = st.empty()
            status_text.text(f"Searching for '{app_name_input}'...")
            
            search_results = search(
                app_name_input,
                lang='en',
                country='us'
            )

            if not search_results:
                st.error(f"No app found for '{app_name_input}'. Try a different name.")
            else:
                # Get the top result
                best_match = search_results[0]
                found_title = best_match['title']
                package_id = best_match['appId']
                icon_url = best_match.get('icon')

                # Show what we found
                col1, col2 = st.columns([1, 5])
                with col1:
                    if icon_url:
                        st.image(icon_url, width=60)
                with col2:
                    st.success(f"Found: **{found_title}**")
                    st.caption(f"Package ID: `{package_id}`")

                # --- 3. Scraping Logic ---
                status_text.text(f"Scraping reviews for {found_title}...")
                progress_bar = st.progress(0)
                
                try:
                    # We use the library's internal pagination by setting count
                    # Note: For very large counts (>10k), this might take a while
                    result, _ = reviews(
                        package_id,
                        lang='en',
                        country='us',
                        sort=Sort.NEWEST,
                        count=target_count
                    )
                    
                    progress_bar.progress(100)
                    status_text.text("Scraping Complete!")
                    
                    # --- 4. Display & Download ---
                    if result:
                        # Convert to DataFrame
                        all_reviews = []
                        for r in result:
                            r['app_name'] = found_title # Use the official Play Store title
                            all_reviews.append(r)
                            
                        result_df = pd.read_json(pd.DataFrame(all_reviews).to_json()) # Clean format
                        
                        # Select useful columns
                        cols_to_keep = ['at', 'app_name', 'score', 'content', 'thumbsUpCount']
                        # Only keep columns that actually exist in the result
                        final_cols = [c for c in cols_to_keep if c in result_df.columns]
                        result_df = result_df[final_cols]

                        st.success(f"Successfully scraped {len(result_df)} reviews!")
                        st.dataframe(result_df.head())

                        # CSV Download Button
                        file_name_slug = found_title.lower().replace(' ', '_')
                        csv = result_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download Reviews CSV",
                            data=csv,
                            file_name=f'{file_name_slug}_reviews.csv',
                            mime='text/csv',
                        )
                    else:
                        st.warning("No reviews found for this app.")
                        
                except Exception as e:
                    st.error(f"Error during scraping: {e}")
                    
        except Exception as e:
            st.error(f"Error searching for app: {e}")

st.markdown("---")
st.caption("Note: This tool fetches the most recent reviews available.")