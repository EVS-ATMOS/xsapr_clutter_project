# X-SAPR Clutter Project

A project analyzing clutter from an X-Band radar in Oklahoma.

Code defines clutter based on a threshold values and a calculation of
the standard deviation, mean and variance. There is also a circle radius
function that allows for gates surrounding a clutter gate to also be marked
as clutter depending on the radius integer.

Currently checking other fields and components to see if they can be used
to determine if a gate it clutter or not.

To download:
```
git clone https://github.com/zssherman/xsapr_clutter_project.git
```
```
cd xsapr_clutter_project
```
```
python setup.py install
```

To use in the terminal:
```
xsapr_clutter <radar_directory> <out_file>
```

An example:
```
xsapr_clutter '/home/usr/clutter_data/03_05_2012/*' '/home/usr/clutter.nc 
```

There are optional arguments such as radius, and threshold min and max.
This can be changed by adding ```-ra <int> -tmin <float> -tmax <float>``` to
the command line.
