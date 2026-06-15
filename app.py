import dash
from dash import dcc, html, dash_table, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os
from datetime import datetime

# ============================================
# LOAD DATA
# ============================================
def load_data():
    csv_path = "data/inc42_articles.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = df.fillna("Not mentioned")
        return df
    return pd.DataFrame()

# ============================================
# APP SETUP
# ============================================
app = dash.Dash(__name__, title="India Startup Analyzer")

# ============================================
# COLORS
# ============================================
COLORS = {
    "bg"         : "#0a0a0f",
    "glass"      : "rgba(255,255,255,0.04)",
    "border"     : "rgba(255,255,255,0.1)",
    "text"       : "#e8e8f0",
    "text_muted" : "rgba(255,255,255,0.4)",
    "blue"       : "#378ADD",
    "purple"     : "#7F77DD",
    "green"      : "#1D9E75",
    "amber"      : "#EF9F27",
    "coral"      : "#D85A30",
}

SECTOR_COLORS = {
    "AI"        : "#378ADD",
    "Fintech"   : "#EF9F27",
    "Healthtech": "#1D9E75",
    "Deeptech"  : "#7F77DD",
    "EV"        : "#639922",
    "Ecommerce" : "#D85A30",
    "Edtech"    : "#D4537E",
    "General"   : "#888780",
    "Fitness"   : "#5DCAA5",
    "SaaS"      : "#AFA9EC",
}

# ============================================
# GLASS CARD STYLE
# ============================================
def glass_card(children, style={}):
    base = {
        "background"      : "rgba(255,255,255,0.04)",
        "border"          : "0.5px solid rgba(255,255,255,0.1)",
        "backdropFilter"  : "blur(12px)",
        "borderRadius"    : "12px",
        "padding"         : "1.1rem 1.25rem",
    }
    base.update(style)
    return html.Div(children, style=base)

# ============================================
# LAYOUT
# ============================================
app.layout = html.Div([

    # Background glow effects
    html.Div(style={
        "position"  : "fixed",
        "top"       : "0", "left": "0",
        "width"     : "100%", "height": "100%",
        "background": """
            radial-gradient(ellipse at 20% 20%, rgba(55,138,221,0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(127,119,221,0.12) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(29,158,117,0.08) 0%, transparent 60%)
        """,
        "zIndex": "-1",
        "pointerEvents": "none",
    }),

    # ── HEADER ──
    html.Div([
        html.Div([
            html.Div([
                html.Span("⬡", style={"color": COLORS["blue"], "fontSize": "20px", "marginRight": "10px"}),
                html.Span("India Startup Funding Analyzer",
                    style={"fontSize": "17px", "fontWeight": "500", "color": "#ffffff"}),
            ], style={"display": "flex", "alignItems": "center"}),
            html.Div("Live data · Inc42 + NewsAPI · Auto-updated 9:00 AM daily",
                style={"fontSize": "12px", "color": COLORS["text_muted"], "marginTop": "3px"}),
        ]),
        html.Div([
            html.Div([
                html.Div(style={
                    "width": "7px", "height": "7px",
                    "borderRadius": "50%",
                    "background": "#5DCAA5",
                    "marginRight": "6px",
                }),
                html.Span("Live", style={"fontSize": "11px", "color": "#5DCAA5"}),
            ], style={
                "display"      : "flex", "alignItems": "center",
                "background"   : "rgba(29,158,117,0.15)",
                "border"       : "0.5px solid rgba(29,158,117,0.3)",
                "borderRadius" : "20px",
                "padding"      : "4px 12px",
            }),
            html.Button([
                html.Span("↻ ", style={"marginRight": "4px"}),
                "Refresh"
            ], id="refresh-btn", style={
                "background"   : "rgba(255,255,255,0.06)",
                "border"       : "0.5px solid rgba(255,255,255,0.15)",
                "color"        : "rgba(255,255,255,0.6)",
                "fontSize"     : "12px",
                "padding"      : "5px 14px",
                "borderRadius" : "8px",
                "cursor"       : "pointer",
            }),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px"}),
    ], style={
        "display"      : "flex",
        "alignItems"   : "center",
        "justifyContent": "space-between",
        "padding"      : "1rem 1.5rem",
        "borderBottom" : "0.5px solid rgba(255,255,255,0.08)",
        "background"   : "rgba(255,255,255,0.03)",
    }),

    # ── INTERVAL for auto refresh ──
    dcc.Interval(id="interval", interval=300000, n_intervals=0),

    # ── MAIN CONTENT ──
    html.Div(id="main-content", style={"padding": "0"}),

], style={
    "minHeight"  : "100vh",
    "background" : COLORS["bg"],
    "fontFamily" : "system-ui, -apple-system, sans-serif",
    "color"      : COLORS["text"],
})

# ============================================
# CALLBACK — Update Dashboard
# ============================================
@app.callback(
    Output("main-content", "children"),
    Input("interval", "n_intervals"),
    Input("refresh-btn", "n_clicks"),
)
def update_dashboard(n_intervals, n_clicks):
    df = load_data()

    if df.empty:
        return html.Div("No data found! Run data_collector.py first.",
            style={"color": COLORS["text_muted"], "padding": "2rem"})

    # ── METRICS ──
    total_deals  = len(df)
    top_sector   = df["sector"].value_counts().index[0] if len(df) > 0 else "N/A"
    top_count    = df["sector"].value_counts().iloc[0] if len(df) > 0 else 0
    total_sources= df["source"].nunique() if "source" in df.columns else 0
    with_amount  = len(df[df["amount"] != "Not mentioned"])
    amount_pct   = round((with_amount / total_deals) * 100) if total_deals > 0 else 0

    def metric_card(icon, label, value, sub, color):
        return glass_card([
            html.Div(icon, style={
                "fontSize"    : "20px",
                "marginBottom": "10px",
                "width"       : "32px", "height": "32px",
                "display"     : "flex", "alignItems": "center",
                "justifyContent": "center",
                "background"  : f"{color}22",
                "borderRadius": "8px",
            }),
            html.Div(label, style={
                "fontSize"   : "11px",
                "color"      : COLORS["text_muted"],
                "marginBottom": "4px",
                "letterSpacing": "0.5px",
                "textTransform": "uppercase",
            }),
            html.Div(str(value), style={
                "fontSize"  : "24px",
                "fontWeight": "500",
                "color"     : "#ffffff",
            }),
            html.Div(sub, style={
                "fontSize": "11px",
                "color"   : COLORS["text_muted"],
                "marginTop": "4px",
            }),
        ])

    metrics_row = html.Div([
        metric_card("📊", "Total Deals",   total_deals,          "Collected today",        COLORS["blue"]),
        metric_card("🚀", "Top Sector",    top_sector,           f"{top_count} deals",     COLORS["purple"]),
        metric_card("📰", "News Sources",  total_sources,        "Active sources",         COLORS["green"]),
        metric_card("💰", "With Amount",   f"{amount_pct}%",     f"{with_amount} articles",COLORS["amber"]),
    ], style={
        "display"            : "grid",
        "gridTemplateColumns": "repeat(4, 1fr)",
        "gap"                : "12px",
        "padding"            : "1.25rem 1.5rem",
    })

    # ── SECTOR CHART ──
    sector_counts = df["sector"].value_counts().reset_index()
    sector_counts.columns = ["sector", "count"]
    bar_colors = [SECTOR_COLORS.get(s, "#888780") for s in sector_counts["sector"]]

    sector_fig = go.Figure(go.Bar(
        x=sector_counts["sector"],
        y=sector_counts["count"],
        marker_color=bar_colors,
        marker_line_width=0,
        text=sector_counts["count"],
        textposition="outside",
        textfont=dict(color="rgba(255,255,255,0.7)", size=12),
    ))
    sector_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.6)", family="system-ui"),
        margin=dict(t=10, b=40, l=10, r=10),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            tickfont=dict(size=11),
            showline=False,
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            tickfont=dict(size=11),
            showline=False,
        ),
        showlegend=False,
        height=220,
    )

    # ── PREDICTION CHART ──
    pred_sectors = ["AI", "Fintech", "Healthtech", "Deeptech", "EV"]
    pred_2026    = [5, 0, 1, 2, 1]
    pred_2027    = [5, 0, 0, 2, 0]
    pred_colors  = [SECTOR_COLORS.get(s, "#888780") for s in pred_sectors]

    pred_fig = go.Figure()
    pred_fig.add_trace(go.Bar(
        name="2026",
        x=pred_sectors,
        y=pred_2026,
        marker_color=pred_colors,
        marker_opacity=0.9,
        marker_line_width=0,
        text=pred_2026,
        textposition="outside",
        textfont=dict(color="rgba(255,255,255,0.7)", size=11),
    ))
    pred_fig.add_trace(go.Bar(
        name="2027",
        x=pred_sectors,
        y=pred_2027,
        marker_color=pred_colors,
        marker_opacity=0.5,
        marker_line_width=0,
    ))
    pred_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.6)", family="system-ui"),
        margin=dict(t=10, b=40, l=10, r=10),
        barmode="group",
        legend=dict(
            font=dict(color="rgba(255,255,255,0.5)", size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=False),
        height=220,
    )

    charts_row = html.Div([
        glass_card([
            html.Div("📊  Sector distribution",
                style={"fontSize": "13px", "fontWeight": "500",
                       "color": "rgba(255,255,255,0.8)", "marginBottom": "0.5rem"}),
            dcc.Graph(figure=sector_fig, config={"displayModeBar": False}),
        ]),
        glass_card([
            html.Div("🔮  2026–2027 predictions",
                style={"fontSize": "13px", "fontWeight": "500",
                       "color": "rgba(255,255,255,0.8)", "marginBottom": "0.5rem"}),
            dcc.Graph(figure=pred_fig, config={"displayModeBar": False}),
        ]),
    ], style={
        "display"            : "grid",
        "gridTemplateColumns": "1fr 1fr",
        "gap"                : "12px",
        "padding"            : "0 1.5rem 1.25rem",
    })

    # ── SECTOR PIE CHART ──
    pie_fig = go.Figure(go.Pie(
        labels=sector_counts["sector"],
        values=sector_counts["count"],
        marker_colors=[SECTOR_COLORS.get(s, "#888780") for s in sector_counts["sector"]],
        hole=0.6,
        textinfo="label+percent",
        textfont=dict(color="rgba(255,255,255,0.7)", size=11),
        showlegend=False,
    ))
    pie_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=10),
        height=220,
    )

    # ── SOURCE CHART ──
    if "source" in df.columns:
        source_counts = df["source"].value_counts().reset_index()
        source_counts.columns = ["source", "count"]
        source_fig = go.Figure(go.Bar(
            x=source_counts["count"],
            y=source_counts["source"],
            orientation="h",
            marker_color=COLORS["blue"],
            marker_opacity=0.8,
            marker_line_width=0,
            text=source_counts["count"],
            textposition="outside",
            textfont=dict(color="rgba(255,255,255,0.6)", size=11),
        ))
        source_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor ="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.5)", family="system-ui"),
            margin=dict(t=10, b=10, l=10, r=30),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=False),
            yaxis=dict(gridcolor="rgba(255,255,255,0)", showline=False,
                       tickfont=dict(size=10)),
            height=220,
        )
    else:
        source_fig = go.Figure()

    charts_row2 = html.Div([
        glass_card([
            html.Div("🍩  Sector breakdown",
                style={"fontSize": "13px", "fontWeight": "500",
                       "color": "rgba(255,255,255,0.8)", "marginBottom": "0.5rem"}),
            dcc.Graph(figure=pie_fig, config={"displayModeBar": False}),
        ]),
        glass_card([
            html.Div("📰  Top news sources",
                style={"fontSize": "13px", "fontWeight": "500",
                       "color": "rgba(255,255,255,0.8)", "marginBottom": "0.5rem"}),
            dcc.Graph(figure=source_fig, config={"displayModeBar": False}),
        ]),
    ], style={
        "display"            : "grid",
        "gridTemplateColumns": "1fr 1fr",
        "gap"                : "12px",
        "padding"            : "0 1.5rem 1.25rem",
    })

    # ── NEWS TABLE ──
    table_df = df[["company", "amount", "sector", "source", "scraped_date"]].copy()
    table_df.columns = ["Company", "Amount", "Sector", "Source", "Date"]

    news_table = glass_card([
        html.Div([
            html.Span("📋  Latest funding news",
                style={"fontSize": "13px", "fontWeight": "500",
                       "color": "rgba(255,255,255,0.8)"}),
            html.Span(f"Updated: {datetime.now().strftime('%b %d, %Y')}",
                style={"fontSize": "11px", "color": COLORS["text_muted"]}),
        ], style={"display": "flex", "justifyContent": "space-between",
                  "marginBottom": "1rem"}),

        dash_table.DataTable(
            data=table_df.to_dict("records"),
            columns=[{"name": c, "id": c} for c in table_df.columns],
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": "rgba(255,255,255,0.05)",
                "color"          : "rgba(255,255,255,0.4)",
                "fontWeight"     : "500",
                "fontSize"       : "11px",
                "border"         : "none",
                "textTransform"  : "uppercase",
                "letterSpacing"  : "0.5px",
                "padding"        : "8px",
            },
            style_cell={
                "backgroundColor": "rgba(0,0,0,0)",
                "color"          : "rgba(255,255,255,0.75)",
                "fontSize"       : "12px",
                "border"         : "none",
                "borderBottom"   : "0.5px solid rgba(255,255,255,0.06)",
                "padding"        : "10px 8px",
                "fontFamily"     : "system-ui",
            },
            style_data_conditional=[{
                "if"             : {"state": "active"},
                "backgroundColor": "rgba(55,138,221,0.1)",
                "border"         : "none",
                "color"          : "#ffffff",
            }],
            page_size=10,
            sort_action="native",
            filter_action="native",
            style_filter={
                "backgroundColor": "rgba(255,255,255,0.04)",
                "color"          : "rgba(255,255,255,0.6)",
                "border"         : "0.5px solid rgba(255,255,255,0.1)",
                "fontSize"       : "12px",
            },
        ),
    ], style={"margin": "0 1.5rem 1.5rem"})

    return [metrics_row, charts_row, charts_row2, news_table]

# ============================================
# RUN APP
# ============================================
if __name__ == "__main__":
    app.run(debug=True)