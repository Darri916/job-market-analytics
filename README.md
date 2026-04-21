# 📊 Job Market Analytics Dashboard

A Streamlit dashboard that analyzes 34,000+ real Data Science job postings across 11 countries, built with live data from the Adzuna API.

🚀 **Live Demo:** [*link coming soon*]

---

## 🔍 Overview

This project collects, processes, and visualizes Data Science job market data using the Adzuna Jobs API. Rather than relying on a static Kaggle dataset, it pulls live job postings directly from Adzuna across 11 countries and 8 role types, giving a more current and representative picture of the global DS job market.

The goal was to answer practical questions: which technical skills appear most frequently in job descriptions, how salary ranges vary by country, and how common remote or hybrid roles actually are — based on real postings, not survey data.

---

## ✨ Dashboard Features

The app is organized into four tabs.

**🛠️ Skills Demand** shows the top 20 technical skills found in job descriptions, with filters for both country and role type. Apply both filters together to see, for example, the skills most commonly required for Machine Learning Engineers in the United Kingdom.

**💰 Salary Insights** displays average advertised salary ranges (min and max) grouped by country, shown in each country's local currency. A grouped bar chart makes it easy to compare the spread between floor and ceiling salaries across markets.

**🏠 Work Type Trends** breaks down job postings by work arrangement — remote, hybrid, on-site, or not specified — with a country filter. A percentage table sits below the chart for quick reference.

**🎯 Skills by Role** lets you pick a specific role type and see the top 15 skills associated with it across all countries. Useful for comparing, for example, the skill profile of a Data Engineer versus a Business Intelligence Analyst.

The sidebar shows total jobs analysed, the data collection date, a list of countries covered, and a compact horizontal bar chart of job counts per country.

---

## 🌍 Data Collection

Data was collected via the [Adzuna Jobs API](https://developer.adzuna.com/) across 11 countries:

United Kingdom, United States, Australia, Canada, Germany, France, Netherlands, Singapore, New Zealand, Austria, India

Eight role types were searched:

Data Scientist, Data Analyst, Machine Learning Engineer, Data Engineer, Business Intelligence Analyst, AI Engineer, MLOps Engineer, Analytics Engineer

Raw results were deduplicated on title + company + location + country, reducing the dataset from 43,152 to 34,078 rows. Rows with empty descriptions were also removed before processing.

---

## ⚠️ Known Limitations

Some job postings appear under slightly different titles from the same company across multiple search terms and may not be fully deduplicated. A posting for "Senior Data Scientist" collected under both the "Data Scientist" and "AI Engineer" searches, for instance, would survive deduplication if its title differs slightly between listings.

Salary data is shown as advertised in local currency. Some employers post annual figures, others post monthly or daily rates — so comparisons are directional only and should not be treated as precise benchmarks, even within the same country.

88% of job postings do not explicitly mention work type keywords (remote, hybrid, on-site) in the description and are therefore labelled *not specified*. This reflects how job descriptions are written, not that those roles have no defined work arrangement.

---

## 📌 Key Insights

- Python and SQL dominate across all roles globally.
- Cloud platforms (AWS, Azure, GCP) appear consistently across job postings.
- Data Analyst roles emphasize SQL and BI tools, while ML Engineer roles emphasize Python and deep learning frameworks.
- Salary ranges vary significantly across countries, with wide spreads between advertised minimum and maximum.
- A large portion of job postings omit explicit work type information, suggesting that remote/hybrid/on-site arrangements are often communicated outside the job description itself.

These insights are derived from 34,000+ real job postings collected in April 2026.

---

## 🔧 Feature Engineering

- Extracted technical skills from job descriptions using regex pattern matching against a predefined taxonomy of 50+ DS tools and frameworks.
- Standardized skill detection across varied text formats using case-insensitive matching.
- Classified work arrangement from unstructured description text by detecting keywords (remote, hybrid, on-site) and applied priority logic to handle overlapping labels.
- Parsed and cleaned ISO timestamp data from API responses for temporal analysis.

---

## 🧠 Final Insight

This project demonstrates how raw, unstructured job posting data can be transformed into meaningful market intelligence. The focus was on handling real-world data collection, extracting structure from free text, and presenting findings that reflect actual hiring demand rather than survey responses or assumptions.

---

## 📁 Project Structure

```
job-market-analytics/
├── app/
│   └── app.py                  # Streamlit dashboard
├── data/
│   ├── raw/
│   │   └── jobs_raw.csv        # Output from data_collection.py
│   └── processed/
│       └── jobs_processed.csv  # Output from data_processing.py
├── src/
│   ├── data_collection.py      # Adzuna API scraper with pagination
│   └── data_processing.py      # Cleaning, skill extraction, work type tagging
├── .env.example                # Template for API credentials
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup and Run

**1. Clone the repository**

```bash
git clone https://github.com/your-username/job-market-analytics.git
cd job-market-analytics
```

**2. Add API credentials**

Copy `.env.example` to `.env` and fill in your Adzuna credentials:

```
ADZUNA_APP_ID=your_app_id_here
ADZUNA_APP_KEY=your_app_key_here
```

Register for a free API key at [developer.adzuna.com](https://developer.adzuna.com/).

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Collect job data**

```bash
python src/data_collection.py
```

This will paginate through Adzuna results for all countries and role types and save the raw output to `data/raw/jobs_raw.csv`.

**5. Process the data**

```bash
python src/data_processing.py
```

This cleans the raw data, extracts skills and work type labels, and saves the result to `data/processed/jobs_processed.csv`.

**6. Launch the dashboard**

```bash
streamlit run app/app.py
```

---

## 🧰 Tech Stack

- **Python** — data collection, processing, and app logic
- **Streamlit** — dashboard framework
- **Pandas** — data cleaning and transformation
- **Plotly Express** — interactive charts
- **Requests** — HTTP client for the Adzuna API
- **Adzuna Jobs API** — source of live job posting data
