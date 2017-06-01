""" An example on how to use xsapr_clutter and how to plot the results. """

import glob
import matplotlib
import matplotlib.pyplot as plt
import pyart

from xsapr_clutter import xsapr_clutter

# Retrieving the radar files used for the xsapr_clutter calculation.
files = sorted(glob.glob('/home/usr/xsapr_clutter_project/data/05_02_2013/*'))

# Creating a clutter radar object using the xsapr_clutter import.
clutter_radar = xsapr_clutter(
                    files, reflect_shape=(8200, 600),
                    clutter_thresh_min=0.0002, clutter_thresh_max=1.5,
                    radius=1, write_radar=False, out_file=None)

print(clutter_radar.fields['xsapr_clutter']['data']

# Creating a plot to view the clutter.
ticks = ([0.25, 0.75])
ticklabs = (['No Clutter', 'Clutter'])
title = 'X-SAPR Clutter Elevation Angle 0.5 Degrees'
lab_colors=['cyan', 'red']
cmap = matplotlib.colors.ListedColormap(lab_colors)

fig = plt.figure(figsize=(14, 7))
display = pyart.graph.RadarMapDisplay(clutter_radar)
display.plot_ppi_map('xsapr_clutter', sweep=0, cmap=cmap, ticks=ticks,
                     ticklabs=ticklabs, title=title)
plt.savefig(
    '/home/usr/xsapr_clutter_project/images/xsapr_clutter_05_02_2013_sweep_0.png',
    bbox_inches='tight')
plt.show()
