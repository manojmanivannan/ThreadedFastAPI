from threading import Thread, Event
import json
import urllib.request as url
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from time import sleep
import numpy as np

iss_url = 'http://api.open-notify.org/iss-now.json'

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
        plt.savefig('static/images/map.png',dpi=80)
        plt.close()
        print('INFO:     Plot saved')

    def main(self):
        try:
            sleep(3)
            self.get_plot()

        except Exception as e:
            raise e