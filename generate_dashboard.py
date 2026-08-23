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
        marker_colors=['#2ca02c', '#d62728'] if 'Ignore' in status_counts.index[0] else ['#d62728', '#2ca02c']
    ), row=1, col=1)

    # Chart 2: Scatter Plot (Risk Matrix)
    fig.add_trace(go.Scatter(
        x=df['active_stuck_shipments'],
        y=df['p90_dwell_hours'],
        mode='markers',
        text=df['courier_warehouse'],
        marker=dict(
            color=df['priority_category'].map({'Prioritize for Clearing': 'red', 'Ignore': 'green'}),
            opacity=0.6,
            size=8
        ),
        name="Warehouses"
    ), row=1, col=2)

    # Chart 3: Bar Chart (Top 15 Choked Hubs)
    fig.add_trace(go.Bar(
        x=choked_df['courier_warehouse'],
        y=choked_df['p90_dwell_hours'],
        marker_color='indianred',
        text=choked_df['p90_dwell_hours'],
        textposition='auto'
    ), row=2, col=1)

    # Update Layout Aesthetics
    fig.update_layout(
        title_text="Logistics Network Bottleneck Intelligence",
        title_font_size=24,
        height=900,
        showlegend=False,
        template="plotly_dark" # Gives it a sleek, professional hacker/dashboard vibe
    )
    
    # Axis labels
    fig.update_xaxes(title_text="Active Stuck Shipments", row=1, col=2)
    fig.update_yaxes(title_text="P90 Dwell Hours", row=1, col=2)
    fig.update_yaxes(title_text="P90 Dwell Hours", row=2, col=1)

    # Export to a static HTML file
    output_file = "index.html"
    fig.write_html(output_file)
    print(f"=> Interactive dashboard successfully generated as '{output_file}'")

if __name__ == "__main__":
    build_dashboard()