# UFC Style Metrics
This is a data-driven study of UFC fighting styles, win ratios, and champion conversion rates (Compared with ESPN champion data.)

This project is a data-driven analysis of UFC fighter styles and championship outcomes, built to showcase analytical, data visualization, and dashboarding skills. Using a custom dataset of UFC fighters alongside ESPN’s champion records, the study explores style representation, overall win ratios, and champion conversion rates. An interactive Streamlit dashboard provides side-by-side comparisons between the dataset and ESPN’s records, highlighting where narratives diverge and which fighting styles are most efficient at producing champions.

The repository includes:

Raw data (UFC fighter dataset + ESPN champion data)

Python analysis & Streamlit app for interactive exploration

Charts and tables showing style representation, win ratios, conversion rates, and cross-source champion comparisons

This project demonstrates practical skills in data wrangling, statistical analysis, visualization, and deployment of interactive dashboards.

# Overview

This project analyzes UFC fighter styles and championship outcomes, using a custom dataset of UFC fighters and ESPN’s published champion records.

The analysis explores:

Style representation: how many fighters come from each martial arts background

Win ratios by style: performance of styles across fights

Champion conversion rates: how often fighters of a given style become champions

Cross-source comparison: differences between my dataset and ESPN’s champion data

An interactive Streamlit dashboard allows exploration of these metrics, with side-by-side comparisons and summary KPIs.

# Features

Style Representation: percentage of fighters by style

Champion Representation: champion counts & shares (my dataset vs ESPN)

Win Ratios: overall and by style (with weighted and simple averages)

Conversion Rates: how effectively each style produces champions

Cross-Source Analysis: champion counts and conversion rates compared across sources

# Repository Structure
ufc-style-analysis/

|
├── data/

|
│   ├── ufc_fighters.xlsx         # UFC dataset

│   └── ufc_fighters.csv          # Same data in CSV for easier loading

|
├── notebooks/

│   └── ufc_analysis.ipynb        # Step-by-step analysis in Jupyter

|
├── app/

|
│   └── ufc_dashboard.py          # Streamlit dashboard code

|
├── requirements.txt              # Python dependencies

|
├── README.md                     # Project documentation (this file)

|
└── LICENSE                       # Open-source license

# Installation

Clone the repo and install dependencies:

git clone https://github.com/dylanagyemang/ufc-style-metrics.git

cd ufc-style-metrics

pip install -r requirements.txt

# Usage
Run the dashboard
streamlit run app/streamlit_ufc_dashboard_ranges.py

Explore the notebook

Open notebooks/ufc_analysis.ipynb in Jupyter to see the calculations, visualizations, and methodology behind the dashboard.

# Example Insights

Wrestling may dominate fighter representation, but Boxing and Karate shows stronger conversion rates into champions.

Striking styles like Kickboxing and Muay Thai tend to have higher win ratios but lower conversion rates compared to Wrestling and Brazilian Jiu-Jitsu styles.

ESPN’s champion distribution sometimes overstates certain styles compared to the raw fighter dataset.
