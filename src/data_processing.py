import re
from pathlib import Path

import pandas as pd

INPUT_PATH = Path(__file__).parent.parent / "data" / "raw" / "jobs_raw.csv"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "processed" / "jobs_processed.csv"

SKILLS = [
    "Python", "SQL", "R", "TensorFlow", "PyTorch", "AWS", "Azure", "GCP",
    "Spark", "Kafka", "Airflow", "dbt", "Tableau", "Power BI", "Excel",
    "scikit-learn", "Keras", "Docker", "Kubernetes", "Git", "Linux", "Scala",
    "Java", "C++", "MATLAB", "SAS", "Hadoop", "Snowflake", "Databricks",
    "BigQuery", "Looker", "FastAPI", "Flask", "MLflow", "Hugging Face",
    "LangChain", "OpenCV", "NumPy", "pandas", "PySpark", "Redshift",
    "dask", "XGBoost", "LightGBM", "CatBoost", "Plotly", "Seaborn",
    "Matplotlib", "Streamlit", "Grafana",
]

# Pre-compile patterns once; escape skills with special regex chars (e.g. C++)
_SKILL_PATTERNS = {
    skill: re.compile(rf"\b{re.escape(skill)}\b", re.IGNORECASE)
    for skill in SKILLS
}

WORK_TYPE_PATTERNS = {
    "remote":  re.compile(r"\bremote\b", re.IGNORECASE),
    "hybrid":  re.compile(r"\bhybrid\b", re.IGNORECASE),
    "on-site": re.compile(r"\bon[- ]?site\b|\bin[- ]?office\b", re.IGNORECASE),
}


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["title", "company", "location", "country"])
    df = df[df["description"].notna() & (df["description"].str.strip() != "")]
    df["created"] = pd.to_datetime(df["created"], utc=True, errors="coerce")
    return df.reset_index(drop=True)


def extract_skills(description: str) -> str:
    if not isinstance(description, str):
        return "[]"
    matched = [skill for skill, pat in _SKILL_PATTERNS.items() if pat.search(description)]
    return str(matched)


def extract_work_type(description: str) -> str:
    if not isinstance(description, str):
        return "not specified"
    found = [label for label, pat in WORK_TYPE_PATTERNS.items() if pat.search(description)]
    if "hybrid" in found:
        return "hybrid"
    if "remote" in found:
        return "remote"
    if "on-site" in found:
        return "on-site"
    return "not specified"


def main():
    print(f"Reading {INPUT_PATH}")
    df = pd.read_csv(INPUT_PATH)
    print(f"  Loaded {len(df):,} rows")

    df = clean(df)
    print(f"  After cleaning: {len(df):,} rows")

    df["skills_found"] = df["description"].apply(extract_skills)
    df["work_type"] = df["description"].apply(extract_work_type)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df):,} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
