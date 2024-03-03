# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px


# Read the airline data into pandas dataframe

# This file is kept in the same directory as this python file.
# If you face any issue loading the file, use Absolute File path instead of relative file path.
file_path = 'spacex_launch_dash.csv'    

# spacex_df = pd.read_csv("spacex_launch_dash.csv")
spacex_df = pd.read_csv(file_path)



max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


# Create a dash application
app = dash.Dash(__name__)


launch_sites = spacex_df['Launch Site'].unique()
dd_options_sites = {'ALL':'ALL'}

for site in launch_sites:
    dd_options_sites[site] = site
    


# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                       id='site-dropdown',
                                       options=dd_options_sites,
                                       value='ALL',
                                       placeholder = 'Select a Launch Site here',
                                       searchable = True
                                       ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                value=[min_payload, max_payload],
                                                marks={0:'0', 1000:'1000'}
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])



# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    
    launch_success_rate = spacex_df.groupby(by='Launch Site')['class'].mean().reset_index()
    
    filtered_df =spacex_df[spacex_df['Launch Site'] ==  entered_site]['class'].value_counts().reset_index()
    
    if entered_site == 'ALL':
        fig = px.pie(launch_success_rate,
                     names='Launch Site',
                     values = 'class',
                     title='Launch Success Rate by Launch Sites (ALL)')
        return fig
    else:
        fig = px.pie(filtered_df,
                     names='class',
                     values = 'count',
                     title=f'Launch Success Rate at {entered_site}')
        return fig
    
    
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, payload_value):
    # pass
    payload_by_mass = spacex_df[(spacex_df['Payload Mass (kg)'] >= float(payload_value[0]))
                                & (spacex_df['Payload Mass (kg)'] <= float(payload_value[1]))]
    
    if entered_site == 'ALL':
        fig = px.scatter(payload_by_mass,
                         y='class',
                         x='Payload Mass (kg)',
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for all Sites')
        return fig
    else:
        payload_by_site = payload_by_mass[payload_by_mass['Launch Site'] == entered_site]
        fig = px.scatter(payload_by_site,
                         y='class',
                         x='Payload Mass (kg)',
                         color='Booster Version Category',
                         title=f'Correlation between Payload and Success the site : {entered_site}')
        return fig



# Run the app
if __name__ == '__main__':
    app.run_server()