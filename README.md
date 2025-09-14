# UFC Style Metrics
This is a data-driven study of UFC fighting styles, win ratios, and champion conversion rates (Compared with ESPN champion data.)

This project is a data-driven analysis of UFC fighter styles and championship outcomes, built to showcase analytical, data visualization, and dashboarding skills. Using a custom dataset of UFC fighters alongside ESPN’s champion records, the study explores style representation, overall win ratios, and champion conversion rates. An interactive Streamlit dashboard provides side-by-side comparisons between the dataset and ESPN’s records, highlighting where narratives diverge and which fighting styles are most efficient at producing champions.
![UFC Dashboard](https://github.com/user-attachments/assets/4226246c-2583-4b64-a0ad-ccde60b3789a)

# UFC Styles Dashboard — Overview

This dashboard provides an interactive visualization of fighting styles in the UFC, focusing on their representation, win ratios, and conversion rates across different data sources. It highlights both the prevalence of each style in the roster and their competitive performance inside the octagon.

Dashboard Sections
1. Representation by Style

Bar Chart (Normalized %): Shows how frequently each style appears in the dataset, normalized to percentages for comparability.

Packed Bubble Chart (Area ∝ Representation %): Visualizes style prevalence proportionally by bubble area, with labels displaying the same values as in the bar chart.

Key Insights:

Freestyle (mixed martial arts with no real style specialty) and wrestling (Collegiate and Freestyle) dominate representation, together accounting for ~60%.

Styles like BJJ, Kickboxing, and Boxing form the next tier of representation.

Striking arts such as Kung Fu and TKD are minimally represented.

2. Win Ratio by Style

Bar Chart: Displays the win ratio (wins/losses) for each style. Includes an "Average (Raw)" benchmark for comparison.

Packed Bubble Chart (Area ∝ Win Value): Bubbles scaled by win ratios, directly reflecting bar chart values without renormalization.

Key Insights:

Boxing and Kickboxing show the highest raw win ratios, outperforming other styles.

Grappling-heavy backgrounds (e.g., Wrestling, BJJ) cluster near the average, highlighting the balance between striking and grappling.

Styles with lower representation also tend to have unstable win ratios due to smaller sample sizes.

3. Conversion by Style

Horizontal Bar Chart (Observed vs. ESPN): Compares style conversion rates (the rate at which a style produces a champion) using two sources: Observed dataset vs ESPN data.

Packed Bubble Charts (Observed and ESPN): Each chart shows bubble areas proportional to percentage conversion values, directly tied to the bar chart values.

Key Insights:

Boxing consistently shows strong conversion across both Observed and ESPN data (~23–25%).

Karate and BJJ conversions vary significantly between Observed and ESPN sources, suggesting data or definition differences.

Certain striking styles (TKD, Kung Fu) have minimal conversion presence.

What This Dashboard Provides

Clarity: Bar charts provide exact values, while bubbles highlight proportion and allow quick visual comparisons.

Consistency: Bubble labels now reflect the same numeric values as their corresponding bar charts, removing confusion from normalization.

Exploration: Users can dynamically filter, scale bubble sizes, and adjust parameters (e.g., Top-K labels) to focus on specific insights.

Example Use Cases

Fighter analysis: Compare how different styles stack up in terms of representation and win ratios.

Scouting/strategy: Identify overrepresented styles versus high-performing but underrepresented styles.

Data integrity checks: Spot discrepancies between observed fight outcomes and reported ESPN metrics.
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

Cross-source comparison: differences between observed dataset and ESPN’s champion data

An interactive Streamlit dashboard allows exploration of these metrics, with side-by-side comparisons and summary KPIs.

# Features

Style Representation: percentage of fighters by style

Champion Representation: champion counts & shares (my dataset vs ESPN)

Win Ratios: overall and by style (with weighted and simple averages)

Conversion Rates: how effectively each style produces champions

Cross-Source Analysis: champion counts and conversion rates compared across sources

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
