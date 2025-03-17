import pytest
import pandas as pd
from src.movie_analyzer import MovieAnalyzer

@pytest.fixture
def analyzer():
    """Fixture to initialize MovieAnalyzer before each test."""
    return MovieAnalyzer()

def test_movie_type(analyzer):
    """Test movie_type returns the correct number of top genres."""
    top_genres = analyzer.movie_type(5)
    assert isinstance(top_genres, pd.DataFrame)
    assert len(top_genres) == 5
    assert "Movie_Type" in top_genres.columns
    assert "Count" in top_genres.columns

def test_releases(analyzer):
    """Test releases function with and without genre filter."""
    all_releases = analyzer.releases()
    assert isinstance(all_releases, pd.DataFrame)
    assert "release_date" in all_releases.columns
    assert "count" in all_releases.columns

    genre_releases = analyzer.releases("Drama")
    assert isinstance(genre_releases, pd.DataFrame)
    assert "release_date" in genre_releases.columns
    assert "count" in genre_releases.columns

def test_ages(analyzer):
    """Test ages function with 'Y' (year) and 'M' (month) modes."""
    age_dist_year = analyzer.ages("Y")
    assert isinstance(age_dist_year, pd.DataFrame)
    assert "actor_dob" in age_dist_year.columns
    assert "count" in age_dist_year.columns

    age_dist_month = analyzer.ages("M")
    assert isinstance(age_dist_month, pd.DataFrame)
    assert "month" in age_dist_month.columns
    assert "count" in age_dist_month.columns

def test_actor_count(analyzer):
    """Test actor_count function returns valid data."""
    actor_counts = analyzer.actor_count(plot=False)
    assert isinstance(actor_counts, pd.DataFrame)
    assert "Number of Actors" in actor_counts.columns
    assert "Movie Count" in actor_counts.columns

def test_actor_distributions(analyzer):
    """Test actor_distributions function filters correctly."""
    filtered_df = analyzer.actor_distributions(gender="Male", min_height=1.5, max_height=2.0)
    assert isinstance(filtered_df, pd.DataFrame)
    assert "actor_name" in filtered_df.columns
    assert "actor_gender" in filtered_df.columns
    assert "actor_height" in filtered_df.columns
    assert (filtered_df["actor_height"] >= 1.5).all()
    assert (filtered_df["actor_height"] <= 2.0).all()

if __name__ == "__main__":
    pytest.main()
