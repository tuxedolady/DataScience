# Import required libraries
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into a pandas DataFrame
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Calculate min and max payload for the range slider
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Create a Dash application
app = dash.Dash(__name__)

# Create the app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    dcc.Dropdown(id='site-dropdown',
                options=[
                    {'label': 'All Sites', 'value': 'ALL'},
                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                ],
                value='ALL',
                placeholder="Select a Launch Site here",
                searchable=True
),
    html.Br(),
    dcc.RangeSlider(id='payload-slider',
                    min=min_payload, max=max_payload, step=1000,
                    marks={0: '0', 100: '100'},
                    value=[min_payload, max_payload]),
    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    html.Div(dcc.Graph(id='scatter-plot')),
])

# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class',
                     names='Launch Site',
                     title='Total Success Launches')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count success and failure for the selected site
        success_count = filtered_df[filtered_df['class'] == 1]['class'].count()
        failure_count = filtered_df[filtered_df['class'] == 0]['class'].count()
        # Create a pie chart figure for success and failure counts
        fig = px.pie(names=['Success', 'Failure'],
                     values=[success_count, failure_count],
                     title=f'Success/Failure Counts for {entered_site}')
        return fig

@app.callback(
    Output(component_id='scatter-plot', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')
)
def get_scatter_chart(selected_site, payload_range):
    if selected_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == selected_site) & (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & (spacex_df['Payload Mass (kg)'] <= payload_range[1])]

    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category', title='Payload vs. Success')
    fig.update_layout(xaxis_title='Payload Mass (Kg)', yaxis_title='Launch Outcome (1=success)')
    return fig


if __name__ == '__main__':
    app.run_server()