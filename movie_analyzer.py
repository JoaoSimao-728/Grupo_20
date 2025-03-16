import os
import pandas as pd
import ast
import tarfile
import urllib.request
import matplotlib.pyplot as plt

class MovieAnalyzer:
    DATA_DIR = os.path.abspath("downloads")
    MOVIE_FILE = "movie.metadata.tsv"
    CHARACTER_FILE = "character.metadata.tsv"
    SUMMARY_FILE = "plot_summaries.txt"
    DATA_URL = "http://www.cs.cmu.edu/~ark/personas/data/MovieSummaries.tar.gz"
    ARCHIVE_NAME = "MovieSummaries.tar.gz"

    def __init__(self):
        os.makedirs(self.DATA_DIR, exist_ok=True)

        if not self._check_data_files():
            self._download_and_extract_data()

        self.movies_df = self._load_movies()
        self.characters_df = self._load_characters()
        self.merged_df = self._merge_data()
        self._clean_data()

    def _check_data_files(self):
        """Check if required data files exist."""
        return (
            os.path.exists(os.path.join(self.DATA_DIR, self.MOVIE_FILE)) and
            os.path.exists(os.path.join(self.DATA_DIR, self.CHARACTER_FILE)) and
            os.path.exists(os.path.join(self.DATA_DIR, self.SUMMARY_FILE))
        )

    def _download_and_extract_data(self):
        """Download and extract dataset if missing."""
        archive_path = os.path.join(self.DATA_DIR, self.ARCHIVE_NAME)
        if not os.path.exists(archive_path):
            print("Downloading dataset...")
            urllib.request.urlretrieve(self.DATA_URL, archive_path)
            print("Download complete.")

        print("Extracting files...")
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=self.DATA_DIR)
        print("Extraction complete.")

    def _load_movies(self):
        """Load movies dataset and extract genres and summaries."""
        file_path = os.path.join(self.DATA_DIR, self.MOVIE_FILE)
        summary_path = os.path.join(self.DATA_DIR, self.SUMMARY_FILE)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"❌ Movie file not found: {file_path}")

        columns = [
            "wikipedia_movie_id", "freebase_movie_id", "movie_name",
            "release_date", "box_office", "runtime", "languages",
            "countries", "genres"
        ]
        df = pd.read_csv(file_path, sep="\t", header=None, names=columns)

        def extract_genres(genre_dict_str):
            try:
                genre_dict = ast.literal_eval(genre_dict_str)
                return [genre_name.strip() for genre_name in genre_dict.values() if genre_name]
            except (ValueError, SyntaxError):
                return []

        df["genres"] = df["genres"].apply(lambda x: extract_genres(x) if isinstance(x, str) else [])

        df["summary"] = "No summary available."

        if os.path.exists(summary_path):
            print("plot_summaries.txt found! Loading summaries...")
            summaries_df = pd.read_csv(summary_path, sep="\t", header=None, names=["wikipedia_movie_id", "summary"])
            df = df.merge(summaries_df, on="wikipedia_movie_id", how="left")

        df["summary"] = df["summary"].fillna("No summary available.")
        
        return df

    def _load_characters(self):
        """Load characters dataset."""
        file_path = os.path.join(self.DATA_DIR, self.CHARACTER_FILE)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Character file not found: {file_path}")

        columns = [
            "wikipedia_movie_id", "freebase_movie_id", "release_date",
            "character_name", "actor_dob", "actor_gender", "actor_height",
            "actor_ethnicity", "actor_name", "actor_age_at_release",
            "character_actor_map_id", "character_id", "actor_id"
        ]

        return pd.read_csv(file_path, sep="\t", header=None, names=columns)

    def _merge_data(self):
        """Merge movie and character datasets."""
        return pd.merge(self.characters_df, self.movies_df, on="wikipedia_movie_id", how="inner")

    def _clean_data(self):
        """Clean and process merged data."""
        self.merged_df["actor_gender"] = self.merged_df["actor_gender"].replace({"M": "Male", "F": "Female"})
        self.merged_df["actor_height"] = pd.to_numeric(self.merged_df["actor_height"], errors="coerce")

    def movie_type(self, n=10):
        """Return top N movie genres."""
        genre_counts = pd.Series(
            [genre for sublist in self.movies_df["genres"] for genre in sublist]
        ).value_counts()

        return genre_counts.head(n).reset_index().rename(columns={"index": "Movie_Type", 0: "Count"})

    def releases(self, genre=None):
        """Return movie releases per year, optionally filtered by genre."""
        df = self.movies_df.copy()
        df["release_date"] = pd.to_numeric(df["release_date"], errors="coerce")

        if genre and genre != "All":
            df = df[df["genres"].apply(lambda genres: isinstance(genres, list) and genre in genres)]

        return df.dropna(subset=["release_date"]).groupby("release_date").size().reset_index(name="count")

    def actor_count(self, plot=False):
        """Return the distribution of the number of actors per movie."""
        actor_counts = self.merged_df.groupby("wikipedia_movie_id").size().value_counts().reset_index()
        actor_counts.columns = ["Number of Actors", "Movie Count"]

        if plot:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(actor_counts["Number of Actors"], actor_counts["Movie Count"], color="blue", alpha=0.7)
            ax.set_xlabel("Number of Actors in a Movie")
            ax.set_ylabel("Number of Movies")
            ax.set_title("Distribution of Number of Actors per Movie")
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            return fig

        return actor_counts

    def ages(self, mode="Y"):
        """Return actor age distribution based on Year or Month."""
        df = self.merged_df[["actor_dob"]].dropna().copy()
        df["actor_dob"] = pd.to_numeric(df["actor_dob"], errors="coerce").dropna()

        df = df[df["actor_dob"] > 1800]  

        if mode == "Y":
            return df.groupby("actor_dob").size().reset_index(name="count")
        elif mode == "M":
            df["month"] = df["actor_dob"].astype(str).str[-2:]
            return df.groupby("month").size().reset_index(name="count")
        return pd.DataFrame()

    def actor_distributions(self, gender="All", min_height=1.5, max_height=2.0):
        """Returns actor height distribution filtered by gender and height."""
        df = self.merged_df[["actor_name", "actor_gender", "actor_height"]].dropna()
        df["actor_height"] = pd.to_numeric(df["actor_height"], errors="coerce")

        if gender in ["Male", "Female"]:
            df = df[df["actor_gender"] == gender]

        df = df[(df["actor_height"] >= min_height) & (df["actor_height"] <= max_height)]

        return df

    def actor_table(self, gender="All", min_height=1.5, max_height=2.0):
        """Returns actor table filtered by gender and height."""
        df = self.merged_df[["actor_name", "actor_gender", "actor_height"]].dropna()

        if gender in ["Male", "Female"]:
            df = df[df["actor_gender"] == gender]

        df = df[(df["actor_height"] >= min_height) & (df["actor_height"] <= max_height)]

        return df[["actor_name", "actor_gender", "actor_height"]].head(10)  














