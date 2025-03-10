import os
import pandas as pd
import ast
import matplotlib.pyplot as plt
import tarfile
import urllib.request


class MovieAnalyzer:
    DATA_DIR = os.path.abspath("downloads")  # Ensure data is stored here
    MOVIE_FILE = "movie.metadata.tsv"
    CHARACTER_FILE = "character.metadata.tsv"
    DATA_URL = "http://www.cs.cmu.edu/~ark/personas/data/MovieSummaries.tar.gz"
    ARCHIVE_NAME = "MovieSummaries.tar.gz"

    # ✅ Correctly initializing GENRE_MAPPING inside the class
    GENRE_MAPPING = {
        "/m/07s9rl0": "Drama",
        "/m/01z4y": "Comedy",
        "/m/02l7c8": "Action",
        "/m/01g6gs": "Romance",
        "/m/02kdv5l": "Horror",
        "/m/01jfsb": "Thriller",
        "/m/02hmvc": "Science Fiction",
        "/m/03q4nz": "Adventure",
        "/m/0lsxr": "Mystery",
        "/m/0219x_": "Animation",
        "/m/02vxn": "Crime",
        "/m/09b5t": "Fantasy",
        "/m/06ntj": "Family",
        "/m/018jz": "Musical",
        "/m/07c6l": "Biography",
        "/m/01h6rj": "War",
        "/m/03tmr": "History",
        "/m/06bm2": "Western",
        "/m/07v9_z": "Sport",
        "/m/0f2f9": "Music",
        "/m/019_rr": "Documentary",
        "/m/0jtdp": "Political Cinema",
        "/m/03npn": "Rockumentary",
        "/m/06ppq": "Indie",
        "/m/03k9fj": "Romantic Comedy",
        "/m/0hqxf": "Romantic Drama",
        "/m/03btsm8": "World Cinema",
        "/m/05p553": "Psychological Thriller",
        "/m/04t36": "Musical",
        "/m/0hcr": "Gay Themed",
        "/m/068d7h": "Crime Thriller"
    }

    def __init__(self):
        os.makedirs(self.DATA_DIR, exist_ok=True)  # Ensure downloads directory exists

        if not self._check_data_files():
            self._download_and_extract_data()

        self._verify_extracted_files()  # ✅ Double-check the extracted files exist

        self.movies_df = self._load_movies()
        self.characters_df = self._load_characters()
        self.merged_df = self._merge_data()
        self._clean_data()

    def _check_data_files(self):
        """Check if the required data files exist in the downloads directory."""
        return (
            os.path.exists(os.path.join(self.DATA_DIR, self.MOVIE_FILE)) and
            os.path.exists(os.path.join(self.DATA_DIR, self.CHARACTER_FILE))
        )

    def _download_and_extract_data(self):
        """Download and extract the dataset if it is missing."""
        archive_path = os.path.join(self.DATA_DIR, self.ARCHIVE_NAME)

        # 🔹 Download only if it doesn't exist
        if not os.path.exists(archive_path):
            print("🔄 Downloading dataset...")
            urllib.request.urlretrieve(self.DATA_URL, archive_path)
            print("✅ Download complete.")

        print("📂 Extracting files...")
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=self.DATA_DIR)  # ✅ Extract inside 'downloads/'

        print("✅ Extraction complete.")

    def _verify_extracted_files(self):
        """Check if files exist after extraction and find correct paths if needed."""
        expected_files = {self.MOVIE_FILE, self.CHARACTER_FILE}
        extracted_files = set(os.listdir(self.DATA_DIR))

        if not expected_files.issubset(extracted_files):
            print("⚠️ Extracted files not found in expected location. Searching...")

            # Search inside extracted folders in 'downloads/'
            for root, _, files in os.walk(self.DATA_DIR):
                for file in files:
                    if file in expected_files:
                        src_path = os.path.join(root, file)
                        dest_path = os.path.join(self.DATA_DIR, file)

                        if src_path != dest_path:
                            os.rename(src_path, dest_path)  # Move file to correct location
                            print(f"✅ Moved {file} to {self.DATA_DIR}")

        # Final check to ensure files exist
        if not self._check_data_files():
            raise FileNotFoundError("❌ Extracted files are missing after extraction.")

    def _load_movies(self):
        """Load movies dataset and extract genre IDs."""
        file_path = os.path.join(self.DATA_DIR, self.MOVIE_FILE)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"❌ Movie file not found: {file_path}")

        columns = [
            "wikipedia_movie_id", "freebase_movie_id", "movie_name",
            "release_date", "box_office", "runtime", "languages",
            "countries", "genres"
        ]

        df = pd.read_csv(file_path, sep="\t", header=None, names=columns)

        def extract_genre_ids(genre_dict_str):
            try:
                genre_dict = ast.literal_eval(genre_dict_str)
                return list(genre_dict.keys())
            except (ValueError, SyntaxError):
                return []

        df["genres"] = df["genres"].apply(lambda x: extract_genre_ids(x) if isinstance(x, str) else [])
        return df

    def _load_characters(self):
        """Load characters dataset."""
        file_path = os.path.join(self.DATA_DIR, self.CHARACTER_FILE)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"❌ Character file not found: {file_path}")

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
        drop_columns = ["release_date_x", "freebase_movie_id_x", "freebase_movie_id_y"]
        self.merged_df.drop(columns=[col for col in drop_columns if col in self.merged_df.columns], inplace=True)

    def movie_type(self, n=10):
        """Return top N movie genres."""
        genre_counts = pd.Series(
            [self.GENRE_MAPPING.get(genre, f"Unknown ({genre})") for sublist in self.movies_df["genres"] for genre in sublist]
        ).value_counts()

        return genre_counts.head(n).reset_index().rename(columns={"index": "Movie_Type", 0: "Count"})

    def releases(self, genre=None):
        """Return movie releases per year, optionally filtered by genre."""
        self.movies_df["release_date"] = pd.to_numeric(self.movies_df["release_date"], errors="coerce")
        df = self.movies_df.dropna(subset=["release_date"])

        if genre:
            df = df[df["genres"].apply(lambda g: genre in g)]

        return df.groupby("release_date").size().reset_index(name="count")



