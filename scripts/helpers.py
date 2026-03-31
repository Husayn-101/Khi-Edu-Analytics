import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style for better visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

def load_survey_data(filename="Karachi Edu Analytics Survey .csv"):
    """Load survey data from the data folder."""
    filepath = DATA_DIR / filename
    df = pd.read_csv(filepath)
    # Clean column names
    df.columns = df.columns.str.strip()
    return df

def clean_survey_data(df):
    """Clean and standardize survey data."""
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(' +', '_', regex=True)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y/%m/%d %I:%M:%S %p %Z', errors='coerce')
    if 'age' in df.columns:
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
    return df

def get_study_hours_category(hours_str):
    """Convert study hours string to numeric."""
    mapping = {
        'less than 1 hour': 0.5,
        '1–2 hours': 1.5,
        '2–4 hours': 3,
        'more than 4 hours': 5
    }
    return mapping.get(str(hours_str).lower().strip(), np.nan)

def get_marginalization_level(response):
    """Convert marginalization response to numeric."""
    mapping = {'never': 0, 'rarely': 1, 'sometimes': 2, 'often': 3}
    return mapping.get(str(response).lower().strip(), np.nan)

def get_demographics_summary(df):
    """Get demographic breakdown."""
    print("=" * 50)
    print("SURVEY DEMOGRAPHICS SUMMARY")
    print("=" * 50)
    print(f"Total Responses: {len(df)}")
    print(f"\nAge Range: {df['age'].min():.0f} - {df['age'].max():.0f}")
    print(f"Average Age: {df['age'].mean():.1f}")
    print(f"\nGender Distribution:")
    print(df['gender'].value_counts())
    print(f"\nGrade/Class Distribution:")
    print(df['grade/class'].value_counts())
    print("=" * 50)

def get_study_habits_summary(df):
    """Analyze study patterns."""
    print("=" * 50)
    print("STUDY HABITS SUMMARY")
    print("=" * 50)
    print(f"Study Hours Distribution:")
    print(df['average_hours_spent_studying_per_day'].value_counts())
    print(f"\nPreferred Study Methods:")
    print(df['preferred_study_method'].value_counts().head(10))
    print("=" * 50)

def get_data_summary(df):
    """Print complete data summary."""
    print(f"\nDataset Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Missing Values:\n{df.isnull().sum()}")
