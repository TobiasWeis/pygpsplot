# pygpsplot

REST-server with python flask and smopy,
supply coordinates and get an image with a pin!
<img src="getimage.png" />

Sample query:

http://restserver:5000/v1/getimage?lat=50.166204&lon=8.658097&zoom=15&width=20&height=10&margin_lat=0.001&margin_lon=0.002

## Clone
smopy is included as a git submodule. to automatically clone it:
<pre>
git clone --recursive https://github.com/TobiasWeis/pygpsplot.git
</pre>

And, for some reason smopy does not come as proper package. If you do not want to install it in the system path,
just create a __init__.py:
<pre>
cd smopy && touch __init__.py
</pre>

## Usage
start server.py

API:
/v1/setcoord?lat=[FLOAT]&lon=[FLOAT]
inserts a geo-coordinate in the sqlite3 database with the current time

/v1/getwebsite?height=250px - get the full html for a website containg a google-map with a custom marker and a info box inside, marker at the latest position in the database

/v1/getimagelast?zoom=[INT]
returns a rendered image with a marker of the last position by matplotlib and smopy, 

/v1/getimage?lat=[FLOAT]&lon=[FLOAT]&zoom=[INT]&margin_lat=[FLOAT]&margin_lon=[FLOAT]
returns a rendered image with a marker on the supplied coordinate
