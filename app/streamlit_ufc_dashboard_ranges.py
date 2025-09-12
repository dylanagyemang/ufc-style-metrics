
import re
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="UFC Styles Dashboard – Ranged Extracts", layout="wide")
st.title("UFC Styles Dashboard")

st.caption("Upload **UFC Fighters (3_2022).xlsx**. The app reads fixed ranges for: "
           "style representation, win ratios, champion conversion rate (cross-source), and champion representation (cross-source).")

uploaded = st.file_uploader("Upload Excel", type=["xlsx","xls"])

def a1_to_ix(a1: str):
    # Convert Excel A1 to 0-based row, col
    m = re.match(r"^\s*([A-Za-z]+)(\d+)\s*$", a1)
    if not m: raise ValueError(f"Bad A1 address: {a1}")
    col_s, row_s = m.groups()
    col = 0
    for ch in col_s.upper():
        col = col*26 + (ord(ch)-64)
    return int(row_s)-1, col-1

def parse_range(df: pd.DataFrame, rng: str):
    # rng like "C1:L1"
    a, b = [x.strip() for x in rng.split(":")]
    r1,c1 = a1_to_ix(a)
    r2,c2 = a1_to_ix(b)
    return df.iloc[min(r1,r2):max(r1,r2)+1, min(c1,c2):max(c1,c2)+1]

def to_numeric_series(s):
    return pd.to_numeric(pd.Series(s).astype(str).str.replace("%","", regex=False), errors='coerce')

if uploaded:
    # Load main (first) sheet in a raw form (no header) to read ranges by A1
    base = pd.read_excel(uploaded, sheet_name=0, header=None)
    sheet_names = pd.ExcelFile(uploaded).sheet_names

    st.markdown("### Overall Style Representation")
    # Names C1:L1, values C2:L2
    names_rep = parse_range(base, "C1:L1").values.flatten().tolist()
    vals_rep = parse_range(base, "C2:L2").values.flatten().tolist()
    rep_df = pd.DataFrame({"Style": names_rep, "Representation": to_numeric_series(vals_rep)}).dropna()
    # If representation appears to be proportions (0-1), keep; if whole numbers, try normalize
    if rep_df["Representation"].max() > 1.0 and rep_df["Representation"].max() <= 100.0:
        # Could be already in percents; that's fine, display as %
        rep_pct = rep_df["Representation"]
        pct_note = "(interpreted as %)"
    else:
        # If looks like proportions (<=1), convert to % for display
        if rep_df["Representation"].max() <= 1.0:
            rep_pct = rep_df["Representation"] * 100.0
            pct_note = "(converted from proportion)"
        else:
            # Large numbers; convert to share of sum
            total = rep_df["Representation"].sum()
            rep_pct = (rep_df["Representation"] / total) * 100.0 if total else rep_df["Representation"]
            pct_note = "(normalized to %)"
    st.dataframe(rep_df.style.format({"Representation":"{:.3f}"}))
    fig_rep = px.bar(rep_df, x="Style", y="Representation", title="Overall Style Representation (raw)")
    st.plotly_chart(fig_rep, use_container_width=True)
    fig_rep_pct = px.bar(pd.DataFrame({"Style": names_rep, "Representation (%)": rep_pct}), x="Style", y="Representation (%)",
                         title=f"Overall Style Representation {pct_note}")
    fig_rep_pct.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig_rep_pct, use_container_width=True)

    st.markdown("### Overall Win Ratio by Style")
    # Names B1:L1, values B6:L6
    names_win = parse_range(base, "B1:L1").values.flatten().tolist()
    vals_win = parse_range(base, "B6:L6").values.flatten().tolist()
    win_df = pd.DataFrame({"Style": names_win, "Win Ratio": to_numeric_series(vals_win)}).dropna()
    st.dataframe(win_df.style.format({"Win Ratio":"{:.3f}"}))
    fig_win = px.bar(win_df.sort_values("Win Ratio", ascending=False), x="Style", y="Win Ratio",
                     title=f"Overall Win Ratio by Style (UW Avg: {win_df['Win Ratio'].mean():.3f})")
    st.plotly_chart(fig_win, use_container_width=True)

    # Cross Source Analysis sheet for conversions and champion representation
    cross_name = None
    for nm in sheet_names:
        if "cross" in nm.lower():
            cross_name = nm
            break
    if cross_name is None:
        st.error("Could not find a sheet named like 'Cross Source Analysis'. Please ensure that sheet exists.")
        st.stop()

    cross = pd.read_excel(uploaded, sheet_name=cross_name, header=None)

    st.markdown("### Champion Conversion Rate by Style — Cross Source Analysis")
    # A3:A13 styles, D3:D13 Observed, E3:E13 ESPN
    styles_conv = parse_range(cross, "A3:A13").values.flatten().tolist()
    observed_conv = to_numeric_series(parse_range(cross, "D3:D13").values.flatten().tolist())
    espn_conv = to_numeric_series(parse_range(cross, "E3:E13").values.flatten().tolist())
    conv_df = pd.DataFrame({
        "Style": styles_conv,
        "Conversion (Observed)": observed_conv,
        "Conversion (ESPN)": espn_conv
    }).dropna(subset=["Style"])
    # If values look like proportions, also show percent
    disp_conv_pct = conv_df.copy()
    if disp_conv_pct[["Conversion (Observed)", "Conversion (ESPN)"]].max().max() <= 1.0:
        disp_conv_pct["Conversion (Observed)"] = disp_conv_pct["Conversion (Observed)"] * 100.0
        disp_conv_pct["Conversion (ESPN)"] = disp_conv_pct["Conversion (ESPN)"] * 100.0
        conv_pct_note = "(converted from proportion)"
    else:
        conv_pct_note = "(interpreted as %)"
    st.dataframe(conv_df.style.format({"Conversion (Observed)":"{:.3f}", "Conversion (ESPN)":"{:.3f}"}))
    fig_conv = px.bar(conv_df.melt(id_vars="Style", var_name="Source", value_name="Conversion"),
                      x="Style", y="Conversion", color="Source", barmode="group",
                      title="Champion Conversion Rate by Style (raw)")
    st.plotly_chart(fig_conv, use_container_width=True)
    fig_conv_pct = px.bar(disp_conv_pct.melt(id_vars="Style", var_name="Source", value_name="Conversion (%)"),
                          x="Style", y="Conversion (%)", color="Source", barmode="group",
                          title=f"Champion Conversion Rate by Style {conv_pct_note}")
    fig_conv_pct.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig_conv_pct, use_container_width=True)

    st.markdown("### Champion Representation by Style — Cross Source Analysis")
    # A3:A13 styles, B3:B13 observed, C3:C13 ESPN 
    styles_rep2 = parse_range(cross, "A3:A13").values.flatten().tolist()
    observed_rep2 = to_numeric_series(parse_range(cross, "B3:B13").values.flatten().tolist())
    espn_rep2 = to_numeric_series(parse_range(cross, "C3:C13").values.flatten().tolist())
    # Align lengths (styles may be 12 entries; B3:B13 gives 11; pad with NaN at top)
    max_len = max(len(styles_rep2), len(observed_rep2), len(espn_rep2))
    def pad(lst, n):
        out = list(lst)
        while len(out) < n: out.append(np.nan)
        return out
    styles_rep2 = pad(styles_rep2, max_len)
    observed_rep2 = pad(observed_rep2, max_len)
    espn_rep2 = pad(espn_rep2, max_len)

    rep2_df = pd.DataFrame({
        "Style": styles_rep2,
        "Champions (Observed)": observed_rep2,
        "Champions (ESPN)": espn_rep2
    }).dropna(subset=["Style"])
    st.dataframe(rep2_df.style.format({"Champions (Observed)":"{:,.0f}", "Champions (ESPN)":"{:,.0f}"}))
    fig_rep2 = px.bar(rep2_df.melt(id_vars="Style", var_name="Source", value_name="Champions"),
                      x="Style", y="Champions", color="Source", barmode="group",
                      title="Champion Representation by Style (Observed vs ESPN)")
    st.plotly_chart(fig_rep2, use_container_width=True)

    # Averages & Summary
    st.markdown("### Averages & Summary")
    win_avg = win_df["Win Ratio"].mean() if not win_df.empty else np.nan
    conv_avg_observed = conv_df["Conversion (Observed)"].mean() if not conv_df.empty else np.nan
    conv_avg_espn  = conv_df["Conversion (ESPN)"].mean() if not conv_df.empty else np.nan
    rep_avg = rep_df["Representation"].mean() if not rep_df.empty else np.nan
    st.write({
        "Average Representation (raw units)": float(rep_avg) if pd.notna(rep_avg) else None,
        "Average Win Ratio": float(win_avg) if pd.notna(win_avg) else None,
        "Average Champion Conversion (Observed)": float(conv_avg_observed) if pd.notna(conv_avg_observed) else None,
        "Average Champion Conversion (ESPN)": float(conv_avg_espn) if pd.notna(conv_avg_espn) else None
    })

    # Downloads
    st.subheader("Downloads")
    def to_csv_bytes(df): return df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Representation CSV", to_csv_bytes(rep_df), "style_representation.csv", "text/csv")
    st.download_button("Download Win Ratios CSV", to_csv_bytes(win_df), "win_ratios.csv", "text/csv")
    st.download_button("Download Conversion CSV", to_csv_bytes(conv_df), "conversion_rates_cross_source.csv", "text/csv")
    st.download_button("Download Champion Representation CSV", to_csv_bytes(rep2_df), "champion_representation_cross_source.csv", "text/csv")
else:
    st.info("Upload the Excel file to generate the dashboard. Expect a sheet named like 'Cross Source Analysis' for the cross-source sections.")
