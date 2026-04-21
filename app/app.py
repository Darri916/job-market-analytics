import ast
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = Path(__file__).parent.parent / "data" / "processed" / "jobs_processed.csv"

st.set_page_config(page_title="Data Science Job Market Analytics", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["created"])
    df["skills_found"] = df["skills_found"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else []
    )
    return df


COUNTRY_NAMES = {
    "AU": "Australia",
    "AT": "Austria",
    "CA": "Canada",
    "FR": "France",
    "DE": "Germany",
    "IN": "India",
    "NL": "Netherlands",
    "NZ": "New Zealand",
    "SG": "Singapore",
    "GB": "United Kingdom",
    "US": "United States",
}


def display_name(code: str) -> str:
    return COUNTRY_NAMES.get(code, code)


df = load_data()
all_countries = sorted(df["country"].dropna().unique())
country_options = ["All"] + all_countries
country_labels = ["All"] + [display_name(c) for c in all_countries]

all_roles_raw = sorted(df["search_term"].dropna().unique())
role_options = ["All Roles"] + all_roles_raw
role_labels = ["All Roles"] + [r.title() for r in all_roles_raw]

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Job Market Analytics")
    st.markdown("---")
    st.metric("Total Jobs Analysed", f"{len(df):,}")

    if df["created"].notna().any():
        latest = df["created"].max()
        st.metric("Data Collection Date", latest.strftime("%d %b %Y"))

    st.markdown("**Countries Covered**")
    st.write(", ".join(display_name(c) for c in all_countries))

    st.markdown("---")
    jobs_per_country = (
        df["country"]
        .value_counts()
        .reset_index()
        .rename(columns={"country": "Code", "count": "Jobs"})
    )
    jobs_per_country["Country"] = jobs_per_country["Code"].apply(display_name)
    jobs_per_country = jobs_per_country.sort_values("Jobs")

    fig_sidebar = px.bar(
        jobs_per_country,
        x="Jobs",
        y="Country",
        orientation="h",
        title="Jobs per Country",
    )
    fig_sidebar.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=320,
        xaxis_title=None,
        yaxis_title=None,
        title_font_size=13,
    )
    st.plotly_chart(fig_sidebar, use_container_width=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Skills Demand", "Salary Insights", "Work Type Trends", "Skills by Role"])


# ── Tab 1: Skills Demand ───────────────────────────────────────────────────────
with tab1:
    st.header("Top 20 In-Demand Skills")

    col_a, col_b = st.columns(2)
    with col_a:
        skills_label = st.selectbox(
            "Filter by country", country_labels, key="skills_country"
        )
    with col_b:
        skills_role_label = st.selectbox(
            "Filter by role", role_labels, key="skills_role"
        )
    skills_code = country_options[country_labels.index(skills_label)]
    skills_role = role_options[role_labels.index(skills_role_label)]

    skills_df = df.copy()
    if skills_code != "All":
        skills_df = skills_df[skills_df["country"] == skills_code]
    if skills_role != "All Roles":
        skills_df = skills_df[skills_df["search_term"] == skills_role]

    skills_exploded = (
        skills_df.explode("skills_found")
        .dropna(subset=["skills_found"])
        .query("skills_found != ''")
    )

    job_count = len(skills_df)
    if job_count == 0:
        st.warning("⚠️ No jobs match this filter — try adjusting your selection.")
    elif job_count < 50:
        noun = "job matches" if job_count == 1 else "jobs match"
        st.warning(f"⚠️ Only {job_count} {noun} this filter — results may not be representative.")

    if skills_exploded.empty:
        st.info("No skill data available for the selected filter.")
    else:
        skill_counts = (
            skills_exploded["skills_found"]
            .value_counts()
            .head(20)
            .reset_index()
        )
        skill_counts.columns = ["Skill", "Count"]

        fig = px.bar(
            skill_counts.sort_values("Count"),
            x="Count",
            y="Skill",
            orientation="h",
            title=f"Top 20 Skills — {skills_label} · {skills_role_label}",
            color="Count",
            color_continuous_scale="Blues",
        )
        fig.update_layout(coloraxis_showscale=False, yaxis_title=None, xaxis_title="Job Postings")
        st.plotly_chart(fig, use_container_width=True)


# ── Tab 2: Salary Insights ─────────────────────────────────────────────────────
with tab2:
    st.header("Average Salary Range by Country")
    st.caption("⚠️ Salaries are shown as advertised in local currency. Some employers post annual salaries, others post monthly — direct comparisons within or across countries may not be meaningful. Use as a directional reference only.")

    salary_df = df.dropna(subset=["salary_min", "salary_max"]).copy()
    salary_df = salary_df[
        pd.to_numeric(salary_df["salary_min"], errors="coerce").notna()
        & pd.to_numeric(salary_df["salary_max"], errors="coerce").notna()
    ]
    salary_df["salary_min"] = salary_df["salary_min"].astype(float)
    salary_df["salary_max"] = salary_df["salary_max"].astype(float)

    if salary_df.empty:
        st.info("No salary data available.")
    else:
        salary_grouped = (
            salary_df.groupby("country")[["salary_min", "salary_max"]]
            .mean()
            .round(0)
            .reset_index()
        )
        salary_grouped["country_name"] = salary_grouped["country"].apply(display_name)
        salary_melted = salary_grouped.melt(
            id_vars=["country", "country_name"],
            value_vars=["salary_min", "salary_max"],
            var_name="Salary Type",
            value_name="Average Salary",
        )
        salary_melted["Salary Type"] = salary_melted["Salary Type"].map(
            {"salary_min": "Avg Min Salary", "salary_max": "Avg Max Salary"}
        )

        fig2 = px.bar(
            salary_melted,
            x="country_name",
            y="Average Salary",
            color="Salary Type",
            barmode="group",
            title="Average Advertised Salary Range by Country (local currency)",
            color_discrete_map={
                "Avg Min Salary": "#636EFA",
                "Avg Max Salary": "#EF553B",
            },
        )
        fig2.update_layout(xaxis_title="Country", yaxis_title="Average Salary")
        st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(
            salary_grouped.rename(columns={
                "country_name": "Country",
                "salary_min": "Avg Min",
                "salary_max": "Avg Max",
            })[["Country", "Avg Min", "Avg Max"]],
            use_container_width=True,
            hide_index=True,
        )


# ── Tab 3: Work Type Trends ────────────────────────────────────────────────────
with tab3:
    st.header("Work Type Distribution")

    wt_label = st.selectbox(
        "Filter by country", country_labels, key="worktype_country"
    )
    wt_code = country_options[country_labels.index(wt_label)]

    wt_df = df.copy()
    if wt_code != "All":
        wt_df = wt_df[wt_df["country"] == wt_code]

    wt_counts = (
        wt_df["work_type"]
        .fillna("not specified")
        .value_counts()
        .reset_index()
    )
    wt_counts.columns = ["Work Type", "Count"]

    color_map = {
        "remote": "#00CC96",
        "hybrid": "#636EFA",
        "on-site": "#EF553B",
        "not specified": "#BBBBBB",
    }

    fig3 = px.bar(
        wt_counts,
        x="Work Type",
        y="Count",
        title=f"Work Type Distribution — {wt_label}",
        color="Work Type",
        color_discrete_map=color_map,
    )
    fig3.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Job Postings")
    st.plotly_chart(fig3, use_container_width=True)

    total = wt_counts["Count"].sum()
    wt_counts["Share (%)"] = (wt_counts["Count"] / total * 100).round(1)
    st.dataframe(wt_counts, use_container_width=True, hide_index=True)


# ── Tab 4: Skills by Role ──────────────────────────────────────────────────────
with tab4:
    st.header("Top 15 Skills by Role")

    role4_label = st.selectbox(
        "Select role", role_labels[1:], key="role4"  # exclude "All Roles"
    )
    role4_code = role_options[role_labels.index(role4_label)]

    role4_df = (
        df[df["search_term"] == role4_code]
        .explode("skills_found")
        .dropna(subset=["skills_found"])
        .query("skills_found != ''")
    )

    if role4_df.empty:
        st.info("No skill data available for this role.")
    else:
        role4_counts = (
            role4_df["skills_found"]
            .value_counts()
            .head(15)
            .reset_index()
        )
        role4_counts.columns = ["Skill", "Count"]

        fig4 = px.bar(
            role4_counts.sort_values("Count"),
            x="Count",
            y="Skill",
            orientation="h",
            title=f"Top 15 Skills — {role4_label}",
            color="Count",
            color_continuous_scale="Teal",
        )
        fig4.update_layout(coloraxis_showscale=False, yaxis_title=None, xaxis_title="Job Postings")
        st.plotly_chart(fig4, use_container_width=True)
