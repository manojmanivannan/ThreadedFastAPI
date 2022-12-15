from fastapi import FastAPI, APIRouter, Query, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn, json
import numpy as np
import matplotlib.pyplot as plt
import threading
from time import sleep
from typing import Optional, Any
from pathlib import Path
from threading import Thread, Event
from time import sleep
from mpl_toolkits.basemap import Basemap # pip does not include this package, install by downloading the binary from web
# for windows install from wheel https://www.lfd.uci.edu/~gohlke/pythonlibs/#basemap
from geopy.geocoders import Nominatim
import urllib.request as url
import os
port = int(os.environ.get('PORT', 5000)) # add 


iss_url = 'http://api.open-notify.org/iss-now.json'

# 1
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))


app = FastAPI(title="Live ISS Tracker")
app.mount("/content", StaticFiles(directory="content"), name="content")
app.mount("/etc", StaticFiles(directory="etc"), name="etc")

# api_router = APIRouter()

# Updated to serve a Jinja2 template
# https://www.starlette.io/templates/
# https://jinja.palletsprojects.com/en/3.0.x/templates/#synopsis
@app.get("/", status_code=200)
def root(request: Request) -> dict:  # 2
    """
    Root GET
    """
    
    # 3
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, },
    )

@app.get("/about", status_code=200)
def show_page(request: Request) -> dict:
    return TEMPLATES.TemplateResponse(
        "about.html",
        {"request": request, },
    )

class PlotGenerator(Thread):

    def __init__(self, interval):
        self.stop_event = Event()
        self.interval = interval
        super(PlotGenerator, self).__init__()

    def run(self):
         if not self.stop_event.is_set():
            
            try:
                 while not self.stop_event.is_set():
                    self.main()
            except KeyboardInterrupt:
                print('Keyboard interrupt recieved at run')
                # wait self.interval seconds or until the stop_event is set

    def terminate(self):
        self.stop_event.set()

    def get_plot(self):
        
        print('INFO:     Getting Location')
        response = url.urlopen(iss_url)
        json_res = json.loads(response.read())
        geo_location = json_res['iss_position']
        print('INFO:     Location obtained')
        timestamp = json_res['timestamp']
        lon, lat = float(geo_location['longitude']), float(geo_location['latitude'])
        self.gps_location = {'timestamp':timestamp, 'latitude': lat,'longitude': lon}

        self.m = Basemap(projection='ortho',
            lat_0=self.gps_location['latitude'],
            lon_0=self.gps_location['longitude'],
            resolution='c')
        self.m.fillcontinents(color='coral',lake_color='aqua')
        # draw parallels and meridians
        self.m.drawparallels(np.arange(-90.,91.,30.))
        self.m.drawmeridians(np.arange(-180.,181.,60.))
        self.m.drawcountries()
        self.m.drawmapboundary(fill_color='aqua')

        x_pt, y_pt = self.m(self.gps_location['longitude'],self.gps_location['latitude'])
        self.point = self.m.plot(x_pt, y_pt,'bo')[0]
        self.point.set_data(x_pt,y_pt)
        plt.text(x_pt, y_pt, 'Lat:{} Lon:{}'.\
            format(\
                round(self.gps_location['latitude'],2),\
                round(self.gps_location['longitude'],2)))
        plt.tight_layout()
        plt.savefig('content/image.png',dpi=80,transparent=True)
        plt.close()
        print('INFO:     Plot saved')

    def main(self):
        try:
            sleep(3)
            self.get_plot()

        except Exception as e:
            raise e


if __name__ == '__main__':
    # the workers main function is called and then 5 seconds sleep
    worker = PlotGenerator(interval=5)
    worker.start()
    print("Obtained port {} from env".format(port))
    uvicorn.run(app, host="0.0.0.0", port=port, workers=1)
    worker.terminate()

