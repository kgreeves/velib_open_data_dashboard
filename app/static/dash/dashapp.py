import os
from pathlib import Path

import dash
from dash.dependencies import Input, Output
from dash import dcc, html

import flask
import pandas as pd
from numpy import round
import plotly.express as px

from app.modules.visualising import col_name_to_text

BASE_PATH = Path(__file__).resolve().parent

def create_dash_app(data_pd:pd.DataFrame, requests_pathname_prefix: str = None) -> dash.Dash:

    #Flask server
    server = flask.Flask(__name__)
    server.secret_key = os.environ.get('secret_key', 'secret')

    #Dash
    app = dash.Dash(__name__, server=server, requests_pathname_prefix=requests_pathname_prefix)
    app.scripts.config.serve_locally = False
    dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

    #Layout
    app.layout = html.Div([

        html.Div([

            html.Font(),

            dcc.Dropdown(id="bike_type",
                         options=[
                             {"label": "All Bikes", "value": 'fields.numbikesavailable'},
                             {"label": "Mechanical", "value": 'fields.mechanical'},
                             {"label": "Electric", "value": 'fields.ebike'},
                             {"label": "Percent Capacity", "value": 'percent_numbikesavailable'},
                             {"label": "Percent Mechanical", "value": 'percent_mechanical'},
                             {"label": "Percent Electric", "value": 'percent_ebike'}],
                         multi=False,
                         value='fields.numbikesavailable',
                         style={'width': '60%','font': '"Nunito Sans",sans-serif;'}
                         ),
            ], style={'align-items': 'right', 'justify-content': 'right' }),

        html.Div(id='output_container', style={'text-align': 'center'}, children=[]),
        html.Br(),

        dcc.Checklist(
            id='heatmap-checklist',
            options=[
                {'label': 'Stations', 'value': 'Stations'},
            ],
            value=['Stations'],
            inline=True,
            style={'width': '240px', 'height': '40px',
                   'text-align' : 'center',
                   'cursor': 'pointer', 'border': '0px',
                   'border-radius': '5px', 'background-color':
                       'black', 'color': 'white', 'text-transform':
                       'uppercase', 'font-size': '15px'}
        ),

        dcc.Graph(id='velib_heatmap', figure={}),

    ])

    @app.callback(
        [Output(component_id='output_container', component_property='children'),
         Output(component_id='velib_heatmap', component_property='figure')],
        [Input(component_id='bike_type', component_property='value'),
         Input(component_id='heatmap-checklist', component_property='value')]
    )
    def update_graph(option_slctd, checklist_slctd:list):

        #container = f'Heatmap for {col_name_to_text(option_slctd)} bikes.'
        container =''

        # Prepare data for plotting
        plot_data = pd.DataFrame(data_pd['geometry.coordinates'].tolist(), columns=['longitude', 'latitude'])
        plot_data['Station Name'] = data_pd['fields.name']

        if 'percent' in option_slctd:
            z_value = col_name_to_text(option_slctd)
            plot_data[z_value] = round(100.*data_pd['fields.'+str(option_slctd.split('_')[-1])]/data_pd['fields.capacity'],2)
            plot_data.dropna(inplace=True, axis=0)
        else:
            z_value = 'Available Bikes'
            plot_data[z_value] = data_pd[option_slctd]

        # Plotly Express
        fig = px.density_mapbox(
            data_frame=plot_data,
            lat='latitude',
            lon='longitude',
            z=z_value,
            hover_name='Station Name',
            mapbox_style='carto-positron',
            radius=50,
            opacity=0.5,
            zoom=10,
            center={
                'lon' : plot_data['longitude'].median(),
                'lat' : plot_data['latitude'].median(),
            },
            title=col_name_to_text(option_slctd),
            width=1050,
            height=900
        )

        if 'Stations' in checklist_slctd:
            fig2 = px.scatter_mapbox(
                data_frame=plot_data,
                lat='latitude',
                lon='longitude',
                size=z_value,
                color=z_value,
                hover_name='Station Name',
                mapbox_style='carto-positron',
                zoom=10,
                center={
                    'lon': plot_data['longitude'].median(),
                    'lat': plot_data['latitude'].median(),
                },
                width=1050,
                height=900
            )

            trace0 = fig2
            fig.add_trace(trace0.data[0])
            trace0.layout.update(showlegend=False)
        fig['layout']['uirevision'] = 'some-constant'
        return container, fig


    '''
    #BEE EXAMPLE
    df = pd.read_csv(
        "https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Other/Dash_Introduction/intro_bees.csv")
    df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
    df.reset_index(inplace=True)

    app.layout = html.Div([

        html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),

        dcc.Dropdown(id="slct_year",
                     options=[
                         {"label": "2015", "value": 2015},
                         {"label": "2016", "value": 2016},
                         {"label": "2017", "value": 2017},
                         {"label": "2018", "value": 2018}],
                     multi=False,
                     value=2015,
                     style={'width': "40%"}
                     ),

        html.Div(id='output_container', children=[]),
        html.Br(),

        dcc.Graph(id='my_bee_map', figure={})

    ])
    
    
    @app.callback(
        [Output(component_id='output_container', component_property='children'),
         Output(component_id='my_bee_map', component_property='figure')],
        [Input(component_id='slct_year', component_property='value')]
    )
    def update_graph(option_slctd):
        print(option_slctd)
        print(type(option_slctd))

        container = "The year chosen by user was: {}".format(option_slctd)

        dff = df.copy()
        dff = dff[dff["Year"] == option_slctd]
        dff = dff[dff["Affected by"] == "Varroa_mites"]

        # Plotly Express
        fig = px.choropleth(
            data_frame=dff,
            locationmode='USA-states',
            locations='state_code',
            scope="usa",
            color='Pct of Colonies Impacted',
            hover_data=['State', 'Pct of Colonies Impacted'],
            color_continuous_scale=px.colors.sequential.YlOrRd,
            labels={'Pct of Colonies Impacted': '% of Bee Colonies'},
            template='plotly_dark'
        )

        return container, fig
    '''

    '''
    #TICKER EXAMPLE
    df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/hello-world-stock.csv')

    app.layout = html.Div([
        html.H1('Stock Tickers'),
        dcc.Dropdown(
            id='my-dropdown',
            options=[
                {'label': 'Tesla', 'value': 'TSLA'},
                {'label': 'Apple', 'value': 'AAPL'},
                {'label': 'Coke', 'value': 'COKE'}
            ],
            value='TSLA'
        ),
        dcc.Graph(id='my-graph')
    ], className="container")
    '''



    return app