import streamlit as st
import openai
import os
import random
from utils import *

openai.api_key = os.getenv("OPENAI_API_KEY")

def app():
    st.title("🎬 AI-Powered TV Show Recommender")
    st.write("💡 **This AI ensures all recommendations match your age.**")
    st.write("🔍 **We compare GPT-4o Mini vs. GPT-4, before and after adding responsible AI rules.**")

    # Age Input
    age = st.number_input("📌 Enter your age:", min_value=1, max_value=120, value=16)
    if age < 5:
        st.warning("⚠️ We recommend TV shows only for ages 5 and up.  Go play outside or read a book if you are younger than 5!")
        st.stop()

    # User Preference Input
    user_query = st.text_area("🎭 Describe what you're looking for:", "Ex. I want a comedic show under 30 minutes.")

    # Generate Recommendations
    if st.button("🎲 Surprise Me!"):
        random_prompts = [
            "Give me a hidden gem TV show that most people don't know about.",
            "Suggest a classic sitcom that aged well.",
            "I want a highly rated sci-fi series from the last 10 years.",
            "What is a fantasy TV show that fans of 'Lord of the Rings' would love?",
            "Suggest an anime that even non-anime fans would enjoy.",
        ]
        user_query = random.choice(random_prompts)
        st.text(f"🎭 Surprise request: {user_query}")
        outputs = get_recommendations(age, user_query)
        display_results(outputs)

    if st.button("🎥 Get Recommendations"):
        with st.spinner("🤖 Generating recommendations..."):
            outputs = get_recommendations(age, user_query)
        
        display_results(outputs)

if __name__ == "__main__":
    app()
