import sys
import os
import streamlit as st
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from movie_analyzer import MovieAnalyzer

# Initialize the MovieAnalyzer class
analyzer = MovieAnalyzer()

# Sidebar for Page Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a Page", ["Main", "Chronological Info"])

if page == "Main":
    # Streamlit App Title
    st.title("🎬 Movie Data Explorer")

    # Sidebar for User Inputs
    st.sidebar.header("🔍 Select Analysis Options")

    # ==========================
    # 📌 Top N Movie Genres
    # ==========================
    st.sidebar.subheader("📌 Top N Movie Genres")
    n_genres = st.sidebar.slider("Select N", min_value=1, max_value=20, value=10)

    if st.sidebar.button("Show Top Genres"):  # ✅ Corrected Indentation
        st.subheader("🎭 Top Movie Genres")
        genres_df = analyzer.movie_type(n_genres)

        # 🔹 Fix Index to Start at 1
        genres_df.index = range(1, len(genres_df) + 1)

        st.dataframe(genres_df)  # ✅ Correct placement

    # ==========================
    # 📊 Actor Count Distribution
    # ==========================
    st.sidebar.subheader("📊 Actor Count Distribution")

    if st.sidebar.button("Show Actor Count Distribution"):
        st.subheader("📊 Distribution of Number of Actors per Movie")

        # Get the data
        actor_counts = analyzer.actor_count(plot=False)

        # Plot in Streamlit
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(actor_counts["Number of Actors"], actor_counts["Movie Count"], color="skyblue", alpha=0.7)
        ax.set_xlabel("Number of Actors in a Movie")
        ax.set_ylabel("Count of Movies")
        ax.set_title("Distribution of Number of Actors per Movie")
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        # Show plot in Streamlit
        st.pyplot(fig)

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
        if filtered_df.empty:
            st.warning("⚠️ No data available for the selected criteria.")
        else:
            st.dataframe(filtered_df.head(10))  # Show first 10 rows

            # Plot the distribution
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.hist(filtered_df["actor_height"], bins=20, color="blue", alpha=0.7)
            ax.set_xlabel("Height (meters)")
            ax.set_ylabel("Frequency")
            ax.set_title(f"Actor Height Distribution ({selected_gender})")
            ax.grid(axis="y", linestyle="--", alpha=0.7)

            # Display the plot
            st.pyplot(fig)

elif page == "Chronological Info":
    st.title("📅 Movie Releases Over Time")

    # Select Genre
    genres = ["Drama", "Comedy", "Action", "Romance", "Horror"]
    selected_genre = st.selectbox("Select a genre", ["All"] + genres)

    # Get movie release data
    data = analyzer.releases() if selected_genre == "All" else analyzer.releases(selected_genre)

    # Plot movie releases per year
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(data['release_date'], data['count'], color='skyblue')
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Movies")
    ax.set_title("Movies Released Per Year")
    st.pyplot(fig)

    # ==========================
    # 🎂 Actor Age Distribution
    # ==========================
    st.title("🎂 Actor Age Distribution")

    mode = st.selectbox("Select mode", ["Year (Y)", "Month (M)"])
    data = analyzer.ages(mode='Y' if mode.startswith("Y") else 'M')

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(data.iloc[:, 0], data['count'], color='green')
    ax.set_xlabel("Year" if mode.startswith("Y") else "Month")
    ax.set_ylabel("Number of Births")
    ax.set_title("Actor Birth Distribution")
    st.pyplot(fig)
