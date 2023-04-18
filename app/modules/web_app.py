import pandas as pd
from pathlib import Path
import plotly.express as px

BASE_PATH = Path(__file__).resolve().parent


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
