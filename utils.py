import streamlit as st
import openai
import os
from dotenv import load_dotenv
from datetime import datetime

# NOTE: Need API key to be in .env file for application to work
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

if openai.api_key is None:
    raise ValueError("⚠️ OpenAI API key not found! Set it in your environment or add it directly in the script.")


# Calls the OpenAI API with the given model (GPT-3.5-turbo or GPT-4).
def openai_generate(prompt: str, model: str = "gpt-3.5-turbo", temperature=0.7, max_tokens=300):
    response = openai.ChatCompletion.create(
        model=model,  # Either "gpt-3.5-turbo" or "gpt-4"
        messages=[
            {"role": "system", "content": "You are a helpful TV show recommender."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response["choices"][0]["message"]["content"]


# Basic recommendation request with no few-shot examples
def generate_no_few_shot(model: str, user_query: str):
    prompt = f"Recommend a TV show based on these preferences:\n{user_query}\nRecommendation:"
    return openai_generate(prompt, model=model)


# Uses few-shot learning with examples before processing the user request.
def generate_few_shot(model: str, user_query: str, age: int):
    example_1_in = """
    I want a crime drama with a tense storyline under 60 minutes.  My favorite city is Washington D.C.
    """
    example_1_out = """
    I recommend 'The Wire', which delivers suspense in ~47-min episodes and is set largely in the Baltimore area near D.C.
    But this show is rated R and is not suitable for viewers under 18.
    """

    example_2_in = """
    User Preferences: Looking for a kids-friendly sitcom series around 30 minutes.
    User Background: I love to play pranks on people and hang out with my friends.
    Favorite Shows: Wizards of Waverly Place, ICarly
    """
    example_2_out = "I recommend 'Suite Life of Zack and Cody'. While it is age appropriate, it also focuses on two high school boys who love to play pranks and get in trouble."

    example_3_in = "I'm looking for a show that lasted at least 5 seasons and is over 40 min. Sci-fi if possible."
    example_3_out = "The Expanse, Babylon 5, and Stargate are all good options. Star Wars the Clone Wars is also a great choice if you like animation."
    
    prompt = f"""
        Before giving a response, **always check if the show is appropriate** for a {age}-year-old.
        Then, provide **a short explanation** for why this show is recommended.
        Here are some examples of recommendations:

        Example 1:
        User: "{example_1_in}"
        Assistant: "{example_1_out}"

        Example 2:
        User: "{example_2_in}"
        Assistant: "{example_2_out}"

        Example 3:
        User: "{example_3_in}"
        Assistant: "{example_3_out}"

        Most Important Rule:
        Before giving a response, **always check if the show is appropriate** for a person that is **{age} years old** by verifying the content rating or certificate.  
        ❌ Do NOT recommend a show rated **TV-MA, R, or 18+** to someone under 18.  
        ✅ Always prioritize age-appropriate content and clearly state the rating.

        Now the user wants an answer to this request:
        "{user_query}"
        Assistant: (recommendation + reasoning)
        """
    return openai_generate(prompt, model=model)


# Returns recommendations for GPT-3.5-turbo and GPT-4, both pre and post few-shot prompting.
def get_recommendations(age: int, user_query: str, user_info: str = "", favorite_shows: str = "", favorite_city: str = ""):
    results = {}

    # **NEW: Combine all inputs into one prompt**
    combined_query = f"""
    User Preferences: {user_query}
    User Background: {user_info}
    Favorite Shows: {favorite_shows}
    Favorite City: {favorite_city}

    Recommend a TV show that matches their taste while ensuring it's appropriate for a {age}-year-old.
    """
    
    # GPT-3.5-turbo (No Few-Shot)
    results["gpt-3.5-turbo_no_fs"] = generate_no_few_shot("gpt-3.5-turbo", combined_query)

    # GPT-3.5-turbo (Few-Shot)
    results["gpt-3.5-turbo_fs"] = generate_few_shot("gpt-3.5-turbo", combined_query, age)

    # GPT-4 (No Few-Shot)
    results["gpt-4_no_fs"] = generate_no_few_shot("gpt-4", combined_query)

    # GPT-4 (Few-Shot)
    results["gpt-4_fs"] = generate_few_shot("gpt-4", combined_query, age)

    return results



def display_results(outputs):
    st.divider()

    st.subheader("📌 GPT-3.5 turbo (No Few-Shot)")
    st.write(outputs["gpt-3.5-turbo_no_fs"])

    st.divider()

    st.subheader("✅ GPT-3.5 turbo (Responsible, Few-Shot)")
    st.write(outputs["gpt-3.5-turbo_fs"])

    st.divider()

    st.subheader("📌 GPT-4 (No Few-Shot)")
    st.write(outputs["gpt-4_no_fs"])

    st.divider()

    st.subheader("✅ GPT-4 (Responsible, Few-Shot)")
    st.write("💡 AI ensures recommendations match your **age** before responding.")
    st.write(outputs["gpt-4_fs"])


# Manually implements a structured AI pipeline for TV show recommendations.
def structured_recommendation_pipeline(age: int, user_query: str, user_info: str = "", favorite_shows: str = "", favorite_city: str = ""):
    # Calculate decade when user was a teenager to give one nostalgic recommendation
    current_year = datetime.now().year
    nostalgic_decade = ((current_year - age + 10) // 10) * 10
    

    # Step 1: Extract Key Details from User Query
    prompt_extract = f"""
    Extract key details from this request:
    "{user_query}"

    Also consider:
    - User Background: {user_info}
    - Favorite Shows: {favorite_shows}
    - Favorite City: {favorite_city}

    Make sure to not return any shows that were listed in {favorite_shows}

    The priority is to answer the "{user_query}". If possible, then consider the user info: {user_info}, their favorite shows: {favorite_shows}, and a show set in {favorite_city}.

    Return structured output:
    - Genre(s):
    - Duration preference:
    - Any specific actors or themes:
    - Nostalgic decade: {nostalgic_decade}
    - Any similar shows based on favorite shows:
    - A show set in {favorite_city} (if available):
    - User info: {user_info}
    """
    extracted_details = openai_generate(prompt_extract)


    # Step 2: Filter Recommendations by Age, Similar Shows, and Nostalgia
    prompt_filter = f"""
    Considering that the user is {age} years old, GUARANTEE that recommendations meet age-appropriate ratings.
    Then, check which of these shows are similar to any shows in {favorite_shows} and prioritize them in your final response if they fit the other parameters.
    
    The first recommendation **must be a show that premiered in the {nostalgic_decade}s**, matching the user's likely nostalgic period.
    The second recommendation can be from any time period.
    The third recommendation should be **a lesser-known show that fits the request but is not extremely famous.**
    
    # NEW: City-based recommendations
    If a show is set in **{favorite_city}**, prioritize it, but never include it if it is in the {favorite_shows}. 
    If no exact match exists, look for a show with a **similar regional setting** (e.g., NYC -> Boston/Philly, LA -> San Diego/SF, Midwest cities grouped together).
    
    Return structured output (2-3 options for each):
    - First show (from nostalgic decade); possibly set in favorite city
    - Second show (popular show that is likely to be enjoyed)  ideally in or near the favorite city and/or including actors and/or themes that match the user input.
    - Third show (lesser-known show that fits request but isn't famous)

    Here’s the extracted preferences:
    {extracted_details}

    What kind of content should be included/excluded?
    """
    filtered_details = openai_generate(prompt_filter)


    # Step 3: Generate Recommendations Based on Processed Details
    prompt_recommend = f"""
    Recommend **exactly 3 TV shows** that fit:
    {filtered_details}

    - The **first recommendation** must be a show that premiered in the **{nostalgic_decade}s**.
    - The **second recommendation** can be from any time period.
    - The **third recommendation** must be **a hidden gem or lesser-known show**.

    Format response as:
    - Show Name
        - Short Description
        - Why it matches your preferences

     with 2 empty lines between each show.

    When a show is set in or near {favorite_city}, then mention that in the description

    **All shows MUST BE AGE APPROPRIATE**
    **Do NOT repeat any shows in the {favorite_shows}.
    If any of these shows are in {favorite_shows}, remove them and use other one(s) that satisfy {filtered_details}
    """
    final_recommendation = openai_generate(prompt_recommend, model="gpt-4")
    # Step 4: Generate AI Explanation for Transparency  # NEW: AI Explanation Generator
    prompt_explanation = f"""
    Explain **why** these 3 TV show recommendations in {final_recommendation} were selected for the user. Do not add any new recommendations at this point.

    Factors to consider:
    - The user's **age** ({age}) and ensuring content is appropriate.
    - Their **nostalgic decade** ({nostalgic_decade}s), if applicable.
    - Their **favorite shows** and finding similar content.
    - If applicable, ensuring a show is **set in {favorite_city}** or in a similar region.
    - One selection must be a **hidden gem**.

    Provide a **short paragraph for each recommendation**, explaining the reasoning behind the choices. The response should end with a full sentence and no half sentences.
    """
    ai_explanation = openai_generate(prompt_explanation, model="gpt-4")

    return final_recommendation, ai_explanation