import streamlit as st
import pandas as pd
from google_play_scraper import reviews, Sort
import time

# --- Page Config ---
st.set_page_config(page_title="Play Store Scraper", page_icon="📱")

st.title("📱 Google Play Reviews Scraper")
st.markdown("Select an LLM app to scrape its reviews from Google Play Store.")

# --- Hardcoded Top LLM Apps ---
LLM_APPS = {
    "ChatGPT": {
        "package_id": "com.openai.chatgpt",
        "icon": "https://play-lh.googleusercontent.com/lXS65xSPXgO6-M5EG8-b6ReZPL4V-PVLrT-PsLnPQX-IHbBhQGDTLEGBJ3nSZBZJqGM"
    },
    "Claude": {
        "package_id": "com.anthropic.claude",
        "icon": "https://play-lh.googleusercontent.com/uPDH5Bfq3mlXPZF6OBBpBPVCDqOLnZjLqzlEE9bYZa5LHJMxNGMZQlOJL9W8g5sW8A"
    },
    "Gemini (Google)": {
        "package_id": "com.google.android.apps.bard",
        "icon": "https://play-lh.googleusercontent.com/VHsqXMhbxXNWGhzXoT7MmcbQ4O5Y6Z2Kk5x6b8v9Z0a1b2c3d4e5f6g7h8i9j0k1"
    },
    "Microsoft Copilot": {
        "package_id": "com.microsoft.copilot",
        "icon": "https://play-lh.googleusercontent.com/9dGgPyPf0EzPVg_VJmTvqoXqC0e0F1Y1L2N3P4Q5R6S7T8U9V0W1X2Y3Z4A5B6C7"
    },
    "Perplexity": {
        "package_id": "ai.perplexity.app.android",
        "icon": "https://play-lh.googleusercontent.com/2xE_j5_vZQHbQZ5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5"
    },
    "Meta AI": {
        "package_id": "com.meta.ai.app",
        "icon": "https://play-lh.googleusercontent.com/3xE_j5_vZQHbQZ5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5"
    },
    "Grok": {
        "package_id": "com.x.grok",
        "icon": "https://play-lh.googleusercontent.com/4xE_j5_vZQHbQZ5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5Y5Z5"
    }
}

# --- 1. App Selection Dropdown ---
selected_app = st.selectbox(
    "Select LLM App",
    options=list(LLM_APPS.keys()),
    index=0
)

# Display selected app info
app_info = LLM_APPS[selected_app]
col1, col2 = st.columns([1, 5])
with col1:
    st.image(app_info["icon"], width=60)
with col2:
    st.info(f"**{selected_app}**")
    st.caption(f"Package ID: `{app_info['package_id']}`")

# User settings
target_count = st.number_input("Reviews to Scrape", min_value=100, max_value=100000, value=1000, step=100)

if st.button("🚀 Start Scraping"):
    package_id = app_info["package_id"]
    
    # --- Scraping Logic ---
    status_text = st.empty()
    status_text.text(f"Scraping reviews for {selected_app}...")
    progress_bar = st.progress(0)
    
    try:
        # Scrape reviews
        result, _ = reviews(
            package_id,
            lang='en',
            country='us',
            sort=Sort.NEWEST,
            count=target_count
        )
        
        progress_bar.progress(100)
        status_text.text("✅ Scraping Complete!")
        
        # --- Display & Download ---
        if result:
            # Convert to DataFrame
            all_reviews = []
            for r in result:
                r['app_name'] = selected_app
                all_reviews.append(r)
                
            result_df = pd.DataFrame(all_reviews)
            
            # Select useful columns
            cols_to_keep = ['at', 'app_name', 'score', 'content', 'thumbsUpCount', 'reviewId']
            final_cols = [c for c in cols_to_keep if c in result_df.columns]
            result_df = result_df[final_cols]

            st.success(f"Successfully scraped **{len(result_df)}** reviews!")
            
            # Show preview
            st.subheader("Preview")
            st.dataframe(result_df.head(10), use_container_width=True)
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Reviews", len(result_df))
            with col2:
                st.metric("Avg Rating", f"{result_df['score'].mean():.2f}")
            with col3:
                st.metric("Total Thumbs Up", f"{result_df['thumbsUpCount'].sum():,}")

            # CSV Download Button
            file_name_slug = selected_app.lower().replace(' ', '_').replace('(', '').replace(')', '')
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
        st.error(f"❌ Error during scraping: {e}")
        st.info("Tip: Try reducing the number of reviews or check your internet connection.")

st.markdown("---")
st.caption("📌 This tool fetches the most recent reviews from Google Play Store for the selected LLM app.")