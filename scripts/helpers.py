import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import hashlib
import re
from pathlib import Path

# Set style for better visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
WAREHOUSE_DIR = DATA_DIR / "warehouse"
STATE_DIR = DATA_DIR / "state"
PUBLIC_ANALYSIS_COLUMNS = (
    "age",
    "grade_class",
    "gender",
    "average_hours_spent_studying_per_day",
    "preferred_study_method",
    "subjects_you_find_most_challenging",
    "extra_curricular_activities_you_participate_in",
    "do_you_feel_marginalized_or_discriminated_against_at_school_college_university",
    "have_you_ever_used_tobacco_alcohol_or_other_substances",
)
SENSITIVE_COLUMN_HINTS = (
    "name",
    "email",
    "phone",
    "address",
    "id",
    "timestamp",
    "student_number",
    "roll_number",
    "location",
    "gps",
    "latitude",
    "longitude",
)


def _find_column(df, *candidate_names):
    """Return the first matching column name from a list of candidates."""
    normalized_lookup = {str(column).strip().lower(): column for column in df.columns}
    for name in candidate_names:
        key = str(name).strip().lower()
        if key in normalized_lookup:
            return normalized_lookup[key]
    return None


def _normalize_column_name(column_name):
    return (
        str(column_name)
        .strip()
        .lower()
        .replace("&", " and ")
        .replace("/", " ")
    )


def _canonicalize_column_name(column_name):
    return re.sub(r"[^a-z0-9]+", "_", _normalize_column_name(column_name)).strip("_")


def get_file_fingerprint(file_path):
    """Return a deterministic fingerprint for a local file."""
    digest = hashlib.sha256()
    with Path(file_path).open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get_sensitive_columns(df):
    """Return columns that look privacy-sensitive or personally identifying."""
    sensitive_columns = []
    for column in df.columns:
        normalized = _canonicalize_column_name(column)
        if any(hint in normalized for hint in SENSITIVE_COLUMN_HINTS):
            sensitive_columns.append(column)
    return sensitive_columns


def get_public_analysis_columns(df):
    """Return the safe analysis columns that should remain in a public export."""
    normalized_lookup = {_canonicalize_column_name(column): column for column in df.columns}
    public_columns = [normalized_lookup[column] for column in PUBLIC_ANALYSIS_COLUMNS if column in normalized_lookup]
    return public_columns


def prepare_public_survey_data(df, drop_sensitive=True):
    """Create a privacy-safe survey frame with only the analysis columns retained."""
    cleaned = clean_survey_data(df)
    public_columns = get_public_analysis_columns(cleaned)

    if not public_columns:
        raise ValueError("No public analysis columns were found in the survey data.")

    public_df = cleaned.loc[:, public_columns].copy()

    if drop_sensitive:
        sensitive_columns = get_sensitive_columns(cleaned)
        columns_to_drop = [column for column in sensitive_columns if column in public_df.columns]
        if columns_to_drop:
            public_df = public_df.drop(columns=columns_to_drop)

    if "timestamp" in public_df.columns:
        public_df = public_df.drop(columns=["timestamp"])

    return public_df


def validate_public_survey_data(df):
    """Raise if a public export still contains direct identifiers."""
    sensitive_columns = get_sensitive_columns(df)
    if sensitive_columns:
        raise ValueError(
            "Public survey data still contains sensitive columns: "
            + ", ".join(map(str, sensitive_columns))
        )


def get_privacy_report(df):
    """Print a compact privacy review for the loaded survey data."""
    sensitive_columns = get_sensitive_columns(df)
    public_columns = get_public_analysis_columns(df)

    print("=" * 50)
    print("PRIVACY REVIEW")
    print("=" * 50)
    print(f"Total Columns: {len(df.columns)}")
    print(f"Analysis-Safe Columns: {len(public_columns)}")
    if sensitive_columns:
        print("Sensitive-looking Columns:")
        for column in sensitive_columns:
            print(f"- {column}")
    else:
        print("Sensitive-looking Columns: none detected")
    print("=" * 50)

def load_survey_data(filename="Karachi Edu Analytics Survey .csv", data_dir=DATA_DIR, **read_csv_kwargs):
    """Load survey data from the data folder."""
    data_dir = Path(data_dir)
    filepath = data_dir / filename
    if not filepath.exists():
        csv_files = sorted(data_dir.glob("*.csv"))
        if len(csv_files) == 1:
            filepath = csv_files[0]
        else:
            raise FileNotFoundError(f"Could not find survey CSV at {filepath}")

    df = pd.read_csv(filepath, **read_csv_kwargs)
    # Clean column names
    df.columns = df.columns.str.strip()
    return df


def get_survey_file_path(filename="Karachi Edu Analytics Survey .csv", data_dir=DATA_DIR):
    """Resolve the most likely survey CSV path from the configured data folder."""
    data_dir = Path(data_dir)
    filepath = data_dir / filename
    if filepath.exists():
        return filepath

    csv_files = sorted(data_dir.glob("*.csv"))
    if len(csv_files) == 1:
        return csv_files[0]

    raise FileNotFoundError(f"Could not find survey CSV at {filepath}")


def build_clean_survey_frame(filename="Karachi Edu Analytics Survey .csv", data_dir=DATA_DIR, **read_csv_kwargs):
    """Load and normalize the raw survey data for downstream ETL steps."""
    raw_df = load_survey_data(filename=filename, data_dir=data_dir, **read_csv_kwargs)
    return clean_survey_data(raw_df)


def build_public_survey_frame(filename="Karachi Edu Analytics Survey .csv", data_dir=DATA_DIR, **read_csv_kwargs):
    """Load, clean, and reduce the survey to the privacy-safe public export."""
    return prepare_public_survey_data(load_survey_data(filename=filename, data_dir=data_dir, **read_csv_kwargs))

def clean_survey_data(df):
    """Clean and standardize survey data."""
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', format='mixed')
    if 'age' in df.columns:
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
    return df


def load_public_survey_data(filename="Karachi Edu Analytics Survey .csv", data_dir=DATA_DIR, **read_csv_kwargs):
    """Load and immediately reduce the survey to privacy-safe analysis columns."""
    return prepare_public_survey_data(load_survey_data(filename=filename, data_dir=data_dir, **read_csv_kwargs))

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
    age_column = _find_column(df, 'age')
    gender_column = _find_column(df, 'gender')
    grade_column = _find_column(df, 'grade_class', 'grade/class', 'gradeclass')

    print("=" * 50)
    print("SURVEY DEMOGRAPHICS SUMMARY")
    print("=" * 50)
    print(f"Total Responses: {len(df)}")
    if age_column is not None:
        print(f"\nAge Range: {df[age_column].min():.0f} - {df[age_column].max():.0f}")
        print(f"Average Age: {df[age_column].mean():.1f}")
    else:
        print("\nAge Range: unavailable")
        print("Average Age: unavailable")
    print(f"\nGender Distribution:")
    if gender_column is not None:
        print(df[gender_column].value_counts())
    else:
        print("Gender column not found")
    print(f"\nGrade/Class Distribution:")
    if grade_column is not None:
        print(df[grade_column].value_counts())
    else:
        print("Grade/Class column not found")
    print("=" * 50)

def get_study_habits_summary(df):
    """Analyze study patterns."""
    study_hours_column = _find_column(df, 'average_hours_spent_studying_per_day')
    study_method_column = _find_column(df, 'preferred_study_method')

    print("=" * 50)
    print("STUDY HABITS SUMMARY")
    print("=" * 50)
    print(f"Study Hours Distribution:")
    if study_hours_column is not None:
        print(df[study_hours_column].value_counts())
    else:
        print("Study hours column not found")
    print(f"\nPreferred Study Methods:")
    if study_method_column is not None:
        print(df[study_method_column].value_counts().head(10))
    else:
        print("Preferred study method column not found")
    print("=" * 50)

def get_data_summary(df):
    """Print complete data summary."""
    print(f"\nDataset Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Missing Values:\n{df.isnull().sum()}")
