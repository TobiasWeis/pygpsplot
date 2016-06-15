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
import sqlite3
import time
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return "pygpsplot. please be nice, this is a private project."

@app.route('/v1/setcoord', methods=['GET'])
def setcoord():
    if request.method == 'GET':
        lat = None
        lon = None

        for key,value in request.args.items():
            if key == 'lat':
                lat = float(request.args.get('lat'))
                print "Got latitude: ", lat
            if key == 'lon':
                lon = float(request.args.get('lon'))
                print "Got longitude: ", lon
        if lat == None or lon == None:
            res = Response(json.dumps({'error' : 'coordinates not proper'}))
            res.status_code = 400
            return res
        else:
            # insert into database using current time
            con = sqlite3.connect('coords.sqlite')
            cur = con.cursor()
            curtime = int(time.time())
            cur.execute("INSERT INTO coords(lat,lon,time) VALUES(%f,%f,%d)" % (lat,lon,curtime))
            con.commit()
            con.close()
            res = Response(json.dumps({'success' : 'coordinates inserted'}))
            res.status_code = 200
            return res


@app.route('/v1/getimagelast', methods=['GET'])
def getimagelast():
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure

    con = sqlite3.connect('coords.sqlite')
    cur = con.cursor()
    curtime = int(time.time())
    cur.execute("SELECT * FROM coords ORDER BY id DESC LIMIT 1")
    data = cur.fetchone()
    lat = data[1]
    lon = data[2]
    curtime = data[3]
    con.close()

    zoom = 6
    margin_lat = 0.001
    margin_lon = 0.001
    width = 10
    height = 10

    if request.method == 'GET':
        for key,value in request.args.items():
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

@app.route('/v1/getwebsite', methods=['GET'])
def getwebsite():
    height = '250px'
    if request.method == 'GET':
        for key,value in request.args.items():
            if key == 'height':
                height = request.args.get('height')

    # get last coordinates from database
    con = sqlite3.connect('coords.sqlite')
    cur = con.cursor()
    curtime = int(time.time())
    cur.execute("SELECT * FROM coords ORDER BY id DESC LIMIT 1")
    data = cur.fetchone()
    lat = "%f" % data[1]
    clat = "%f" % (data[1] + 0.05)
    lon = "%f" % data[2]
    curtime = datetime.datetime.fromtimestamp(int(data[3])).strftime('%d.%m.%Y - %H:%M')
    #curtime = "%d" % data[3]
    con.close()

    name ="Team /AFK"

    website = "<!DOCTYPE HTML><html><head> \r\n"
    website += "<script type=\"text/javascript\"> \r\n"
    website += "function initMap() { \r\n"
    website += "var curpos = {lat: %s, lng: %s}; \r\n" % (lat,lon)
    website += "var map = new google.maps.Map(document.getElementById('map'), { \r\n"
    website += "zoom: 6, \r\n"
    website += "center: {lat: %s, lng:%s} \r\n" % (clat,lon)
    website += "}); \r\n"
    website += "var contentString = '<div id=\"content\">'+ \r\n"
    website += "'<div id=\"siteNotice\">'+ \r\n"
    website += "'</div>'+ \r\n"
    website += "'<div id=\"bodyContent\" style=\"text-align:center;\">'+ \r\n"
    website += "'<span><b>%s</b></span><br />'+ \r\n" % (curtime)
    website += "'<img src=\"http://s379089165.online.de/teamafk/wp-content/uploads/2015/09/afk_logo_small.png\" style=\"width:80px;\"/>'+ \r\n"
    #website += "'<p>%s</p>'+ \r\n" % (curtime)
    website += "'</div>'+ \r\n"
    website += "'</div>'; \r\n"
    website += "var infowindow = new google.maps.InfoWindow({ \r\n"
    website += "content: contentString \r\n"
    website += "}); \r\n"
    website += "var marker = new google.maps.Marker({ \r\n"
    website += "position: curpos, \r\n"
    website += "map: map, \r\n"
    website += "title: '%s' \r\n" % (name)
    website += "}); \r\n"
    website += "marker.addListener('click', function() { \r\n"
    website += "infowindow.open(map, marker); \r\n"
    website += "}); \r\n"
    website += "infowindow.open(map, marker); \r\n"
    website += "} \r\n"
    website += "</script> \r\n"
    website += "</head><body>"
    website += "<div id=\"map\" style=\"width:100%%;height:%s;\">" % (height)
    website += "</div><script src=\"http://maps.google.com/maps/api/js?key=AIzaSyCtK5OFzBRsGum9Jt1Mwdc1XHMTCloDVXY&callback=initMap\" type=\"text/javascript\"></script></body></html>" 

    return website, 200, {'Content-Type': 'text/html; charset=utf-8'}

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
    app.run(debug=True, host='0.0.0.0')
