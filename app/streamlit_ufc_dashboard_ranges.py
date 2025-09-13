
import re
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="UFC Styles Dashboard", layout="wide")
st.title("UFC Styles Dashboard")

uploaded = st.file_uploader("Upload Excel", type=["xlsx","xls"])

# ---------------- Helpers ----------------
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

def to_percent_series_no_drop(s):
    s = pd.to_numeric(pd.Series(s), errors='coerce').replace([np.inf,-np.inf], np.nan).fillna(0.0)
    if s.max() <= 1.0:
        return s * 100.0
    s_sum = s.sum()
    if 95.0 <= s_sum <= 105.0:
        return s
    return (s / s_sum * 100.0) if s_sum > 0 else s

def _contrast_text(color: str) -> str:
    s = str(color).strip()
    try:
        if s.startswith("#"):
            h = s[1:]
            if len(h) == 3:
                h = "".join([c*2 for c in h])
            r = int(h[0:2], 16); g = int(h[2:4], 16); b = int(h[4:6], 16)
        elif s.lower().startswith("rgba") or s.lower().startswith("rgb"):
            nums = s[s.find("(")+1:s.find(")")].split(",")
            r = float(nums[0]); g = float(nums[1]); b = float(nums[2])
            if r <= 1 and g <= 1 and b <= 1:
                r, g, b = int(r*255), int(g*255), int(b*255)
            else:
                r, g, b = int(round(r)), int(round(g)), int(round(b))
        else:
            return "white"
        luminance = (0.2126*r + 0.7152*g + 0.0722*b) / 255.0
        return "black" if luminance > 0.6 else "white"
    except Exception:
        return "white"

# -------- Packed bubbles with Top-K labels and legend --------
def packed_bubbles(df, label_col, value_col, title, palette=None, template="plotly_dark",
                   size_scale=1.0, top_k_labels=2, show_values=True):
    try:
        import circlify
    except ImportError:
        st.error("Missing dependency: circlify. Install with: pip install circlify")
        return None

    work = df[[label_col, value_col]].copy()
    work[value_col] = to_percent_series_no_drop(work[value_col])
    EPS = 1e-6
    work[value_col] = work[value_col].clip(lower=EPS)
    work = work.sort_values(value_col, ascending=False).reset_index(drop=True)

    # Determine top-k IDs for labeling
    top_ids = set(work.head(max(0, int(top_k_labels)))[label_col].astype(str).tolist())

    items = [{"id": str(row[label_col]), "datum": float(row[value_col])} for _, row in work.iterrows()]
    circles = circlify.circlify(items, show_enclosure=False, target_enclosure=circlify.Circle(x=0, y=0, r=1))

    colors = (palette or px.colors.qualitative.Set2)
    id_to_val = {it["id"]: it["datum"] for it in items}
    id_to_color = {it["id"]: colors[i % len(colors)] for i, it in enumerate(items)}

    fig = go.Figure()
    # Invisible base
    fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(size=1, color="rgba(0,0,0,0)"),
                             showlegend=False, hoverinfo="skip"))

    # Legend entries (off-canvas points)
    for i, it in enumerate(items):
        cid = it["id"]
        fig.add_trace(go.Scatter(
            x=[999+i], y=[999+i],
            mode="markers",
            marker=dict(size=10, color=id_to_color[cid]),
            name=cid,
            showlegend=True,
            hoverinfo="skip",
            visible=True
        ))

    for c in circles:
        cid = getattr(c, "id", None)
        if cid is None and hasattr(c, "ex") and isinstance(c.ex, dict):
            cid = c.ex.get("id")
        if cid is None or cid not in id_to_val:
            continue

        val = id_to_val[cid]
        fill = id_to_color[cid]
        r = c.r * size_scale

        fig.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=c.x - r, x1=c.x + r, y0=c.y - r, y1=c.y + r,
            line=dict(width=1.0, color="rgba(0,0,0,0.35)"),
            fillcolor=fill, opacity=0.95,
        )

        if cid in top_ids:
            txt_color = _contrast_text(fill)
            text = f"{cid}" + (f"<br>{val:.1f}%" if show_values else "")
            fig.add_annotation(
                x=c.x, y=c.y, text=text, showarrow=False,
                font=dict(size=max(14, int(12 + r * 26)), color=txt_color, family="Arial Black"),
                align="center", xanchor="center", yanchor="middle"
            )

    lim = 1.15 * size_scale
    fig.update_xaxes(visible=False, scaleanchor="y", scaleratio=1, range=[-lim, lim])
    fig.update_yaxes(visible=False, range=[-lim, lim])
    fig.update_layout(title=title, template=template, margin=dict(l=10, r=10, t=60, b=10), showlegend=True)
    return fig

# ---------------- App ----------------
if uploaded:
    base = pd.read_excel(uploaded, sheet_name=0, header=None)
    sheet_names = pd.ExcelFile(uploaded).sheet_names

    size_scale = st.slider("Bubble size scale", 0.6, 1.6, 1.0, 0.05)
    topk = st.slider("How many bubbles to label?", 0, 5, 2, 1)

    # -------- Representation --------
    st.subheader("Representation by Style")
    names_rep = parse_range(base, "C1:L1").values.flatten().tolist()
    vals_rep = parse_range(base, "C2:L2").values.flatten().tolist()
    rep_df = pd.DataFrame({"Style": names_rep, "Representation": to_numeric_series(vals_rep)}).fillna(0.0)

    rep_bars = rep_df.copy()
    if rep_bars["Representation"].max() > 1.0 and rep_bars["Representation"].max() <= 100.0:
        rep_bars["Representation (%)"] = rep_bars["Representation"]
        pct_note = "(interpreted as %)"
    elif rep_bars["Representation"].max() <= 1.0:
        rep_bars["Representation (%)"] = rep_bars["Representation"] * 100.0
        pct_note = "(converted from proportion)"
    else:
        total = rep_bars["Representation"].sum()
        rep_bars["Representation (%)"] = (rep_bars["Representation"] / total) * 100.0 if total else rep_bars["Representation"]
        pct_note = "(normalized to %)"

    col1, col2 = st.columns(2, gap="large")
    with col1:
        fig_rep_h = px.bar(
            rep_bars.sort_values("Representation (%)", ascending=True),
            x="Representation (%)", y="Style", orientation="h",
            color="Style", color_discrete_sequence=px.colors.qualitative.Dark2,
            title=f"Representation by Style {pct_note}"
        )
        fig_rep_h.update_xaxes(ticksuffix="%")
        st.plotly_chart(fig_rep_h, use_container_width=True)

    with col2:
        rep_for_bubbles = pd.DataFrame({"Style": rep_df["Style"], "Value": to_percent_series_no_drop(rep_df["Representation"])})
        fig_rep_pack = packed_bubbles(
            rep_for_bubbles, "Style", "Value",
            title="Representation by Style — Packed Bubbles (area ∝ win %)",
            palette=px.colors.qualitative.Set2, template="plotly_dark",
            size_scale=size_scale, top_k_labels=topk, show_values=True
        )
        st.plotly_chart(fig_rep_pack, use_container_width=True)

    # -------- Win Ratios --------
    st.subheader("Win Ratio by Style")
    names_win = parse_range(base, "B1:L1").values.flatten().tolist()
    vals_win = parse_range(base, "B6:L6").values.flatten().tolist()
    win_df = pd.DataFrame({"Style": names_win, "Win Ratio": to_numeric_series(vals_win)}).fillna(0.0)

    col3, col4 = st.columns(2, gap="large")
    with col3:
        fig_win_h = px.bar(
            win_df.sort_values("Win Ratio", ascending=True),
            x="Win Ratio", y="Style", orientation="h",
            color="Style", color_discrete_sequence=px.colors.qualitative.Dark2,
            title=f"Win Ratio by Style"
        )
        st.plotly_chart(fig_win_h, use_container_width=True)

    with col4:
        win_for_bubbles = pd.DataFrame({"Style": win_df["Style"], "Value": to_percent_series_no_drop(win_df["Win Ratio"])})
        fig_win_pack = packed_bubbles(
            win_for_bubbles, "Style", "Value",
            title="Win Ratio by Style — Packed Bubbles (area ∝ win %)",
            palette=px.colors.qualitative.Set3, template="plotly_dark",
            size_scale=size_scale, top_k_labels=topk, show_values=True
        )
        st.plotly_chart(fig_win_pack, use_container_width=True)

    # -------- Conversion (Observed vs ESPN) --------
    cross_name = next((nm for nm in sheet_names if "cross" in nm.lower()), None)
    if cross_name is None:
        st.error("Could not find a sheet named like 'Cross Source Analysis'.")
        st.stop()
    cross = pd.read_excel(uploaded, sheet_name=cross_name, header=None)

    styles_conv = parse_range(cross, "A3:A13").values.flatten().tolist()
    observed_conv = to_numeric_series(parse_range(cross, "D3:D13").values.flatten().tolist())
    espn_conv = to_numeric_series(parse_range(cross, "E3:E13").values.flatten().tolist())
    conv_df = pd.DataFrame({"Style": styles_conv, "Observed": observed_conv, "ESPN": espn_conv}).fillna(0.0)

    conv_obs_bubbles = pd.DataFrame({"Style": conv_df["Style"], "Value": to_percent_series_no_drop(conv_df["Observed"])})
    conv_espn_bubbles = pd.DataFrame({"Style": conv_df["Style"], "Value": to_percent_series_no_drop(conv_df["ESPN"])})

    col5, col6, col7 = st.columns([1.2, 1, 1], gap="large")
    with col5:
        conv_long = pd.DataFrame({
            "Style": conv_df["Style"],
            "Observed %": conv_obs_bubbles["Value"],
            "ESPN %": conv_espn_bubbles["Value"]
        }).melt(id_vars="Style", var_name="Source", value_name="Conversion (%)")

        fig_conv_h = px.bar(
            conv_long.sort_values(["Source","Conversion (%)"], ascending=[True, True]),
            x="Conversion (%)", y="Style", color="Source", orientation="h",
            color_discrete_map={"Observed %":"#1f77b4", "ESPN %":"#ff7f0e"},
            barmode="group", title="Conversion by Style — Observed vs ESPN (horizontal)"
        )
        fig_conv_h.update_xaxes(ticksuffix="%")
        st.plotly_chart(fig_conv_h, use_container_width=True)

    with col6:
        fig_conv_obs = packed_bubbles(
            conv_obs_bubbles, "Style", "Value",
            title="Conversion — Observed (Bubble area ∝ %)",
            palette=px.colors.qualitative.Dark2, template="plotly_dark",
            size_scale=size_scale, top_k_labels=topk, show_values=True
        )
        st.plotly_chart(fig_conv_obs, use_container_width=True)

    with col7:
        fig_conv_espn = packed_bubbles(
            conv_espn_bubbles, "Style", "Value",
            title="Conversion — ESPN (Bubble area ∝ %)",
            palette=px.colors.qualitative.Pastel1, template="plotly_dark",
            size_scale=size_scale, top_k_labels=topk, show_values=True
        )
        st.plotly_chart(fig_conv_espn, use_container_width=True)

else:
    st.info("Upload the Excel file to generate the dashboard. Expect a sheet named like 'Cross Source Analysis'.")
