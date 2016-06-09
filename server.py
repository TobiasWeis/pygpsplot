#!/usr/bin/python
from smopy import smopy
import matplotlib.pyplot as plt
from flask import Flask, request
from flask import Response
from flask import jsonify
from flask import send_file
from flask import make_response
import numpy as np
import json      
import cv2
from io import BytesIO
from matplotlib.offsetbox import OffsetImage, AnnotationBbox   

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/v1/getimage', methods=['GET', 'POST'])
def getimage():
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure

    lat = None
    lon = None
    zoom = 6
    margin_lat = 0.001
    margin_lon = 0.001
    width = 10
    height = 10

    if request.method == 'GET':
        for key,value in request.args.items():

            if key == 'lat':
                lat = float(request.args.get('lat'))
                print "Got latitude: ", lat
            if key == 'lon':
                lon = float(request.args.get('lon'))
                print "Got longitude: ", lon
            if key == 'zoom':
                zoom = int(request.args.get('zoom'))
            if key == 'margin_lat':
                margin_lat = float(request.args.get('margin_lat'))
            if key == 'margin_lon':
                margin_lon = float(request.args.get('margin_lon'))

            if key == 'width':
                width = int(request.args.get('width'))
            if key == 'height':
                height = int(request.args.get('height'))


        if lat == None or lon == None:
            res = Response(json.dumps({'error' : 'coordinates not proper'}))
            res.status_code = 400
            return res
        else:
            # create map and put marker in middle
            map = smopy.Map((lat - margin_lat, lon - margin_lon, lat + margin_lat, lon + margin_lon), z=zoom)

            fig = plt.figure(figsize=(width,height), dpi=100)
            ax = plt.subplot(111)
            plt.xticks([]);
            plt.yticks([]);
            plt.grid(False)
            plt.xlim(0, map.w);
            plt.ylim(map.h, 0)
            plt.axis('off');
            plt.tight_layout();

            map.show_mpl(ax=ax,figsize=(width,height))
            
            coords = map.to_pixels(lat,lon)
            #ax.plot(coords[0], coords[1], 'ro', ms=22)

            import copy
            benz = cv2.imread("Pin.png", -1)
            tmp = copy.copy(benz[:,:,0])
            benz[:,:,0] = benz[:,:,2]
            benz[:,:,2] = tmp
            im = OffsetImage(benz, zoom=1.)
            ab = AnnotationBbox(im, (coords[0]+20,coords[1]-17), xycoords='data', frameon=False)
            ax.add_artist(ab)

            imgo = BytesIO()
            plt.savefig(imgo, format='png', bbox_inches='tight', pad_inches=-1.)
            imgo.seek(0)

            return send_file(imgo, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
