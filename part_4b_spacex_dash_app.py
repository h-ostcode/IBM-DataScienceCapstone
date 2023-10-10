# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

#Capitalize class column for chart labeling purposes
spacex_df = spacex_df.rename(columns={'class':'Class'})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div(dcc.Dropdown(
                                            id='site-dropdown',
                                            options=[
                                                    {'label': 'All Sites', 'value': 'ALL'},
                                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                                    ],
                                            value='ALL',
                                            placeholder='Select a Launch Site',
                                            searchable=True,
                                            ),
                                        style={'width':'50%', 'margin': '0 auto', 'padding':'3px', 'font-size': '20px','textAlign': 'center'}
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload Range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                marks={0:'0', 2500:'2500', 5000:'5000',7500:'7500', 10000:'10000'},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

#Create Callback Functions
# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='Class', 
        names='Launch Site', 
        title='Total Success Launches by Site')
        fig.update_traces(textfont_color='white')
        fig.update_layout(hoverlabel=dict(font_color='white', bordercolor='black'))
        return fig
    else:
        # return the outcomes piechart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site].groupby('Class').size().reset_index(name='Counts')
        color_map = {0: '#eb553f', 1: '#636efa'}
        fig = px.pie(filtered_df, values='Counts', 
        names=['Failed' if i == 0 else 'Successful' for i in filtered_df.groupby(['Class']).size().index], 
        title='Total Success Launches for Site {}'.format(entered_site),
        color='Class',
        color_discrete_map=color_map)
        fig.update_traces(textfont_color='white')
        fig.update_layout(hoverlabel=dict(font_color='white', bordercolor='black'))
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])

def get_scatter_plot(entered_site, payload_range):
    filtered_payload = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    if entered_site == 'ALL':
        fig = px.scatter(filtered_payload,
        x='Payload Mass (kg)', 
        y='Class',
        color="Booster Version Category", 
        title='Correlation between Payload and Success for All Sites')
        return fig
    else:
        filtered_df = filtered_payload[filtered_payload['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df,
        x='Payload Mass (kg)', 
        y='Class',
        color="Booster Version Category", 
        title='Correlation between Payload and Success for Site {}'.format(entered_site))
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()