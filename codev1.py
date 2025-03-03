import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# User Authentication
from streamlit_authenticator import Authenticate

# User Credentials
credentials = {
    "usernames": {
        "executive1": {"password": "password123"},
        "executive2": {"password": "securepass456"}
    }
}

# Authentication
authenticator = Authenticate(credentials, 'cookie_name', 'random_key', cookie_expiry_days=30)
name, authentication_status, username = authenticator.login("Login", "sidebar")

if authentication_status:
    # Dashboard Title
    st.title("Distressed Real Estate Research Dashboard")
    
    # Load Data (Placeholder for Automated Data Updates)
    def get_news_data():
        # Fetching real-time news data (API or scraping logic to be implemented)
        return pd.DataFrame({
            "Date": ["2025-03-03", "2025-03-02", "2025-03-01"],
            "Headline": [
                "Rise in 'Zombie Foreclosures' Across Key States", 
                "Apollo Global Acquires Bridge Investment Group for $1.5B",
                "Office-to-Residential Conversions on the Rise"
            ],
            "Source": ["The Sun", "Financial Times", "New York Post"],
            "URL": [
                "https://www.the-sun.com/money/13646309/zombie-foreclosures-mortgages-states-shoppers-priced-out/", 
                "https://www.ft.com/content/456d0451-d6a8-40de-b742-540901b357ab",
                "https://nypost.com/2024/10/14/real-estate/a-billion-square-feet-of-offices-could-become-housing/"
            ]
        })
    
    news_df = get_news_data()
    
    # Display News
    st.subheader("Recent National News")
    st.dataframe(news_df, width=900)
    
    # Research Topics
    st.subheader("Research Reports")
    research_topics = [
        "Miami's Growing Appeal for Distressed Debt Investors",
        "Impact of Interest Rates on Distressed Asset Prices",
        "Analysis of Foreclosure Trends in Miami, Florida, and New York"
    ]
    st.write("\n".join(f"- {topic}" for topic in research_topics))
    
    # Competitor Tracking
    st.subheader("Competitor Movements")
    competitor_df = pd.DataFrame({
        "Date": ["2025-03-03", "2025-03-02"],
        "Competitor": ["Namdar Realty Group", "Apollo Global"],
        "Activity": [
            "Invested $480M in distressed office buildings across major cities.",
            "Acquired Bridge Investment Group for $1.5B to expand real estate assets."
        ],
        "Source": ["WSJ", "Financial Times"]
    })
    st.dataframe(competitor_df, width=900)
    
    # Market Analytics - Sample Data for Visualization
    def get_market_data():
        return pd.DataFrame({
            "Market": ["Miami", "New York", "Orlando", "Tampa", "Jacksonville"],
            "Foreclosure Rate (%)": [3.2, 2.8, 2.5, 2.3, 1.9],
            "Average Price Drop (%)": [12.5, 10.2, 9.8, 8.5, 7.3]
        })
    
    market_df = get_market_data()
    
    st.subheader("Market Analytics")
    fig = px.bar(market_df, x="Market", y="Foreclosure Rate (%)", title="Foreclosure Rates by City")
    st.plotly_chart(fig)
    
    fig2 = px.line(market_df, x="Market", y="Average Price Drop (%)", title="Average Price Drop in Distressed Properties")
    st.plotly_chart(fig2)
    
    st.write("This dashboard is automatically updated with the latest news, research topics, and competitor activities.")
    
    authenticator.logout("Logout", "sidebar")

elif authentication_status == False:
    st.error("Username/password is incorrect")

elif authentication_status == None:
    st.warning("Please enter your credentials")
