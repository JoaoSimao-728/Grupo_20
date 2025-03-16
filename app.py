import streamlit as st
import matplotlib.pyplot as plt
from movie_analyzer import MovieAnalyzer
import Page3  

@st.cache_data
def load_data():
    return MovieAnalyzer()

analyzer = load_data()

# ==========================
# 🎛 Sidebar for Navigation
# ==========================
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a Page", ["Main", "Chronological Info", "Classification"])

# ==========================
# 🏠 Main Page
# ==========================
if page == "Main":
    st.title("🎬 Movie Data Explorer")

    st.sidebar.header("🔍 Select Analysis Options")

    # 📌 Top N Movie Genres
    st.sidebar.subheader("📌 Top N Movie Genres")
    n_genres = st.sidebar.slider("Select N", min_value=1, max_value=20, value=10)

    if st.sidebar.button("Show Top Genres"):  
        st.subheader("🎭 Top Movie Genres")
        genres_df = analyzer.movie_type(n_genres)
        genres_df.index = range(1, len(genres_df) + 1)
        st.dataframe(genres_df)

    # 📊 Actor Count Distribution
    st.sidebar.subheader("📊 Actor Count Distribution")

    if st.sidebar.button("Show Actor Count Distribution"):
        st.subheader("📊 Distribution of Number of Actors per Movie")
        actor_counts = analyzer.actor_count(plot=False)
        if not actor_counts.empty:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(actor_counts["Number of Actors"], actor_counts["Movie Count"], color="skyblue", alpha=0.7)
            ax.set_xlabel("Number of Actors in a Movie")
            ax.set_ylabel("Count of Movies")
            ax.set_title("Distribution of Number of Actors per Movie")
            ax.grid(axis="y", linestyle="--", alpha=0.7)
            st.pyplot(fig)
        else:
            st.warning("⚠️ No actor data available.")

    # 📏 Actor Height Distribution
    st.sidebar.subheader("📏 Actor Height Distribution")
    selected_gender = st.sidebar.selectbox("Select Gender", ["All", "Male", "Female"])
    min_height = st.sidebar.number_input("Min Height (m)", min_value=0.5, max_value=2.5, value=1.5)
    max_height = st.sidebar.number_input("Max Height (m)", min_value=0.5, max_value=2.5, value=2.0)

    if st.sidebar.button("Show Actor Height Distribution"):
        st.subheader(f"📏 Actor Height Distribution ({selected_gender})")
        filtered_df = analyzer.actor_distributions(gender=selected_gender, min_height=min_height, max_height=max_height)

        if not filtered_df.empty:
            # ✅ Show Data Table
            st.dataframe(filtered_df)

            # ✅ Show Histogram
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.hist(filtered_df["actor_height"], bins=20, color="blue", alpha=0.7)
            ax.set_xlabel("Height (meters)")
            ax.set_ylabel("Frequency")
            ax.set_title(f"Actor Height Distribution ({selected_gender})")
            ax.grid(axis="y", linestyle="--", alpha=0.7)
            st.pyplot(fig)
        else:
            st.warning("⚠️ No data available for the selected criteria.")

# ==========================
# 📅 Chronological Info Page
# ==========================
elif page == "Chronological Info":
    st.title("📅 Movie Releases Over Time")

    # ✅ Get available genres dynamically
    available_genres = sorted(set(g for sublist in analyzer.movies_df["genres"] for g in sublist))
    selected_genre = st.selectbox("Select a genre", ["All"] + available_genres)

    data = analyzer.releases(selected_genre)

    if data.empty:
        st.warning("⚠️ No movies found for the selected genre.")
    else:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(data['release_date'], data['count'], color='skyblue')
        ax.set_xlabel("Year")
        ax.set_ylabel("Number of Movies")
        ax.set_title("Movies Released Per Year")
        st.pyplot(fig)

    # 🎂 Actor Age Distribution
    st.title("🎂 Actor Age Distribution")

    mode = st.selectbox("Select mode", ["Year (Y)", "Month (M)"])

    @st.cache_data
    def get_actor_age_data(mode):
        return analyzer.ages(mode='Y' if mode.startswith("Y") else 'M')

    data = get_actor_age_data(mode)

    if not data.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(data.iloc[:, 0], data['count'], color='green')
        ax.set_xlabel("Year" if mode.startswith("Y") else "Month")
        ax.set_ylabel("Number of Births")
        ax.set_title("Actor Birth Distribution")
        st.pyplot(fig)
    else:
        st.warning("⚠️ No actor age data available.")

# ==========================
# 🎭 Classification Page
# ==========================
elif page == "Classification":
    Page3.run_page()



