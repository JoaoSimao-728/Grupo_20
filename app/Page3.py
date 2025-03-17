import streamlit as st
import random
from ollama import chat
from movie_analyzer import MovieAnalyzer  # Import the class

# Load movie data
@st.cache_data
def load_movies():
    analyzer = MovieAnalyzer()
    return analyzer.movies_df

movies_df = load_movies()

# Function to classify genres with Ollama
def classify_genre(movie_summary):
    model = "deepseek-r1:1.5B"
    prompt = f"""
    Based on the following movie summary, classify its genre.
    Respond **ONLY** with a comma-separated list of genres. Do NOT add explanations.

    Movie Summary: {movie_summary}
    Genres:
    """
    response = chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response['message']['content'].strip()

# Function to check if predicted genres match actual genres
def check_genre_match(actual_genres, predicted_genres):
    model = "deepseek-r1:1.5B"
    match_prompt = f"""
    Here are two lists of movie genres. The first list comes from the dataset, and the second is AI-generated.
    Do the AI-generated genres match the actual genres? Answer **ONLY "YES" or "NO"**.

    Actual Genres: {actual_genres}
    AI-Generated Genres: {predicted_genres}
    """
    response = chat(model=model, messages=[{"role": "user", "content": match_prompt}])
    return response['message']['content'].strip()

st.title("🎭 Movie Genre Classification with Local LLM")

if st.button("🔀 Shuffle"):
    # Pick a random movie
    random_movie = movies_df.sample(1).iloc[0]

    movie_title = random_movie["movie_name"]
    movie_summary = random_movie["summary"]
    
    # Clean and filter actual genres (remove unknown tags)
    actual_genres_list = [g for g in random_movie["genres"] if not g.startswith("Unknown")]
    actual_genres = ", ".join(actual_genres_list) if actual_genres_list else "No genres available"

    # Handle missing summary
    if not isinstance(movie_summary, str) or movie_summary.strip() == "":
        movie_summary = random_movie["summary"]
# Display title and summary
st.text_area("🎬 Movie Title & Summary", f"**{movie_title}**\n\n{movie_summary}", height=200)

# Prepare actual genres string for display (after cleaning, as above)
actual_genres_list = [g for g in random_movie["genres"] if g]  # already cleaned of "Unknown"
actual_genres = ", ".join(actual_genres_list) if actual_genres_list else "No genres available"
st.text_area("🎭 Actual Genres", actual_genres)

# Only classify if a summary exists
if not movie_summary or movie_summary == "No summary available.":
    predicted_genres = "Not enough information to classify."
else:
    predicted_genres = classify_genre(movie_summary)

    # Ensure valid output from LLM
    if not predicted_genres or predicted_genres.lower() in ["none", "unknown", "n/a"]:
        predicted_genres = "Could not classify."

    st.text_area("🤖 Predicted Genres by LLM", predicted_genres)

    # Check if the predicted genres match the actual ones (only if LLM classified)
    genre_match = check_genre_match(actual_genres, predicted_genres) if movie_summary != "No summary available." else "N/A"
    st.text_area("✅ Do Genres Match?", genre_match)



