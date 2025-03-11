import streamlit as st
import openai
import os
import random
from utils import *

openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit app for TV show recommendations
def app():
    st.title("🎬 Personalized AI Content Recommendation Engine")
    st.write("💡 **This service compares different AI recommendation methods while giving age-appropriate options.**")

    # Age Input
    age = st.number_input("📌 Enter your age:", max_value=120, value=1)
    if age < 5:
        st.warning("⚠️ We recommend TV shows only for ages 5 and up.  Go play outside or read a book if you are younger than 5!")
        st.stop()

    favorite_city = st.text_input("🏙️ What is your favorite city in the USA? (optional)", "Ex. New York, Chicago, Los Angeles")

    # **NEW: Added personalization inputs**
    user_info = st.text_area("🧑‍💻 Tell us about yourself (optional):", "Ex. I love adventure and mystery. I enjoy deep storytelling.")
    favorite_shows = st.text_area("📺 What are some shows you liked? (optional):", "Ex. Stranger Things, Sherlock, and The Office.")

    # User Preference Input
    user_query = st.text_area("🎭 Describe what you're looking for:", "Ex. I want a comedic show under 30 minutes.")

    # **User Chooses AI Mode**
    mode = st.radio("⚙️ Choose AI Mode:", ["🔹 Standard Mode", "🛠️ Structured AI Workflow"])

    # Surprise Me Mode
    # if st.button("🎲 Surprise Me!"):
    #     random_prompts = [
    #         "Give me a hidden gem TV show that most people don't know about.",
    #         "Suggest a classic sitcom that aged well.",
    #         "I want a highly rated sci-fi series from the last 10 years.",
    #         "What is a fantasy TV show that fans of 'Lord of the Rings' would love?",
    #         "Suggest an anime that even non-anime fans would enjoy.",
    #     ]
    #     user_query = random.choice(random_prompts)
    #     st.text(f"🎭 Surprise request: {user_query}")

    # AI Recommendation
    if st.button("🎥 Get Recommendations"):
        with st.spinner("🤖 Generating recommendations..."):
            if mode == "🔹 Standard Mode":
                outputs = get_recommendations(age, user_query, user_info, favorite_shows, favorite_city)  # **Updated Function Call**
                display_results(outputs)
            elif mode == "🛠️ Structured AI Workflow":
                structured_result, ai_explanation = structured_recommendation_pipeline(age, user_query, user_info, favorite_shows, favorite_city)  # **Updated Function Call**
                st.subheader("🛠️ Structured AI Workflow Recommendation")
                st.write(structured_result)
                st.subheader("📖 AI Explanation: Why These Shows Were Chosen")  
                st.write(ai_explanation)  

if __name__ == "__main__":
    app()
