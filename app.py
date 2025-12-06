import streamlit as st
import datetime
import json
import time
from utils import GitHubStorage, fetch_and_analyze

# Page Configuration
st.set_page_config(
    page_title="Personal AI Newsroom",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Secrets
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = st.secrets["REPO_NAME"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    ADMIN_PW = st.secrets["ADMIN_PW"]
except Exception as e:
    st.error(f"Secrets not configured correctly: {e}")
    st.stop()

# Initialize GitHub Storage
storage = GitHubStorage(GITHUB_TOKEN, REPO_NAME)

# --- Helper Functions ---
def load_data(filename, default_value):
    data = storage.load_json(filename)
    return data if data else default_value

def save_data(filename, content):
    return storage.save_json(filename, content)

# --- UI Layout ---

# Sidebar - Admin Login
with st.sidebar:
    st.header("Admin Access")
    admin_password = st.text_input("Password", type="password")
    is_admin = admin_password == ADMIN_PW

# Main Content
st.title("📰 Personal AI Newsroom")
st.markdown("---")

# Tabs
tab1, tab2 = st.tabs(["Today's Briefing", "Admin Dashboard"])

# --- Tab 1: User Mode ---
with tab1:
    # Date Selection
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # Load news data
    news_data = load_data("news_data.json", {})
    
    # Available dates (keys in news_data)
    available_dates = sorted(news_data.keys(), reverse=True)
    
    if not available_dates:
        st.info("No news briefings available yet.")
    else:
        selected_date = st.selectbox("Select Date", available_dates, index=0)
        
        if selected_date:
            st.markdown(news_data[selected_date])
            
    # Update Stats
    if "stats_updated" not in st.session_state:
        stats = load_data("stats.json", {"total_visits": 0, "last_visit": ""})
        stats["total_visits"] += 1
        stats["last_visit"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # We don't want to block the UI for stats saving, so maybe skip or do it silently
        # For now, let's just save it.
        save_data("stats.json", stats)
        st.session_state["stats_updated"] = True

# --- Tab 2: Admin Mode ---
with tab2:
    if not is_admin:
        st.warning("Please enter the correct admin password in the sidebar to access this section.")
    else:
        st.success("Admin Logged In")
        
        # 1. RSS Feed Management
        st.subheader("RSS Feed Management")
        feeds = load_data("feeds.json", [])
        
        # Display current feeds
        if feeds:
            st.table(feeds)
            
            # Delete Feed
            feed_names = [f["name"] for f in feeds]
            feed_to_delete = st.selectbox("Select Feed to Delete", ["None"] + feed_names)
            if feed_to_delete != "None":
                if st.button("Delete Feed"):
                    feeds = [f for f in feeds if f["name"] != feed_to_delete]
                    if save_data("feeds.json", feeds):
                        st.success(f"Deleted {feed_to_delete}")
                        st.rerun()
                    else:
                        st.error("Failed to delete feed.")
        else:
            st.info("No RSS feeds configured.")
            
        # Add New Feed
        with st.form("add_feed_form"):
            new_name = st.text_input("Feed Name")
            new_url = st.text_input("Feed URL")
            submitted = st.form_submit_button("Add Feed")
            
            if submitted and new_name and new_url:
                feeds.append({"name": new_name, "url": new_url})
                if save_data("feeds.json", feeds):
                    st.success(f"Added {new_name}")
                    st.rerun()
                else:
                    st.error("Failed to save feed.")

        st.markdown("---")
        
        # 2. Manual Trigger
        st.subheader("Manual News Analysis")
        if st.button("Fetch & Analyze News"):
            with st.spinner("Fetching RSS feeds and analyzing with Gemini..."):
                if not feeds:
                    st.error("No feeds configured.")
                else:
                    report = fetch_and_analyze(feeds, GEMINI_API_KEY)
                    st.markdown("### Preview")
                    st.markdown(report)
                    
                    # Save to news_data.json
                    current_date = datetime.date.today().strftime("%Y-%m-%d")
                    news_data = load_data("news_data.json", {})
                    news_data[current_date] = report
                    
                    if save_data("news_data.json", news_data):
                        st.success(f"Successfully published news for {current_date}")
                    else:
                        st.error("Failed to save news data.")

        st.markdown("---")
        
        # 3. Stats
        st.subheader("Statistics")
        stats = load_data("stats.json", {"total_visits": 0, "last_visit": "N/A"})
        st.json(stats)
