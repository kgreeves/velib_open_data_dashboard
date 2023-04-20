import requests
import json

from pathlib import Path
from numpy import round

from datetime import datetime

import pandas as pd

from app.modules.api_operations import call_api
from app.modules.postgres_operations import get_latest_bicycle_count
from app.modules.static_analysis import plot_occupancy, plot_bikes_avail

from fastapi import FastAPI, APIRouter, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import FileResponse

from app.modules.web_app import gen_heatmap
from app.static.dash.dashapp import create_dash_app
from app.modules.visualising import col_name_to_text

import matplotlib.pyplot as plt
import seaborn as sns

BASE_URL = 'https://opendata.paris.fr/api/records/1.0/search/?'
BASE_PATH = Path(__file__).resolve().parent


def assess_criticality(percent: float) -> str:
    if percent >= 0.95:
        criticality = 'critical (high)'
    elif 0.90 < percent < 0.95:
        criticality = 'attention (high)'
    elif 0.15 > percent > 0.05:
        criticality = 'attention (low)'
    elif 0.05 >= percent:
        criticality = 'critical (low)'
    else:
        criticality = 'normal'

    return criticality

search_dict = {
    'dataset': 'velib-disponibilite-en-temps-reel',
    'q': '',
    'rows': -1,
    'facet': []
}
app = FastAPI(
    title="Velib' Dashboard and Bayesian Analyses", openapi_url="/openapi.json"
)

# MacOS

app.mount(
    "/app/static",
    StaticFiles(directory=str(str(Path(__file__).parent.absolute()))+"/app/static", html=True),
    name="static",
)
templates = Jinja2Templates(directory=str(Path(__file__).parent.absolute())+"/app/templates")
'''

# Windows
app.mount(
    "/app/static",
    StaticFiles(directory=str(str(Path(__file__).parent.absolute()))+"\\app\\static", html=True),
    name="static",
)
templates = Jinja2Templates(directory=str(Path(__file__).parent.absolute())+"\\app\\templates")
'''

api_router = APIRouter()

@api_router.get("/dashboard.html", status_code=200)
async def root(request: Request):

    current_payload = call_api(BASE_URL, search_dict)
    total_bikes = current_payload['fields.numbikesavailable'].sum()

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request,
         "routes": [
             {"method": "GET", "path": "/", "summary": "Landing"},
             {"method": "GET", "path": "/status", "summary": "App status"},
             {"method": "GET", "path": "/dash", "summary": "Sub-mounted Dash application"},
         ],
         'total_bikes': f'{total_bikes:,}',
         },
    )

@api_router.get("/blank.html", status_code=200)
async def root(request: Request):

    return templates.TemplateResponse(
        "blank.html",
        {"request": request, },
    )

@api_router.get("/api_response_statistics", status_code=200)
async def root(request: Request):

    current_payload = call_api(BASE_URL, search_dict)
    #current_payload = get_latest_bicycle_count()

    current_payload['fields.percent_capacity'] = (
        current_payload['fields.numbikesavailable']/current_payload['fields.capacity']
        .dropna()
    )

    current_payload['fields.percent_capacity'] = (current_payload['fields.percent_capacity']
                                                  .apply(lambda x: round(x, 2))
                                                  )

    current_payload['fields.criticality'] = (current_payload['fields.percent_capacity']
                                             .apply(lambda x: assess_criticality(x))
                                             )

    sns.histplot(data=current_payload, x='fields.percent_capacity')
    plt.savefig(str(BASE_PATH)+'/app/static/img/percent_capacity.png')

    df_timestamp = current_payload['record_timestamp'].iloc[0]
    #df_timestamp = datetime.fromisoformat(df_timestamp.replace('Z', '+00:00'))

    current_payload = (
        current_payload
        [(current_payload['fields.percent_capacity'] > 0.90) |
         (current_payload['fields.percent_capacity'] < 0.15)]
        [['fields.name',
          'fields.percent_capacity',
          'fields.numbikesavailable',
          'fields.ebike',
          'fields.mechanical',
          'fields.capacity',
          'fields.criticality']]
        .dropna()
        .sort_values(by=['fields.percent_capacity',
                         'fields.numbikesavailable'], ascending=False)

    )

    styled_df = current_payload.style.apply(
        lambda x: ['font-weight: bold; color: #f50000'

                   if (type(value) == str and
                       value == 'critical')
                   else '' for i, value in enumerate(x)])

    print(current_payload['fields.criticality'].value_counts())
    critical_count_low = (current_payload
                            [current_payload['fields.criticality'] == 'critical (low)']
                            ['fields.criticality']
                            .count())

    critical_count_high = (current_payload
                            [current_payload['fields.criticality'] == 'critical (high)']
                            ['fields.criticality']
                            .count())


    current_payload.columns = [col_name_to_text(x) for x in current_payload.columns]
    return templates.TemplateResponse(
        "blank.html",
        {"request": request,
         "payload_timestamp": df_timestamp.strftime("%Y-%m-%d, %H:%M"),
         "page_title": 'Data Collected at:',
         'critical_count_low': critical_count_low,
         'critical_count_high': critical_count_high,
         "current_payload": current_payload.to_html(index=False,
                                                    justify='center',
                                                    table_id='capacity-critical')},
    )




@api_router.get("/generate_critcality_table", status_code=200)
async def root(request: Request):
    current_payload = call_api(BASE_URL, search_dict)
    return {"current_payload": current_payload.to_html(index=False,
                                                       justify='center',
                                                       table_id='capacity-critical')}


app.include_router(api_router)



#gen_heatmap(curr_payload_df)

dash_app = create_dash_app(call_api(BASE_URL, search_dict),
                           requests_pathname_prefix="/dash/")
app.mount("/dash", WSGIMiddleware(dash_app.server))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8002, log_level="debug")
    '''
    r = requests.get(generate_q_url(BASE_URL, search_dict))
    payload = json.loads(r.text)
    payload = payload['records']
    curr_payload_df = pd.json_normalize(payload)
    print(curr_payload_df.columns)

    #plot_bikes_avail(curr_payload_df, capacity=None, y_col='fields.mechanical')

    plot_occupancy(curr_payload_df, x_col='fields.capacity', y_col='fields.numbikesavailable')
    '''
