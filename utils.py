import streamlit as st
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

if openai.api_key is None:
    raise ValueError("⚠️ OpenAI API key not found! Set it in your environment or add it directly in the script.")

def openai_generate(prompt: str, model: str = "gpt-3.5-turbo", temperature=0.7, max_tokens=200):
    """
    Calls the OpenAI API with the given model (GPT-3.5-turbo or GPT-4).
    """
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

def generate_no_few_shot(model: str, user_query: str):
    """
    Basic recommendation request with no few-shot examples.
    """
    prompt = f"Recommend a TV show based on these preferences:\n{user_query}\nRecommendation:"
    return openai_generate(prompt, model=model)

def generate_few_shot(model: str, user_query: str, age: int):
    """
    Uses few-shot learning with examples before processing the user request.
    """
    example_1_in = "I want a crime drama with a tense storyline under 60 minutes."
    example_1_out = "I recommend 'Breaking Bad', which delivers suspense in ~47-min episodes."

    example_2_in = "Looking for a kids-friendly fantasy series around 30 minutes."
    example_2_out = "I recommend 'The Owl House', a fun fantasy cartoon with 22-min episodes."

    example_3_in = "Give me some options for a show that stars Allison Janney"
    example_3_out = "You should check out West Wing if you like political dramas or Mom if you feel more in the mood for a sitcom."

    example_4_in = "I'm looking for a show that lasted at least 5 seasons and is over 40 min. Sci-fi if possible."
    example_4_out = "The Expanse, Babylon 5, and Stargate are all good options. Star Wars the Clone Wars is also a great choice if you like animation."
    
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

        Example 4:
        User: "{example_4_in}"
        Assistant: "{example_4_out}"

        Most Important Rule:
        Before giving a response, **always check if the show is appropriate** for a person that is **{age} years old** by verifying the content rating or certificate.  
        ❌ Do NOT recommend a show rated **TV-MA, R, or 18+** to someone under 18.  
        ✅ Always prioritize age-appropriate content and clearly state the rating.

        Now the user wants an answer to this request:
        "{user_query}"
        Assistant: (recommendation + reasoning)
        """
    return openai_generate(prompt, model=model)

def get_recommendations(age: int, user_query: str):
    """
    Returns recommendations for GPT-3.5-turbo and GPT-4, both pre and post few-shot prompting.
    """
    results = {}

    # GPT-3.5-turbo (No Few-Shot)
    results["gpt-3.5-turbo_no_fs"] = generate_no_few_shot("gpt-3.5-turbo", user_query)

    # GPT-3.5-turbo (Few-Shot)
    results["gpt-3.5-turbo_fs"] = generate_few_shot("gpt-3.5-turbo", user_query, age)

    # GPT-4 (No Few-Shot)
    results["gpt-4_no_fs"] = generate_no_few_shot("gpt-4", user_query)

    # GPT-4 (Few-Shot)
    results["gpt-4_fs"] = generate_few_shot("gpt-4", user_query, age)

    return results

def display_results(outputs):
    # Display Results
    st.divider()  # Adds a line separator

    st.subheader("📌 GPT-3.5 turbo (No Few-Shot)")
    st.write(outputs["gpt-3.5-turbo_no_fs"])

    st.divider()

    st.subheader("✅ GPT-3.5 turbo (Responsible, Few-Shot)")
    st.write("💡 AI ensures recommendations match your **age** before responding.")
    st.write(outputs["gpt-3.5-turbo_fs"])

    st.divider()

    st.subheader("📌 GPT-4 (No Few-Shot)")
    st.write(outputs["gpt-4_no_fs"])

    st.divider()

    st.subheader("✅ GPT-4 (Responsible, Few-Shot)")
    st.write("💡 AI ensures recommendations match your **age** before responding.")
    st.write(outputs["gpt-4_fs"])