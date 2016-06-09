#!/usr/bin/python

import smopy
import matplotlib.pyplot as plt

lat = 50.162638
lon = 8.643391

map = smopy.Map((lat-0.01, lon-0.01, lat+0.01, lon+0.01), z=15)
#map = smopy.Map((48.85, 2.32, 48.87, 2.34), z=15)

x, y = map.to_pixels(48.86151, 2.33474)
ax = map.show_mpl(figsize=(8, 6))
ax.plot(x, y, 'or', ms=10, mew=2);

plt.show()

