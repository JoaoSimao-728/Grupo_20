import streamlit as st
import matplotlib.pyplot as plt
from movie_analyzer import MovieAnalyzer

# Initialize the MovieAnalyzer class
analyzer = MovieAnalyzer()

# Streamlit App Title
st.title("🎬 Movie Data Explorer")

# Sidebar for User Inputs
st.sidebar.header("🔍 Select Analysis Options")

# ==========================
# 📌 Top N Movie Genres
# ==========================
st.sidebar.subheader("📌 Top N Movie Genres")
n_genres = st.sidebar.slider("Select N", min_value=1, max_value=20, value=10)

if st.sidebar.button("Show Top Genres"):
    st.subheader("🎭 Top Movie Genres")
    genres_df = analyzer.movie_type(n_genres)
    st.dataframe(genres_df)

# ==========================
# 📊 Actor Count Distribution
# ==========================
st.sidebar.subheader("📊 Actor Count Distribution")

if st.sidebar.button("Show Actor Count Distribution"):
    st.subheader("📊 Distribution of Number of Actors per Movie")
    analyzer.actor_count(plot=True)

# ==========================
# 📏 Actor Height Distribution
# ==========================
st.sidebar.subheader("📏 Actor Height Distribution")
selected_gender = st.sidebar.selectbox("Select Gender", ["All", "Male", "Female"])
height_min = st.sidebar.number_input("Min Height (m)", min_value=0.5, max_value=2.5, value=1.5)
height_max = st.sidebar.number_input("Max Height (m)", min_value=0.5, max_value=2.5, value=2.0)

if st.sidebar.button("Show Actor Height Distribution"):
    st.subheader(f"📏 Actor Height Distribution ({selected_gender})")

    # Get the filtered DataFrame
    filtered_df = analyzer.actor_distributions(
        gender=selected_gender, min_height=height_min, max_height=height_max, plot=False
    )

    # Debugging: Show filtered DataFrame
    st.write(filtered_df)

    # Check if there is data to plot
    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(filtered_df["actor_height"], bins=20, color="blue", alpha=0.7)
        ax.set_xlabel("Height (meters)")
        ax.set_ylabel("Frequency")
        ax.set_title(f"Actor Height Distribution ({selected_gender})")
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        
        # Display plot in Streamlit
        st.pyplot(fig)
    else:
        st.warning("⚠️ No data available for the selected criteria.")
