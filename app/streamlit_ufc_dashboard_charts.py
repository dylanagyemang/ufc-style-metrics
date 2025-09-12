
import re
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="UFC Styles Dashboard – Streamlined", layout="wide")
st.title("🥊 UFC Styles Dashboard — Streamlined")

uploaded = st.file_uploader("Upload Excel", type=["xlsx","xls"])

def a1_to_ix(a1: str):
    m = re.match(r"^\s*([A-Za-z]+)(\d+)\s*$", a1)
    if not m: raise ValueError(f"Bad A1 address: {a1}")
    col_s, row_s = m.groups()
    col = 0
    for ch in col_s.upper():
        col = col*26 + (ord(ch)-64)
    return int(row_s)-1, col-1

def parse_range(df: pd.DataFrame, rng: str):
    a, b = [x.strip() for x in rng.split(":")]
    r1,c1 = a1_to_ix(a)
    r2,c2 = a1_to_ix(b)
    return df.iloc[min(r1,r2):max(r1,r2)+1, min(c1,c2):max(c1,c2)+1]

def to_numeric_series(s):
    return pd.to_numeric(pd.Series(s).astype(str).str.replace("%","", regex=False), errors='coerce')

if uploaded:
    base = pd.read_excel(uploaded, sheet_name=0, header=None)
    sheet_names = pd.ExcelFile(uploaded).sheet_names

    # Representation
    names_rep = parse_range(base, "C1:L1").values.flatten().tolist()
    vals_rep = parse_range(base, "C2:L2").values.flatten().tolist()
    rep_df = pd.DataFrame({"Style": names_rep, "Representation": to_numeric_series(vals_rep)}).dropna()
    if rep_df["Representation"].max() > 1.0 and rep_df["Representation"].max() <= 100.0:
        rep_pct = rep_df["Representation"]
    elif rep_df["Representation"].max() <= 1.0:
        rep_pct = rep_df["Representation"] * 100.0
    else:
        total = rep_df["Representation"].sum()
        rep_pct = (rep_df["Representation"]/total)*100.0 if total else rep_df["Representation"]

    c1, c2 = st.columns(2)
    with c1:
        fig_rep = px.bar(rep_df.sort_values("Representation", ascending=True),
                         x="Representation", y="Style", orientation="h",
                         title="Representation by Style")
        st.plotly_chart(fig_rep, use_container_width=True)
    with c2:
        fig_rep_bub = px.scatter(pd.DataFrame({"Style": names_rep, "Representation (%)": rep_pct}),
                                 x="Style", y="Representation (%)",
                                 size="Representation (%)", text="Style",
                                 title="Representation — Bubble Chart")
        fig_rep_bub.update_traces(textposition="top center",
                                  marker=dict(sizemode="area", line=dict(width=1, color="rgba(0,0,0,0.25)")))
        st.plotly_chart(fig_rep_bub, use_container_width=True)

    # Win Ratios
    names_win = parse_range(base, "B1:L1").values.flatten().tolist()
    vals_win = parse_range(base, "B6:L6").values.flatten().tolist()
    win_df = pd.DataFrame({"Style": names_win, "Win Ratio": to_numeric_series(vals_win)}).dropna()
    uw_avg = win_df["Win Ratio"].mean() if not win_df.empty else np.nan

    c3, c4 = st.columns(2)
    with c3:
        fig_win = px.bar(win_df.sort_values("Win Ratio", ascending=True),
                         x="Win Ratio", y="Style", orientation="h",
                         title=f"Win Ratios by Style (UAM {uw_avg:.3f})")
        st.plotly_chart(fig_win, use_container_width=True)
    with c4:
        fig_win_bub = px.scatter(win_df, x="Style", y="Win Ratio",
                                 size="Win Ratio", text="Style",
                                 title="Win Ratios — Bubble Chart")
        fig_win_bub.update_traces(textposition="top center",
                                  marker=dict(sizemode="area", line=dict(width=1, color="rgba(0,0,0,0.25)")))
        st.plotly_chart(fig_win_bub, use_container_width=True)

    # Cross Source
    cross_name = None
    for nm in sheet_names:
        if "cross" in nm.lower():
            cross_name = nm
            break
    if cross_name:
        cross = pd.read_excel(uploaded, sheet_name=cross_name, header=None)
        styles_conv = parse_range(cross, "A3:A13").values.flatten().tolist()
        observed_conv = to_numeric_series(parse_range(cross, "D3:D13").values.flatten().tolist())
        espn_conv = to_numeric_series(parse_range(cross, "E3:E13").values.flatten().tolist())
        conv_df = pd.DataFrame({"Style": styles_conv, "Observed": observed_conv, "ESPN": espn_conv}).dropna()

        conv_long = conv_df.melt(id_vars="Style", var_name="Source", value_name="Conversion")
        c5, c6 = st.columns(2)
        with c5:
            fig_conv = px.bar(conv_long.sort_values("Conversion", ascending=True),
                              x="Conversion", y="Style", color="Source", orientation="h",
                              barmode="group", title="Champion Conversion by Style")
            st.plotly_chart(fig_conv, use_container_width=True)
        with c6:
            fig_conv_bub = px.scatter(conv_long, x="Style", y="Conversion",
                                      size="Conversion", color="Source", text="Style",
                                      title="Conversion — Bubble Chart")
            fig_conv_bub.update_traces(textposition="top center",
                                       marker=dict(sizemode="area", line=dict(width=1, color="rgba(0,0,0,0.25)")))
            st.plotly_chart(fig_conv_bub, use_container_width=True)

        # Champion Representation Counts
        styles_rep2 = parse_range(cross, "A3:A13").values.flatten().tolist()
        observed_rep2 = to_numeric_series(parse_range(cross, "B3:B13").values.flatten().tolist())
        espn_rep2 = to_numeric_series(parse_range(cross, "C3:C13").values.flatten().tolist())
        rep2_df = pd.DataFrame({"Style": styles_rep2, "Observed": observed_rep2, "ESPN": espn_rep2}).dropna()

        fig_rep2 = px.bar(rep2_df.melt(id_vars="Style", var_name="Source", value_name="Champions"),
                          x="Champions", y="Style", color="Source", orientation="h",
                          barmode="group", title="Champion Representation by Style")
        st.plotly_chart(fig_rep2, use_container_width=True)
else:
    st.info("Upload the Excel file to generate the dashboard.")
