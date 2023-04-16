import pandas as pd
from pathlib import Path
import numpy as np
import plotly.express as px

BASE_PATH = Path(__file__).resolve().parent

data=pd.DataFrame({'latitude': {0: 37.9844383,
  1: 37.987244200000006,
  2: 37.9783811,
  3: 37.9934691,
  4: 37.9842815,
  5: 37.9844383,
  6: 37.9844383,
  7: 39.29853170000001,
  8: 39.29853170000001,
  9: 39.29853170000001,
  10: 38.2280667,
  11: 38.2280667,
  12: 38.0045679,
  13: 37.9944925,
  14: 38.0158537,
  15: 38.0026161,
  16: 37.9823979,
  17: 37.9816306,
  18: 37.9787307,
  19: 37.9755042,
  20: 37.977031200000006,
  21: 37.9824516,
  22: 37.9756512,
  23: 37.9844383,
  24: 37.9755042,
  25: 37.9755042,
  26: 37.9779718,
  27: 37.9734542,
  28: 37.9769393,
  29: 40.6953398},
 'longitude': {0: 23.7281172,
  1: 23.726373100000004,
  2: 23.7805126,
  3: 23.7275065,
  4: 23.7177254,
  5: 23.7281172,
  6: 23.7281172,
  7: 22.3844827,
  8: 22.3844827,
  9: 22.3844827,
  10: 21.7632893,
  11: 21.7632893,
  12: 23.7160906,
  13: 23.7042077,
  14: 23.7268584,
  15: 23.7334402,
  16: 23.6940037,
  17: 23.7281396,
  18: 23.7246486,
  19: 23.73267610000001,
  20: 23.7223758,
  21: 23.730563,
  22: 23.7340008,
  23: 23.7281172,
  24: 23.73267610000001,
  25: 23.73267610000001,
  26: 23.74299580000001,
  27: 23.735698,
  28: 23.743741600000003,
  29: 23.2203643},
 'Available Bikes': {0: 1,
  1: 3,
  2: 4,
  3: 4,
  4: 2,
  5: 4,
  6: 9,
  7: 4,
  8: 4,
  9: 7,
  10: 12,
  11: 9,
  12: 20,
  13: 5,
  14: 15,
  15: 12,
  16: 1,
  17: 4,
  18: 1,
  19: 2,
  20: 1,
  21: 1,
  22: 2,
  23: 3,
  24: 2,
  25: 2,
  26: 1,
  27: 2,
  28: 2,
  29: 1}})



def gen_heatmap(data_pd: pd.DataFrame):

    plot_data = pd.DataFrame(data_pd['geometry.coordinates'].tolist(), columns = ['longitude','latitude'])
    plot_data['Available Bikes'] = data_pd['fields.numbikesavailable']
    plot_data['Station Name'] = data_pd['fields.name']


    fig = px.density_mapbox(plot_data, lat='latitude', lon='longitude', z='Available Bikes',
                            hover_name='Station Name',
                            mapbox_style='carto-positron',
                            radius=50, opacity=0.5)

    fig2 = px.scatter_mapbox(plot_data, lat='latitude', lon='longitude', color='Available Bikes',
                            hover_name='Station Name',
                            mapbox_style='carto-positron')

    trace0 = fig2
    fig.add_trace(trace0.data[0])
    trace0.layout.update(showlegend=False)

    #fig.write_image('/Users/kgreeves/PycharmProjects/velib_open_data/app/static/img/test.png')
    fig.show()


#gen_heatmap()