import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def build_dashboard():
    # Load the processed data
    df = pd.read_csv('warehouse_priority_list.csv')
    
    # Filter for the worst offenders for the bar chart
    choked_df = df[df['priority_category'] == 'Prioritize for Clearing'].head(15)
    
    # Initialize a 2x2 dashboard layout
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "domain"}, {"type": "xy"}],
               [{"colspan": 2, "type": "xy"}, None]],
        subplot_titles=("Network Status Breakdown", 
                        "Risk Matrix: Dwell Time vs Backlog", 
                        "Top 15 Critical Bottlenecks (P90 Dwell Hours)"),
        vertical_spacing=0.15
    )

    # Chart 1: Donut Chart (Status Breakdown)
    status_counts = df['priority_category'].value_counts()
    fig.add_trace(go.Pie(
        labels=status_counts.index, 
        values=status_counts.values, 
        hole=0.4,
        marker_colors=['#22c55e', '#ef4444'] if 'Ignore' in status_counts.index[0] else ['#ef4444', '#22c55e']
    ), row=1, col=1)

    # Chart 2: Scatter Plot (Risk Matrix)
    fig.add_trace(go.Scatter(
        x=df['active_stuck_shipments'],
        y=df['p90_dwell_hours'],
        mode='markers',
        text=df['courier_warehouse'],
        marker=dict(
            color=df['priority_category'].map({'Prioritize for Clearing': '#ef4444', 'Ignore': '#22c55e'}),
            opacity=0.7,
            size=9
        ),
        name="Warehouses"
    ), row=1, col=2)

    # Chart 3: Bar Chart (Top 15 Choked Hubs)
    fig.add_trace(go.Bar(
        x=choked_df['courier_warehouse'],
        y=choked_df['p90_dwell_hours'],
        marker_color='#ef4444',
        text=choked_df['p90_dwell_hours'],
        textposition='auto'
    ), row=2, col=1)

    # Update Layout Aesthetics for Dark Modern Theme
    fig.update_layout(
        title_text="", # Handled by custom HTML header for better design
        height=850,
        showlegend=False,
        template="plotly_dark",
        paper_bgcolor="#1e293b",
        plot_bgcolor="#1e293b",
        font=dict(family="Inter, sans-serif", color="#f8fafc")
    )
    
    # Axis labels & styling
    fig.update_xaxes(title_text="Active Stuck Shipments", row=1, col=2, gridcolor="#334155")
    fig.update_yaxes(title_text="P90 Dwell Hours", row=1, col=2, gridcolor="#334155")
    fig.update_yaxes(title_text="P90 Dwell Hours", row=2, col=1, gridcolor="#334155")
    fig.update_xaxes(tickangle=-30, row=2, col=1, gridcolor="#334155")

    # Generate Plotly's raw HTML snippet string
    plotly_div = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # Construct the modern custom HTML wrapper
    modern_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Swift Logistics: Warehouse Bottleneck Intelligence</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }}
        body {{ background-color: #0f172a; color: #f8fafc; padding: 24px; }}
        header {{
            max-width: 1400px; margin: 0 auto 24px auto;
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid #1e293b; padding-bottom: 16px;
        }}
        .title-group h1 {{ font-size: 22px; font-weight: 700; color: #f1f5f9; }}
        .title-group p {{ font-size: 13px; color: #94a3b8; margin-top: 4px; }}
        .badge {{
            background-color: rgba(239, 68, 68, 0.15); color: #fca5a5;
            border: 1px solid rgba(239, 68, 68, 0.3); padding: 6px 12px;
            border-radius: 6px; font-size: 11px; font-weight: 600; text-transform: uppercase;
        }}
        .dashboard-wrapper {{
            max-width: 1400px; margin: 0 auto;
            background-color: #1e293b; border: 1px solid #334155;
            border-radius: 12px; padding: 20px;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
        }}
        footer {{
            max-width: 1400px; margin: 24px auto 0 auto; text-align: center;
            font-size: 12px; color: #64748b; border-top: 1px solid #1e293b; padding-top: 16px;
        }}
    </style>
</head>
<body>
    <header>
        <div class="title-group">
            <h1>Swift Logistics: Warehouse Bottleneck Intelligence</h1>
            <p>Interactive telemetry, P90 dwell time analysis, and live active inventory backlogs.</p>
        </div>
        <div>
            <span class="badge">Production Dashboard</span>
        </div>
    </header>

    <div class="dashboard-wrapper">
        {plotly_div}
    </div>

    <footer>
        <p>Built with DuckDB, Pandas, & Plotly &bull; Swift Logistics Assessment</p>
    </footer>
</body>
</html>
"""

    # Export to index.html
    output_file = "index.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(modern_html)
        
    print(f"=> Modern interactive dashboard successfully generated as '{output_file}'")

if __name__ == "__main__":
    build_dashboard()