import requests
import json

from pathlib import Path

import pandas as pd

from app.modules.static_analysis import plot_occupancy, plot_bikes_avail

from fastapi import FastAPI, APIRouter, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import FileResponse

from app.modules.web_app import gen_heatmap
from app.static.dash.dashapp import create_dash_app

BASE_URL = 'https://opendata.paris.fr/api/records/1.0/search/?'
BASE_PATH = Path(__file__).resolve().parent

search_dict = {
    'dataset': 'velib-disponibilite-en-temps-reel',
    'q': '',
    'rows': -1,
    'facet': ['name', 'capacity', 'is_installed', 'is_renting', 'is_returning', 'nom_arrondissement_communes']
}

app = FastAPI(
    title="Velib' Dashboard and Bayesian Analyses", openapi_url="/openapi.json"
)

app.mount(
    "/app/static",
    StaticFiles(directory=str(str(Path(__file__).parent.absolute()))+"/app/static", html=True),
    name="static",
)

templates = Jinja2Templates(directory=str(Path(__file__).parent.absolute())+"/app/templates")

api_router = APIRouter()

@api_router.get("/dashboard.html", status_code=200)
async def root(request: Request):

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request,
         "routes": [
             {"method": "GET", "path": "/", "summary": "Landing"},
             {"method": "GET", "path": "/status", "summary": "App status"},
             {"method": "GET", "path": "/dash", "summary": "Sub-mounted Dash application"},
         ]
         },
    )

@api_router.get("/blank.html", status_code=200)
async def root(request: Request):

    return templates.TemplateResponse(
        "blank.html",
        {"request": request, },
    )

app.include_router(api_router)



#gen_heatmap(curr_payload_df)

dash_app = create_dash_app(curr_payload_df, requests_pathname_prefix="/dash/")
app.mount("/dash", WSGIMiddleware(dash_app.server))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001, log_level="debug")
    '''
    r = requests.get(generate_q_url(BASE_URL, search_dict))
    payload = json.loads(r.text)
    payload = payload['records']
    curr_payload_df = pd.json_normalize(payload)
    print(curr_payload_df.columns)

    #plot_bikes_avail(curr_payload_df, capacity=None, y_col='fields.mechanical')

    plot_occupancy(curr_payload_df, x_col='fields.capacity', y_col='fields.numbikesavailable')
    '''

